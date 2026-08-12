#!/usr/bin/env bash
# =============================================================================
#      FileName : run.sh
#        Author : marslo
#       Created : 2026-08-05 18:42:35
#    LastChange : 2026-08-12 01:41:45
# =============================================================================
#
# One-shot Titillium Upright -> Nerd Font builder.
#
#   unzip sources -> stage roman + upright-italic (prep.py, + guillemet fix)
#                 -> font-patcher (per role) -> unify metadata (fixnf.py, +install)
#
# Produces the full RIBBI set (Regular / Italic / Bold / Bold Italic, plus the Thin / Light / Semibold weights) under one family "Titillium Nerd Font Upright".
#
# Usage:
#   ./run.sh --input path/to/titillium.zip --output path/to/dir [options]
#   ./run.sh --src path/to/extracted    --output work/dir --fonts out/dir [options]
#
# Options:
#   --input  FILE   source zip (16 flat Titillium-*.otf)          [required unless --src]
#   --src    DIR    already-extracted vendor OTFs; skips unzip (repeatable, dirs searched in order)
#   --output DIR    work directory (build/ + nf/, and src/ when unzipping) [required]
#   --fonts  DIR    final deliverables directory (default: <output>/fonts)
#   --patcher PATH  font-patcher (else $FONT_PATCHER / autodetect)
#   --install       copy final faces to ~/Library/Fonts, flush fontd, register
#   --dry-run       print every step, write nothing, skip patch + install
#
# Layout:
#   src/                           unzipped vendor OTFs (or --src, verbatim)
#   <output>/build/{roman,italic}  staged, per-role patcher input
#   <output>/nf/{roman,italic}     font-patcher output, per role
#   <fonts>/                       final, renamed, metadata-fixed deliverables

set -euo pipefail

# @credit: https://github.com/ppo/bash-colors
# shellcheck disable=SC2015,SC2059
c() { [ $# == 0 ] && printf "\033[0m" || printf "$1" | sed 's/\(.\)/\1;/g;s/\([SDIUFNHT]\)/2\1/g;s/\([KRGYBMCW]\)/3\1/g;s/\([krgybmcw]\)/4\1/g;y/SDIUFNHTsdiufnhtKRGYBMCWkrgybmcw/12345789123457890123456701234567/;s/^\(.*\);$/\\033[\1m/g'; }

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"

# display helpers: render path(s) relative to the current working directory (the
# call site), so build.sh (repo root) and a direct `cd scripts && ./run.sh` each
# print paths relative to where the command was launched
rel()  { "${PY}" -c 'import os,sys; print(os.path.relpath(sys.argv[1]))' "$1"; }
relj() { local out='' a; for a in "$@"; do out="${out:+${out} }$(rel "${a}")"; done; printf '%s' "${out}"; }

INPUT='' OUTPUT='' PATCHER="${FONT_PATCHER:-}" INSTALL='' DRY='' FONTS_DIR=''
declare -a SRC_DIRS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --input     ) INPUT="$2"              ;  shift 2 ;;
    --src       ) SRC_DIRS+=( "$2" )      ;  shift 2 ;;
    --output    ) OUTPUT="$2"             ;  shift 2 ;;
    --fonts     ) FONTS_DIR="$2"          ;  shift 2 ;;
    --patcher   ) PATCHER="$2"            ;  shift 2 ;;
    --install   ) INSTALL="--install"     ;  shift   ;;
    --dry-run   ) DRY="--dry-run"         ;  shift   ;;
    --input=*   ) INPUT="${1#*=}"         ;  shift   ;;
    --src=*     ) SRC_DIRS+=( "${1#*=}" ) ;  shift   ;;
    --output=*  ) OUTPUT="${1#*=}"        ;  shift   ;;
    --fonts=*   ) FONTS_DIR="${1#*=}"     ;  shift   ;;
    --patcher=* ) PATCHER="${1#*=}"       ;  shift   ;;
    -h|--help   ) sed -n '9,33p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *           ) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

test -n "${OUTPUT}" || { echo '!! --output <dir> is required' >&2; exit 2; }
if [ "${#SRC_DIRS[@]}" -gt 0 ]; then
  for d in "${SRC_DIRS[@]}"; do
    test -d "${d}" || { echo "!! --src dir not found: ${d}" >&2; exit 2; }
  done
else
  test -n "${INPUT}" || { echo '!! --input <titillium.zip> or --src <dir> is required' >&2; exit 2; }
  test -f "${INPUT}" || { echo "!! input not found: ${INPUT}" >&2; exit 2; }
fi

BUILD="${OUTPUT}/build"
NF="${OUTPUT}/nf"
FONTS="${FONTS_DIR:-${OUTPUT}/fonts}"

# resolve source dir(s): with --src (one or more) skip unzip; else unzip the zip
declare -a SRCS=()
if [ "${#SRC_DIRS[@]}" -gt 0 ]; then
  SRCS=( "${SRC_DIRS[@]}" )
else
  SRCS=( "${OUTPUT}/src" )
fi

# call-site-relative display strings (the real paths above stay as-is for the tools)
if [ "${#SRC_DIRS[@]}" -gt 0 ]; then IN_DISP="$(relj "${SRC_DIRS[@]}")"; else IN_DISP="$(rel "${INPUT}")"; fi
SRCS_DISP="$(relj "${SRCS[@]}")"
OUT_DISP="$(rel "${OUTPUT}")"
FONTS_DISP="$(rel "${FONTS}")"
NF_DISP="$(rel "${NF}")"

function message() {
  local msg=''
  if [[ 2 -eq "$#" ]]; then
    msg="$(c 0Mi)$1$(c 0Wdi):    $(c 0Gi)$2$(c)"
  elif [[ 3 -eq "$#" ]]; then
    msg="$(c 0Ms)[$1] $(c 0Gi)$2 $(c 0Wdi)-> $(c 0Ys)$3$(c)\n"
  elif [[ 4 -eq "$#" ]] && [[ 'info' = "${4}" ]]; then
    msg="$(c 0Mi)$1$(c 0Wdi):    $(c 0Gi)$2    $(c 0Wdi)($3)$(c)"
  fi
  printf "\n$(c Wdi)==>$(c) %b" "${msg}"
}

message 'input' "${IN_DISP}"
message 'work ' "${OUT_DISP}" 'intermediate build/ + nf/' 'info'
message 'fonts' "${FONTS_DISP}" 'final deliverables'     'info'
[ -n "${DRY}" ] && echo -e "$(c 0Wdi)==> $(c 0Mi)mode$(c 0Wdi):    DRY-RUN (no writes, no patch, no install)$(c)"

# --- [1/4] source ----------------------------------------------------------
message '1/4' 'source' "${SRCS_DISP}"
if [ "${#SRC_DIRS[@]}" -gt 0 ]; then
  echo "   using existing src dir(s) (no unzip): ${SRCS_DISP}"
elif [ -n "${DRY}" ]; then
  echo "[dry-run] would unzip $(basename "${INPUT}") into ${SRCS[0]}"
else
  mkdir -p "${SRCS[0]}"
  unzip -o -j "${INPUT}" '*.otf' -d "${SRCS[0]}" >/dev/null
  echo "   $(find "${SRCS[0]}" -maxdepth 1 -name '*.otf' | wc -l | tr -d ' ') OTFs extracted"
fi

# --- [2/4] stage roman + upright-italic + guillemet ------------------------
message '2/4' 'stage sources' '(roman + upright-italic) + repair «/»'
declare -a PREP_SRC=()
for d in "${SRCS[@]}"; do PREP_SRC+=( --src "${d}" ); done
"${PY}" "${HERE}/prep.py" "${PREP_SRC[@]}" --build "${BUILD}" ${DRY}

# --- [3/4] font-patcher ----------------------------------------------------
message '3/4' 'font-patcher' "${NF_DISP}/{roman,italic}"
if [ -n "${DRY}" ]; then
  echo "[dry-run] would patch build/roman/*.otf -> nf/roman/ and build/italic/*.otf -> nf/italic/"
else
  if [ -z "${PATCHER}" ]; then
    for c in /opt/FontPatcher/font-patcher "$HOME/git/nerd-fonts/font-patcher" "$HOME/code/nerd-fonts/font-patcher"; do
      test -f "${c}" && PATCHER="${c}" && break
    done
  fi
  [ -n "${PATCHER}" ] && [ -f "${PATCHER}" ] || { echo "!! font-patcher not found; pass --patcher PATH or set FONT_PATCHER" >&2; exit 1; }
  command -v fontforge >/dev/null 2>&1 || { echo "!! fontforge not found (brew install fontforge)" >&2; exit 1; }
  echo "   patcher: ${PATCHER}"
  shopt -s nullglob
  for role in roman italic; do
    mkdir -p "${NF}/${role}"
    for f in "${BUILD}/${role}"/*.otf; do
      echo -e "   $(c 0Mi)[${role}]$(c 0Wdi) patching $(c 0Gi)$(basename "${f}")$(c)"
      # fontforge's C engine prints glyph-mapping / metrics warnings straight to stderr, unaffected by font-patcher's --quiet; drop them for a clean log
      fontforge -quiet -script "${PATCHER}" "${f}" --complete --careful --quiet --no-progressbars --outputdir "${NF}/${role}" 2>/dev/null
    done
  done
fi

# --- [4/4] unify metadata (+ install) --------------------------------------
message '4/4' 'unify metadata' "${FONTS_DISP}${INSTALL:+ + install}"
"${PY}" "${HERE}/fixnf.py" --roman "${NF}/roman" --italic "${NF}/italic" --out "${FONTS}" ${DRY} ${INSTALL}

echo
echo "==> done."
if [ -z "${DRY}" ]; then
  echo "    final faces: ${FONTS_DISP}"
  [ -z "${INSTALL}" ] && echo "    re-run with --install to copy to ~/Library/Fonts and register."
fi

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
