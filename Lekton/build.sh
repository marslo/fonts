#!/usr/bin/env bash
# =============================================================================
#      FileName : build.sh
#        Author : marslo
#       Created : 2026-09-04 04:12:03
#    LastChange : 2026-09-04 04:12:56
# =============================================================================
# build the ligaturized desktop Lekton ( LektonLig ) — the complex half of the Lekton pipeline, kept out of the repo-root build.sh:
#
#   Lekton-{Regular,Bold,Italic}.ttf
#     └─[ bolditalic.py ]─ synth Bold Italic
#         └─[ dotzero.py ]─ dot 0   └─[ glyphfix.py --square ]─ enlarge • + add ^ `   ( optimized, temp )
#             └─[ ligaturize.sh -> Ligaturizer ]─ + Fira Code ligatures ─▶ LektonLig/
#
# the repo-root build.sh ( patchLekton ) then Nerd-Font-patches LektonLig/ -> LektonLigNF/.
#
# usage: bash Lekton/build.sh [ -n | --dry-run ]

set -euo pipefail

HERE="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" && pwd )"
declare -r HERE
declare -r BOLDITALIC="${HERE}/bolditalic.py"
declare -r DOTZERO="${HERE}/dotzero.py"
declare -r GLYPHFIX="${HERE}/glyphfix.py"
declare -r ROOT="$( cd "${HERE}/.." && pwd )"
declare -r LIGATURIZE="${ROOT}/ligaturize.sh"       # shared, repo-root
declare -r LIG="${HERE}/LektonLig"
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
    -h | --help    ) printf 'usage: bash Lekton/build.sh [ -n | --dry-run ]\n'; exit 0 ;;
    *              ) die "unknown option: ${arg}" ;;
  esac
done

command -v fontforge >/dev/null 2>&1 || die 'fontforge required ( brew install fontforge )'
for f in "${BOLDITALIC}" "${DOTZERO}" "${GLYPHFIX}" "${LIGATURIZE}"; do
  test -f "${f}" || die "missing: ${f}"
done

# 1. optimized base faces in a temp dir: synth Bold Italic, dot 0, enlarge • + add ^ `
step 'optimized ( Bold Italic + dotted 0 + big • + ^ ` )'
WORK="$( mktemp -d )"
trap 'rm -rf "${WORK}"' EXIT
run cp "${HERE}/Lekton-Regular.ttf" "${HERE}/Lekton-Bold.ttf" "${HERE}/Lekton-Italic.ttf" "${WORK}/"
run fontforge -script "${BOLDITALIC}" --italic "${HERE}/Lekton-Italic.ttf" --bold "${HERE}/Lekton-Bold.ttf" -o "${WORK}/Lekton-BoldItalic.ttf"
run fontforge -script "${DOTZERO}"  -o "${WORK}" "${WORK}"/Lekton-Regular.ttf "${WORK}"/Lekton-Bold.ttf "${WORK}"/Lekton-Italic.ttf "${WORK}"/Lekton-BoldItalic.ttf
run fontforge -script "${GLYPHFIX}" --square -o "${WORK}" "${WORK}"

# 2. copy Fira Code ligatures ( + calt ) into every optimized face -> LektonLig/
step 'ligaturize ( Lekton + Fira Code ) -> LektonLig/'
run rm -f "${LIG}"/*.ttf "${LIG}"/*.otf
run bash "${LIGATURIZE}" --from "${WORK}" --to "${LIG}" --name LektonLig

step 'DONE'
printf 'LektonLig/ rebuilt ( 4 faces ).\n'

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
