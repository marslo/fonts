#!/usr/bin/env bash
# shellcheck source=/dev/null disable=SC2155,SC1079,SC1078

# credit belongs to https://github.com/ppo/bash-colors/blob/master/bash-colors.sh
# colorizing the output
source ~/.marslo/bin/bash-color.sh
set -euo pipefail

declare -r FONT_PATCHER='/opt/FontPatcher/font-patcher'
declare -r OPTIONS='--complete --careful --quiet'
declare -r MONO_OPTIONS="--mono ${OPTIONS}"

function message() {
  if [[ 1 -eq "$#" ]]; then
    command -v c >/dev/null && msg="$(c Rsi)$1$(c)" || msg="$1"
    msg="clean up Nerd Fonts ${msg}"
  elif [[ 2 -eq "$#" ]]; then
    command -v c >/dev/null && msg="$(c Gi)$1$(c) » $(c Ys)$2$(c)" || msg="$1 » $2"
    msg="building ${msg}"
  elif [[ 3 -eq "$#" ]]; then
    command -v c >/dev/null && msg="$(c Ms)$1$(c) » $(c Gi)$2$(c) » $(c Ys)$3$(c)" || msg="$1 » $2 » $3"
    msg="building ${msg}"
  fi
  echo -e "\n.. ${msg}"
}

function patchRecursiveDesktop() {
  if ls Recursive/Recursive_Desktop_NF/*/* >/dev/null 2>&1; then
    message "Recursive/Recursive_Desktop_NF/*/*"
    rm -rfv Recursive/Recursive_Desktop_NF/*/*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")_NF";
    fontfamily="$(fc-query -f '%{family}' "$(realpath "${_f}")" | awk -F, '{print $1}')";
    style="$(fc-query -f '%{style}' "$(realpath "${_f}")" | awk -F, '{print $1}')";
    name="${fontfamily} ${style} Nerd Font";
    for _e in otf ttf; do
      [[ -d "${outpath}/${_e}" ]] || mkdir -p "${outpath}/${_e}";
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      eval "command \"${FONT_PATCHER}\" \"$(realpath "${_f}")\" ${OPTIONS} -ext \"${_e}\" -out \"${outpath}\" --name \"${name}\" 2>/dev/null";
    done
  done < <(fd -u -tf -e ttf -e otf --full-path Recursive/Recursive_Desktop/)
}

function patchMonaco() {
  if ls Monaco/*NF/*/* >/dev/null 2>&1; then
    message "Monaco"/*NF/*/*
    rm -rfv Monaco/*NF/*/*
  fi
  while read -r _f; do
    for _e in otf ttf; do
      outpath="$(dirname "${_f}")NF/${_e}";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      message "$(basename "${_f}")" "${outpath}"
      eval "command \"${FONT_PATCHER}\" \"$(realpath "${_f}")\" ${MONO_OPTIONS} -ext \"${_e}\" -out \"${outpath}\" 2>/dev/null";
    done
  done < <(fd -u -tf -e ttf -e otf --full-path ./Monaco)
}

function patchOperatorMono() {
  if ls Operator/*Mono*NF >/dev/null 2>&1; then
    message "Operator/*Mono*NF"
    rm -rfv Operator/*Mono*NF
  fi
  while read -r _f; do
    for _e in otf ttf; do
      outpath="$(dirname "${_f}")NF/${_e}";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      message "$(basename "${_f}")" "${outpath}"
      eval "command \"${FONT_PATCHER}\" \"$(realpath "${_f}")\" ${MONO_OPTIONS} -ext \"${_e}\" -out \"${outpath}\" 2>/dev/null";
    done
  done < <(fd . Operator/OperatorMono Operator/OperatorMonoLig Operator/OperatorMonoSSmLig -tf -e ttf -e otf)
}

function patchSans() {
  path="$1"
  if ls "${path}"/*NerdFont* >/dev/null 2>&1; then
    message "${path}"/*NerdFont*
    rm -rfv "${path}"/*NerdFont*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")";
    message "$(basename "${_f}")" "${outpath}"
    eval "command \"${FONT_PATCHER}\" \"$(realpath "${_f}")\" ${OPTIONS} -out \"${outpath}\" 2>/dev/null";
  done < <(fd -u -tf -e ttf -e otf --full-path "${path}")
}

function patchMono() {
  path="$1"
  if ls "${path}"/*NerdFont* >/dev/null 2>&1; then
    message "${path}"/*NerdFont*
    rm -rfv "${path}"/*NerdFont*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")";
    for _e in otf ttf; do
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      eval "command \"${FONT_PATCHER}\" \"$(realpath "${_f}")\" ${MONO_OPTIONS} -ext \"${_e}\" -out \"${outpath}\" 2>/dev/null";
    done;
  done < <(fd -u -tf -e ttf -e otf --full-path "${path}")
}

# mono
patchMonaco
patchOperatorMono
patchMono ./VictorMono
patchMono ./ComicMono

# sans
patchRecursiveDesktop
patchSans ./Grandstander
patchSans ./Titillium
patchSans ./Candara
patchSans ./Gisha

# handwriting
patchSans ./Papyrus
patchSans ./segoe-print

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh
