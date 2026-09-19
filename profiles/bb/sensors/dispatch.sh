#!/usr/bin/env bash
# dispatch.sh — run one sensor, record findings, and notify the owner thread.
#
# This is what the BB script automations actually invoke. Sensors stay pure and
# testable; this handles the plumbing:
#
#   sensor output (JSON) -> ledger ingest -> owner thread notify (only on change)
#
# Prints nothing when the sensor finds nothing, so the run is recorded as a
# silent skipped tick by BB.
#
# Usage: dispatch.sh <sensor-name>   or   SENSOR=<name> dispatch.sh

set -uo pipefail
# BB script automations pass configuration as environment variables (--env-json),
# not arguments, so accept both.
SENSOR="${1:-${SENSOR:-}}"
if [ -z "$SENSOR" ]; then
  echo "usage: dispatch.sh <sensor-name>  (or set SENSOR)" >&2
  exit 2
fi

SENSORS_DIR="${PI_MAINT_SENSORS_DIR:-$HOME/.config/pi/profiles/bb/sensors}"
ROOT="${PI_MAINT_ROOT:-$HOME/.local/state/pi-maintenance}"
LOG="$ROOT/logs/dispatch.log"
mkdir -p "$ROOT/logs"

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG"; }

# The owner thread that receives notifications. Kept in a file so it can be
# changed without editing this script.
OWNER_FILE="$ROOT/owner-thread"
OWNER_THREAD=""
[ -f "$OWNER_FILE" ] && OWNER_THREAD="$(head -1 "$OWNER_FILE" | tr -d '[:space:]')"

# Resolve the bb CLI. BB_CLI is injected by the automation plugin when it can
# find bb; fall back to PATH.
BB_BIN="${BB_CLI:-}"
if [ -z "$BB_BIN" ] || [ ! -x "$BB_BIN" ]; then
  BB_BIN="$(command -v bb || true)"
fi

REPORT="$(timeout 600 "$SENSORS_DIR/$SENSOR.sh" 2>>"$LOG")"
rc=$?

# Non-zero from a sensor is a real failure: surface it.
if [ "$rc" -ne 0 ]; then
  log "$SENSOR exited $rc"
  if [ -n "$REPORT" ]; then
    printf '%s\n' "$REPORT"
    exit 0   # report is the payload; do not double-fail the automation
  fi
  exit "$rc"
fi

# No output -> nothing changed -> silent skipped tick.
if [ -z "$REPORT" ]; then
  exit 0
fi

# Record findings in the ledger.
REPORT_FILE="$(mktemp)"
printf '%s' "$REPORT" >"$REPORT_FILE"
if [ -n "$BB_BIN" ] && [ -x "$BB_BIN" ]; then
  if out="$("$BB_BIN" maintenance ingest "$REPORT_FILE" 2>&1)"; then
    log "$SENSOR: $out"
  else
    log "$SENSOR: ingest failed: $out"
  fi
fi
rm -f "$REPORT_FILE"

# Build the terse digest: one message per wake, never per item.
SUMMARY="$(printf '%s' "$REPORT" | jq -r '
  "Maintenance — \(.findings | length) item(s) from \(.sensor)\n" +
  ([.findings[] | "• \(.component): \(.current) → \(.available) [\(.risk)]"] | join("\n")) +
  "\n→ /plugins/maintenance"
' 2>/dev/null)"

[ -n "$SUMMARY" ] || SUMMARY="Maintenance: $SENSOR reported changes. → /plugins/maintenance"

# Notify the owner thread, if one is configured.
if [ -n "$BB_BIN" ] && [ -x "$BB_BIN" ] && [ -n "$OWNER_THREAD" ]; then
  if out="$("$BB_BIN" thread tell "$OWNER_THREAD" "$SUMMARY" 2>&1)"; then
    log "$SENSOR: notified $OWNER_THREAD"
  else
    log "$SENSOR: notify failed: $out"
    printf '%s\n' "$SUMMARY"
  fi
else
  # No owner configured yet: print so the run is visible.
  printf '%s\n' "$SUMMARY"
fi
