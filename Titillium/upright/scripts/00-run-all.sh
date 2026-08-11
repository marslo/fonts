#!/usr/bin/env bash
#
# Full Titillium Upright -> Nerd Font pipeline:
#   1) generate upright-italics      (01-gen-upright-italic.py)
#   2) clean upright source metadata (02-fix-upright-source.py)
#   3) repair single-chevron «/»     (04-fix-guillemet.py)
#   4) font-patcher -> up/nf/
#   5) fix patched metadata          (03-fix-nf.py)  [+ optional install]
#
# Config (env):
#   FONT_ROOT     source root              (default: ~/Desktop/titillium)
#   FONT_PATCHER  path to font-patcher     (default: ~/git/nerd-fonts/font-patcher)
#
# Flags:
#   --dry-run   print every step, write nothing, skip patch + install
#   --install   after fixing, copy to ~/Library/Fonts, flush fontd, register (.user)
#
# Usage:
#   ./00-run-all.sh --dry-run
#   FONT_PATCHER=~/code/nerd-fonts/font-patcher ./00-run-all.sh --install
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${FONT_ROOT:-$HOME/Desktop/titillium}"
UP="$ROOT/up"
NF="$UP/nf"
PATCHER="${FONT_PATCHER:-$HOME/git/nerd-fonts/font-patcher}"

DRY=""
INSTALL=""
for a in "$@"; do
  case "$a" in
    --dry-run) DRY="--dry-run" ;;
    --install) INSTALL="--install" ;;
    *) echo "unknown flag: $a" >&2; exit 2 ;;
  esac
done

echo "==> root:    $ROOT"
echo "==> patcher: $PATCHER"
[ -n "$DRY" ] && echo "==> mode:    DRY-RUN (no writes, no patch, no install)"

PY="${PYTHON:-python3}"

echo
echo "==> [1/5] generate upright-italics"
"$PY" "$HERE/01-gen-upright-italic.py" "$ROOT" $DRY

echo
echo "==> [2/5] clean upright source metadata"
"$PY" "$HERE/02-fix-upright-source.py" "$UP" $DRY

echo
echo "==> [3/5] repair single-chevron guillemets («/»)"
"$PY" "$HERE/04-fix-guillemet.py" "$UP" --root="$ROOT" $DRY

echo
echo "==> [4/5] font-patcher -> $NF"
if [ -n "$DRY" ]; then
  echo "[dry-run] would patch: $UP/Titillium-*Upright.otf and $UP/Titillium-*UprightItalic.otf"
else
  if ! command -v fontforge >/dev/null 2>&1; then
    echo "!! fontforge not found (brew install fontforge)" >&2; exit 1
  fi
  if [ ! -f "$PATCHER" ]; then
    echo "!! font-patcher not found at: $PATCHER" >&2
    echo "   set FONT_PATCHER=/path/to/nerd-fonts/font-patcher" >&2; exit 1
  fi
  mkdir -p "$NF"
  shopt -s nullglob
  for f in "$UP"/Titillium-*Upright.otf "$UP"/Titillium-*UprightItalic.otf; do
    echo "   patching $(basename "$f")"
    fontforge -quiet -script "$PATCHER" "$f" --complete --careful --outputdir "$NF"
  done
fi

echo
echo "==> [5/5] fix NF metadata${INSTALL:+ + install}"
"$PY" "$HERE/03-fix-nf.py" "$NF" $DRY $INSTALL

echo
echo "==> done."
if [ -z "$DRY" ] && [ -z "$INSTALL" ]; then
  echo "    re-run with --install to copy to ~/Library/Fonts and register."
fi
