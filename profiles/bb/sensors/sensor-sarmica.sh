#!/usr/bin/env bash
# sensor-sarmica: detect new upstream releases for the Sarmica production stacks.
#
# Sarmica images are pinned by IMMUTABLE digest, so watching digests can never
# fire. The real signal is a newer upstream release for the products in
# hosts/sarmica/README.md: Pangolin, Gerbil, Forgejo, Traefik, PostgreSQL.
#
# Reports only. Sarmica changes are always human-approved and human-applied.
# Silent when nothing changed; transient network errors are not failures.

set -uo pipefail
SENSOR_NAME="sensor-sarmica"
# shellcheck source=lib.sh
. "$(dirname "$0")/lib.sh"

SARMICA="$NIXOS_MACHINES/hosts/sarmica"
README="$SARMICA/README.md"

# Latest release tag from the GitHub API. Empty on any non-200 (transient).
gh_latest_release() {
  local owner_repo="$1" out code
  out="$(timeout 30 curl -sS -w '\n%{http_code}' \
    "https://api.github.com/repos/${owner_repo}/releases/latest" 2>/dev/null)" || {
    log "curl failed for $owner_repo"; return 0; }
  code="$(printf '%s' "$out" | tail -1)"
  if [ "$code" != "200" ]; then log "github api $code for $owner_repo"; return 0; fi
  printf '%s' "$out" | sed '$d' | jq -r '.tag_name // empty' 2>/dev/null
}

# Read the currently-selected version for a product from the README table.
pinned_in_readme() {
  local product="$1"
  [ -f "$README" ] || return 0
  # Rows look like: | Pangolin EE+PostgreSQL | [`1.21.1`](...) | ...
  # Forgejo has a suffix: [`16.0.3-rootless`](...)
  grep -F "$product" "$README" 2>/dev/null \
    | grep -oE '`v?[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 \
    | tr -d '`' | sed 's/^v//'
}

check_product() {
  local key="$1" product="$2" owner_repo="$3"
  local pinned latest
  pinned="$(pinned_in_readme "$product")"
  latest="$(gh_latest_release "$owner_repo")"
  latest="${latest#v}"
  [ -n "$latest" ] || return 0
  prev="$(state_get "$key")"
  case "$(observe "$key" "$latest")" in
    baseline)
      log "$key baseline: pinned=$pinned latest=$latest"
      if [ -n "$pinned" ] && [ "${pinned#v}" != "$latest" ]; then
        add_finding "$key" "$product" "release" \
          "${pinned#v}" "$latest" "review" \
          "Sarmica production: resolve tag to immutable linux/amd64 digest, verify signature, human-approved only"
      fi
      ;;
    changed)
      if [ -n "$pinned" ] && [ "${pinned#v}" != "$latest" ]; then
        add_finding "$key" "$product" "release" \
          "${pinned#v}" "$latest" "review" \
          "Sarmica production: resolve tag to immutable linux/amd64 digest, verify signature, human-approved only"
      else
        log "$key upstream release list changed (latest=$latest, pinned=${pinned:-?})"
      fi
      ;;
  esac
}

check_product "sarmica_pangolin" "Pangolin" "fosrl/pangolin"
check_product "sarmica_gerbil" "Gerbil" "fosrl/gerbil"
check_product "sarmica_badger" "Badger plugin" "fosrl/badger"

# Forgejo and Traefik/PostgreSQL are not all on GitHub releases; check the
# Forgejo codeberg project's latest tag via its API.
forgejo_latest() {
  local out code
  out="$(timeout 30 curl -sS -w '\n%{http_code}' \
    "https://codeberg.org/api/v1/repos/forgejo/forgejo/releases?limit=1" 2>/dev/null)" || {
    log "codeberg curl failed"; return 0; }
  code="$(printf '%s' "$out" | tail -1)"
  [ "$code" = "200" ] || { log "codeberg api $code"; return 0; }
  printf '%s' "$out" | sed '$d' | jq -r '.[0].tag_name // empty' 2>/dev/null
}

fj_pinned="$(pinned_in_readme "Forgejo rootless")"
fj_latest="$(forgejo_latest)"
fj_latest="${fj_latest#v}"
if [ -n "$fj_latest" ]; then
  prev="$(state_get "sarmica_forgejo")"
  case "$(observe "sarmica_forgejo" "$fj_latest")" in
    baseline)
      log "forgejo baseline: pinned=$fj_pinned latest=$fj_latest"
      if [ -n "$fj_pinned" ] && [ "$fj_pinned" != "$fj_latest" ]; then
        add_finding "sarmica_forgejo" "Forgejo" "release" \
          "$fj_pinned" "$fj_latest" "review" \
          "Sarmica production: match exact registry indexes, human-approved only"
      fi
      ;;
    changed)
      if [ -n "$fj_pinned" ] && [ "$fj_pinned" != "$fj_latest" ]; then
        add_finding "sarmica_forgejo" "Forgejo" "release" \
          "$fj_pinned" "$fj_latest" "review" \
          "Sarmica production: match exact registry indexes, human-approved only"
      fi
      ;;
  esac
fi

finish
