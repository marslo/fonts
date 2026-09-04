#!/usr/bin/env bash
# =============================================================================
#      FileName : ligaturize.sh
#        Author : marslo
# =============================================================================
# add Fira Code ligatures to any monospace font via Ligaturizer ( /opt/Ligaturizer ):
# copies FiraCode's ligature glyphs + calt rules into each face, scale-corrected,
# and renames the family to <name> ( one word, like OperatorMonoLig / IBMPlexMonoLig / LektonLig ).
#
# <name> defaults to the basename of --to ( --to .../LektonLig -> LektonLig ); pass --name to
# override — callers pass it explicitly so a later dir rename can't silently change the family.
#
# the source faces must already carry '^' ( asciicircum ) — Ligaturizer aborts
# without it ( Lekton needs Lekton/glyphfix.py first; IBM Plex already ships it ).
#
# usage:
#   bash ligaturize.sh --from <src-dir> --to <dst-dir> [ --name <family> ] [ -n | --dry-run ]
#   e.g. bash ligaturize.sh --from ./Blex/IBMPlexMono --to ./Blex/IBMPlexMonoLig
#        bash ligaturize.sh --from <optimized-dir>    --to ./Lekton/LektonLig
#
# override the Ligaturizer location with $LIGATURIZER.

set -euo pipefail

declare -r LIGATURIZER="${LIGATURIZER:-/opt/Ligaturizer}"
declare -r LIG_URL='https://github.com/ToxicFrog/Ligaturizer.git'
declare -r LIG_MATCH='ToxicFrog/Ligaturizer'     # remote must contain this
declare -r LIG_BRANCH='master'
declare FROM=''
declare TO=''
declare NAME=''                                  # output family name; default: basename of --to
declare DRYRUN=false

function die()   { printf 'error: %s\n' "${*}" >&2; exit 1; }
function usage() { printf 'usage: bash ligaturize.sh --from <src-dir> --to <dst-dir> [ --name <family> ] [ -n | --dry-run ]\n'; exit 0; }

# clone Ligaturizer if missing / not a repo; update it if it's the right repo; die otherwise
function ensureLigaturizer() {
  local url=''
  if test -d "${LIGATURIZER}" && git -C "${LIGATURIZER}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    url="$( git -C "${LIGATURIZER}" remote get-url origin 2>/dev/null || true )"
    case "${url}" in
      *"${LIG_MATCH}"* )
        printf '==> updating Ligaturizer in %s\n' "${LIGATURIZER}"
        git -C "${LIGATURIZER}" clean -dffx >/dev/null
        git -C "${LIGATURIZER}" fetch --all --prune --recurse-submodules
        git -C "${LIGATURIZER}" reset --hard "origin/${LIG_BRANCH}"
        git -C "${LIGATURIZER}" submodule update --init --recursive
        printf '==> Ligaturizer at %s\n' "$( git -C "${LIGATURIZER}" rev-parse --short=9 HEAD )" ;;
      * ) die "not the Ligaturizer repo at ${LIGATURIZER} ( remote: ${url:-none} )" ;;
    esac
  else
    printf '==> cloning Ligaturizer into %s\n' "${LIGATURIZER}"
    git clone --recurse-submodules "${LIG_URL}" "${LIGATURIZER}" || die "failed to clone ${LIG_URL}"
  fi
  test -f "${LIGATURIZER}/ligaturize.py" || die "ligaturize.py missing in ${LIGATURIZER}"
}

while test "${#}" -gt 0; do
  case "${1}" in
    --from         ) FROM="${2}"; shift 2 ;;
    --to           ) TO="${2}";   shift 2 ;;
    --name         ) NAME="${2}"; shift 2 ;;
    -n | --dry-run ) DRYRUN=true; shift   ;;
    -h | --help    ) usage                ;;
    *              ) die "unknown option: ${1}" ;;
  esac
done

test -n "${FROM}" && test -n "${TO}" || usage
NAME="${NAME:-$( basename "${TO}" )}"            # default output family = dest dir name; --name overrides
command -v git       >/dev/null 2>&1 || die 'git required'
command -v fontforge >/dev/null 2>&1 || die 'fontforge required ( brew install fontforge )'
test -d "${FROM}"                    || die "missing source dir: ${FROM}"
ensureLigaturizer     # clone / update /opt/Ligaturizer as needed

# ligaturize.py resolves its bundled FiraCode via a relative path, so it must run from the Ligaturizer dir; pass absolute in/out paths
FROM="$( cd "${FROM}" && pwd )"
"${DRYRUN}" || mkdir -p "${TO}"
TO="$( cd "${TO}" 2>/dev/null && pwd || echo "${TO}" )"

shopt -s nullglob
declare -a srcs=( "${FROM}"/*.ttf "${FROM}"/*.otf )
shopt -u nullglob
test "${#srcs[@]}" -gt 0 || die "no .ttf/.otf found in ${FROM}"

for src in "${srcs[@]}"; do
  printf '  >> ligaturize %s -> %s\n' "$( basename "${src}" )" "${NAME}"
  "${DRYRUN}" && continue
  ( cd "${LIGATURIZER}" && fontforge -lang=py -script ligaturize.py "${src}" --output-dir "${TO}" --output-name "${NAME}" --prefix '' ) 2>/dev/null
done

printf 'done: %d face(s) -> %s ( %s )\n' "${#srcs[@]}" "${TO}" "${NAME}"

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
