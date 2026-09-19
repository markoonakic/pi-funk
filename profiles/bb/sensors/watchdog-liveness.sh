#!/usr/bin/env bash
# watchdog-liveness: the only sensor that speaks when something is BROKEN.
#
# It fails loudly (non-zero exit) when:
#   - our automations are disabled or paused
#   - a sensor has not written state within its expected window
#
# Self-contained on purpose: BB script automations run a private snapshot, so a
# sibling lib.sh would not be present. Exit non-zero so BB records a failed run
# and the automation's own last_status/last_error surfaces it. It writes to the
# local log FIRST, because a broken network can prevent any notification.

set -uo pipefail

ROOT="${PI_MAINT_ROOT:-$HOME/.local/state/pi-maintenance}"
STATE="$ROOT/state"
LOGS="$ROOT/logs"
mkdir -p "$STATE" "$LOGS"
LOG="$LOGS/watchdog-liveness.log"

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG"; }

BB_BIN="${BB_CLI:-}"
if [ -z "$BB_BIN" ] || [ ! -x "$BB_BIN" ]; then
  BB_BIN="$(command -v bb || true)"
fi

PROJECT_AGENT="proj_cw8axdqa9y"
problems=()

# --- our automations enabled? ---------------------------------------------

if [ -n "$BB_BIN" ] && [ -x "$BB_BIN" ]; then
  json="$(timeout 30 "$BB_BIN" automation list --project "$PROJECT_AGENT" --json 2>/dev/null)"
  if [ -z "$json" ]; then
    log "could not list automations (bb missing or server unreachable)"
  else
    while IFS= read -r row; do
      name="$(printf '%s' "$row" | jq -r '.name // "?"')"
      case "$name" in
        sensor-*|watchdog-*)
          enabled="$(printf '%s' "$row" | jq -r '.enabled')"
          [ "$enabled" = "true" ] || problems+=("automation disabled: $name")
          ;;
      esac
    done < <(printf '%s' "$json" | jq -c '.[]' 2>/dev/null)
  fi
else
  log "bb CLI not found; skipping automation checks"
fi

# --- sensors fresh? --------------------------------------------------------

check_fresh() {
  local sensor="$1" max_age_h="$2"
  local f="$STATE/${sensor}.json"
  if [ ! -f "$f" ]; then
    problems+=("sensor has never run: $sensor")
    return
  fi
  local mtime now age_h
  mtime="$(stat -c %Y "$f" 2>/dev/null || echo 0)"
  now="$(date +%s)"
  age_h=$(( (now - mtime) / 3600 ))
  if [ "$age_h" -gt "$max_age_h" ]; then
    problems+=("sensor stale: $sensor (${age_h}h > ${max_age_h}h)")
  fi
}

# Daily sensors: alert after 2 days of silence.
check_fresh "sensor-agent-stack" 48
check_fresh "sensor-flake" 48
check_fresh "sensor-sarmica" 2160   # monthly cadence tolerance

# --- verdict ---------------------------------------------------------------

if [ "${#problems[@]}" -eq 0 ]; then
  log "watchdog OK"
  exit 0
fi

{
  printf 'WATCHDOG PROBLEMS (%d):\n' "${#problems[@]}"
  for p in "${problems[@]}"; do printf '  - %s\n' "$p"; done
} | tee -a "$LOG"

exit 1
