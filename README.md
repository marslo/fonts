<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [setup](#setup)
- [patch fonts](#patch-fonts)
  - [Operator](#operator)
  - [Monaco](#monaco)
  - [Recursive Code](#recursive-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## setup
```bash
$ brew install fontforge

# font-patcher
$ [[ -d /opt/FontPatcher ]] || mkdir -p /opt/FontPatcher
$ curl -o /opt/FontPatcher/FontPatcher.zip \
       -fsSL https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FontPatcher.zip
$ unzip -o /opt/FontPatcher/FontPatcher.zip /opt/FontPatcher
```

## patch fonts
### Operator
- mono
  ```bash
  $ /opt/FontPatcher/font-patcher -out Operator/OperatorMonoNF --mono --complete --progressbars -ext ttf Operator/OperatorMono/OperatorMono-Light.otf
  $ /opt/FontPatcher/font-patcher -out Operator/OperatorMonoNF --mono --complete --progressbars -ext otf Operator/OperatorMono/OperatorMono-Light.otf
  $ /opt/FontPatcher/font-patcher -out Operator/OperatorMonoNF --mono --complete --progressbars -ext ttf Operator/OperatorMono/OperatorMono-LightItalic.otf
  $ /opt/FontPatcher/font-patcher -out Operator/OperatorMonoNF --mono --complete --progressbars -ext otf Operator/OperatorMono/OperatorMono-LightItalic.otf
  ```
- mono lig
  ```bash
  $ /opt/FontPatcher/font-patcher -out Operator/OperatorMonoLigNF --mono --complete --progressbars -ext ttf Operator/OperatorMonoLig/OperatorMonoLig-Light.otf
  $ /opt/FontPatcher/font-patcher -out Operator/OperatorMonoLigNF --mono --complete --progressbars -ext otf Operator/OperatorMonoLig/OperatorMonoLig-Light.otf
  $ /opt/FontPatcher/font-patcher -out Operator/OperatorMonoLigNF --mono --complete --progressbars -ext ttf Operator/OperatorMonoLig/OperatorMonoLig-LightItalic.otf
  $ /opt/FontPatcher/font-patcher -out Operator/OperatorMonoLigNF --mono --complete --progressbars -ext otf Operator/OperatorMonoLig/OperatorMonoLig-LightItalic.otf
  ```

- Pro

  > TIPS
  > - `OperatorPro-Book` -> `OperatoProNerdFont-Regular`
  > - `OperatorPro-BookItalic` -> `OperatoProNerdFont-Italic`

  ```bash
  $ /opt/FontPatcher/font-patcher Operator/OperatorPro/OperatorPro-Light.otf       -out Operator/OperatorProNF --complete --progressbars -ext ttf
  $ /opt/FontPatcher/font-patcher Operator/OperatorPro/OperatorPro-Light.otf       -out Operator/OperatorProNF --complete --progressbars -ext otf
  $ /opt/FontPatcher/font-patcher Operator/OperatorPro/OperatorPro-LightItalic.otf -out Operator/OperatorProNF --complete --progressbars -ext ttf
  $ /opt/FontPatcher/font-patcher Operator/OperatorPro/OperatorPro-LightItalic.otf -out Operator/OperatorProNF --complete --progressbars -ext otf
  $ /opt/FontPatcher/font-patcher Operator/OperatorPro/OperatorPro-Book.otf        -out Operator/OperatorProNF --complete --progressbars -ext ttf --name 'Operato Pro Book Nerd Font'
  $ /opt/FontPatcher/font-patcher Operator/OperatorPro/OperatorPro-Book.otf        -out Operator/OperatorProNF --complete --progressbars -ext otf --name 'Operato Pro Book Nerd Font'
  $ /opt/FontPatcher/font-patcher Operator/OperatorPro/OperatorPro-BookItalic.otf  -out Operator/OperatorProNF --complete --progressbars -ext ttf --name 'Operato Pro Book Italic Nerd Font'
  $ /opt/FontPatcher/font-patcher Operator/OperatorPro/OperatorPro-BookItalic.otf  -out Operator/OperatorProNF --complete --progressbars -ext otf --name 'Operato Pro Book Italic Nerd Font'
  ```

### Monaco
```bash
$ /opt/FontPatcher/font-patcher Monaco/monaco.ttf --mono --complete --progressbars -ext ttf
$ /opt/FontPatcher/font-patcher Monaco/monaco.ttf --mono --complete --progressbars -ext otf
```

### [Recursive](https://github.com/arrowtype/recursive)
- code
  ```bash
  $ while read -r _f; do
      outpath="$(dirname $(dirname $_f))_NF/$(basename $(dirname $_f))";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      for _e in otf ttf; do
        echo ".. ${_e} » $(basename ${_f}) » ${outpath}";
        /opt/FontPatcher/font-patcher $(realpath "${_f}") --mono --complete --quiet -ext ${_e} -out "${outpath}";
      done;
    done < <(fd -u -tf -e ttf -e otf --full-path Recursive/Recursive_Code/)
  ```
- desktop
  ```bash
  $ while read -r _f; do
      outpath="$(dirname $_f)_NF";
      for _e in otf ttf; do
        [[ -d "${outpath}/${_e}" ]] || mkdir -p "${outpath}/${_e}";
        echo ".. ${_e} » $(basename ${_f}) » ${outpath}";
        /opt/FontPatcher/font-patcher $(realpath "${_f}") --complete --quiet -ext ${_e} -out "${outpath}/${_e}"
      done
    done < <(fd -u -tf -e ttf -e otf --full-path Recursive/Recursive_Desktop/)
  ```

### victor mono
```bash
$ while read -r _f; do
    for _e in otf ttf; do
      echo ".. ${_e} >> $(basename ${_f})";
      /opt/FontPatcher/font-patcher $(realpath "${_f}") --mono --complete --quiet -ext ${_e} -out ../VictorMonoNF/$(dirname "${_f}");
    done;
  done < <(fd -u -tf -e ttf -e otf --full-path VictorMono/)
```
