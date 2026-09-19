#!/usr/bin/env bash
# watchdog-liveness: the only sensor that speaks when something is BROKEN.
#
# It fails loudly (non-zero exit) when:
#   - the maintenance automations are disabled or paused
#   - a sensor has not produced a state update within its expected window
#
# Exit non-zero so BB records a failed run and the automation's own
# last_status/last_error surfaces it. It also writes to the local log first,
# because a broken network can prevent any notification.

set -uo pipefail
SENSOR_NAME="watchdog-liveness"
# shellcheck source=lib.sh
. "$(dirname "$0")/lib.sh"

BB_CLI_BIN="${BB_CLI:-$(command -v bb || true)}"
PROJECT_AGENT="proj_cw8axdqa9y"
PROJECT_NIXOS="proj_vhqzipxwvz"

problems=()

# --- automations healthy? --------------------------------------------------

if [ -n "$BB_CLI_BIN" ] && [ -x "$BB_CLI_BIN" ]; then
  for proj in "$PROJECT_AGENT" "$PROJECT_NIXOS"; do
    json="$(timeout 30 "$BB_CLI_BIN" automation list --project "$proj" --json 2>/dev/null)" || {
      log "could not list automations for $proj"
      continue
    }
    [ -n "$json" ] || continue
    while IFS= read -r row; do
      name="$(printf '%s' "$row" | jq -r '.name // "?"')"
      # Only our sensors need liveness checking; ignore unrelated automations.
      case "$name" in
        sensor-*|watchdog-*)
          enabled="$(printf '%s' "$row" | jq -r '.enabled')"
          if [ "$enabled" != "true" ]; then
            problems+=("automation disabled: $name")
          fi
          ;;
      esac
    done < <(printf '%s' "$json" | jq -c '.[]' 2>/dev/null)
  done
fi

# --- sensors fresh? --------------------------------------------------------

# Each sensor writes state on success. If a sensor's state file is older than
# its window, it is stale.
check_fresh() {
  local sensor="$1" max_age_h="$2"
  local f="$PI_MAINT_STATE/${sensor}.json"
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
check_fresh "sensor-sarmica" 2160   # monthly, 90 days

# --- verdict ---------------------------------------------------------------

if [ "${#problems[@]}" -eq 0 ]; then
  log "watchdog OK"
  exit 0
fi

{
  printf 'WATCHDOG PROBLEMS (%d):\n' "${#problems[@]}"
  for p in "${problems[@]}"; do printf '  - %s\n' "$p"; done
} | tee -a "$PI_MAINT_LOGS/${SENSOR_NAME}.log"

exit 1
