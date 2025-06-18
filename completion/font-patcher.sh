#!/usr/bin/env bash
#=============================================================================
#     FileName : font-patcher.sh
#       Author : marslo.jiao@gmail.com
#      Created : 2024-04-15 19:31:20
#   LastChange : 2025-06-18 15:18:41
#=============================================================================

_font_patcher() {
  # shellcheck disable=SC2034
  local cur prev words cword
  _init_completion -n = || return

  # option → values
  local -A opt_vals=(
    [--debug]="0 1 2 3"
    [--makegroups]="-1 0 1 2 3 4 5 6"
    [--metrics]="HHEA TYPO WIN"
    [--extension]="ttf otf woff woff2"
  )

  # shotr option → long option
  local -A short_to_long=(
    [-ext]=--extension
    [-out]=--outputdir
    [-c]=--complete
    [-h]=--help
    [-q]=--quiet
    [-s]=--mono
    [-v]=--version
    [-l]=--adjust-line-height
  )

  # directory options
  local path_opts=(--outputdir --glyphdir --configfile --custom)

  # long options
  local long_opts=(
    --careful --debug --extension --help --makegroups --mono --outputdir --quiet
    --single-width-glyphs --variable-width-glyphs --version --complete --codicons
    --fontawesome --fontawesomeext --fontlogos --material --mdi --octicons --pomicons
    --powerline --powerlineextra --powersymbols --weather --adjust-line-height
    --boxdrawing --cell --configfile --custom --dry --glyphdir --has-no-italic
    --metrics --name --postprocess --removeligatures --removeligs --xavgcharwidth
    --progressbars --no-progressbars
  )

  # short options
  local short_opts=(-ext -h -s -out -q -v -c -l)

  # the previous parameter is a parameter with a value (such as --debug)
  local prev_opt="${short_to_long[${prev}]:-${prev}}"
  if [[ -n "${opt_vals[${prev_opt}]}" ]]; then
    mapfile -t COMPREPLY < <(compgen -W "${opt_vals[${prev_opt}]}" -- "${cur}")
    return 0
  fi

  # for the previous parameter is the one that requires a path.
  if [[ " ${path_opts[*]} " == *" ${prev} "* ]]; then
    mapfile -t COMPREPLY < <(compgen -d -- "${cur}")
    return 0
  fi

  # for long option - `--xxx`
  if [[ "${cur}" == --* ]]; then
    mapfile -t COMPREPLY < <(compgen -W "${long_opts[*]}" -- "${cur}")
    return 0
  fi

  # for short option - `-x`
  if [[ "${cur}" == -* && "${cur}" != --* ]]; then
    mapfile -t COMPREPLY < <(compgen -W "${short_opts[*]}" -- "${cur}")
    return 0
  fi

  _filedir
}

complete -F _font_patcher font-patcher

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:
