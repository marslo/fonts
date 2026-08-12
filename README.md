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
  - [iosevka](#iosevka)
- [tips](#tips)
  - [get font version](#get-font-version)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## environment setup
### `font-patcher` for Nerd Font
```bash
$ brew install fontforge
```

- font-patcher [v3.5.0.1](https://github.com/marslo/fonts/releases/tag/v3.5.0.1)

  ```
  $ test -d /opt/FontPatcher || mkdir -p /opt/FontPatcher

  # download
  $ curl -o FontPatcher.zip -fsSL https://github.com/marslo/fonts/releases/download/v3.5.0.1/FontPatcher.v3.5.0.1.zip
  $ unzip -o FontPatcher.zip /opt/FontPatcher
  ## or download and extract in one-line command, `bsdtar` is required
  $ curl -fsSL https://github.com/marslo/fonts/releases/download/v3.5.0.1/FontPatcher.v3.5.0.1.zip | bsdtar xzf - -C /opt/FontPatcher
  ## or via clone
  $ git clone --single-branch --branch v3.5.0.1 https://github.com/marslo/fonts.git /opt/FontPatcher

  # environment variable to make `font-patcher` as system command line
  $ echo "test -d '/opt/FontPatcher' && export PATH=\"\$PATH:/opt/FontPatcher\"" >> ~/.bashrc
  ```

- setup auto completion
  ```bash
  # osx
  $ cp completion/font-patcher.bash $(brew --prefix)/etc/bash_completion.d/

  # ubuntu/centos/wsl
  $ cp completion/font-patcher.bash /usr/share/bash-completion/completions/
  # or
  $ cp completion/font-patcher.bash /etc/bash_completion.d/
  ```

  ![font-patcher bash completion](https://github.com/marslo/fonts/raw/main/screenshots/font-patcher-v3.5.0.1-auto-completion.png)

- [v3.5.0](https://github.com/ryanoasis/nerd-fonts/tree/v3.5.0) | [changelog](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.5.0)
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
  $ brew install --HEAD fonttools
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

  # optional
  # -- remove less_slash glyphs --
  $ find . -name less_slash.liga.xml -type f -delete

  # build ligature fonts
  $ npm install
  $ ./build.sh                  # linux
  $ build                       # windows

  # check fonts in `build` folder
  ```

## patch nerd fonts

[![build.sh](https://github.com/marslo/fonts/raw/main/screenshots/font-build.sh--help.png)](https://github.com/marslo/fonts/raw/fonts/build.sh)

| TYPE             | DIR                       | --all COVERED | MANUAL BUILD                                                                                            | MANUAL INSTALL                      |
| ---------------- | ------------------------- | :-----------: | ------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| mono             | **Operator (Mono*NF)**    |       √       | `bash build.sh --operator-mono`                                                                         | `bash install.sh Operator`          |
| sans             | **Operator (ProNF)**      |       √       | `bash build.sh --operator-pro`                                                                          | `bash install.sh Operator`          |
| sans             | **Recursive (DesktopNF)** |       √       | `bash build.sh --recursive-desktop`                                                                     | `bash install.sh Recursive`         |
| mono             | **Recursive (CodeNF)**    |       √       | `bash build.sh --recursive-mono`                                                                        | `bash install.sh Recursive`         |
| mono             | **ComicMono**             |       √       | `bash build.sh --mono --path ComicMono`                                                                 | `bash install.sh ComicMono`         |
| cn (mono)        | **LXGW-WenKai/mono**      |       √       | `bash build.sh --mono --path LXGW-WenKai/mono`                                                          | `bash install.sh LXGW-WenKai`       |
| mono             | **VictorMono**            |       √       | `bash build.sh --mono --path VictorMono`                                                                | `bash install.sh VictorMono`        |
| mono             | **audiolink/console**     |       √       | `bash build.sh --mono --path audiolink/console`                                                         | `bash install.sh audiolink`         |
| mono             | **audiolink/mono**        |       √       | `bash build.sh --mono --path audiolink/mono`                                                            | `bash install.sh audiolink`         |
| mono             | **monaspace/radon**       |       √       | `bash build.sh --mono --path monaspace/radon`                                                           | `bash install.sh monaspace`         |
| mono             | **Monaco**                |       √       | `bash build.sh --monaco`                                                                                | `bash install.sh Monaco`            |
| mono             | **Lekton**                |       √       | `bash build.sh --mono --path Lekton`                                                                    | `bash install.sh Lekton`            |
| mono             | **MonoLisa**              |       √       | `bash build.sh --mono --path MonoLisa`                                                                  | `bash install.sh MonoLisa`          |
| mono             | **agave**                 |       √       | `bash build.sh --mono --path agave`                                                                     | `bash install.sh agave`             |
| mono             | **iosevka**               |       √       | `bash build.sh --mono --path iosevka/marslo`<br>`bash build.sh --mono --path iosevka/ss15`              | `bash install.sh iosevka`           |
| mono             | **menlo**                 |       √       | `bash build.sh --mono --path menlo`                                                                     | `bash install.sh menlo`             |
| mono             | **monofur**               |       √       | `bash build.sh --mono --path monofur`                                                                   | `bash install.sh monofur`           |
| mono             | **spleen**                |       √       | `bash build.sh --mono --path spleen`                                                                    | `bash install.sh spleen`            |
| mono             | **iAWriterMonoS**         |       √       | `bash build.sh --mono --path iAWriterMonoS`                                                             | `bash install.sh iAWriterMonoS`     |
| upright (sans)   | **Titillium/upright**     |       √       | `bash build.sh --titillium-upright`                                                                     | `bash install.sh Titillium/upright` |
| sans             | **Titillium**             |       √       | `bash build.sh --sans --path Titillium`                                                                 | `bash install.sh Titillium`         |
| sans             | **Candara**               |       √       | `bash build.sh --sans --path Candara`                                                                   | `bash install.sh Candara`           |
| sans             | **Gisha**                 |       √       | `bash build.sh --sans --path Gisha`                                                                     | `bash install.sh Gisha`             |
| sans             | **Grandstander**          |       √       | `bash build.sh --sans --path Grandstander`                                                              | `bash install.sh Grandstander`      |
| sans             | **NotoSansSC**            |       √       | `bash build.sh --sans --path NotoSansSC`                                                                | `bash install.sh NotoSansSC`        |
| sans             | **iAWriterQuattroS**      |       √       | `bash build.sh --sans --path iAWriterQuattroS --ext otf --ext ttf`                                      | `bash install.sh iAWriterQuattroS`  |
| sans             | **Orbitron**              |       √       | `bash build.sh --sans --path Orbitron --ext otf --ext ttf`                                              | `bash install.sh Orbitron`          |
| sans             | **msyh**                  |       √       | `bash build.sh --sans --path msyh --ext otf --ext ttf`                                                  | `bash install.sh msyh`              |
| cn (sans)        | **LXGW-WenKai/bright**    |       √       | `bash build.sh --sans --path LXGW-WenKai/bright --ext otf --ext ttf`                                    | `bash install.sh LXGW-WenKai`       |
| cn (sans)        | **LXGW-WenKai/sans**      |       √       | `bash build.sh --sans --path LXGW-WenKai/sans --ext otf --ext ttf`                                      | `bash install.sh LXGW-WenKai`       |
| cn (sans)        | **Yozai**                 |       √       | `bash build.sh --sans --path Yozai --ext otf --ext ttf`                                                 | `bash install.sh Yozai`             |
| handwrite (sans) | **Papyrus**               |       √       | `bash build.sh --sans --path Papyrus`                                                                   | `bash install.sh Papyrus`           |
| handwrite (sans) | **segoe-print**           |       √       | `bash build.sh --sans --path segoe-print`                                                               | `bash install.sh segoe-print`       |
| handwrite (sans) | **BradleyHandITC**        |       √       | `bash build.sh --sans --path BradleyHandITC`                                                            | `bash install.sh BradleyHandITC`    |
|                  |                           |               |                                                                                                         |                                     |
| cn (sans)        | **Shayufeite**            |       ✗       | `bash build.sh --sans --path Shayufeite --ext otf --ext ttf -- --name 'YosheShayufeite Nerd Font'`      | `bash install.sh Shayufeite`        |
| cn (sans)        | **QianLiJiangShan**       |       ✗       | `bash build.sh --sans --path QianLiJiangShan --ext otf --ext ttf -- --name 'QianLiJiangShan Nerd Font'` | `bash install.sh QianLiJiangShan`   |

| SCENARIO                                          | SANS              | MONO        |
| ------------------------------------------------- | ----------------- | ----------- |
| _DEFAULT_                                         | `ttf`             | `otf` `ttf` |
| `--ext otf`                                       | `otf`             | `otf`       |
| `--ext otf,ttf`                                   | `otf` `ttf`       | `otf` `ttf` |
| `-- -ext otf` (passthrough)                       | `otf`             | `otf`       |
| `-- -ext otf -ext ttf` (invalid for font-patcher) | `ttf` (last-wins) | `ttf`       |
| `--ext otf -- -ext ttf` (union)                   | `otf` `ttf`       | `otf` `ttf` |

### Operator
- mono

  ```bash
  $ while read -r _f; do
      for _e in otf ttf; do
        outpath="$(dirname "${_f}")NF/${_e}";
        [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
        echo ".. ${_e} » $(basename ${_f}) » ${outpath}";
        font-patcher "$(realpath "${_f}")" \
                     --mono --complete --careful --quiet --no-progressbars \
                     -ext "${_e}" -out "${outpath}" 2>/dev/null;
      done
    done < <( fd . Operator/OperatorMono Operator/OperatorMonoLig Operator/OperatorMonoSSmLig -tf -e ttf -e otf )
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
                   --mono --complete --careful --quiet --no-progressbars \
                   -ext "${_e}" -out "${outpath}" 2>/dev/null";
    done
  done < <( fd -u -tf -e ttf -e otf --full-path ./Monaco )
```

### [iosevka](https://github.com/be5invis/iosevka)

> [!NOTE]
> - [iosevka](https://typeof.net/Iosevka) | [be5invis/iosevka](https://github.com/be5invis/iosevka)
> - [package link](https://github.com/be5invis/Iosevka/blob/main/doc/PACKAGE-LIST.md)
> - font types
>   - [stylistic sets](https://github.com/be5invis/Iosevka/blob/main/doc/stylistic-sets.md)
>   - [ligation sets](https://github.com/be5invis/Iosevka/blob/main/doc/language-specific-ligation-sets.md)
> - original fonts:
>   - [PkgTTF-IosevkaSS15-34.4.0.zip](https://github.com/be5invis/Iosevka/releases/download/v34.4.0/PkgTTF-IosevkaSS15-34.4.0.zip)
>   - [PkgTTF-IosevkaTermSS15-34.4.0.zip](https://github.com/be5invis/Iosevka/releases/download/v34.4.0/PkgTTF-IosevkaTermSS15-34.4.0.zip)

```bash
$ bash build.sh --mono --path iosevka
```

#### build iosevka custom fonts

1. clone code
   ```bash
   $ git clone --depth 1 https://github.com/be5invis/Iosevka.git /path/to/iosevka
   ```

2. copy the toml file and build

    > [!TIP]
    > - [generate toml automatically](https://typeof.net/Iosevka/customizer)
    > - [Building Iosevka from Source](https://github.com/be5invis/Iosevka/blob/main/doc/custom-build.md)

    ```bash
    $ cp iosevka/marslo/private-build-plans.normal.toml /path/to/iosevka/private-build-plans.toml
    # or
    $ cp iosevka/marslo-term/private-build-plans.term.toml /path/to/iosevka/private-build-plans.toml

    # build
    $ npm install
    $ npm run build -- contents::$(sed -nE '1s/^.*\.(.+)]$/\1/p' < private-build-plans.toml)

    # cleanup
    $ test -d /path/to/iosevka/dist && rm -rf /path/to/iosevka/dist
    ```

### [Recursive](https://github.com/arrowtype/recursive)
- code
  ```bash
  $ while read -r _f; do
      outpath="$(dirname $(dirname $_f))_NF/$(basename $(dirname $_f))";
      [[ -d "${outpath}" ]] || mkdir -p "${outpath}";
      for _e in otf ttf; do
        echo ".. ${_e} » $(basename ${_f}) » ${outpath}";
        font-patcher $(realpath "${_f}") --mono --complete --quiet --no-progressbars -ext ${_e} -out "${outpath}";
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
        font-patcher "$(realpath "${_f}")" --complete --quiet --no-progressbars -ext ${_e} -out "${outpath}/${_e}" --name "\"${name}\""
      done
    done < <(fd -u -tf -e ttf -e otf --full-path Recursive/Recursive_Desktop/)
  ```

### victor mono
```bash
$ while read -r _f; do
    for _e in otf ttf; do
      echo ".. ${_e} >> $(basename ${_f})";
      font-patcher $(realpath "${_f}") --mono --complete --quiet --no-progressbars -ext ${_e} -out ../VictorMono;
    done;
  done < <(fd -u -tf -e ttf -e otf --full-path VictorMono/)
```

### monofur
```bash
$ font-patcher ./monofur/monofur.ttf        --mono --complete --progressbars --extension ttf --outputdir ./monofur --name "monofur Regular Nerd Font" 2>/dev/null
$ font-patcher ./monofur/monofur-italic.ttf --mono --complete --progressbars --extension ttf --outputdir ./monofur --name "monofur Italic Nerd Font"  2>/dev/null
```

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

### get font version

| FIELDS       | DESCRIPTION                                                                                                                                                                                            |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `platformID` | `1`: Unicode<br>`2`: Macintosh<br>`3`: Windows                                                                                                                                                         |
| `platEncID`  | `0`: Unicode<br>`1`: Roman<br>`2`: ShiftJIS<br>`3`: PRC<br>`4`: Big5<br>`5`: Wansung<br>`6`: Johab                                                                                                     |
| `langID`     | `0x0`: Unicode<br>`0x409`: English (US)<br>`0x804`: Chinese (PRC)<br>`0x804`: Chinese (Taiwan)<br>`0x411`: Japanese<br>`0x412`: Korean<br>`0x804`: Chinese (Hong Kong)<br>`0xC04`: Chinese (Singapore) |
| `unicode`    | `True`: Unicode<br>`False`: non-Unicode                                                                                                                                                                |
| `nameID`     | `5`: Version<br>`6`: PostScript name<br>`7`: Trademark<br>`8`: Manufacturer<br>`9`: Designer<br>`10`: Description<br>`11`: URL Vendor<br>`12`: URL Designer<br>`13`: License<br>`14`: License URL      |

```bash
# -- install fonttools --
$ pip install fonttools
```

```bash
# -- check --
$ ttx -o - -t name LXGWWenKaiMono-Regular.ttf | sed -n '/<namerecord nameID="5"/,/<\/namerecord>/p'
Dumping "LXGWWenKaiMono-Regular.ttf" to "<stdout>"...
Dumping 'name' table...
    <namerecord nameID="5" platformID="3" platEncID="1" langID="0x409">
      Version 1.520; June 14, 2025
    </namerecord>

$ ttx -o - -t name LXGWWenKaiMonoNerdFontMono-Regular.otf | sed -n '/<namerecord nameID="5"/,/<\/namerecord>/p'
Dumping "LXGWWenKaiMonoNerdFontMono-Regular.otf" to "<stdout>"...
Dumping 'name' table...
    <namerecord nameID="5" platformID="1" platEncID="0" langID="0x0" unicode="True">
      Version 1.520; June 14, 2025;Nerd Fonts 3.4.0.1
    </namerecord>
    <namerecord nameID="5" platformID="3" platEncID="1" langID="0x409">
      Version 1.520; June 14, 2025;Nerd Fonts 3.4.0.1
    </namerecord>
```
