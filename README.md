<h2>!! The project is only for learning records, NOT for any commercial use !!</h2>

---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [environment setup](#environment-setup)
  - [`font-patcher` for Nerd Font](#font-patcher-for-nerd-font)
  - [`fonttools` for Operator Mono Lig](#fonttools-for-operator-mono-lig)
- [patch nerd fonts](#patch-nerd-fonts)
  - [Operator](#operator)
  - [Monaco](#monaco)
  - [Recursive](#recursive)
  - [victor mono](#victor-mono)
  - [monofur](#monofur)
  - [functions](#functions)
- [tips](#tips)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## environment setup
### `font-patcher` for Nerd Font
```bash
$ brew install fontforge
```

- font-patcher [v3.2.1.1](https://github.com/marslo/fonts/releases/tag/v3.2.1.1) | [changelog](https://github.com/marslo/fonts/releases/tag/untagged-46572d85c7f7bd03c993)

  ```
  $ [[ -d /opt/FontPatcher ]] || mkdir -p /opt/FontPatcher

  # download v3.2.1.1
  $ curl -o FontPatcher.zip \
         -fsSL https://github.com/marslo/fonts/releases/download/v3.2.1.1/FontPatcher.v3.2.1.1.zip
  $ unzip -o FontPatcher.zip /opt/FontPatcher
  ## or download and extract in one-line command, `bsdtar` is required
  $ curl -fsSL https://github.com/marslo/fonts/releases/download/v3.2.1.1/FontPatcher.v3.2.1.1.zip |
    bsdtar xzf - -C /opt/FontPatcher
  ## or via clone
  $ git clone --branch v3.2.1.1 https://github.com/marslo/fonts.git /opt/FontPatcher

  # environment variable to make `font-patcher` as system command line
  $ echo "test -d '/opt/FontPatcher' && export PATH=\"\$PATH:/opt/FontPatcher\"" >> ~/.bashrc
  ```

- setup auto completion
  ```bash
  # osx
  $ cp completion/font-patcher.sh /usr/local/etc/bash_completion.d/

  # ubuntu/centos/wsl
  $ cp completion/font-patcher.sh /usr/share/bash-completion/completions/
  # or
  $ cp completion/font-patcher.sh /etc/bash_completion.d/
  ```

  ![font-patcher 3.2.1.1 auto completion](https://github.com/marslo/fonts/raw/main/screenshots/font-patcher-v3.2.1.1-auto-completion.png)

- [v3.2.1](https://github.com/ryanoasis/nerd-fonts/tree/v3.2.1) | [changelog](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.2.1)
  ```bash
  $ [[ -d /opt/FontPatcher ]] || mkdir -p /opt/FontPatcher
  $ curl -o FontPatcher.zip \
         -fsSL https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FontPatcher.zip
  $ unzip -o FontPatcher.zip /opt/FontPatcher

  # or
  $ curl -fsSL https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FontPatcher.zip |
    bsdtar xzf - -C /opt/FontPatcher
  ```

### `fonttools` for [Operator Mono Lig](https://github.com/kiliman/operator-mono-lig)

- install fonttools
  ```bash
  # osx
  $ brew install fonttools
  # ubuntu
  $ sudo apt install fonttools
  # others
  $ python3 -m pip install fonttools
  ```

- patch Operator Momo Lig
  ```bash
  # download repo
  $ git clone git@github.com:kiliman/operator-mono-lig.git /opt/operator-mono-lig
  # or
  $ curl -fsSL https://github.com/kiliman/operator-mono-lig/archive/refs/tags/v2.5.2.tar.gz| tar xzf - -C /opt/operator-mono-lig

  # copy fonts into `original` folder
  $ cp OperatorMono*.otf /opt/operator-mono-lig/original
  $ cd /opt/operator-mono-lig

  # build ligature fonts
  $ npm install
  $ ./build.sh                  # linux
  $ build                       # windows

  # check fonts in `build` folder
  ```

## patch nerd fonts

[![build.sh](https://github.com/marslo/fonts/raw/main/screenshots/font-build.sh--help.png)](https://github.com/marslo/fonts/raw/fonts/build.sh)

### Operator
- mono

  ```bash
  $ while read -r _f; do
      for _e in otf ttf; do
        outpath="$(dirname "${_f}")NF/${_e}";
        [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
        echo ".. ${_e} » $(basename ${_f}) » ${outpath}";
        font-patcher "$(realpath "${_f}")" \
                     --mono --complete --careful --quiet \
                     -ext "${_e}" -out "${outpath}" 2>/dev/null;
      done
    done < <(fd . Operator/OperatorMono \
                  Operator/OperatorMonoLig \
                  Operator/OperatorMonoSSmLig \
                  -tf -e ttf -e otf
            )
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

> the Ligature version of Monaco originally from [thep0y/monaco-nerd-font](https://github.com/thep0y/monaco-nerd-font)
> <p>
> the `MonacoLigNF` and `MonacoLig` are all not supported in iTerm2 v3.4.23

```bash
$ while read -r _f; do
    for _e in otf ttf; do
      outpath="$(dirname "${_f}")NF/${_e}";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      echo ".. ${_e} » $(basename ${_f}) » ${outpath}";
      font-patcher "$(realpath ${_f}")"  \
                   --mono --complete --careful --quiet \
                   -ext "${_e}" -out "${outpath}" 2>/dev/null";
    done
  done < <(fd -u -tf -e ttf -e otf --full-path ./Monaco)
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
- [patchSans](./build.sh#L75-L85)
- [patchMono](./build.sh#L88-L101)

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
  $ fc-list | sed -re 's/^.+\/([^:]+):\s?([^,:]+),?:?.*$/\1 : \2/g' | column -t -s: -o: | sort -t: -k2
  ```

  - i.e.:
    ```bash
    $ fc-list | sed -re 's/^.+\/([^:]+):\s?([^,:]+),?:?.*$/\1 : \2/g' | column -t -s: -o: | sort -t: -k2 | grep operator
    OperatorMonoLigNerdFontMono-Light.otf            : OperatorMonoLig Nerd Font Mono
    OperatorMonoLigNerdFontMono-LightItalic.otf      : OperatorMonoLig Nerd Font Mono
    OperatorMonoNerdFontMono-Light.ttf               : OperatorMono Nerd Font Mono
    OperatorMonoNerdFontMono-LightItalic.ttf         : OperatorMono Nerd Font Mono
    OperatorProNerdFont-Light.ttf                    : OperatorPro Nerd Font
    OperatorProNerdFont-LightItalic.ttf              : OperatorPro Nerd Font
    ```
