#!/usr/bin/env bash

set -euo pipefail

declare FONT_PATCHER="/opt/FontPatcher/font-patcher"

function patchRecursiveDesktop() {
  while read -r _f; do
    outpath="$(dirname "${_f}")_NF";
    fontfamily="$(fc-query -f '%{family}' "$(realpath "${_f}")" | awk -F, '{print $1}')";
    style="$(fc-query -f '%{style}' "$(realpath "${_f}")" | awk -F, '{print $1}')";
    name="${fontfamily} ${style} Nerd Font";
    for _e in otf ttf; do
      [[ -d "${outpath}/${_e}" ]] || mkdir -p "${outpath}/${_e}";
      echo ".. ${_e} » $(basename "${_f}") » ${outpath}";
      command "${FONT_PATCHER}" "$(realpath "${_f}")" --complete --quiet -ext ${_e} -out "${outpath}/${_e}" --name "${name}" 2>/dev/null;
    done
  done < <(fd -u -tf -e ttf -e otf --full-path Recursive/Recursive_Desktop/)
}

function patchSans() {
  path="$1"
  echo ".. clean up Nerd Fonts .."
  rm -rf "${path}/*NerdFont*"
  while read -r _f; do
    outpath="$(dirname "${_f}")";
    echo ".. build $(basename "${_f}") » ${outpath}";
    command "${FONT_PATCHER}" "$(realpath "${_f}")" --complete --quiet -out "${outpath}" 2>/dev/null;
  done < <(fd -u -tf -e ttf -e otf --full-path "${path}")
}

function patchMono() {
  path="$1"
  echo ".. clean up Nerd Fonts .."
  rm -rf "${path}/*NerdFont*"
  while read -r _f; do
    outpath="$(dirname "${_f}")";
    for _e in otf ttf; do
      echo ".. patching ${_e} >> $(basename "${_f}")";
      font-patcher "$(realpath "${_f}")" --mono --complete --quiet -ext "${_e}" -out "${outpath}" 2>/dev/null;
    done;
  done < <(fd -u -tf -e ttf -e otf --full-path "${path}")
}

# mono
patchRecursiveDesktop
patchMono ./VictorMono

# sans
patchSans ./Grandstander
patchSans ./Titillium
patchSans ./Candara
patchSans ./Gisha

# handwriting
patchSans ./Papyrus

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh
