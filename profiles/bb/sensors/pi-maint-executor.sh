#!/usr/bin/env bash
# pi-maint-executor.sh — perform an approved BB/Pi hot-swap OUT OF BAND.
#
# Why this exists: an agent running inside BB cannot restart BB without killing
# its own turn. A `systemd-run --user` transient unit is a SIBLING of bb.service
# under user@1000.service, so restarting bb does not kill this script.
#
# It runs one job file and writes a result file that the owner thread reads.
#
# Usage: pi-maint-executor.sh <job.json>
#
# Job format:
#   {
#     "id": "job-20260919T120000Z",
#     "action": "swap-dropin" | "restart-bb" | "noop",
#     "dropin": "/path/to/drop-in.conf",      # for swap-dropin
#     "expectExecStart": "/nix/store/.../bb-app"  # assert after start
#   }
#
# Safety: never activates NixOS, never touches Sarmica, never runs GC.

set -uo pipefail

JOB="${1:-}"
ROOT="${PI_MAINT_ROOT:-$HOME/.local/state/pi-maintenance}"
LOGS="$ROOT/logs"
RESULTS="$ROOT/results"
mkdir -p "$LOGS" "$RESULTS"
LOG="$LOGS/executor.log"

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG"; }

# sqlite3 may not be on PATH until the next Home Manager rebuild exposes it.
# Prefer a pinned local copy so backups and migration checks work today.
if ! command -v sqlite3 >/dev/null 2>&1 && [ -x "$ROOT/bin/sqlite3" ]; then
  PATH="$ROOT/bin:$PATH"
  export PATH
fi

fail() {
  local id="${1:-unknown}" msg="$2"
  log "FAIL($id): $msg"
  printf '{"id":"%s","ok":false,"error":%s}\n' "$id" "$(printf '%s' "$msg" | jq -R .)" \
    >"$RESULTS/$id.json"
  exit 1
}

[ -n "$JOB" ] || { echo "usage: pi-maint-executor.sh <job.json>" >&2; exit 2; }
[ -f "$JOB" ] || fail "unknown" "job file not found: $JOB"

ID="$(jq -r '.id // "job-unknown"' "$JOB")"
ACTION="$(jq -r '.action // "noop"' "$JOB")"
DROPIN="$(jq -r '.dropin // empty' "$JOB")"
EXPECT="$(jq -r '.expectExecStart // empty' "$JOB")"

log "start $ID action=$ACTION"

# --- backup bb.db and thread state before any BB restart -------------------

backup() {
  local dest="$ROOT/backups/bb/$ID"
  mkdir -p "$dest" || return 1
  # Never fill the disk with a backup: require 5 GB free.
  local avail_kb
  avail_kb="$(df -Pk "$HOME" | awk 'NR==2 {print $4}')"
  if [ "${avail_kb:-0}" -lt 5242880 ]; then
    log "backup skipped: less than 5GB free"
    return 1
  fi
  # sqlite3 may be absent from PATH until a rebuild; fall back to the pinned copy.
  local sq="sqlite3"
  if ! command -v sqlite3 >/dev/null 2>&1 && [ -x "$ROOT/bin/sqlite3" ]; then
    sq="$ROOT/bin/sqlite3"
  fi
  if command -v "$sq" >/dev/null 2>&1 || [ -x "$sq" ]; then
    "$sq" "$HOME/.bb/bb.db" ".backup '$dest/bb.db'" || return 1
    "$sq" "$dest/bb.db" "PRAGMA integrity_check;" >/dev/null || return 1
    log "bb.db backed up to $dest"
  else
    # A copied live WAL database is not a safe backup, so refuse rather than
    # produce a corrupt one.
    log "backup skipped: sqlite3 not installed"
    return 1
  fi
  return 0
}

case "$ACTION" in
  swap-dropin)
    [ -n "$DROPIN" ] || fail "$ID" "swap-dropin requires dropin"
    [ -f "$DROPIN" ] || fail "$ID" "drop-in not found: $DROPIN"

    backup || log "proceeding without a fresh db backup (see above)"

    DEST="$HOME/.config/systemd/user/bb.service.d/70-intended.conf"
    cp "$DROPIN" "$DEST" || fail "$ID" "cannot write $DEST"
    log "installed $DEST"

    # Remove a volatile override if it is shadowing the intended state.
    VOLATILE="/run/user/$(id -u)/systemd/user/bb.service.d/99-workflow-fork-test.conf"
    [ -f "$VOLATILE" ] && { rm -f "$VOLATILE" && log "removed volatile $VOLATILE"; }

    systemctl --user daemon-reload || fail "$ID" "daemon-reload failed"
    systemctl --user restart bb || fail "$ID" "bb restart failed"
    ;;

  restart-bb)
    backup || log "proceeding without a fresh db backup (see above)"
    systemctl --user restart bb || fail "$ID" "bb restart failed"
    ;;

  noop)
    log "noop"
    ;;

  *)
    fail "$ID" "unknown action: $ACTION"
    ;;
esac

# --- verify the effective executable --------------------------------------

sleep 3
EFFECTIVE="$(systemctl --user show bb -p ExecStart --value 2>/dev/null \
  | grep -oE 'path=[^ ;]+' | head -1 | cut -d= -f2)"
ACTIVE="$(systemctl --user is-active bb 2>/dev/null)"

if [ -n "$EXPECT" ] && [ "$EFFECTIVE" != "$EXPECT" ]; then
  fail "$ID" "effective ExecStart is $EFFECTIVE, expected $EXPECT"
fi
if [ "$ACTIVE" != "active" ]; then
  fail "$ID" "bb is $ACTIVE after restart"
fi

log "ok $ID active=$ACTIVE effective=$EFFECTIVE"
printf '{"id":"%s","ok":true,"action":"%s","active":"%s","effective":%s}\n' \
  "$ID" "$ACTION" "$ACTIVE" "$(printf '%s' "$EFFECTIVE" | jq -R .)" \
  >"$RESULTS/$ID.json"

# Tell the owner thread if one is configured.
OWNER_FILE="$ROOT/owner-thread"
BB_BIN="${BB_CLI:-$(command -v bb || true)}"
if [ -f "$OWNER_FILE" ] && [ -n "$BB_BIN" ] && [ -x "$BB_BIN" ]; then
  OWNER="$(head -1 "$OWNER_FILE" | tr -d '[:space:]')"
  "$BB_BIN" thread tell "$OWNER" \
    "Applied $ID ($ACTION). BB is $ACTIVE and running the intended build. → /plugins/maintenance" \
    >/dev/null 2>&1 || log "notify failed"
fi

exit 0
