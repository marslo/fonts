<h1>!! The project is only for learning records, NOT for any commercial use !!</h1>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Nerd Fonts for DevIcons](#nerd-fonts-for-devicons)
- [install patched fonts](#install-patched-fonts)
  - [Operator](#operator)
    - [OperatorMono Nerd Font Mono](#operatormono-nerd-font-mono)
    - [OperatorMonoLig Nerd Font Mono](#operatormonolig-nerd-font-mono)
    - [OperatorMonoSSmLig Nerd Font Mono](#operatormonossmlig-nerd-font-mono)
    - [Operator Pro Nerd Font](#operator-pro-nerd-font)
  - [Recursive](#recursive)
    - [RecMonoCasual Nerd Font Mono](#recmonocasual-nerd-font-mono)
    - [RecMonoLinear Nerd Font Mono](#recmonolinear-nerd-font-mono)
    - [RecMonoSmCasual Nerd Font Mono](#recmonosmcasual-nerd-font-mono)
    - [RecMonoDuotone Nerd Font Mono](#recmonoduotone-nerd-font-mono)
    - [Recursive Sans Casual Static Nerd Font](#recursive-sans-casual-static-nerd-font)
    - [Recursive Sans Linear Static Nerd Font](#recursive-sans-linear-static-nerd-font)
  - [Monaco Nerd Font Mono](#monaco-nerd-font-mono)
    - [Monaco Nerd Font Mono](#monaco-nerd-font-mono-1)
    - [MonacoLigaturized Nerd Font Mono](#monacoligaturized-nerd-font-mono)
  - [VictorMono Nerd Font Mono](#victormono-nerd-font-mono)
  - [ComicMono Nerd Font Mono](#comicmono-nerd-font-mono)
  - [Monofur Nerd Font Mono](#monofur-nerd-font-mono)
  - [Menlo Nerd Font Mono](#menlo-nerd-font-mono)
- [tips](#tips)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Nerd Fonts for DevIcons

![devicons](./screenshots/devicons-1.png)

# install patched fonts

> [!TIP]
> - `fontsPath`:
>   - `osx`: `~/Library/Fonts`
>   - `linux`: `~/.local/share/fonts`

## Operator
### OperatorMono Nerd Font Mono

> [!TIP]
> support both `otf` and `ttf`:
>> - `https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/<NAME>.otf`
>> - `https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/ttf/<NAME>.ttf`

```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-Bold.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-BoldItalic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-ExtraLight.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-ExtraLightItalic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-Italic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-Light.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-LightItalic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-Medium.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-MediumItalic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNF/otf/OperatorMonoNerdFontMono-Regular.otf &&
  fc-cache -f -v
```

![OperatorMonoNFM-Light](https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNFM-Light.png)

### OperatorMonoLig Nerd Font Mono

> [!TIP]
> support both `otf` and `ttf`
>> - `https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/otf/<NAME>.otf`
>> - `https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/ttf/<NAME>.ttf`
> - or
>> - `https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/NoLessSlash/otf/<NAME>.otf`
>> - `https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/NoLessSlash/ttf/<NAME>.ttf`

```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/otf/OperatorMonoLigNerdFontMono-Italic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/otf/OperatorMonoLigNerdFontMono-Light.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/otf/OperatorMonoLigNerdFontMono-LightItalic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/otf/OperatorMonoLigNerdFontMono-Regular.otf &&
  fc-cache -f -v

# or ligatures without less-slash ( `</` )
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/NoLessSlash/otf/OperatorMonoLigNerdFontMono-Italic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/NoLessSlash/otf/OperatorMonoLigNerdFontMono-Light.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/NoLessSlash/otf/OperatorMonoLigNerdFontMono-LightItalic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/NoLessSlash/otf/OperatorMonoLigNerdFontMono-Regular.otf &&
  fc-cache -f -v
```

![OperatorMonoLigNFM-Light](https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNFM-Light.png)

### OperatorMonoSSmLig Nerd Font Mono

> [!TIP]
> support both `otf` and `ttf`
>> - `https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/otf/<NAME>.otf`
>> - `https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/ttf/<NAME>.ttf`

```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/otf/OperatorMonoSSmLigNerdFontMono-Bold.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/otf/OperatorMonoSSmLigNerdFontMono-BoldItalic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/otf/OperatorMonoSSmLigNerdFontMono-Italic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/otf/OperatorMonoSSmLigNerdFontMono-Light.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/otf/OperatorMonoSSmLigNerdFontMono-LightItalic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/otf/OperatorMonoSSmLigNerdFontMono-Medium.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/otf/OperatorMonoSSmLigNerdFontMono-MediumItalic.otf \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNF/otf/OperatorMonoSSmLigNerdFontMono-Regular.otf &&
  fc-cache -f -v
```

![OperatorMonoSSmLigNFM-Light](https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoSSmLigNFM-Light.png)

### Operator Pro Nerd Font

> [!TIP]
> - `OperatorPro-Book` -> `OperatorProNerdFont-Regular`
> - `OperatorPro-BookItalic` -> `OperatorProNerdFont-Italic`

```bash
$ ext='otf'             # or ext='ttf'
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-Black.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-BlackItalic.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-Bold.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-BoldItalic.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-Italic.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-Light.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-LightItalic.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-Medium.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-MediumItalic.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProNerdFont-Regular.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProXNerdFont-Light.${ext} \
       https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/${ext}/OperatorProXNerdFont-LightItalic.${ext} &&
  fc-cache -f -v
```

## [Recursive](https://github.com/arrowtype/recursive)

> [!TIP]
> support both `otf` and `ttf`

### RecMonoCasual Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoCasual/RecMonoCasualNerdFontMono-Regular.otf \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoCasual/RecMonoCasualNerdFontMono-Italic.otf  \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoCasual/RecMonoCasualNerdFontMono-Bold.otf    \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoCasual/RecMonoCasualNerdFontMono-BoldItalic.otf &&
  fc-cache -f -v
```

### RecMonoLinear Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoLinear/RecMonoLinearNerdFontMono-Regular.otf \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoLinear/RecMonoLinearNerdFontMono-Italic.otf  \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoLinear/RecMonoLinearNerdFontMono-Bold.otf    \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoLinear/RecMonoLinearNerdFontMono-BoldItalic.otf &&
  fc-cache -f -v
```

### RecMonoSmCasual Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoSemicasual/RecMonoSmCasualNerdFontMono-Regular.otf \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoSemicasual/RecMonoSmCasualNerdFontMono-Italic.otf  \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoSemicasual/RecMonoSmCasualNerdFontMono-Bold.otf    \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoSemicasual/RecMonoSmCasualNerdFontMono-BoldItalic.otf &&
  fc-cache -f -v
```

### RecMonoDuotone Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoDuotone/RecMonoDuotoneNerdFontMono-Regular.otf \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoDuotone/RecMonoDuotoneNerdFontMono-Italic.otf  \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoDuotone/RecMonoDuotoneNerdFontMono-Bold.otf    \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveCodeNF/RecMonoDuotone/RecMonoDuotoneNerdFontMono-BoldItalic.otf &&
  fc-cache -f -v
```

![RecMonoCasualNFM](https://github.com/marslo/fonts/raw/fonts/Recursive/RecMonoCasualNFM.png)

### Recursive Sans Casual Static Nerd Font
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveDesktopNF/otf/RecursiveSansCasualStaticNerdFont-Regular.otf \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveDesktopNF/otf/RecursiveSansCasualStaticNerdFont-Italic.otf  \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveDesktopNF/otf/RecursiveSansCasualStaticNerdFont-Light.otf   \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveDesktopNF/otf/RecursiveSansCasualStaticNerdFont-LightItalic.otf &&
  fc-cache -f -v
```

### Recursive Sans Linear Static Nerd Font
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveDesktopNF/otf/RecursiveSansLinearStaticNerdFont-Regular.otf \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveDesktopNF/otf/RecursiveSansLinearStaticNerdFont-Italic.otf  \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveDesktopNF/otf/RecursiveSansLinearStaticNerdFont-Light.otf   \
       https://github.com/marslo/fonts/raw/fonts/Recursive/RecursiveDesktopNF/otf/RecursiveSansLinearStaticNerdFont-LightItalic.otf &&
  fc-cache -f -v
```

## Monaco Nerd Font Mono

> [!TIP]
> - support both `otf` and `ttf`
> - MonacoLigaturized not support for iTerm2 ( not sure why )

### Monaco Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL \
       https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoNF/otf/MonacoNerdFontMono-Regular.otf  \
       https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoNF/otf/MonacoNerdFontMono-Italic.otf   \
       https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoNF/otf/MonacoNerdFontMono-Bold.otf     \
       https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoNF/otf/MonacoNerdFontMono-BoldItalic.otf &&
  fc-cache -f -v
```

### MonacoLigaturized Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL \
       https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoLigNF/otf/MonacoLigaturizedNerdFontMono-Regular.otf  \
       https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoLigNF/otf/MonacoLigaturizedNerdFontMono-Italic.otf   \
       https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoLigNF/otf/MonacoLigaturizedNerdFontMono-Bold.otf     \
       https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoLigNF/otf/MonacoLigaturizedNerdFontMono-BoldItalic.otf &&
  fc-cache -f -v
```

![MonacoNFM](https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoNFM.png)

## VictorMono Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/VictorMono/VictorMono-Light.ttf \
       https://github.com/marslo/fonts/raw/fonts/VictorMono/VictorMono-LightItalic.ttf &&
  fc-cache -f -v
```

![VictorMonoNFM-Light](https://github.com/marslo/fonts/raw/fonts/VictorMono/VictorMonoNFM-Light.png)

## ComicMono Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/ComicMono/ComicMonoNerdFontMono-Regular.otf \
       https://github.com/marslo/fonts/raw/fonts/ComicMono/ComicMonoNerdFontMono-Bold.otf &&
  fc-cache -f -v
```

![ComicMonoNFM](https://github.com/marslo/fonts/raw/fonts/ComicMono/ComicMonoNFM.png)

## Monofur Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/monofur/MonofurNerdFontMono-Regular.ttf \
       https://github.com/marslo/fonts/raw/fonts/monofur/MonofurNerdFontMono-Italic.ttf &&
  fc-cache -f -v
```

![MonofurNFM](https://github.com/marslo/fonts/raw/fonts/monofur/MonofurNFM.png)

## Menlo Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" -fsSL \
       https://github.com/marslo/fonts/raw/fonts/menlo/MenloNerdFontMono-Regular.otf &&
  fc-cache -f -v
```

![MenloNFM-Regular](https://github.com/marslo/fonts/raw/fonts/menlo/MenloNFM-Regular.png)

# tips
- list fonts properties
  ```bash
  $ fc-query /path/to/font.ttf
  ```

- [list particular field of fonts properties](https://stackoverflow.com/a/43614521/2940319)
  ```bash
  $ fc-query -f '%{family}\n' /path/to/font.ttf

  # shwo `guifont` value for nvim/vim
  $ fc-query -f '%{family}\n%{postscriptname}' ~/Library/Fonts/OperatorMonoSSmLigNerdFontMono-Light.otf | awk -F, '{print $NF}'
  OperatorMonoSSmLig Nerd Font Mono Light
  OperatorMonoSSmLigNFM-Light
  ```

- list all installed fonts
  ```bash
  $ fc-list | sed -re 's/^.+\/([^:]+):\s?([^,:]+),?:?.*$/\1 : \2/g' | column -t -s: -o: | sort -t: -k2
  ```
