#!/usr/bin/env bash
# shellcheck disable=SC2216

set -euo pipefail

fontPath="$HOME/Library/Fonts"

# sans
yes | cp {Candara,Gisha,Titillium,Grandstander}/*NerdFont* "${fontPath}"
yes | cp Recursive/*_Desktop_NF/*/*SansCasual*NerdFont-*.ttf "${fontPath}"
yes | cp Operator/*ProNF/*NerdFont*.ttf "${fontPath}"

# mono
yes | cp {Monaco,monofur,VictorMono}/*NerdFont* "${fontPath}"
yes | cp Operator/*Mono*NF/*NerdFont*.ttf "${fontPath}"
yes | cp Recursive/Recursive_Code_NF/RecMonoCasual/*NerdFont*.ttf "${fontPath}"

# handwriting
yes | cp segoe-print/*NerdFont* "${fontPath}"
yes | cp Papyrus/*NerdFont* "${fontPath}"

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh
