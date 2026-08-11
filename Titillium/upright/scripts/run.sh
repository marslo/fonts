#!/usr/bin/env bash
# =============================================================================
#      FileName : run.sh
#        Author : marslo
#       Created : 2026-08-05 18:42:35
#    LastChange : 2026-08-11 16:41:34
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
#
# Options:
#   --input  FILE   source zip (16 flat Titillium-*.otf)          [required]
#   --output DIR    work + output directory                       [required]
#   --patcher PATH  font-patcher (else $FONT_PATCHER / autodetect)
#   --install       copy final faces to ~/Library/Fonts, flush fontd, register
#   --dry-run       print every step, write nothing, skip patch + install
#
# Layout created under --output:
#   src/                           unzipped vendor OTFs
#   build/roman/  build/italic/    staged, per-role patcher input
#   nf/roman/     nf/italic/       font-patcher output, per role
#   fonts/                         final, renamed, metadata-fixed deliverables

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"

INPUT="" OUTPUT="" PATCHER="${FONT_PATCHER:-}" INSTALL="" DRY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --input     ) INPUT="$2"          ;  shift 2 ;;
    --output    ) OUTPUT="$2"         ;  shift 2 ;;
    --patcher   ) PATCHER="$2"        ;  shift 2 ;;
    --install   ) INSTALL="--install" ;  shift   ;;
    --dry-run   ) DRY="--dry-run"     ;  shift   ;;
    --input=*   ) INPUT="${1#*=}"     ;  shift   ;;
    --output=*  ) OUTPUT="${1#*=}"    ;  shift   ;;
    --patcher=* ) PATCHER="${1#*=}"   ;  shift   ;;
    -h|--help   ) sed -n '9,31p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *           ) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

test -n "${INPUT}"  || { echo "!! --input <titillium.zip> is required" >&2; exit 2; }
test -n "${OUTPUT}" || { echo "!! --output <dir> is required" >&2; exit 2; }
test -f "${INPUT}"  || { echo "!! input not found: ${INPUT}" >&2; exit 2; }

SRC="${OUTPUT}/src"
BUILD="${OUTPUT}/build"
NF="${OUTPUT}/nf"
FONTS="${OUTPUT}/fonts"

echo "==> input:   ${INPUT}"
echo "==> output:  ${OUTPUT}"
[ -n "${DRY}" ] && echo "==> mode:    DRY-RUN (no writes, no patch, no install)"

# --- [1/4] unzip -----------------------------------------------------------
echo
echo "==> [1/4] unzip sources -> ${SRC}"
if [ -n "${DRY}" ]; then
  echo "[dry-run] would unzip $(basename "${INPUT}") into ${SRC}"
else
  mkdir -p "${SRC}"
  unzip -o -j "${INPUT}" '*.otf' -d "${SRC}" >/dev/null
  echo "   $(find "${SRC}" -maxdepth 1 -name '*.otf' | wc -l | tr -d ' ') OTFs extracted"
fi

# --- [2/4] stage roman + upright-italic + guillemet ------------------------
echo
echo "==> [2/4] stage sources (roman + upright-italic) + repair «/»"
"${PY}" "${HERE}/prep.py" --src "${SRC}" --build "${BUILD}" ${DRY}

# --- [3/4] font-patcher ----------------------------------------------------
echo
echo "==> [3/4] font-patcher -> ${NF}/{roman,italic}"
if [ -n "${DRY}" ]; then
  echo "[dry-run] would patch build/roman/*.otf -> nf/roman/ and build/italic/*.otf -> nf/italic/"
else
  if [ -z "${PATCHER}" ]; then
    for c in /opt/FontPatcher/font-patcher "$HOME/git/nerd-fonts/font-patcher" "$HOME/code/nerd-fonts/font-patcher"; do
      [ -f "${c}" ] && PATCHER="${c}" && break
    done
  fi
  [ -n "${PATCHER}" ] && [ -f "${PATCHER}" ] || { echo "!! font-patcher not found; pass --patcher PATH or set FONT_PATCHER" >&2; exit 1; }
  command -v fontforge >/dev/null 2>&1 || { echo "!! fontforge not found (brew install fontforge)" >&2; exit 1; }
  echo "   patcher: ${PATCHER}"
  shopt -s nullglob
  for role in roman italic; do
    mkdir -p "${NF}/${role}"
    for f in "${BUILD}/${role}"/*.otf; do
      echo "   [${role}] patching $(basename "${f}")"
      fontforge -quiet -script "${PATCHER}" "${f}" --complete --careful --outputdir "${NF}/${role}"
    done
  done
fi

# --- [4/4] unify metadata (+ install) --------------------------------------
echo
echo "==> [4/4] unify metadata -> ${FONTS}${INSTALL:+ + install}"
"${PY}" "${HERE}/fixnf.py" --roman "${NF}/roman" --italic "${NF}/italic" --out "${FONTS}" ${DRY} ${INSTALL}

echo
echo "==> done."
if [ -z "${DRY}" ]; then
  echo "    final faces: ${FONTS}"
  [ -z "${INSTALL}" ] && echo "    re-run with --install to copy to ~/Library/Fonts and register."
fi

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
