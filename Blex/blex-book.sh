#!/usr/bin/env bash
# =============================================================================
#      FileName : blex-book.sh
#        Author : marslo
#       Created : 2026-09-04 02:10:00
#    LastChange : 2026-09-04 03:07:43
# =============================================================================
# stage 0 ( run once ): make a real "Book" ( ~350 ) weight for IBM Plex Mono by
# instancing the official variable fonts at wght=350 -- NO glyph editing, the
# font's own deltas interpolate a true 350 for every glyph, upright and italic.
# output is CFF/OpenType ( .otf ) to match the OTF vendor set; quadratic->cubic
# is exact, so the glyf variable source converts to CFF losslessly.
#
# variable sources live in IBMPlexMonoVar/ ( kept OUT of IBMPlexMono/ so
# ligaturize.sh does not glob them ); missing ones are fetched from IBM/plex.
#
# only needed when IBM Plex Mono is updated -- IBMPlexMono-Book{,Italic}.otf are
# committed, so a fresh checkout needs nothing.
#
# usage:
#   bash blex-book.sh [ --weight N ] [ --name NAME ] [ --src DIR ] [ --to DIR ] [ -n | --dry-run ]
#   e.g. bash blex-book.sh                 # wght=350, "Book" + "Book Italic"
#        bash blex-book.sh --weight 340    # a touch lighter

set -euo pipefail

# shellcheck disable=SC2155
declare -r SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" && pwd )"
declare SRC="${SCRIPT_DIR}/IBMPlexMonoVar"    # variable-font sources
declare TO="${SCRIPT_DIR}/IBMPlexMono"        # where the Book faces land ( vendor dir )
declare WEIGHT='350'                          # wght instance / OS/2 usWeightClass
declare NAME='Book'                           # weight name ( nameID 17 / PS style )
declare DRYRUN=false

declare -r RAW='https://raw.githubusercontent.com/IBM/plex/master/packages/plex-mono-variable/fonts/complete/ttf'
declare -r VF_ROMAN='IBMPlexMonoVar-Roman.ttf'
declare -r VF_ITALIC='IBMPlexMonoVar-Italic.ttf'
declare -r URL_ROMAN="${RAW}/IBM%20Plex%20Mono%20Var-Roman.ttf"
declare -r URL_ITALIC="${RAW}/IBM%20Plex%20Mono%20Var-Italic.ttf"

function die()   { printf 'error: %s\n' "${*}" >&2; exit 1; }
function usage() { printf 'usage: bash blex-book.sh [ --weight N ] [ --name NAME ] [ --src DIR ] [ --to DIR ] [ -n | --dry-run ]\n'; exit 0; }

# fetch a variable source into SRC if it is not already there
function ensureVF() {
  local file="${1}" url="${2}"
  test -f "${SRC}/${file}" && return 0
  "${DRYRUN}" && { printf '  [dry-run] would fetch %s\n' "${file}"; return 0; }
  printf '==> fetching %s\n' "${file}"
  mkdir -p "${SRC}"
  curl -fsSL "${url}" -o "${SRC}/${file}" || die "failed to fetch ${url}"
}

while test "${#}" -gt 0; do
  case "${1}" in
    --weight       ) WEIGHT="${2}"; shift 2     ;;
    --name         ) NAME="${2}";   shift 2     ;;
    --src          ) SRC="${2}";    shift 2     ;;
    --to           ) TO="${2}";     shift 2     ;;
    -n | --dry-run ) DRYRUN=true;   shift       ;;
    -h | --help    ) usage                      ;;
    *              ) die "unknown option: ${1}" ;;
  esac
done

command -v python3   >/dev/null 2>&1      || die 'python3 required'
python3 -c 'import fontTools' 2>/dev/null || die 'fonttools required ( pip install fonttools )'
command -v fontforge >/dev/null 2>&1      || die 'fontforge required ( brew install fontforge -- glyf->CFF conversion )'
command -v curl      >/dev/null 2>&1      || die 'curl required ( to fetch the variable sources )'

ensureVF "${VF_ROMAN}"  "${URL_ROMAN}"
ensureVF "${VF_ITALIC}" "${URL_ITALIC}"

declare -r OUT_ROMAN="IBMPlexMono-${NAME}.otf"
declare -r OUT_ITALIC="IBMPlexMono-${NAME}Italic.otf"

if "${DRYRUN}"; then
  printf '[dry-run] instance wght=%s ( glyf ) then convert to CFF/OTF:\n' "${WEIGHT}"
  printf '  %s -> %s/%s\n' "${VF_ROMAN}"  "${TO}" "${OUT_ROMAN}"
  printf '  %s -> %s/%s\n' "${VF_ITALIC}" "${TO}" "${OUT_ITALIC}"
  exit 0
fi

test -f "${SRC}/${VF_ROMAN}"  || die "missing variable source: ${SRC}/${VF_ROMAN}"
test -f "${SRC}/${VF_ITALIC}" || die "missing variable source: ${SRC}/${VF_ITALIC}"

# delegate the font work to blex-book.py ( fonttools instance -> FontForge glyf->CFF )
python3 "${SCRIPT_DIR}/blex-book.py" \
        --roman  "${SRC}/${VF_ROMAN}" \
        --italic "${SRC}/${VF_ITALIC}" \
        --out    "${TO}" \
        --weight "${WEIGHT}" \
        --name   "${NAME}"

printf 'done: %s/%s + %s\n' "${TO}" "${OUT_ROMAN}" "${OUT_ITALIC}"

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
