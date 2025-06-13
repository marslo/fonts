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
cp -f Candara/*NerdFont*                                     "${fontPath}"
cp -f Gisha/*NerdFont*                                       "${fontPath}"
cp -f Titillium/*NerdFont*                                   "${fontPath}"
cp -f Grandstander/*NerdFont*                                "${fontPath}"
cp -f Recursive/*DesktopNF/*/*SansCasual*NerdFont-*.otf      "${fontPath}"
cp -f Operator/*ProNF/otf/*NerdFont*.otf                     "${fontPath}"
cp -f NotoSansSC/*NerdFont*                                  "${fontPath}"
cp -f spleen/*NerdFont*.otf                                  "${fontPath}"
cp -f Orbitron/*NerdFont*                                    "${fontPath}"
cp -f msyh/*NerdFont*.otf                                    "${fontPath}"

# mono
cp -f {VictorMono,ComicMono}/*NerdFont*.otf                  "${fontPath}"
cp -f monofur/*NerdFont*.ttf                                 "${fontPath}"
cp -f Monaco/*NF/otf/*.otf                                   "${fontPath}"
cp -f menlo/*NerdFont*.otf                                   "${fontPath}"
cp -f Operator/*Mono*NF/otf/*.otf                            "${fontPath}"
cp -f Recursive/RecursiveCodeNF/RecMonoCasual/*NerdFont*.otf "${fontPath}"
cp -f audiolink/mono/*NerdFont*.otf                          "${fontPath}"
cp -f monaspace/radon/*NerdFont*.otf                         "${fontPath}"
cp -f Lekton/*NerdFont*                                      "${fontPath}"
cp -f agave/*NerdFont*                                       "${fontPath}"

# cn
cp -f QianLiJiangShan/*NerdFont*                             "${fontPath}"
cp -f LXGW-WenKai/mono/*NerdFont*.otf                        "${fontPath}"
cp -f LXGW-WenKai/sans/*NerdFont*                            "${fontPath}"
cp -f Yozai/*NerdFont*                                       "${fontPath}"
cp -f Shayufeite/*NerdFont*                                  "${fontPath}"

# handwriting
cp -f segoe-print/*NerdFont*                                 "${fontPath}"
cp -f Papyrus/*NerdFont*                                     "${fontPath}"
cp -f BradleyHandITC/*NerdFont*                              "${fontPath}"

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
