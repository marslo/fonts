#!/usr/bin/env bash
# =============================================================================
#      FileName : build.sh
#        Author : marslo
#       Created : 2026-09-04 04:48:29
#    LastChange : 2026-09-04 04:59:48
# =============================================================================
# build the ligaturized IBM Plex Mono ( IBMPlexMonoLig ) — the complex half of the Blex pipeline, kept out of the repo-root build.sh:
#
#   IBMPlexMono/*.otf ( vendor, all-OTF )  +  IBMPlexMonoVar/ ( variable fonts )
#     └─[ blex-book.sh ]─ instance the Book (350) weight ( upright + italic )
#         └─[ ligaturize.sh -> Ligaturizer ]─ + Fira Code ligatures ─▶ IBMPlexMonoLig/
#
# the repo-root build.sh ( patchBlex ) then Nerd-Font-patches IBMPlexMonoLig/ -> IBMPlexMonoLigNF/ via blex-fixnames.py ( keeps Book distinct + names canonical ).
#
# usage: bash Blex/build.sh [ -n | --dry-run ]

set -euo pipefail

HERE="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" && pwd )"
declare -r HERE
declare -r BOOK="${HERE}/blex-book.sh"
# shellcheck disable=SC2155
declare -r ROOT="$( git -C "${HERE}" rev-parse --show-toplevel 2>/dev/null || ( cd "${HERE}/.." && pwd ) )"
declare -r LIGATURIZE="${ROOT}/ligaturize.sh"       # shared, repo-root
declare -r VENDOR="${HERE}/IBMPlexMono"             # all-OTF vendor faces
declare -r LIG="${HERE}/IBMPlexMonoLig"
declare DRYRUN=false

function die()  { printf 'error: %s\n' "${*}" >&2; exit 1; }
function step() { printf '\n\033[1;36m==>\033[0m \033[1m%s\033[0m\n' "${*}"; }
# run a command, or just print it under --dry-run
function run() {
  if "${DRYRUN}"; then printf '   $ %s\n' "${*}"; return 0; fi
  "${@}"
}

for arg in "${@}"; do
  case "${arg}" in
    -n | --dry-run ) DRYRUN=true ;;
    -h | --help    ) printf 'usage: bash Blex/build.sh [ -n | --dry-run ]\n'; exit 0 ;;
    *              ) die "unknown option: ${arg}" ;;
  esac
done

command -v fontforge >/dev/null 2>&1 || die 'fontforge required ( brew install fontforge )'
for f in "${BOOK}" "${LIGATURIZE}"; do
  test -f "${f}" || die "missing: ${f}"
done

# 1. assemble the ligaturize input in a temp dir: the OTF vendor faces + a freshly
#    instanced Book (350) — keeps the committed IBMPlexMono/ pristine
step 'Book ( 350 ) + vendor -> work dir'
WORK="$( mktemp -d )"
trap 'rm -rf "${WORK}"' EXIT
run cp "${VENDOR}"/*.otf "${WORK}/"
run bash "${BOOK}" --to "${WORK}"

# 2. copy Fira Code ligatures ( + calt ) into every face -> IBMPlexMonoLig/
step 'ligaturize ( IBM Plex Mono + Fira Code ) -> IBMPlexMonoLig/'
run rm -f "${LIG}"/*.ttf "${LIG}"/*.otf
run bash "${LIGATURIZE}" --from "${WORK}" --to "${LIG}" --name IBMPlexMonoLig

step 'DONE'
printf 'IBMPlexMonoLig/ rebuilt.\n'

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
