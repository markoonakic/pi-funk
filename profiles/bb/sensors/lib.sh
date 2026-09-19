#!/usr/bin/env bash
# Shared library for pi-maintenance sensors.
#
# Contract for every sensor:
#   - nothing changed  -> exit 0 with NO output (BB records a silent skipped tick)
#   - something changed -> exit 0 with one JSON report on stdout
#   - real failure      -> exit non-zero
#
# Transient network errors are logged locally and treated as "no change", so a
# brief outage never wakes the agent.

set -uo pipefail

PI_MAINT_ROOT="${PI_MAINT_ROOT:-$HOME/.local/state/pi-maintenance}"
PI_MAINT_STATE="$PI_MAINT_ROOT/state"
PI_MAINT_LOGS="$PI_MAINT_ROOT/logs"
NIXOS_MACHINES="${NIXOS_MACHINES:-$HOME/Projects/nixos-machines}"
PI_CONFIG="${PI_CONFIG:-$HOME/.config/pi}"

mkdir -p "$PI_MAINT_STATE" "$PI_MAINT_LOGS"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" \
    >>"$PI_MAINT_LOGS/${SENSOR_NAME:-sensor}.log"
}

state_file() { printf '%s/%s.json' "$PI_MAINT_STATE" "${SENSOR_NAME}"; }

# Print the stored value for a key (empty if absent).
state_get() {
  local f
  f="$(state_file)"
  [ -f "$f" ] || return 0
  jq -r --arg k "$1" '.[$k] // empty' "$f" 2>/dev/null || true
}

# Atomically set one key. Key must be a simple identifier.
state_set() {
  local f tmp
  f="$(state_file)"
  tmp="$(mktemp)"
  if ! jq -e . "$f" >/dev/null 2>&1; then
    printf '{}\n' >"$f"
  fi
  if jq --arg k "$1" --arg v "$2" '.[$k] = $v' "$f" >"$tmp" 2>/dev/null; then
    mv "$tmp" "$f"
  else
    rm -f "$tmp"
    log "state_set failed for $1"
  fi
}

# Record a key/value and report whether it differs from the previous value.
# Always stores. Prints: baseline | changed | same
observe() {
  local key="$1" value="$2" prev
  prev="$(state_get "$key")"
  state_set "$key" "$value"
  if [ -z "$prev" ]; then printf 'baseline'
  elif [ "$prev" != "$value" ]; then printf 'changed'
  else printf 'same'
  fi
}

FINDINGS_FILE=""
_findings_init() { FINDINGS_FILE="$(mktemp)"; }

# Record a finding. Only meaningful when the sensor will report.
# args: id component kind current available risk action [title] [summary] [detail]
#
# `title`, `summary`, and `detail` are the HUMAN fields the dashboard shows.
# `current`/`available` are technical and stay hidden behind a disclosure, so a
# raw 40-character revision never clutters the main view.
add_finding() {
  [ -n "$FINDINGS_FILE" ] || _findings_init
  jq -nc \
    --arg id "${1:-}" --arg component "${2:-}" --arg kind "${3:-}" \
    --arg current "${4:-}" --arg available "${5:-}" \
    --arg risk "${6:-}" --arg action "${7:-}" \
    --arg title "${8:-}" --arg summary "${9:-}" --arg detail "${10:-}" \
    '{id:$id,component:$component,kind:$kind,current:$current,available:$available,
      risk:$risk,action:$action,
      title:(if $title=="" then $component else $title end),
      summary:(if $summary=="" then $action else $summary end),
      detail:$detail}' \
    >>"$FINDINGS_FILE"
}

# True when a value looks like a raw hash/revision rather than a version.
is_hashy() {
  case "$1" in
    *[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*) [ "${#1}" -ge 32 ] ;; 
    *) return 1 ;;
  esac
}

# A short, human way to refer to a revision: "a1b2c3d" or "updated".
short_ref() {
  if is_hashy "$1"; then printf '%s' "${1:0:7}"; else printf '%s' "$1"; fi
}

# If any findings were recorded, emit the report and exit 0. Otherwise exit 0
# silently (the run is recorded as skipped by BB).
finish() {
  [ -n "$FINDINGS_FILE" ] || exit 0
  if [ ! -s "$FINDINGS_FILE" ]; then exit 0; fi
  jq -sc \
    --arg sensor "${SENSOR_NAME:-unknown}" \
    --arg checked "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{sensor:$sensor,checked:$checked,findings:.}' <"$FINDINGS_FILE"
  rm -f "$FINDINGS_FILE"
  exit 0
}
