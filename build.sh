#!/usr/bin/env bash
# shellcheck source=/dev/null disable=SC2155,SC1079,SC1078
#=============================================================================
#     FileName : build.sh
#       Author : marslo
#      Created : 2024-04-21 00:21:58
#   LastChange : 2026-09-04 00:56:02
#=============================================================================

set -euo pipefail

# @credit: https://github.com/ppo/bash-colors
# shellcheck disable=SC2015,SC2059
c() { [ $# == 0 ] && printf "\033[0m" || printf "$1" | sed 's/\(.\)/\1;/g;s/\([SDIUFNHT]\)/2\1/g;s/\([KRGYBMCW]\)/3\1/g;s/\([krgybmcw]\)/4\1/g;y/SDIUFNHTsdiufnhtKRGYBMCWkrgybmcw/12345789123457890123456701234567/;s/^\(.*\);$/\\033[\1m/g'; }

declare -r FONT_PATCHER='/opt/FontPatcher/font-patcher'
declare -ra OPTIONS=( --complete --careful --quiet --no-progressbars )
declare -ra MONO_OPTIONS=( --mono "${OPTIONS[@]}" )
declare -a cmd=()
declare -r ME="bash $(basename "${BASH_SOURCE[0]:-$0}")"
# shellcheck disable=SC2155
declare -r SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" && pwd )"
declare -r TU_RUN="${SCRIPT_DIR}/Titillium/upright/scripts/run.sh"   # titillium upright pipeline

# for parameters
declare SANS=false
declare MONO=false
declare OPERATOR_M=false
declare OPERATOR_P=false
declare MONACO=false
declare RECURSIVE_D=false
declare RECURSIVE_M=false
declare TITILLIUM_UP=false
declare LEKTON=false
declare BLEX=false
declare ALL=false
declare ALL_SANS=false
declare ALL_MONO=false
declare ALL_HANDWRITING=false
declare DRYRUN=false
declare path=''
declare -a EXTS=()      # build.sh's own --ext/--extension: which formats to (re)build & clean
declare -a _extv=()     # scratch for comma-splitting --ext values
declare -a REQ_EXTS=()  # resolveExts(): union of default + --ext + PATCHER_OPT -ext ( uniq )
declare -a BASEOPT=()   # resolveExts(): PATCHER_OPT with every -ext/--extension stripped

declare -r USAGE="""DESCRIPTION
  To build $(c s)Nerd Fonts$(c) for Sans or Mono type

SYNOPSIS
  $(c sY)\$ ${ME} $(c 0Wd)[ $(c 0G)OPTION $(c 0Wd)] [ $(c 0Bi)-- <PATCHER_OPT> $(c 0Wd)]$(c)

OPTIONS
  $(c G)-a$(c), $(c G)--all$(c)               patch all fonts
  $(c G)--all-sans$(c)              patch all sans fonts
  $(c G)--all-mono$(c)              patch all mono fonts
  $(c G)--all-handwriting$(c)       patch all handwriting fonts

  $(c G)--sans$(c)                  patch individual sans font recursively, requires $(c Mi)--path$(c)
  $(c G)--mono$(c)                  patch individual mono font recursively, requires $(c Mi)--path$(c)
  $(c G)-p$(c), $(c G)--path $(c 0Mi)<path>$(c)       the input path to patch fonts
  $(c G)--ext$(c), $(c G)--extension $(c 0Mi)<e>$(c)  format(s) to build & clean $(c 0Wdi)( comma or repeated; default sans=follow source, mono=otf+ttf )$(c)

  $(c G)--operator-mono$(c)         patch for operator mono font
  $(c G)--operator-pro$(c)          patch for operator pro font
  $(c G)--monaco$(c)                patch for monaco font
  $(c G)--recursive-desktop$(c)     patch for recursive desktop font
  $(c G)--recursive-mono$(c)        patch for recursive mono font
  $(c G)--titillium-upright$(c)     build Titillium Upright NF: italic + NF + metadata fix. $(c 0Wdi)( src $(c 0Mi)Titillium$(c 0Wdi) -> target $(c 0Mi)Titillium/upright $(c 0Wdi))$(c)
  $(c G)--lekton$(c)                build Lekton + Fira Code ligatures + NF $(c 0Wdi)( Lekton -> LektonLig -> LektonLigNF, via Lekton/build.sh )$(c)
  $(c G)--blex$(c)                  build IBM Plex Mono + Book (350) + Fira Code ligatures + NF $(c 0Wdi)( IBMPlexMono -> IBMPlexMonoLig -> NF, via Blex/build.sh )$(c)

  $(c G)--dry-run$(c)               show what would be done, but do not execute
  $(c G)-h$(c), $(c G)--help$(c)              show this help message

EXAMPLE
  $(c Wdi)# show help$(c)
  $(c Ys)\$ ${ME} $(c 0G)-h$(c) | $(c Ys)\$ ${ME} $(c 0G)--help$(c)

  $(c Wdi)# show patch command only ( dryrun mode )$(c)
  $(c Ys)\$ ${ME} $(c 0Ci)--OPTION $(c 0Gi)--dry-run$(c)
  $(c Wdi)# i.e.:$(c)
  $(c Ys)\$ ${ME} $(c 0Gi)--operator-mono --dry-run$(c)

  $(c Wdi)# to patch $(c 0Gi)Sans $(c 0Wdi)with only $(c 0Bi)otf$(c 0Wdi) ( keeps a prior ttf build )$(c)
  $(c Ys)\$ ${ME} $(c 0Gi)--sans --path $(c 0Mi)<path> $(c 0Gi)--ext otf$(c)

  $(c Wdi)# both formats ( comma or repeated )$(c)
  $(c Ys)\$ ${ME} $(c 0Gi)--sans --path $(c 0Mi)<path> $(c 0Gi)--ext otf,ttf$(c)

  $(c Wdi)# $(c 0Bi)-- <PATCHER_OPT>$(c 0Wdi) is passed verbatim to font-patcher ( its own args )$(c)
  $(c Ys)\$ ${ME} $(c 0Gi)--mono --path $(c 0Mi)<path>$(c) $(c 0Bi)-- --name 'NEW NAME Nerd Font'$(c)
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
    "${DRYRUN}" && for i in Recursive/RecursiveDesktopNF/*/*; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done || rm -rfv Recursive/RecursiveDesktopNF/*/*
  fi
  while read -r _f; do
    outpath="$(dirname "${_f}")NF";
    fontfamily="$(fc-query -f '%{family}' "$(realpath "${_f}" --relative-to=.)" | awk -F, '{print $1}')";
    style="$(fc-query -f '%{style}' "$(realpath "${_f}" --relative-to=.)" | awk -F, '{print $1}')";
    name="${fontfamily} ${style} Nerd Font";
    for _e in otf ttf; do
      [[ -d "${outpath}/${_e}" ]] || mkdir -p "${outpath}/${_e}";
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}" --relative-to=.)" "${OPTIONS[@]}" -ext "${_e}" -out "${outpath}" --name "${name}" )
      # shellcheck disable=SC2015
      "${DRYRUN}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <( fd -u -tf -e ttf -e otf --full-path Recursive/RecursiveDesktop/ )
}

function patchRecursiveMono() {
  if ls Recursive/RecursiveCodeNF/*/* >/dev/null 2>&1; then
    message "Recursive/RecursiveCodeNF/*/*"
    # shellcheck disable=SC2015
    "${DRYRUN}" && for i in Recursive/RecursiveCodeNF/*/*; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done || rm -rfv Recursive/RecursiveCodeNF/*/*
  fi
  while read -r _f; do
    input="$(dirname "${_f}")";
    IFS='/' read -r first second rest <<< "${input}"
    outpath="${first}/${second}NF${rest:+/${rest}}";      # Recursive/RecursiveCodeNF/RecMono*
    [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
    for _e in otf ttf; do
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}" --relative-to=.)" "${MONO_OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      # shellcheck disable=SC2015
      "${DRYRUN}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <( fd -u -tf -e ttf -e otf -E '*NerdFont*' --full-path Recursive/RecursiveCode/ )
}

function patchMonaco() {
  if ls Monaco/*NF/*/* >/dev/null 2>&1; then
    message "Monaco/*NF/*/*"
    # shellcheck disable=SC2015
    "${DRYRUN}" && for i in Monaco/*NF/*/*; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done || rm -rfv Monaco/*NF/*/*
  fi
  while read -r _f; do
    for _e in otf ttf; do
      outpath="$(dirname "${_f}")NF/${_e}";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      message "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}" --relative-to=.)" "${MONO_OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      # shellcheck disable=SC2015
      "${DRYRUN}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <( fd -u -tf -e ttf -e otf --full-path ./Monaco )
}

function patchOperatorMono() {
  if ls Operator/*Mono*NF >/dev/null 2>&1; then
    message "Operator/*Mono*NF"
    # shellcheck disable=SC2015
    "${DRYRUN}" && for i in Operator/*Mono*NF; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done || rm -rfv Operator/*Mono*NF
  fi
  while read -r _f; do
    for _e in otf ttf; do
      input="$(dirname "${_f}")";
      IFS='/' read -r first second rest <<< "${input}"
      outpath="${first}/${second}NF${rest:+/${rest}}/${_e}";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      message "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}" --relative-to=.)" "${MONO_OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      # shellcheck disable=SC2015
      "${DRYRUN}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <( fd . Operator/OperatorMono Operator/OperatorMonoLig Operator/OperatorMonoSSmLig -tf -e ttf -e otf )
}

function patchOperatorPro() {
  if ls Operator/Pro*NF* >/dev/null 2>&1; then
    message "Operator/*Pro*NF"
    # shellcheck disable=SC2015
    "${DRYRUN}" && for i in Operator/*Pro*NF; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done || rm -rfv Operator/*Pro*NF
  fi
  while read -r _f; do
    for _e in otf ttf; do
      input="$(dirname "${_f}")";
      IFS='/' read -r first second rest <<< "${input}"
      outpath="${first}/${second}NF${rest:+/${rest}}/${_e}";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      message "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}" --relative-to=.)" "${OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      # shellcheck disable=SC2015
      "${DRYRUN}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done < <( fd . Operator/OperatorPro -tf -e ttf -e otf )
}

# resolve the effective extensions and passthrough options:
#   REQ_EXTS = uniq( build.sh --ext ( all ) + PATCHER_OPT -ext ( last only ) ); may be
#              empty, in which case the caller applies its default ( sans: ttf, mono: otf+ttf )
#   BASEOPT  = PATCHER_OPT with every -ext/--extension stripped ( rest passed verbatim )
function resolveExts() {
  local a want='' e optlast=''
  local -a all=( "${EXTS[@]}" )
  BASEOPT=()
  for a in "$@"; do
    if test -n "${want}"; then optlast="${a}"; want=''; continue; fi
    if   [[ "${a}" =~ ^(-ext|--ext[a-z]*)$ ]];      then want=1
    elif [[ "${a}" =~ ^(-ext|--ext[a-z]*)=(.+)$ ]]; then optlast="${BASH_REMATCH[2]}"
    else BASEOPT+=( "${a}" )
    fi
  done
  test -n "${optlast}" && all+=( "${optlast}" )
  local -A seen=(); REQ_EXTS=()   # may stay empty -> caller applies its own default
  for e in "${all[@]}"; do test -n "${seen[${e}]:-}" || { REQ_EXTS+=( "${e}" ); seen[${e}]=1; }; done
}

# remove prior NerdFont outputs for exactly the formats that will be (re)built ( REQ_EXTS ), so a prior build of another format is kept ( .png etc. left ).
function cleanOldNF() {
  local path="$1"
  local e i label
  local -a nfOld=()
  shopt -s nullglob
  for e in "${REQ_EXTS[@]}"; do nfOld+=( "${path}"/*NerdFont*."${e}" ); done
  shopt -u nullglob
  test "${#nfOld[@]}" -eq 0 && return 0

  label="$( IFS=,; echo "${REQ_EXTS[*]}" )"
  message "${path}/*NerdFont*.{${label}}"
  # shellcheck disable=SC2015
  "${DRYRUN}" && for i in "${nfOld[@]}"; do echo -e "$(c Wi)  >> rm -rvf ${i}$(c)"; done || rm -rfv "${nfOld[@]}"
}

function patchSans() {
  local path="$1"; shift
  resolveExts "$@"           # -> REQ_EXTS ( union + uniq ) + BASEOPT ( passthrough w/o -ext )
  local dynamic=false
  test "${#REQ_EXTS[@]}" -eq 0 && dynamic=true   # sans default: follow each source's own format ( ttf->ttf, otf->otf )

  # collect sources once ( needed twice: cleanup union + per-file build )
  local -a srcs=()
  while read -r _f; do srcs+=( "${_f}" ); done \
    < <( fd -u -tf -e ttf -e otf -E '*NerdFont*' -E '*[Uu]pright*' -E out --full-path "${path}" )

  # dynamic: clean the union of the sources' own extensions; explicit --ext: clean REQ_EXTS
  if "${dynamic}"; then
    local _u; local -A useen=(); REQ_EXTS=()
    for _f in "${srcs[@]}"; do _u="${_f##*.}"; _u="${_u,,}"; test -n "${useen[${_u}]:-}" || { REQ_EXTS+=( "${_u}" ); useen[${_u}]=1; }; done
  fi
  cleanOldNF "${path}"

  local -a exts=()
  for _f in "${srcs[@]}"; do
    outpath="$(dirname "${_f}")";
    # dynamic -> this source's own ext only ( lowercased ); explicit --ext -> every requested ext
    if "${dynamic}"; then _e="${_f##*.}"; exts=( "${_e,,}" ); else exts=( "${REQ_EXTS[@]}" ); fi
    for _e in "${exts[@]}"; do               # one font-patcher run per ext
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}" --relative-to=.)" "${OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      [[ "${#BASEOPT[@]}" -gt 0 ]] && cmd+=( "${BASEOPT[@]}" )
      # shellcheck disable=SC2015
      "${DRYRUN}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done
}

function patchMono() {
  local path="$1"; shift
  resolveExts "$@"
  test "${#REQ_EXTS[@]}" -eq 0 && REQ_EXTS=( otf ttf )   # mono default: otf + ttf
  cleanOldNF "${path}"
  while read -r _f; do
    outpath="$(dirname "${_f}")";
    for _e in "${REQ_EXTS[@]}"; do
      message "${_e}" "$(basename "${_f}")" "${outpath}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}" --relative-to=.)" "${MONO_OPTIONS[@]}" -ext "${_e}" -out "${outpath}" )
      [[ "${#BASEOPT[@]}" -gt 0 ]] && cmd+=( "${BASEOPT[@]}" )
      # shellcheck disable=SC2015
      "${DRYRUN}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done;
  done < <( fd -u -tf -e ttf -e otf -E '*NerdFont*' -E '*[Uu]pright*' -E out --full-path "${path}" )
}

# build Titillium Upright NF by delegating to the upright pipeline ( prep.py italic staging + «/» fix -> font-patcher -> fixnf.py metadata ). this only generates italic + NF + fixes metadata.
#   source: Titillium (already-extracted vendor OTFs)
#   target: Titillium/upright
function patchTitilliumUpright() {
  local fonts="${SCRIPT_DIR}/Titillium/upright"  # final deliverables
  local work="${fonts}/.build"                   # intermediate build/ + nf/
  # search both dirs for each weight's source: upright roman may live under Titillium/upright, the normal italic (upright-italic glyph source) under Titillium
  local -a src=( "${fonts}" "${SCRIPT_DIR}/Titillium" )

  test -f "${TU_RUN}" || die "titillium upright pipeline not found: ${TU_RUN}"

  local -a runCmd=( bash "${TU_RUN}" )
  local d srcLabel=''
  for d in "${src[@]}"; do
    runCmd+=( --src "${d}" )
    srcLabel="${srcLabel:+${srcLabel}, }${d#"${SCRIPT_DIR}/"}"     # repo-relative, comma-joined
  done
  runCmd+=( --output "${work}" --fonts "${fonts}" --patcher "${FONT_PATCHER}" )
  "${DRYRUN}" && runCmd+=( --dry-run )

  message "titillium upright" "${srcLabel}" "${fonts#"${SCRIPT_DIR}/"}"
  "${runCmd[@]}"
  # clean intermediates only on success; a failed/interrupted run keeps .build (partial nf/ + logs) for inspection, and set -e already aborted before here
  "${DRYRUN}" || rm -rf "${work}"
}

# build the ligaturized Lekton Nerd Font ( no plain NF ):
#   Lekton/build.sh -> Lekton/LektonLig ( Bold Italic + dotted 0 + big • + ^ grave + Fira Code ligatures )
#   then font-patcher -> Lekton/LektonLigNF/ ( otf + ttf ) ; honors --dry-run.
function patchLekton() {
  local path='./Lekton'
  local ligbuild="${SCRIPT_DIR}/Lekton/build.sh"               # Bold Italic + optimized + ligaturize -> LektonLig/
  local ligdir="${path}/LektonLig"                             # optimized + ligatures ( 4 faces )
  local nfdir="${path}/LektonLigNF"                            # + Nerd Font glyphs ( otf + ttf )

  test -f "${ligbuild}" || die "Lekton/build.sh not found: ${ligbuild}"
  command -v fontforge >/dev/null 2>&1 || die "fontforge required ( brew install fontforge )"

  # 1. optimized + ligatures ( delegated to Lekton/build.sh ) -> LektonLig/
  message "build LektonLig ( Bold Italic + fixes + ligatures )" "$(basename "${path}")" "${ligdir}"
  local -a ligCmd=( bash "${ligbuild}" )
  "${DRYRUN}" && ligCmd+=( --dry-run )
  "${ligCmd[@]}"

  # 2. Nerd Font patch LektonLig -> LektonLigNF/ ( otf + ttf )
  shopt -s nullglob
  local -a ligFonts=( "${ligdir}"/*.ttf )
  shopt -u nullglob
  test "${#ligFonts[@]}" -eq 0 && return 0

  message "clean + NF patch" "LektonLig" "${nfdir}"
  # shellcheck disable=SC2015
  "${DRYRUN}" && printf "  $(c Wi)>> \$ rm -rf %q$(c)\n" "${nfdir}" || rm -rf "${nfdir:?}"
  "${DRYRUN}" || mkdir -p "${nfdir}"
  local _f _e cmd
  for _f in "${ligFonts[@]}"; do
    for _e in otf ttf; do
      message "${_e}" "$(basename "${_f}")" "${nfdir}"
      cmd=( "${FONT_PATCHER}" "$(realpath "${_f}" --relative-to=.)" "${MONO_OPTIONS[@]}" -ext "${_e}" -out "${nfdir}" )
      # shellcheck disable=SC2015
      "${DRYRUN}" && printf "  $(c Wi)>> \$ %s$(c)\n" "$(printf "%q " "${cmd[@]}")" || "${cmd[@]}" 2>/dev/null
    done
  done

  # 3. drop the old plain NF ( superseded by LektonLigNF )
  # shellcheck disable=SC2015
  "${DRYRUN}" && printf "  $(c Wi)>> \$ rm -f %s$(c)\n" "${path}/LektonNerdFontMono-*.{otf,ttf}" || rm -f "${path}"/LektonNerdFontMono-*.otf "${path}"/LektonNerdFontMono-*.ttf
}

# build IBM Plex Mono + Book (350) + Fira Code ligatures, then Nerd Font patch ( otf-only ):
#   Blex/build.sh -> Blex/IBMPlexMonoLig ( Book + Fira Code ligatures )
#   then font-patcher -> Blex/IBMPlexMonoLigNF/ ( via blex-fixnames.py ) ; honors --dry-run.
function patchBlex() {
  local path='./Blex'
  local ligbuild="${SCRIPT_DIR}/Blex/build.sh"                # Book + ligaturize -> IBMPlexMonoLig/
  local ligdir="${path}/IBMPlexMonoLig"                       # ligaturized intermediate ( CFF )
  local nfdir="${path}/IBMPlexMonoLigNF"                      # + Nerd Font glyphs ( otf-only )
  local fixnames="${SCRIPT_DIR}/Blex/blex-fixnames.py"       # canonical name + filename restamp

  test -f "${ligbuild}" || die "Blex/build.sh not found: ${ligbuild}"
  test -f "${fixnames}" || die "blex-fixnames.py not found: ${fixnames}"
  command -v fontforge >/dev/null 2>&1 || die "fontforge required ( brew install fontforge )"

  # 1. Book + ligatures ( delegated to Blex/build.sh ) -> IBMPlexMonoLig/
  message "build IBMPlexMonoLig ( Book + ligatures )" "$(basename "${path}")" "${ligdir}"
  local -a ligCmd=( bash "${ligbuild}" )
  "${DRYRUN}" && ligCmd+=( --dry-run )
  "${ligCmd[@]}"

  # 2. Nerd Font patch IBMPlexMonoLig -> IBMPlexMonoLigNF/ ( otf-only ). font-patcher names by usWeightClass ( folding the non-standard Book 350 onto Regular )
  #    and can leak ligaturize's abbreviated weights into some italic families, so patch each face into its own temp dir then blex-fixnames.py restamps name + filename from usWeightClass + the italic bit -- keeps Book distinct + every face canonical.
  shopt -s nullglob
  local -a ligFonts=( "${ligdir}"/*.otf )
  shopt -u nullglob
  test "${#ligFonts[@]}" -eq 0 && return 0

  message "clean + NF patch" "IBMPlexMonoLig" "${nfdir}"
  # shellcheck disable=SC2015
  "${DRYRUN}" && printf "  $(c Wi)>> \$ rm -rf %q$(c)\n" "${nfdir}" || rm -rf "${nfdir:?}"
  "${DRYRUN}" || mkdir -p "${nfdir}"
  local _f _tmp
  local -a _patched=()
  for _f in "${ligFonts[@]}"; do
    message "otf" "$(basename "${_f}")" "${nfdir}"
    if "${DRYRUN}"; then
      printf "  $(c Wi)>> \$ %s -ext otf -out <tmp> | python3 %s --in <tmp>/*.otf --out-dir %q$(c)\n" "${FONT_PATCHER} $(basename "${_f}")" "${fixnames}" "${nfdir}"
      continue
    fi
    _tmp="$( mktemp -d )"
    "${FONT_PATCHER}" "$(realpath "${_f}" --relative-to=.)" "${MONO_OPTIONS[@]}" -ext otf -out "${_tmp}" 2>/dev/null
    shopt -s nullglob; _patched=( "${_tmp}"/*.otf ); shopt -u nullglob
    test -f "${_patched[0]:-}" && python3 "${fixnames}" --in "${_patched[0]}" --out-dir "${nfdir}"
    rm -rf "${_tmp}"
  done
}

function patchAllMono() {
  patchOperatorMono
  patchMonaco
  patchRecursiveMono
  patchLekton                 # lekton: Lekton -> LektonLig ( ligatures ) -> LektonLigNF
  patchBlex                   # blex: ligaturize IBM Plex Mono + Nerd Font

  # common mono
  while read -r _path; do
    patchMono "./${_path}"
  done < <(command fmt -1 <<< 'ComicMono menlo monofur MonoLisa agave iAWriterMonoS spleen FantasqueSansMono LXGW-WenKai/mono VictorMono audiolink/console audiolink/mono monaspace/radon iosevka/marslo iosevka/ss15')
}

function patchAllSans() {
  patchRecursiveDesktop
  patchOperatorPro
  patchTitilliumUpright

  # common sans
  while read -r _path; do
    patchSans "./${_path}"
  done < <(command fmt -1 <<< 'Candara Gisha Grandstander iAWriterQuattroS Orbitron msyh AtkinsonHyperlegibleNext LXGW-WenKai/bright LXGW-WenKai/sans NotoSansSC Titillium Yozai')
}

function patchAllHandwriting() {
  while read -r _path; do
    patchSans "./${_path}"
  done < <(command fmt -1 <<< 'Papyrus segoe-print BradleyHandITC')
}

function patchAll() {
  patchAllMono          # mono
  patchAllSans          # sans
  patchAllHandwriting   # handwriting
}

function showHelp() { echo -e "${USAGE}"; exit 0; }
function die() { echo -e "$(c R)ERROR$(c) : $*" >&2; exit 2; }

declare -a PATCHER_OPT=()

[[ 0 = "$#" ]] && showHelp
# shellcheck disable=SC2124,SC2034
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sans                  ) SANS=true                ; shift   ;;
    --mono                  ) MONO=true                ; shift   ;;
    --operator-mono         ) OPERATOR_M=true          ; shift   ;;
    --operator-pro          ) OPERATOR_P=true          ; shift   ;;
    --monaco                ) MONACO=true              ; shift   ;;
    --recursive-desktop     ) RECURSIVE_D=true         ; shift   ;;
    --recursive-mono        ) RECURSIVE_M=true         ; shift   ;;
    --titillium-upright     ) TITILLIUM_UP=true        ; shift   ;;
    --lekton                ) LEKTON=true              ; shift   ;;
    --blex                  ) BLEX=true               ; shift   ;;
    --dry-run               ) DRYRUN=true              ; shift   ;;
    -a | --all              ) ALL=true                 ; shift   ;;
    --all-sans              ) ALL_SANS=true            ; shift   ;;
    --all-mono              ) ALL_MONO=true            ; shift   ;;
    --all-handwriting       ) ALL_HANDWRITING=true     ; shift   ;;
    -p | --path             ) path="$2"                ; shift 2 ;;
    --ext | --extension     ) IFS=',' read -ra _extv <<< "$2" ; EXTS+=( "${_extv[@]}" ) ; shift 2 ;;
    --ext=* | --extension=* ) IFS=',' read -ra _extv <<< "${1#*=}" ; EXTS+=( "${_extv[@]}" ) ; shift ;;
    --                      ) shift ; PATCHER_OPT=("$@") ; break   ;;
    -h | --help | *         ) showHelp                           ;;
  esac
done

[[ -z "${path}" ]] && { "${SANS:-false}" || "${MONO:-false}"; } &&
  die "Please specify the path ( via \`-p/--path <path>\` )"
# shellcheck disable=SC2001
path="$(sed 's#/*$##' <<< "${path}")"

# for --all
"${ALL}"             && { patchAll;            exit 0; }
"${ALL_SANS}"        && { patchAllSans;        exit 0; }
"${ALL_MONO}"        && { patchAllMono;        exit 0; }
"${ALL_HANDWRITING}" && { patchAllHandwriting; exit 0; }

"${OPERATOR_M}"      && patchOperatorMono
"${OPERATOR_P}"      && patchOperatorPro
"${MONACO}"          && patchMonaco
"${RECURSIVE_D}"     && patchRecursiveDesktop
"${RECURSIVE_M}"     && patchRecursiveMono
"${TITILLIUM_UP}"    && patchTitilliumUpright
"${LEKTON}"          && patchLekton "${PATCHER_OPT[@]}"
"${BLEX}"            && patchBlex

"${SANS}"            && patchSans "${path}" "${PATCHER_OPT[@]}"
"${MONO}"            && patchMono "${path}" "${PATCHER_OPT[@]}"

# guard flags above are `false && cmd` when their mode is off, so the last one would leave $? = 1 on success; set -e already aborts on any real failure.
exit 0

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
