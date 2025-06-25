#!/usr/bin/env bash
# shellcheck source=/dev/null disable=SC2155,SC1079,SC1078
#=============================================================================
#     FileName : build.sh
#       Author : marslo.jiao@gmail.com
#      Created : 2024-04-21 00:21:58
#   LastChange : 2025-06-11 18:59:25
#=============================================================================

set -euo pipefail

# @credit: https://github.com/ppo/bash-colors
# @usage:  or copy & paste the `c()` function from:
#          https://github.com/ppo/bash-colors/blob/master/bash-colors.sh#L3
if [[ -f "${HOME}/.marslo/bin/bash-color.sh" ]]; then
  source "${HOME}/.marslo/bin/bash-color.sh"
else
  c() { :; }
fi

declare -r FONT_PATCHER='/opt/FontPatcher/font-patcher'
declare -ra OPTIONS=( --complete --careful --quiet )
declare -ra MONO_OPTIONS=( --mono "${OPTIONS[@]}" )
declare -a cmd=()
declare -r ME="bash $(basename "${BASH_SOURCE[0]:-$0}")"

# for parameters
declare sans=false
declare mono=false
declare operatorm=false
declare operatorp=false
declare monaco=false
declare recursived=false
declare recursivem=false
declare all=false
declare dryrun=false
declare path=''

declare -r USAGE="""DESCRIPTION
  To build $(c s)Nerd Fonts$(c) for Sans or Mono type

SYNOPSIS
  $(c sY)\$ ${ME} $(c 0Wd)[ $(c 0G)OPTION $(c 0Wd)] [ $(c 0Bi)-- <PATCH_OPT> $(c 0Wd)]$(c)

OPTIONS
  $(c G)--sans$(c)                patch with sans font, requires $(c Mi)--path$(c)
  $(c G)--mono$(c)                patch with mono font, requires $(c Mi)--path$(c)
  $(c G)-a$(c), $(c G)--all$(c)             patch all fonts
  $(c G)-p$(c), $(c G)--path $(c 0Mi)<path>$(c)     the input path to patch fonts

  $(c G)--operator-mono$(c)       patch with operator mono font
  $(c G)--operator-pro$(c)        patch with operator pro font
  $(c G)--monaco$(c)              patch with monaco font
  $(c G)--recursive-desktop$(c)   patch with recursive desktop font
  $(c G)--recursive-mono$(c)      patch with recursive mono font

  $(c G)--dry-run$(c)             show what would be done, but do not execute
  $(c G)-h$(c), $(c G)--help$(c)            show this help message

EXAMPLE
  $(c Wdi)# show help$(c)
  $(c Ys)\$ ${ME} $(c 0G)-h$(c) | $(c Ys)\$ ${ME} $(c 0G)--help$(c)

  $(c Wdi)# show patch command only ( dryrun mode )$(c)
  $(c Ys)\$ ${ME} $(c 0G)--OPTION $(c 0Gi)--dry-run$(c)
  $(c Wdi)# i.e.:$(c)
  $(c Ys)\$ ${ME} $(c 0G)--operator-mono $(c 0Gi)--dry-run$(c)

  $(c Wdi)# to patch Nerd Fonts for $(c 0G)Sans $(c 0Wdi)type with $(c 0Bi)otf$(c 0Wdi) format$(c)
  $(c Ys)\$ ${ME} $(c 0G)--sans --path $(c 0Mi)<path>$(c) $(c 0Bi)-- -ext otf$(c)

  $(c Wdi)# to patch Nerd Fonts for $(c 0G)Mono $(c 0Wdi)type with $(c 0Bi)particular name$(c)
  $(c Ys)\$ ${ME} $(c 0G)--mono --path $(c 0Mi)<path>$(c) $(c 0Bi)-- --name 'NEW NAME Nerd Font'$(c)
"""

function message() {
  local msg=''
  if [[ 1 -eq "$#" ]]; then
    msg="$(c Wdi)clean up Nerd Fonts $(c 0Rsi)'$1'$(c)"
  elif [[ 2 -eq "$#" ]]; then
    msg="$(c Wdi)building $(c 0Gi)$1$(c) $(c Wdi)»$(c) $(c Ys)$2$(c)"
  elif [[ 3 -eq "$#" ]]; then
    msg="$(c Wdi)building $(c 0Ms)$1$(c) $(c Wdi)»$(c) $(c Gi)$2$(c) $(c Wdi)»$(c) $(c Ys)$3$(c)"
  fi
  printf "\n$(c Wdi)..$(c) %b\n" "${msg}"
}

