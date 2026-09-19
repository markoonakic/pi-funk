#!/usr/bin/env bash
# sensor-flake: detect movement in the nixos-machines flake inputs.
#
# Ref/rev-based inputs are compared against upstream, because
# `nix flake metadata` on a rev pin compares a rev to itself and never fires.
#
# Silent when nothing changed. Never fails on a transient network error.

set -uo pipefail
SENSOR_NAME="sensor-flake"
# shellcheck source=lib.sh
. "$(dirname "$0")/lib.sh"

FLAKE="$NIXOS_MACHINES/flake.nix"

# Latest rev of a branch on GitHub, via the public API (no auth needed, but
# rate-limited; a 403 is treated as transient).
branch_rev() {
  local owner_repo="$1" branch="$2" out code
  out="$(timeout 30 curl -sS -w '\n%{http_code}' \
    "https://api.github.com/repos/${owner_repo}/commits/${branch}" 2>/dev/null)" || {
    log "curl failed for ${owner_repo}@${branch} (transient)"
    return 0
  }
  code="$(printf '%s' "$out" | tail -1)"
  if [ "$code" != "200" ]; then
    log "github api ${code} for ${owner_repo}@${branch} (transient)"
    return 0
  fi
  printf '%s' "$out" | sed '$d' | jq -r '.sha // empty' 2>/dev/null
}

# Check one rev-pinned or branch-tracking input.
check_input() {
  local key="$1" label="$2" owner_repo="$3" branch="$4" input_name="$5"
  local remote prev
  remote="$(branch_rev "$owner_repo" "$branch")"
  [ -n "$remote" ] || return 0
  prev="$(state_get "$key")"
  case "$(observe "$key" "$remote")" in
    baseline)
      log "$key baseline: $remote"
      # Only report on first run when the local lock actually trails.
      if command -v jq >/dev/null && [ -f "$NIXOS_MACHINES/flake.lock" ]; then
        local locked
        locked="$(jq -r --arg n "$input_name" '.nodes[$n].locked.rev // empty' \
          "$NIXOS_MACHINES/flake.lock" 2>/dev/null)"
        if [ -n "$locked" ] && [ "$locked" != "$remote" ]; then
          add_finding "$key" "$label" "flake-input" \
            "$locked" "$remote" "safe" \
            "Locked rev differs from upstream; build and diff before applying"
        fi
      fi
      ;;
    changed)
      add_finding "$key" "$label" "flake-input" \
        "${prev:-unknown}" "$remote" "safe" \
        "Flake input moved; build disko+sarmica+pi and diff the closure before applying"
      ;;
  esac
}

check_input "nixpkgs_unstable" "nixpkgs (unstable)" "NixOS/nixpkgs" "nixos-unstable" "nixpkgs"
check_input "nixpkgs_sarmica" "nixpkgs (sarmica 26.05)" "NixOS/nixpkgs" "nixos-26.05" "nixpkgs-sarmica"
check_input "home_manager" "home-manager" "nix-community/home-manager" "master" "home-manager"
check_input "sops_nix" "sops-nix" "Mic92/sops-nix" "master" "sops-nix"

# Record the local lock for drift detection (does not itself notify).
if [ -f "$NIXOS_MACHINES/flake.lock" ]; then
  lock_hash="$(sha256sum "$NIXOS_MACHINES/flake.lock" | awk '{print $1}')"
  cur="$(state_get "flake_lock_sha")"
  if [ -n "$cur" ] && [ "$cur" != "$lock_hash" ]; then
    add_finding "flake-lock-drift" "nixos-machines" "note" \
      "$cur" "$lock_hash" "info" \
      "flake.lock changed locally; confirm it is intended and CI-clean"
  fi
  state_set "flake_lock_sha" "$lock_hash"
fi

finish
