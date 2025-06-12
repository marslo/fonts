#!/usr/bin/env bash
# shellcheck source=/dev/null disable=SC2155,SC1079,SC1078

# credit belongs to https://github.com/ppo/bash-colors/blob/master/bash-colors.sh
# colorizing the output
source ~/.marslo/bin/bash-color.sh
set -euo pipefail

declare -r FONT_PATCHER='/opt/FontPatcher/font-patcher'
declare -r OPTIONS='--complete --careful --quiet'
declare -r MONO_OPTIONS="--mono ${OPTIONS}"

# for parameters
declare sans=false
declare mono=false
declare operator=false
declare monaco=false
declare all=false
declare path=''

# usage
declare usage="""
to build Nerd Fonts for Sans or Mono type

SYNOPSIS

  $(c sY)\$ bash build.sh [ -h | --help ]
                  [ --operator-mono | --monaco ]
                  [ --mono | --sans ]
                  [ --sans | --mono ]
                  [ -a/--all ]
                  [ -p/--path <path> ]
                  [ -- <PATCH_OPT> ]$(c)

EXAMPLE

  \t$(c Wdi)# show help$(c)
  \t$(c G)\$ bash build.sh -h$(c) | $(c G)\$ bash build.sh --help$(c)

  \t$(c Wdi)#to build Nerd Fonts for Sans type with otf format$(c)
  \t$(c G)\$ bash build.sh --sans --path <path> -- -ext otf$(c)

  \t$(c Wdi)#to build Nerd Fonts for Mono type with particular name$(c)
  \t$(c G)\$ bash build.sh --mono --path <path> -- --name 'NEW NAME Nerd Font'$(c)
"""

function message() {
  local msg=''
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
  printf "\n.. %b\n" "${msg}"
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
  opt="${2:-}"
  if ls "${path}"/*NerdFont* >/dev/null 2>&1; then
    message "${path}"/*NerdFont*
    rm -rfv "${path}"/*NerdFont*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")";
    message "$(basename "${_f}")" "${outpath}"
    eval "command \"${FONT_PATCHER}\" \"$(realpath "${_f}")\" ${OPTIONS} -out \"${outpath}\" ${opt} 2>/dev/null";
  done < <(fd -u -tf -e ttf -e otf --full-path "${path}")
}

function patchMono() {
  path="$1"
  opt="${2:-}"
  if ls "${path}"/*NerdFont* >/dev/null 2>&1; then
    message "${path}"/*NerdFont*
    rm -rfv "${path}"/*NerdFont*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")";
    for _e in otf ttf; do
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      eval "command \"${FONT_PATCHER}\" \"$(realpath "${_f}")\" ${MONO_OPTIONS} -ext \"${_e}\" -out \"${outpath}\" ${opt} 2>/dev/null";
    done;
  done < <(fd -u -tf -e ttf -e otf --full-path "${path}")
}

function showHelp() { echo -e "${usage}"; exit 0; }
function die() { echo -e "$(c R)ERROR$(c) : $*" >&2; exit 2; }

[[ 0 = "$#" ]] && showHelp
# shellcheck disable=SC2124
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sans          ) sans=true              ; shift   ;;
    --mono          ) mono=true              ; shift   ;;
    --operator-mono ) operator=true          ; shift   ;;
    --monaco        ) monaco=true            ; shift   ;;
    -a | --all      ) all=true               ; shift   ;;
    -p | --path     ) path="$2"              ; shift 2 ;;
    --              ) shift ; PATCH_OPT="$@" ; break   ;;
    -h | --help | * ) showHelp                         ;;
  esac
done
[[ -z "${path}" ]] && die "Please specify the path ( via \`-p/--path <path>\` )"
# shellcheck disable=SC2001
path="$(sed 's#/*$##' <<< "${path}")"

PATCH_OPT=$(echo "${PATCH_OPT:-}" |
             sed -r 's/\s+--/\n--/g' |
             sed -r "s/^([^ ]+) (.+)$/\1 '\2'/g" |
             sed -e 'N;s/\n/ /'
          )
export PATCH_OPT

# for `--all`
if "${all}"; then
  # mono
  patchMonaco
  patchOperatorMono
  patchRecursiveDesktop
  while read -r _path; do
    patchMono "./${_path}"
  done < <(fmt -1 <<< 'ComicMono LXGW-WenKai/mono VictorMono audiolink/console audiolink/mono monaspace/radon')

  # sans
  patchRecursiveDesktop
  while read -r _path; do
    patchSans "./${_path}"
  done < <(fmt -1 <<< 'Candara Gisha Grandstander LXGW-WenKai/bright LXGW-WenKai/sans NotoSansSC Shayufeite Titillium Yozai')

  # handwriting
  while read -r _path; do
    patchSans "./${_path}"
  done < <(fmt -1 <<< 'Papyrus segoe-print')
fi

"${operator}" && patchOperatorMono
"${monaco}"   && patchMonaco

"${sans}" && patchSans "${path}" "${PATCH_OPT}"
"${mono}" && patchMono "${path}" "${PATCH_OPT}"

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