function patchRecursiveDesktop() {
  if ls Recursive/RecursiveDesktopNF/*/* >/dev/null 2>&1; then
    message "Recursive/RecursiveDesktopNF/*/*"
    # shellcheck disable=SC2015
    "${dryrun}" &&
      for i in Recursive/RecursiveDesktopNF/*/*; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done ||
      rm -rfv Recursive/RecursiveDesktopNF/*/*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")NF";
    fontfamily="$(fc-query -f '%{family}' "$(realpath "${_f}")" | awk -F, '{print $1}')";
    style="$(fc-query -f '%{style}' "$(realpath "${_f}")" | awk -F, '{print $1}')";
    name="${fontfamily} ${style} Nerd Font";
    for _e in otf ttf; do
      [[ -d "${outpath}/${_e}" ]] || mkdir -p "${outpath}/${_e}";
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}")" "${OPTIONS[@]}" -ext "${_e}" -out "${outpath}" --name "${name}" )
      # shellcheck disable=SC2015
      "${dryrun}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <(fd -u -tf -e ttf -e otf --full-path Recursive/RecursiveDesktop/)
}

function patchRecursiveMono() {
  if ls Recursive/RecursiveRecursiveMonoNF/*/* >/dev/null 2>&1; then
    message "Recursive/RecursiveRecursiveMonoNF/*/*"
    # shellcheck disable=SC2015
    "${dryrun}" &&
      for i in Recursive/RecursiveRecursiveMonoNF/*/*; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done ||
      rm -rfv Recursive/RecursiveRecursiveMonoNF/*/*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")NF";
    fontfamily="$(fc-query -f '%{family}' "$(realpath "${_f}")" | awk -F, '{print $1}')";
    style="$(fc-query -f '%{style}' "$(realpath "${_f}")" | awk -F, '{print $1}')";
    name="${fontfamily} ${style} Nerd Font";
    for _e in otf ttf; do
      [[ -d "${outpath}/${_e}" ]] || mkdir -p "${outpath}/${_e}";
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}")" "${MONO_OPTIONS[@]}" -ext "${_e}" -out "${outpath}" --name "${name}" )
      # shellcheck disable=SC2015
      "${dryrun}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <(fd -u -tf -e ttf -e otf --full-path Recursive/RecursiveDesktop/)
}

function patchMonaco() {
  if ls Monaco/*NF/*/* >/dev/null 2>&1; then
    message "Monaco/*NF/*/*"
    # shellcheck disable=SC2015
    "${dryrun}" &&
      for i in Monaco/*NF/*/*; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done ||
      rm -rfv Monaco/*NF/*/*
  fi
  while read -r _f; do
    for _e in otf ttf; do
      outpath="$(dirname "${_f}")NF/${_e}";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      message "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}")" "${MONO_OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      # shellcheck disable=SC2015
      "${dryrun}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <(fd -u -tf -e ttf -e otf --full-path ./Monaco)
}

function patchOperatorMono() {
  if ls Operator/*Mono*NF >/dev/null 2>&1; then
    message "Operator/*Mono*NF"
    # shellcheck disable=SC2015
    "${dryrun}" &&
      for i in Operator/*Mono*NF; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done ||
      rm -rfv Operator/*Mono*NF
  fi
  while read -r _f; do
    for _e in otf ttf; do
      input="$(dirname "${_f}")";
      IFS='/' read -r first second rest <<< "${input}"
      outpath="${first}/${second}NF${rest:+/${rest}}/${_e}";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      message "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}")" "${MONO_OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      # shellcheck disable=SC2015
      "${dryrun}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <(fd . Operator/OperatorMono Operator/OperatorMonoLig Operator/OperatorMonoSSmLig -tf -e ttf -e otf)
}

function patchOperatorPro() {
  if ls Operator/Pro*NF* >/dev/null 2>&1; then
    message "Operator/*Pro*NF"
    # shellcheck disable=SC2015
    "${dryrun}" &&
      for i in Operator/*Pro*NF; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done ||
      rm -rfv Operator/*Pro*NF
  fi
  while read -r _f; do
    for _e in otf ttf; do
      input="$(dirname "${_f}")";
      IFS='/' read -r first second rest <<< "${input}"
      outpath="${first}/${second}NF${rest:+/${rest}}/${_e}";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      message "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}")" "${OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      # shellcheck disable=SC2015
      "${dryrun}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <(fd . Operator/OperatorPro -tf -e ttf -e otf)
}

function patchSans() {
  path="$1"
  opt="${2:-}"
  if ls "${path}"/*NerdFont* >/dev/null 2>&1; then
    message "${path}/*NerdFont*"
    # shellcheck disable=SC2015
    "${dryrun}" &&
      for i in "${path}"/*NerdFont*; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done ||
      rm -rfv "${path}"/*NerdFont*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")";
    message "$(basename "${_f}")" "${outpath}"
    cmd=( "${FONT_PATCHER}" "$(realpath "${_f}")" "${OPTIONS[@]}" -out "${outpath}" )
    [[ -n "${opt}" ]] && cmd+=("${opt}")
    # shellcheck disable=SC2015
    "${dryrun}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
  done < <(fd -u -tf -e ttf -e otf --full-path "${path}")
}

function patchMono() {
  path="$1"
  opt="${2:-}"
  if ls "${path}"/*NerdFont* >/dev/null 2>&1; then
    message "${path}/*NerdFont*"
    # shellcheck disable=SC2015
    "${dryrun}" &&
      for i in "${path}"/*NerdFont*; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done ||
      rm -rfv "${path}"/*NerdFont*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")";
    for _e in otf ttf; do
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      cmd=("${FONT_PATCHER}" "$(realpath "${_f}")" "${MONO_OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      [[ -n "${opt}" ]] && cmd+=("${opt}")
      # shellcheck disable=SC2015
      "${dryrun}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done;
  done < <(fd -u -tf -e ttf -e otf --full-path "${path}")
}

function showHelp() { echo -e "${USAGE}"; exit 0; }
function die() { echo -e "$(c R)ERROR$(c) : $*" >&2; exit 2; }

[[ 0 = "$#" ]] && showHelp
# shellcheck disable=SC2124
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sans              ) sans=true                ; shift   ;;
    --mono              ) mono=true                ; shift   ;;
    --operator-mono     ) operatorm=true           ; shift   ;;
    --operator-pro      ) operatorp=true           ; shift   ;;
    --monaco            ) monaco=true              ; shift   ;;
    --recursive-desktop ) recursived=true          ; shift   ;;
    --recursive-mono    ) recursivem=true          ; shift   ;;
    --dry-run           ) dryrun=true              ; shift   ;;
    -a | --all          ) all=true                 ; shift   ;;
    -p | --path         ) path="$2"                ; shift 2 ;;
    --                  ) shift ; PATCH_OPT="$@"   ; break   ;;
    -h | --help | *     ) showHelp                         ;;
  esac
done

[[ -z "${path}" ]] && { "${sans:-false}" || "${mono:-false}"; } &&
  die "Please specify the path ( via \`-p/--path <path>\` )"
# shellcheck disable=SC2001
path="$(sed 's#/*$##' <<< "${path}")"

PATCH_OPT=$( echo "${PATCH_OPT:-}" |
             sed -r 's/\s+--/\n--/g' |
             sed -r "s/^([^ ]+) (.+)$/\1 '\2'/g" |
             sed -e 'N;s/\n/ /'
           )
export PATCH_OPT

# for `--all`
if "${all}"; then
  # mono
  operatorm=true
  monaco=true
  recursivem=true
  while read -r _path; do
    patchMono "./${_path}"
  done < <(fmt -1 <<< 'ComicMono LXGW-WenKai/mono VictorMono audiolink/console audiolink/mono monaspace/radon')

  # sans
  recursived=true
  operatorp=true
  while read -r _path; do
    patchSans "./${_path}"
  done < <(fmt -1 <<< 'Candara Gisha Grandstander LXGW-WenKai/bright LXGW-WenKai/sans NotoSansSC Shayufeite Titillium Yozai')

  # handwriting
  while read -r _path; do
    patchSans "./${_path}"
  done < <(fmt -1 <<< 'Papyrus segoe-print')
fi

"${operatorm}"  && patchOperatorMono
"${operatorp}"  && patchOperatorPro
"${monaco}"     && patchMonaco
"${recursived}" && patchRecursiveDesktop
"${recursivem}" && patchRecursiveMono

"${sans}"       && patchSans "${path}" "${PATCH_OPT}"
"${mono}"       && patchMono "${path}" "${PATCH_OPT}"

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
