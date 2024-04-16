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

patchRecursiveDesktop

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh
