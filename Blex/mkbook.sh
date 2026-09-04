#!/usr/bin/env bash
# =============================================================================
#      FileName : mkbook.sh
#        Author : marslo
#       Created : 2026-09-04 02:10:00
#    LastChange : 2026-09-04 02:25:00
# =============================================================================
# stage 0 ( run once ): make a real "Book" ( ~350 ) weight for IBM Plex Mono by
# instancing the official variable fonts at wght=350 -- NO glyph editing, the
# font's own deltas interpolate a true 350 for every glyph, upright and italic.
# outputs are monospaced and dropped into the vendor dir so the normal pipeline
# ( ligaturize.sh -> font-patcher ) picks them up like any other face.
#
# variable sources live in IBMPlexMonoVar/ ( kept OUT of IBMPlexMono/ so
# ligaturize.sh does not glob them ); missing ones are fetched from IBM/plex.
#
# only needed when IBM Plex Mono is updated -- IBMPlexMono-Book{,Italic}.ttf are
# committed, so a fresh checkout needs nothing.
#
# usage:
#   bash mkbook.sh [ --weight N ] [ --name NAME ] [ --src DIR ] [ --to DIR ] [ -n | --dry-run ]
#   e.g. bash mkbook.sh                 # wght=350, "Book" + "Book Italic"
#        bash mkbook.sh --weight 340    # a touch lighter

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
function usage() { printf 'usage: bash mkbook.sh [ --weight N ] [ --name NAME ] [ --src DIR ] [ --to DIR ] [ -n | --dry-run ]\n'; exit 0; }

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
    --weight       ) WEIGHT="${2}"; shift 2 ;;
    --name         ) NAME="${2}";   shift 2 ;;
    --src          ) SRC="${2}";    shift 2 ;;
    --to           ) TO="${2}";     shift 2 ;;
    -n | --dry-run ) DRYRUN=true;   shift   ;;
    -h | --help    ) usage                  ;;
    *              ) die "unknown option: ${1}" ;;
  esac
done

command -v python3 >/dev/null 2>&1 || die 'python3 required'
python3 -c 'import fontTools' 2>/dev/null || die 'fonttools required ( pip install fonttools )'
command -v curl    >/dev/null 2>&1 || die 'curl required ( to fetch the variable sources )'

ensureVF "${VF_ROMAN}"  "${URL_ROMAN}"
ensureVF "${VF_ITALIC}" "${URL_ITALIC}"

if "${DRYRUN}"; then
  printf '[dry-run] instance wght=%s from:\n' "${WEIGHT}"
  printf '  %s -> %s/IBMPlexMono-%s.ttf\n'       "${VF_ROMAN}"  "${TO}" "${NAME}"
  printf '  %s -> %s/IBMPlexMono-%sItalic.ttf\n' "${VF_ITALIC}" "${TO}" "${NAME}"
  exit 0
fi

test -f "${SRC}/${VF_ROMAN}"  || die "missing variable source: ${SRC}/${VF_ROMAN}"
test -f "${SRC}/${VF_ITALIC}" || die "missing variable source: ${SRC}/${VF_ITALIC}"
mkdir -p "${TO}"

# instance both axes at wght=<WEIGHT> and restamp the weight name records to
# mirror IBM Plex's own layout ( e.g. vendor "Light" / "Light Italic" ).
python3 - "${SRC}/${VF_ROMAN}" "${SRC}/${VF_ITALIC}" "${TO}" "${WEIGHT}" "${NAME}" <<'PY'
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

roman, italic, to, weight, name = sys.argv[1], sys.argv[2], sys.argv[3], int( sys.argv[4] ), sys.argv[5]
FAM, PSFAM = 'IBM Plex Mono', 'IBMPlexMono'


def setName( font, nid, value ):
    font[ 'name' ].setName( value, nid, 3, 1, 0x409 )   # windows / unicode
    font[ 'name' ].setName( value, nid, 1, 0, 0 )       # mac / roman


def build( src, italic ):
    style = '%s Italic' % name if italic else name          # nameID 17
    ps    = '%s-%s%s' % ( PSFAM, name, 'Italic' if italic else '' )
    full  = '%s %s' % ( FAM, style )
    font  = TTFont( src )
    instantiateVariableFont( font, { 'wght': weight }, inplace=True )
    font[ 'OS/2' ].usWeightClass = weight
    setName( font, 1,  '%s %s' % ( FAM, name ) )            # family ( RIBBI-grouped )
    setName( font, 2,  'Italic' if italic else 'Regular' )  # subfamily
    setName( font, 3,  '2.3;IBM ;%s' % ps )                 # unique id
    setName( font, 4,  full )                               # full name
    setName( font, 6,  ps )                                 # postscript name
    setName( font, 16, FAM )                                # typographic family
    setName( font, 17, style )                              # typographic subfamily
    out = '%s/%s.ttf' % ( to, ps )
    font.save( out )
    print( 'generated %s ( usWeightClass %d )' % ( out, weight ) )
    font.close()


build( roman,  italic=False )
build( italic, italic=True )
PY

printf 'done: %s/IBMPlexMono-%s.ttf + IBMPlexMono-%sItalic.ttf\n' "${TO}" "${NAME}" "${NAME}"

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
