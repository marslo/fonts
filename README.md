<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [setup](#setup)
  - [font-patcher](#font-patcher)
- [patch fonts](#patch-fonts)
  - [Operator](#operator)
  - [Monaco](#monaco)
  - [Recursive](#recursive)
  - [victor mono](#victor-mono)
  - [monofur](#monofur)
  - [functions](#functions)
- [tips](#tips)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## setup
```bash
$ brew install fontforge
```

### font-patcher
- v3.2.1.1

  > *updates for `v3.2.1.1`*
  > - extended the length limitation 100 ( was 31 )
  > - fixed the `SyntaxWarning: invalid escape sequence '\='`
  > - add command-line completion for font-patcher

  ```
  $ [[ -d /opt/FontPatcher ]] || mkdir -p /opt/FontPatcher
  $ curl -o FontPatcher.zip \
         -fsSL https://github.com/marslo/fonts/raw/fonts/FontPatcher.v3.2.1.1.zip
  $ unzip -o FontPatcher.zip /opt/FontPatcher

  # setup completion
  ## osx
  $ cp completion/font-patcher.sh /usr/local/etc/bash_completion.d/

  ## centos/wsl
  $ cp completion/font-patcher.sh /usr/share/bash-completion/completions/
  # or
  $ cp completion/font-patcher.sh /etc/bash_completion.d/

  # setup environment
  $ cat >> ~/.bashrc << EOF
  FONT_PATCHER='/opt/FontPatcher'
  test -d "${FONT_PATCHER}" && PATH+=":${FONT_PATCHER}"
  export $PATH
  EOF
  ```

  ![font-patcher 3.2.1.1 auto completion](https://github.com/marslo/fonts/raw/main/screenshots/font-patcher-v3.2.1.1-auto-completion.png)

- v3.2.1
  ```bash
  $ [[ -d /opt/FontPatcher ]] || mkdir -p /opt/FontPatcher
  $ curl -o FontPatcher.zip \
         -fsSL https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FontPatcher.zip
  $ unzip -o FontPatcher.zip /opt/FontPatcher
  ```

## patch fonts
### Operator
- mono
  ```bash
  $ font-patcher Operator/OperatorMono/OperatorMono-Light.otf       -out Operator/OperatorMonoNF --mono --complete --progressbars -ext ttf 2>/dev/null
  $ font-patcher Operator/OperatorMono/OperatorMono-Light.otf       -out Operator/OperatorMonoNF --mono --complete --progressbars -ext otf 2>/dev/null
  $ font-patcher Operator/OperatorMono/OperatorMono-LightItalic.otf -out Operator/OperatorMonoNF --mono --complete --progressbars -ext ttf 2>/dev/null
  $ font-patcher Operator/OperatorMono/OperatorMono-LightItalic.otf -out Operator/OperatorMonoNF --mono --complete --progressbars -ext otf 2>/dev/null
  ```

- mono lig
  ```bash
  $ font-patcher Operator/OperatorMonoLig/OperatorMonoLig-Light.otf       -out Operator/OperatorMonoLigNF --mono --complete --progressbars -ext ttf 2>/dev/null
  $ font-patcher Operator/OperatorMonoLig/OperatorMonoLig-Light.otf       -out Operator/OperatorMonoLigNF --mono --complete --progressbars -ext otf 2>/dev/null
  $ font-patcher Operator/OperatorMonoLig/OperatorMonoLig-LightItalic.otf -out Operator/OperatorMonoLigNF --mono --complete --progressbars -ext ttf 2>/dev/null
  $ font-patcher Operator/OperatorMonoLig/OperatorMonoLig-LightItalic.otf -out Operator/OperatorMonoLigNF --mono --complete --progressbars -ext otf 2>/dev/null
  ```

- Pro

  > TIPS
  > - `OperatorPro-Book` -> `OperatorProNerdFont-Regular`
  > - `OperatorPro-BookItalic` -> `OperatorProNerdFont-Italic`

  ```bash
  $ font-patcher Operator/OperatorPro/OperatorPro-Light.otf       -out Operator/OperatorProNF --complete --progressbars -ext ttf
  $ font-patcher Operator/OperatorPro/OperatorPro-Light.otf       -out Operator/OperatorProNF --complete --progressbars -ext otf
  $ font-patcher Operator/OperatorPro/OperatorPro-LightItalic.otf -out Operator/OperatorProNF --complete --progressbars -ext ttf
  $ font-patcher Operator/OperatorPro/OperatorPro-LightItalic.otf -out Operator/OperatorProNF --complete --progressbars -ext otf
  $ font-patcher Operator/OperatorPro/OperatorPro-Book.otf        -out Operator/OperatorProNF --complete --progressbars -ext ttf --name 'Operator Pro Book Nerd Font'
  $ font-patcher Operator/OperatorPro/OperatorPro-Book.otf        -out Operator/OperatorProNF --complete --progressbars -ext otf --name 'Operator Pro Book Nerd Font'
  $ font-patcher Operator/OperatorPro/OperatorPro-BookItalic.otf  -out Operator/OperatorProNF --complete --progressbars -ext ttf --name 'Operator Pro Book Italic Nerd Font'
  $ font-patcher Operator/OperatorPro/OperatorPro-BookItalic.otf  -out Operator/OperatorProNF --complete --progressbars -ext otf --name 'Operator Pro Book Italic Nerd Font'
  ```

### Monaco
```bash
$ font-patcher Monaco/monaco.ttf --mono --complete --progressbars -ext ttf
$ font-patcher Monaco/monaco.ttf --mono --complete --progressbars -ext otf
```

### [Recursive](https://github.com/arrowtype/recursive)
- code
  ```bash
  $ while read -r _f; do
      outpath="$(dirname $(dirname $_f))_NF/$(basename $(dirname $_f))";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      for _e in otf ttf; do
        echo ".. ${_e} » $(basename ${_f}) » ${outpath}";
        font-patcher $(realpath "${_f}") --mono --complete --quiet -ext ${_e} -out "${outpath}";
      done;
    done < <(fd -u -tf -e ttf -e otf --full-path Recursive/Recursive_Code/)
  ```
- desktop

  > TIP:
  > Recursive_Desktop requires setup `name` cause the original file using abbreviation for font family and fullname

  ```bash
  $ while read -r _f; do
      outpath="$(dirname "${_f}")_NF";
      fontfamily="$(fc-query -f '%{family}' "$(realpath "${_f}")" | awk -F, '{print $1}')";
      style="$(fc-query -f '%{style}' "$(realpath "${_f}")")";
      name="${fontfamily}";
      if echo "${style}" | grep -i -q "italic"; then name+=" Italic"; fi
      name+=" Nerd Font"
      for _e in otf ttf; do
        [[ -d "${outpath}/${_e}" ]] || mkdir -p "${outpath}/${_e}";
        echo ".. ${_e} » $(basename "${_f}") » ${outpath}";
        font-patcher "$(realpath "${_f}")" --complete --quiet -ext ${_e} -out "${outpath}/${_e}" --name "\"${name}\""
      done
    done < <(fd -u -tf -e ttf -e otf --full-path Recursive/Recursive_Desktop/)
  ```

### victor mono
```bash
$ while read -r _f; do
    for _e in otf ttf; do
      echo ".. ${_e} >> $(basename ${_f})";
      font-patcher $(realpath "${_f}") --mono --complete --quiet -ext ${_e} -out ../VictorMono;
    done;
  done < <(fd -u -tf -e ttf -e otf --full-path VictorMono/)
```

### monofur
```bash
$ font-patcher ./monofur/monofur.ttf        --mono --complete --progressbars --extension ttf --outputdir ./monofur --name "monofur Regular Nerd Font" 2>/dev/null
$ font-patcher ./monofur/monofur-italic.ttf --mono --complete --progressbars --extension ttf --outputdir ./monofur --name "monofur Italic Nerd Font"  2>/dev/null
```

### functions
- [patchSans](./run.sh#L21-L30)
- [patchMono](./run.sh#L32-L43)

## tips
- list fonts properties
  ```bash
  $ fc-query /path/to/font.ttf
  ```

  - i.e.:
    ```bash
    $ fc-query Operator/OperatorMonoLigNF/OperatorMonoLigNerdFontMono-Light.ttf | grep -E 'family|style|fullname|weight|slant|spacing|file'
      family: "OperatorMonoLig Nerd Font Mono"(s) "OperatorMonoLig Nerd Font Mono Light"(s)
      familylang: "en"(s) "en"(s)
      style: "Light"(s) "Regular"(s)
      stylelang: "en"(s) "en"(s)
      fullname: "OperatorMonoLig Nerd Font Mono Light"(s)
      fullnamelang: "en"(s)
      slant: 0(i)(s)
      weight: 50(f)(s)
      spacing: 100(i)(s)
      file: "Operator/OperatorMonoLigNF/OperatorMonoLigNerdFontMono-Light.ttf"(s)
    ```

- [list particular field of fonts properties](https://stackoverflow.com/a/43614521/2940319)
  ```bash
  $ fc-query -f '%{family}\n' /path/to/font.ttf
  ```

  - i.e.:
    ```bash
    $ fc-query -f '%{family}\n%{style}\n%{fullname}' Recursive/Recursive_Desktop/RecursiveSansCslSt-LtItalic.ttf
    Recursive Sans Casual Static,Recursive Sn Csl St Lt
    Light Italic,Italic
    Recursive Sn Csl St Lt Italic

    $ fc-query -f '%{family}\n%{style}\n%{fullname}' Recursive/Recursive_Desktop/RecursiveSansCslSt-LtItalic.ttf | awk -F, '{print $1}'
    Recursive Sans Casual Static
    Light Italic
    Recursive Sn Csl St Lt Italic
    ```

- list all installed fonts
  ```bash
  $ fc-list | sed -re 's/^.+\/([^:]+):\s?([^,:]+),?:?.*$/\1 : \2/g' | column -t -s: -o:
  ```

  - i.e.:
    ```bash
    $ fc-list | sed -re 's/^.+\/([^:]+):\s?([^,:]+),?:?.*$/\1 : \2/g' | column -t -s: -o: | grep operator | sort -t2
    OperatorMonoLigNerdFontMono-Light.otf            : OperatorMonoLig Nerd Font Mono
    OperatorMonoLigNerdFontMono-LightItalic.otf      : OperatorMonoLig Nerd Font Mono
    OperatorMonoNerdFontMono-Light.ttf               : OperatorMono Nerd Font Mono
    OperatorMonoNerdFontMono-LightItalic.ttf         : OperatorMono Nerd Font Mono
    OperatorProNerdFont-Light.ttf                    : OperatorPro Nerd Font
    OperatorProNerdFont-LightItalic.ttf              : OperatorPro Nerd Font
    ```
