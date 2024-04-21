#!/usr/bin/env bash
# shellcheck disable=SC2216

set -euo pipefail

function isWSL()   { [[ -f /proc/version ]] && grep -qEi "(Microsoft|WSL)" /proc/version; }
function isLinux() { ! isWSL && [[ "$(uname)" == "Linux" ]]; }
function isOSX()   { [[ "$(uname)" == "Darwin" ]]; }

if isOSX; then
  fontPath="$HOME/Library/Fonts"
elif isLinux; then
  fontPath="$HOME/.local/share/fonts"
else
  echo "Unsupported OS $(uname)"
  exit 1
fi

# sans
cp -f Candara/*NerdFont* "${fontPath}"
cp -f Gisha/*NerdFont* "${fontPath}"
cp -f Titillium/*NerdFont* "${fontPath}"
cp -f Grandstander/*NerdFont* "${fontPath}"
cp -f Recursive/*_Desktop_NF/*/*SansCasual*NerdFont-*.otf "${fontPath}"
cp -f Operator/*ProNF/*NerdFont*.otf "${fontPath}"

# mono
cp -f {VictorMono,ComicMono}/*NerdFont*.otf "${fontPath}"
cp -f monofur/*NerdFont*.ttf "${fontPath}"
cp -f Monaco/*NF/otf/*.otf "${fontPath}"
cp -f Operator/*Mono*NF/otf/*.otf "${fontPath}"
cp -f Recursive/Recursive_Code_NF/RecMonoCasual/*NerdFont*.otf "${fontPath}"

# handwriting
cp -f segoe-print/*NerdFont* "${fontPath}"
cp -f Papyrus/*NerdFont* "${fontPath}"

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh
