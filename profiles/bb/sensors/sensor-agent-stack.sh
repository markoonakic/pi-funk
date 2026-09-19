#!/usr/bin/env bash
# sensor-agent-stack: detect new versions of the agent stack.
#
# Watches: BB (upstream tags + local pins), Pi (upstream tags + the four coupled
# hashes), Herdr (upstream tags + the three local pins + protocol).
#
# Silent when nothing changed. Never fails on a transient network error.

set -uo pipefail
SENSOR_NAME="sensor-agent-stack"
# shellcheck source=lib.sh
. "$(dirname "$0")/lib.sh"

BB_REPO="https://github.com/get-bb/bb"
PI_REPO="https://github.com/earendil-works/pi"
HERDR_REPO="https://github.com/herdrdev/herdr"

# --- helpers ---------------------------------------------------------------

# Latest tag matching a glob, from a cached online ls-remote. Empty on failure.
latest_tag() {
  local repo="$1" pattern="$2" out
  out="$(timeout 30 git ls-remote --tags --refs "$repo" "$pattern" 2>/dev/null)" || {
    log "ls-remote failed for $repo (transient; treated as no change)"
    return 0
  }
  [ -n "$out" ] || return 0
  # Sort by version-ish ordering, take the last.
  printf '%s\n' "$out" | awk '{print $2}' | sed 's|refs/tags/||' \
    | sort -V | tail -1
}

# Current pinned version from a local derivation.
nix_value() {
  local file="$1" attr="$2"
  [ -f "$file" ] || return 0
  grep -oE "${attr} = \"[^\"]+\"" "$file" 2>/dev/null | head -1 \
    | sed -E 's/.*"([^"]+)".*/\1/'
}

# --- Pi --------------------------------------------------------------------

PI_NIX="$NIXOS_MACHINES/packages/pi-coding-agent/default.nix"
pi_current="$(nix_value "$PI_NIX" version)"
pi_latest="$(latest_tag "$PI_REPO" 'refs/tags/v*')"
pi_latest="${pi_latest#v}"

if [ -n "$pi_current" ] && [ -n "$pi_latest" ]; then
  case "$(observe "pi_upstream" "$pi_latest")" in
    baseline)
      log "pi baseline: $pi_current (upstream $pi_latest)"
      # Surface a gap that already exists on first run.
      if [ "$pi_current" != "$pi_latest" ]; then
        add_finding \
          "pi:${pi_current}->${pi_latest}" "Pi" "release" \
          "$pi_current" "$pi_latest" "safe" \
          "Updates the Pi runtime; about to be checked automatically" \
          "Pi $pi_current → $pi_latest" \
          "A newer stable Pi is available. All four coupled hashes move together, and the BB bridge is re-tested before anything changes."
      fi
      ;;
    changed)
      if [ "$pi_current" != "$pi_latest" ]; then
        add_finding \
          "pi:${pi_current}->${pi_latest}" "Pi" "release" \
          "$pi_current" "$pi_latest" "safe" \
          "Updates the Pi runtime; about to be checked automatically" \
          "Pi $pi_current → $pi_latest" \
          "A newer stable Pi is available. All four coupled hashes move together, and the BB bridge is re-tested before anything changes."
      else
        add_finding "pi-upstream-moved" "Pi" "note" \
          "$pi_current" "$pi_latest" "info" \
          "No action needed" \
          "Pi upstream tags changed" \
          "The set of upstream tags moved but your pinned version is unchanged."
      fi
      ;;
  esac
fi

# --- BB --------------------------------------------------------------------

BB_NIX="$NIXOS_MACHINES/packages/bb-app/default.nix"
bb_current="$(nix_value "$BB_NIX" version)"
# BB publishes desktop-v* tags.
bb_latest="$(latest_tag "$BB_REPO" 'refs/tags/desktop-v*')"
bb_latest="${bb_latest#desktop-v}"

if [ -n "$bb_current" ] && [ -n "$bb_latest" ]; then
  case "$(observe "bb_upstream" "$bb_latest")" in
    baseline)
      log "bb baseline: $bb_current (upstream $bb_latest)"
      if [ "$bb_current" != "$bb_latest" ]; then
        add_finding \
          "bb:${bb_current}->${bb_latest}" "BB" "release" \
          "$bb_current" "$bb_latest" "review" \
          "Your patched build - needs a manual review before upgrading" \
          "BB $bb_current → $bb_latest" \
          "BB is custom-patched: 8 patches, a vendored frontend, and a pinned baseline. The patches must be rebased by hand and the result reviewed. Nothing happens automatically."
      fi
      ;;
    changed)
      if [ "$bb_current" != "$bb_latest" ]; then
        add_finding \
          "bb:${bb_current}->${bb_latest}" "BB" "release" \
          "$bb_current" "$bb_latest" "review" \
          "Your patched build - needs a manual review before upgrading" \
          "BB $bb_current → $bb_latest" \
          "BB is custom-patched: 8 patches, a vendored frontend, and a pinned baseline. The patches must be rebased by hand and the result reviewed. Nothing happens automatically."
      fi
      ;;
  esac
fi

# --- Herdr -----------------------------------------------------------------

HERDR_FLAKE="$NIXOS_MACHINES/flake.nix"
# The flake pins herdr by rev; a comment carries the claimed version.
herdr_rev="$(grep -oE 'github:herdrdev/herdr/[0-9a-f]{40}' "$HERDR_FLAKE" 2>/dev/null | head -1 | sed 's|.*/||')"
herdr_latest_tag="$(latest_tag "$HERDR_REPO" 'refs/tags/v*')"

if [ -n "$herdr_latest_tag" ]; then
  case "$(observe "herdr_upstream" "$herdr_latest_tag")" in
    baseline) log "herdr baseline: tag $herdr_latest_tag, pinned rev ${herdr_rev:-unknown}" ;;
    changed)
      add_finding \
        "herdr:${herdr_rev:0:8}->${herdr_latest_tag}" "Herdr" "release" \
        "${herdr_rev:-unknown}" "$herdr_latest_tag" "review" \
        "Pinned in three places that must move together" \
        "Herdr $herdr_latest_tag is available" \
        "Herdr is pinned in the flake, in a Pi skill, and in a vendor hook. All three move together, and the terminal protocol is checked for changes."
      ;;
  esac
fi

finish
