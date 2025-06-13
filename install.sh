#!/usr/bin/env bash
# shellcheck source=/dev/null
#=============================================================================
#     FileName : install.sh
#       Author : marslo.jiao@gmail.com
#      Created : 2024-04-16 01:39:12
#   LastChange : 2025-06-13 01:22:34
#=============================================================================

set -euo pipefail

# @credit: https://github.com/ppo/bash-colors
# @usage:  or copy & paste the `c()` function from:
#          https://github.com/ppo/bash-colors/blob/master/bash-colors.sh#L3
if [[ -f "${HOME}/.marslo/bin/bash-color.sh" ]]; then
  source "${HOME}/.marslo/bin/bash-color.sh"
else
  function c() { :; }
fi

# shellcheck disable=SC2155
declare -r ME="$(basename "${BASH_SOURCE[0]:-$0}")"
declare -A typeFlag=( [sans]=false [mono]=false [cn]=false [handwriting]=false )
declare dryRun=false
declare forceCopy=false
declare -a paramList=()

function isWSL()   { [[ -f /proc/version ]] && grep -qEi "(Microsoft|WSL)" /proc/version; }
function isLinux() { ! isWSL && [[ "$(uname)" == "Linux" ]]; }
function isOSX()   { [[ "$(uname)" == "Darwin" ]]; }

function die() { echo -e "$(c Ri)ERROR$(c)$(c 0i): $*.$(c) $(c 0Wdi)exit ...$(c)" >&2; exit 1; }
function skip() { echo -e "$(c Ys)SKIP$(c)$(c 0i): $*.$(c) $(c 0Wdi)skip ...$(c)" >&2; }

declare targetDir
if isOSX; then
  targetDir="$HOME/Library/Fonts"
elif isLinux; then
  targetDir="$HOME/.local/share/fonts"
else
  die "unsupported OS: $(uname)"
fi

declare -A fontMeta=(
  [Candara]='sans:normal'
  [Gisha]='sans:normal'
  [Titillium]='sans:normal'
  [Grandstander]='sans:normal'
  [Recursive]='sans:otf:*DesktopNF/*;mono:otf:RecursiveCodeNF/RecMonoCasual'
  [Operator]='sans:otf:*ProNF/otf;mono:otf:*Mono*NF/otf'
  [NotoSansSC]='sans:normal'
  [spleen]='sans:otf'
  [msyh]='sans:otf'
  [Orbitron]='sans:normal'
  [VictorMono]='mono:otf'
  [ComicMono]='mono:otf'
  [monofur]='mono:ttf'
  [Monaco]='mono:otf'
  [menlo]='mono:otf'
  [audiolink]='mono:otf'
  [monaspace]='mono:otf'
  [Lekton]='mono:normal'
  [agave]='mono:normal'
  [QianLiJiangShan]='cn:otf'
  [LXGW-WenKai]='cn:mono:otf:mono;cn:sans:normal:sans'
  [Yozai]='cn:normal'
  [Shayufeite]='cn:normal'
  [segoe-print]='handwriting:normal'
  [Papyrus]='handwriting:normal'
  [BradleyHandITC]='handwriting:normal'
)

# shellcheck disable=SC2155
declare USAGE="""
USAGE
  $(c Ys)\$ bash ${ME}$(c) $(c 0Wdi)[ $(c 0Gi)OPTIONS $(c 0Wdi)] $(c 0Mi)<FONT_NAME|DIR> $(c 0Wdi)...$(c)

OPTIONS
  $(c G)--sans$(c)               install all sans type fonts
  $(c G)--mono$(c)               install all mono type fonts
  $(c G)--cn$(c)                 install all cn type fonts
  $(c G)--handwriting$(c)        install all handwriting type fonts

  $(c G)--dryrun$(c)             only print cp command, do not execute
  $(c G)--force$(c), $(c G)-f$(c)          force overwrite
  $(c G)--help$(c), $(c G)-h$(c)           show this help

EXAMPLE
  $(c 0Ys)\$ bash ${ME} $(c 0Gi)--dryrun $(c 0Mi)Operator$(c)
  $(c 0Ys)\$ bash ${ME} $(c 0Gi)--force --sans$(c)
  $(c 0Ys)\$ bash ${ME} $(c 0Mi)Monaco Gisha Titillium $(c 0Gi)--force$(c)
  $(c 0Ys)\$ bash ${ME} $(c 0Wi)/path/to/folder$(c)

SUPPORTED FONT NAMES:
"""

function showHelp() {
  # restructuring array list for help message
  local -A fontGroups
  for name in "${!fontMeta[@]}"; do
    IFS=';' read -ra groups <<< "${fontMeta[$name]}"
    for group in "${groups[@]}"; do
      groupType="${group%%:*}"
      [[ -z "${fontGroups[${groupType}]:-}" ]] && fontGroups[${groupType}]="$name" || fontGroups[${groupType}]+=",$name"
    done
  done
  echo -en "${USAGE}"
  for group in "${!fontGroups[@]}"; do
    line="  • ${group}:\n    "
    IFS=',' read -ra names <<< "${fontGroups[${group}]}"
    for i in "${!names[@]}"; do
      [[ ${i} -gt 0 ]] && line+=', '
      line+="$(c 0Mi)${names[${i}]}$(c)"
    done
    printf "%b\n" "${line}"
  done
  exit 0;
}

# parameters
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sans | --mono | --cn | --handwriting )
      type="${1#--}"; typeFlag["${type}"]=true;
      shift ;;
    --dryrun     ) dryRun=true         ; shift ;;
    --force | -f ) forceCopy=true      ; shift ;;
    --help | -h  ) showHelp                    ;;
    --*          ) die "unknown option: $1"    ;;
    *            ) paramList+=( "$1" ) ; shift ;;
  esac
done

function parseFontGroup() {
  local fontName="$1"
  local group="$2"
  IFS=':' read -r t1 t2 source path <<< "${group}"
  local filterType="" fontType="" fontSource="" fontPath="" srcPattern="" tag="" srcDesc=""

  if [[ -n "${path}" ]]; then
    # 4 fields
    filterType="${t1}"; fontType="${t2}"; fontSource="${source}"; fontPath="${path}"
  elif [[ -n "${source}" ]]; then
    # 3 fields: filterType:fontType:fontSource
    filterType="${t1}"; fontType="${t2}"; fontSource="${t2}"; fontPath="${source}"
  elif [[ -n "${t2}" ]]; then
    # 2 fields: filterType:fontType
    filterType="${t1}"; fontType="normal"; fontSource="${t2}"; fontPath=""
  else
    # 1 field: filterType
    filterType="${t1}"; fontType="normal"; fontSource="normal"; fontPath=""
  fi

  if [[ -n "${fontPath}" ]]; then
    [[ "${fontPath}" == /* ]] && srcPattern="${fontPath}" || srcPattern="${fontName}/${fontPath}"
  else
    srcPattern="${fontName}/${fontType}"
    [[ "${fontType}" == "normal" ]] && srcPattern="${fontName}"
  fi

  case "${fontSource}" in
    otf ) srcPattern="${srcPattern}/*NerdFont*.otf" ;;
    ttf ) srcPattern="${srcPattern}/*NerdFont*.ttf" ;;
    *   ) srcPattern="${srcPattern}/*NerdFont*"     ;;
  esac

  tag="${filterType^^}/${fontType^^}/${fontSource}"
  srcDesc="${fontName}/${fontPath:-${fontType}}"
  echo "${srcPattern}|${tag}|${srcDesc}"
}

function copyFonts() {
  local srcPattern="$1"
  local tgtDir="$2"
  local tag="$3"
  local srcDesc="$4"
  local cpCmd=( cp )
  "${forceCopy}" && cpCmd+=( -f )
  cpCmd+=( --target-directory="${tgtDir}" )

  # shellcheck disable=SC2206
  declare -a tags=( ${tag//\// } )
  [[ "${#tags[@]}" -eq 1 ]] && tag="${tags[0]}" || tag="${tags[0]}::${tags[1]}"

  # shellcheck disable=SC2206
  declare -a fontInfo=( ${srcDesc//\//} )

  if compgen -G "${srcPattern}" > /dev/null; then
    # shellcheck disable=SC2086
    set -- ${srcPattern}
    srcs+=( "$@" )
    srcsStr="$(printf '  %s\n' "${srcs[@]}" | sed '$!s/$/ \\/')"      # for dryrun mode print only
    "${dryRun}" && echo -e "$(c 0Wdi)# ${srcDesc}$(c)\n$(c Mi)[${fontInfo[0]}::${tag}]$(c) $(c 0Gi)\$ ${cpCmd[*]}$(c 0Gi) \\ \n${srcsStr}$(c)"
    cpCmd+=( "${srcs[@]}" )
    if ! "${dryRun}"; then
      echo -e "$(c Mi)>> ${fontInfo[0]} ${tag,,}$(c)"
      "${cpCmd[@]}" 2>/dev/null || true;
    fi
  else
    skip "no files matched: ${srcPattern}    $(c 0Wdi)# from ${srcDesc}$(c)"
  fi
}

# --- main ---
declare -A fontsToInstall=()
for t in "${!typeFlag[@]}"; do
  if [[ "${typeFlag[$t]}" == true ]]; then
    for font in "${!fontMeta[@]}"; do
      [[ "${fontMeta[$font]}" == *"${t}"* ]] && fontsToInstall["${font}"]=1
    done
  fi
done
for arg in "${paramList[@]}"; do
  [[ -n "${fontMeta[$arg]:-}" ]] && fontsToInstall["${arg}"]=1
done

if [[ "${#fontsToInstall[@]}" -gt 0 ]]; then
  for font in "${!fontsToInstall[@]}"; do
    IFS=';' read -ra groups <<< "${fontMeta[$font]}"
    for group in "${groups[@]}"; do
      result="$(parseFontGroup "${font}" "${group}")"
      IFS='|' read -r srcPattern tag srcDesc <<< "${result}"
      [[ -z "${srcPattern}"  ]] && continue
      copyFonts "${srcPattern}" "${targetDir}" "${tag}" "${srcDesc}"
    done
  done
else
  for arg in "${paramList[@]}"; do
    if [[ -d "${arg}" ]]; then
      copyFonts "${arg}/*NerdFont*" "${targetDir}" "DIRECTORY" "${arg}"
    else
      skip "no font matched: ${arg}"
    fi
  done
fi

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
