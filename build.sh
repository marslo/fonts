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
declare path=''

# usage
declare usage="""
\t to build Nerd Fonts for Sans or Mono type
\nSYNOPSIS:
\n\t$(c sY)\$ bash build.sh [ -h  | --help ]
\t\t\t[ --sans | --mono ]
\t\t\t[ -p/--path <path> ]
\t\t\t[ -- <PATCH_OPT> ]$(c)
\nEXAMPLE:
\n\tshow help
\t\t$(c G)\$ bash build.sh -h$(c) | $(c G)\$ bash build.sh --help$(c)
\n\tget verbose
\t\t$(c G)\$ bash build.sh -v$(c) | $(c G)\$ bash build.sh --verbose$(c) | $(c G)\$ bash build.sh --debug$(c)
\n\tto list all statistic for current user
\t\t$(c G)\$ bash build.sh -a$(c)
\n\tto list line changes for current user since 1 month ago
\t\t$(c G)\$ bash build.sh --line-change -- --since='1 month ago'$(c)
\n\tto list line-changes statistic for particular account
\t\t$(c G)\$ bash build.sh -l -u <account>$(c) | $(c G)\$ bash build.sh --line-change --account <account>$(c)
\n\tto list statistic for current user with specific GIT_OPT
\t\t$(c G)\$ bash build.sh -- --after='2022-01-01' --before='2023-01-01'$(c)
\t\t$(c G)\$ bash build.sh -- --since='2 weeks 3 days 2 hours 30 minutes 59 seconds ago'$(c)
"""
declare sans=false
declare mono=false
declare path=''
declare usage="""
\t $(c R)git-statistic$(c) - to get bash build.sh for line-changes and commit count
\nSYNOPSIS:
\n\t$(c sY)\$ bash build.sh [ -h  | --help ]
\t\t\t[ -v  | --verbose | --debug ]
\t\t\t[ -a  | --all ]
\t\t\t[ -au | --all-user ]
\t\t\t[ -l  | --line-change ]
\t\t\t[ -c  | --commit-count ]
\t\t\t[ -u  | --user | --account <account> ]
\t\t\t[ -- <GIT_OPT> ]$(c)
\nEXAMPLE:
\n\tshow help
\t\t$(c G)\$ bash build.sh -h$(c) | $(c G)\$ bash build.sh --help$(c)
\n\tbuild sans with specific path
\t\t$(c G)\$ bash build.sh --sans --path </path/to/folder>$(c)
\n\tbuild mono with specific path with specific font name
\t\t$(c G)\$ bash build.sh --mono --path </path/to/folder> -- --name 'NEW NAME'$(c)
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
    eval "command \"${FONT_PATCHER}\" \"$(realpath "${_f}")\" ${OPTIONS} -out \"${outpath} ${opt}\" 2>/dev/null";
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
      eval "command \"${FONT_PATCHER}\" \"$(realpath "${_f}")\" ${MONO_OPTIONS} -ext \"${_e}\" -out \"${outpath} ${opt}\" 2>/dev/null";
    done;
  done < <(fd -u -tf -e ttf -e otf --full-path "${path}")
}

# # mono
# patchMonaco
# patchOperatorMono
# patchMono ./VictorMono
# patchMono ./ComicMono
# patchMono ./audiolink/console
# patchMono ./audiolink/mono
# patchMono ./monaspace/radon
# patchMono ./LXGW-WenKai/mono
#
# # sans
# patchRecursiveDesktop
# patchSans ./Grandstander
# patchSans ./Titillium
# patchSans ./Candara
# patchSans ./Gisha
# patchSans ./NotoSansSC
# patchSans ./LXGW-WenKai/sans
patchSans ./LXGW-WenKai/bright
# patchSans ./Yozai
# patchSans ./Shayufeite
#
# # handwriting
# patchSans ./Papyrus
# patchSans ./segoe-print

function showHelp() { echo -e "${usage}"; exit 0; }
function die() { echo -e "$(c R)ERROR$(c) : $*" >&2; exit 2; }

# shellcheck disable=SC2124
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sans          ) sans=true ; shift                  ;;
    --mono          ) mono=true ; shift                  ;;
    -p | --path     ) path="$2" ; shift 2                ;;
    --              ) shift     ; PATCH_OPT="$@" ; break ;;
    -h | --help | * ) showHelp                           ;;
  esac
done

PATCH_OPT=$(echo "${PATCH_OPT}" |
             sed -r 's/\s+--/\n--/g' |
             sed -r "s/^([^=]+)=(.+)$/\1='\2'/g" |
             sed -e 'N;s/\n/ /'
          )
export PATCH_OPT

[[ -z "${path}" ]] && die "Please specify the path"
if [[ 'true' = "${sans}" ]]; then
  patchSans "${path}" "${PATCH_OPT}"
fi

if [[ 'true' = "${mono}" ]]; then
  patchMono "${path}" "${PATCH_OPT}"
fi

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh
