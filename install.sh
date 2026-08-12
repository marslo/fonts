#!/usr/bin/env bash
# shellcheck source=/dev/null
#=============================================================================
#     FileName : install.sh
#       Author : marslo
#      Created : 2024-04-16 01:39:12
#   LastChange : 2026-08-11 22:40:32
#=============================================================================

set -euo pipefail

# @credit: https://github.com/ppo/bash-colors
# shellcheck disable=SC2015,SC2059
c() { [ $# == 0 ] && printf "\033[0m" || printf "$1" | sed 's/\(.\)/\1;/g;s/\([SDIUFNHT]\)/2\1/g;s/\([KRGYBMCW]\)/3\1/g;s/\([krgybmcw]\)/4\1/g;y/SDIUFNHTsdiufnhtKRGYBMCWkrgybmcw/12345789123457890123456701234567/;s/^\(.*\);$/\\033[\1m/g'; }

# shellcheck disable=SC2155
declare -r ME="$(basename "${BASH_SOURCE[0]:-$0}")"
# shellcheck disable=SC2155
declare -r SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" && pwd )"
declare -r REGISTER="${SCRIPT_DIR}/register.py"
declare -A typeFlag=( [sans]=false [mono]=false [cn]=false [handwriting]=false )
declare dryRun=false
declare forceCopy=false
declare doRegister=true             # run cache-flush/re-register after copy (--no-register disables)
declare registerOnly=false          # --register: registration-only mode, no copy
declare -a paramList=()
declare -a INSTALLED_FILES=()       # target paths actually (re)installed this run

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
  $(c G)--sans$(c)                 install all sans type fonts
  $(c G)--mono$(c)                 install all mono type fonts
  $(c G)--cn$(c)                   install all cn type fonts
  $(c G)--handwriting$(c)          install all handwriting type fonts

  $(c G)--register$(c) $(c 0Mi)<PATTERN>$(c)   registration-only: (re)register existing fonts by ls-glob, no copy
  $(c G)--no-register$(c)          skip the CoreText re-register / cache-flush step

  $(c G)--dryrun$(c)               only print cp command, do not execute
  $(c G)--force$(c), $(c G)-f$(c)            force overwrite $(c 0Wdi)and install NEW fonts (bypass the already-installed filter)$(c)
  $(c G)--help$(c), $(c G)-h$(c)             show this help

NOTE
  by default only refresh fonts already present in $(c 0Wi)${targetDir}$(c);
  fonts not yet installed there are skipped ($(c 0Gi)--force$(c) installs them anyway).
  after copying, macOS runs $(c 0Wi)register.py$(c) to flush the CoreText cache
  and re-register (.user scope); Linux falls back to $(c 0Wi)fc-cache$(c).

REGISTER EXAMPLE
  $(c 0Ys)\$ bash ${ME} $(c 0Gi)--register $(c 0Mi)'~/Library/Fonts/TitilliumNerdFont-UprightSemibold*.otf'$(c)
  $(c 0Ys)\$ bash ${ME} $(c 0Gi)--register $(c 0Mi)~/Library/Fonts/TitilliumNerdFont-UprightSemibold*$(c)

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
    --dryrun      ) dryRun=true        ; shift ;;
    --force | -f  ) forceCopy=true     ; shift ;;
    --register    ) registerOnly=true  ; shift ;;
    --no-register ) doRegister=false   ; shift ;;
    --help | -h   ) showHelp                   ;;
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

function isFontFile() {
  local ext="${1##*.}"
  case "${ext,,}" in otf | ttf | ttc | otc ) return 0 ;; * ) return 1 ;; esac
}

# widen a metadata glob so refresh matches whatever format is installed:
#   .../otf/*NerdFont*.otf -> .../*/*NerdFont*   (any format subdir, any ext)
function broadenPattern() {
  local p="$1"
  p="${p%.otf}"; p="${p%.ttf}"          # drop trailing format ext
  p="${p//\/otf\//\/*\/}"               # /otf/ segment -> /*/
  p="${p//\/ttf\//\/*\/}"               # /ttf/ segment -> /*/
  printf '%s' "${p}"
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

  # candidate glob: --force uses the metadata format (exact); refresh mode is
  # format-agnostic so an installed .ttf face is refreshed from repo .ttf and is
  # never overwritten by the repo .otf (and vice versa).
  local pattern="${srcPattern}"
  "${forceCopy}" || pattern="$( broadenPattern "${srcPattern}" )"

  if ! compgen -G "${pattern}" > /dev/null; then
    skip "no files matched: ${pattern}    $(c 0Wdi)# from ${srcDesc}$(c)"
    return 0
  fi

  # shellcheck disable=SC2086
  set -- ${pattern}
  local -a matched=( "$@" )
  local -a srcs=() skipped=()
  local f base stem
  if "${forceCopy}"; then
    srcs=( "${matched[@]}" )
  else
    # refresh only the same format already present under tgtDir; a stem (face
    # name w/o ext) counts as "not installed" only when NO format of it exists.
    local -A stemSeen=() stemHit=()
    for f in "${matched[@]}"; do
      base="${f##*/}"
      isFontFile "${base}" || continue
      stem="${base%.*}"
      stemSeen["${stem}"]=1
      test -e "${tgtDir}/${base}" && { srcs+=( "${f}" ); stemHit["${stem}"]=1; }
    done
    for stem in "${!stemSeen[@]}"; do
      [[ -z "${stemHit[${stem}]:-}" ]] && skipped+=( "${stem}" )
    done
  fi

  [[ "${#skipped[@]}" -gt 0 ]] &&
    skip "not installed under ${tgtDir}, skip ${#skipped[@]}: ${skipped[*]}    $(c 0Wdi)# from ${srcDesc}$(c)"
  [[ "${#srcs[@]}" -eq 0 ]] && return 0

  local srcsStr
  srcsStr="$(printf '  %s\n' "${srcs[@]}" | sed '$!s/$/ \\/')"      # for dryrun mode print only
  "${dryRun}" && echo -e "$(c 0Wdi)# ${srcDesc}$(c)\n$(c Mi)[${fontInfo[0]}::${tag}]$(c) $(c 0Gi)\$ ${cpCmd[*]}$(c 0Gi) \\ \n${srcsStr}$(c)"
  cpCmd+=( "${srcs[@]}" )
  if ! "${dryRun}"; then
    echo -e "$(c Mi)>> ${fontInfo[0]} ${tag,,}$(c)"
    "${cpCmd[@]}" 2>/dev/null || true;
    for f in "${srcs[@]}"; do INSTALLED_FILES+=( "${tgtDir}/${f##*/}" ); done
  fi
}

# (re)register given inputs (font files, dirs, or ls-globs) via register.py on macOS,
# fall back to fc-cache on linux. defaults to the whole target dir when no input is given.
function registerFonts() {
  local -a inputs=( "$@" )
  [[ "${#inputs[@]}" -eq 0 ]] && inputs=( "${targetDir}" )

  if isOSX; then
    test -f "${REGISTER}" || { skip "register script not found: ${REGISTER}"; return 0; }
    local -a regCmd=( python3 "${REGISTER}" )
    "${dryRun}" && regCmd+=( --dry-run )
    local i
    for i in "${inputs[@]}"; do regCmd+=( --input "${i}" ); done
    echo -e "$(c Mi)>> register (.user): ${inputs[*]}$(c)"
    "${regCmd[@]}"
  elif isLinux; then
    "${dryRun}" && { echo -e "$(c Mi)>> [dry-run] fc-cache -f ${targetDir}$(c)"; return 0; }
    command type -P fc-cache >/dev/null && fc-cache -f "${targetDir}" || true
  fi
}

# post-copy refresh: register only the files (re)installed this run
function refreshFonts() {
  "${doRegister}" || { skip "--no-register: skip cache refresh"; return 0; }
  "${dryRun}"     && { skip "dry-run: skip cache refresh (register.py)"; return 0; }
  [[ "${#INSTALLED_FILES[@]}" -eq 0 ]] && { skip "nothing (re)installed; skip cache refresh"; return 0; }
  registerFonts "${INSTALLED_FILES[@]}"
}

# --- registration-only mode: (re)register existing fonts by ls-glob, no copy ---
if "${registerOnly}"; then
  registerFonts "${paramList[@]}"
  exit 0
fi

# --- install mode ---
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

# flush CoreText cache + re-register the fonts (re)installed this run
refreshFonts

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
