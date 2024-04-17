## Nerd Fonts for DevIcons

- devicons:

  ![devicons](./screenshots/devicons-1.png)

## install patched fonts

> TIPS:
> - `fontsPath`:
>   - `osx`: `~/Library/Fonts`
>   - `linux`: `~/.local/share/fonts`

### Operator
- OperatorMono Nerd Font Mono
  ```bash
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMono/OperatorMono-Light.otf \
         https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMono/OperatorMono-LightItalic.otf
  ```

  ![OperatorMonoNFM-Light](https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoNFM-Light.png)

- OperatorMonoLig Nerd Font Mono
  ```bash
  $ ext='otf'             # or ext='ttf'
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/"${ext}"/OperatorMonoLigNerdFontMono-Light."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNF/"${ext}"/OperatorMonoLigNerdFontMono-LightItalic."${ext}"
  ```

  ![OperatorMonoLigNFM-Light](https://github.com/marslo/fonts/raw/fonts/Operator/OperatorMonoLigNFM-Light.png)

- OperatorMonoSSmLig Nerd Font Mono
  ```bash
  $ ext='otf'             # or ext='ttf'
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/blob/fonts/Operator/OperatorMonoSSmLigNF/"${ext}"/OperatorMonoSSmLigNerdFontMono-Regular."${ext}" \
         https://github.com/marslo/fonts/blob/fonts/Operator/OperatorMonoSSmLigNF/"${ext}"/OperatorMonoSSmLigNerdFontMono-Italic."${ext}" \
         https://github.com/marslo/fonts/blob/fonts/Operator/OperatorMonoSSmLigNF/"${ext}"/OperatorMonoSSmLigNerdFontMono-Light."${ext}" \
         https://github.com/marslo/fonts/blob/fonts/Operator/OperatorMonoSSmLigNF/"${ext}"/OperatorMonoSSmLigNerdFontMono-LightItalic."${ext}"
  ```

  ![OperatorMonoSSmLigNFM-Light](https://github.com/marslo/fonts/blob/fonts/Operator/OperatorMonoSSmLigNFM-Light.png)

- Operator Pro Nerd Font

  > TIPS
  > - `OperatorPro-Book` -> `OperatorProNerdFont-Regular`
  > - `OperatorPro-BookItalic` -> `OperatorProNerdFont-Italic`

  ```bash
  $ ext='otf'             # or ext='ttf'
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/OperatorProNerdFont-Regular."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/OperatorProNerdFont-Italic."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/OperatorProNerdFont-Light."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Operator/OperatorProNF/OperatorProNerdFont-LightItalic."${ext}"
  ```

### Monaco Nerd Font Mono
```bash
$ ext='otf'             # or ext='ttf'
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL \
       https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoNerdFontMono-Regular."${ext}"
```

![MonacoNFM](https://github.com/marslo/fonts/raw/fonts/Monaco/MonacoNFM.png)

### [Recursive](https://github.com/arrowtype/recursive)

- Mono

  > support ttf and otf

  ```bash
  # RecMonoCasual
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoCasual/RecMonoCasualNerdFontMono-Regular.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoCasual/RecMonoCasualNerdFontMono-Italic.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoCasual/RecMonoCasualNerdFontMono-Bold.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoCasual/RecMonoCasualNerdFontMono-BoldItalic.otf

  # RecMonoLinear
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoLinear/RecMonoLinearNerdFontMono-Regular.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoLinear/RecMonoLinearNerdFontMono-Italic.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoLinear/RecMonoLinearNerdFontMono-Bold.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoLinear/RecMonoLinearNerdFontMono-BoldItalic.otf

  # RecMonoSemicasual
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoSemicasual/RecMonoSmCasualNerdFontMono-Regular.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoSemicasual/RecMonoSmCasualNerdFontMono-Italic.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoSemicasual/RecMonoSmCasualNerdFontMono-Bold.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoSemicasual/RecMonoSmCasualNerdFontMono-BoldItalic.otf

  # RecMonoDuotone
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoDuotone/RecMonoDuotoneNerdFontMono-Regular.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoDuotone/RecMonoDuotoneNerdFontMono-Italic.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoDuotone/RecMonoDuotoneNerdFontMono-Bold.otf \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Code_NF/RecMonoDuotone/RecMonoDuotoneNerdFontMono-BoldItalic.otf
  ```

  ![RecMonoCasualNFM](https://github.com/marslo/fonts/raw/fonts/Recursive/RecMonoCasualNFM.png)

- desktop
  ```bash
  $ ext='otf'             # or ext='ttf'

  # RecursiveSansCasualStatic
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Desktop_NF/"${ext}"/RecursiveSansCasualStaticNerdFont-Regular."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Desktop_NF/"${ext}"/RecursiveSansCasualStaticNerdFont-Italic."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Desktop_NF/"${ext}"/RecursiveSansCasualStaticNerdFont-Light."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Desktop_NF/"${ext}"/RecursiveSansCasualStaticNerdFont-LightItalic."${ext}"

  # RecursiveSansLinearStatic
  $ curl --create-dirs -O --output-dir "${fontsPath}" \
         -fsSL --remote-name-all \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Desktop_NF/"${ext}"/RecursiveSansLinearStaticNerdFont-Regular."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Desktop_NF/"${ext}"/RecursiveSansLinearStaticNerdFont-Italic."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Desktop_NF/"${ext}"/RecursiveSansLinearStaticNerdFont-Light."${ext}" \
         https://github.com/marslo/fonts/raw/fonts/Recursive/Recursive_Desktop_NF/"${ext}"/RecursiveSansLinearStaticNerdFont-LightItalic."${ext}"
  ```

### VictorMono Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/VictorMono/VictorMono-Light.ttf \
       https://github.com/marslo/fonts/raw/fonts/VictorMono/VictorMono-LightItalic.ttf
```

![VictorMonoNFM-Light](https://github.com/marslo/fonts/raw/fonts/VictorMono/VictorMonoNFM-Light.png)

### ComicMono Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/blob/fonts/ComicMono/ComicMonoNerdFontMono-Regular.otf \
       https://github.com/marslo/fonts/blob/fonts/ComicMono/ComicMonoNerdFontMono-Bold.otf
```

![ComicMonoNFM](https://github.com/marslo/fonts/blob/fonts/ComicMono/ComicMonoNFM.png)

### Monofur Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" \
       -fsSL --remote-name-all \
       https://github.com/marslo/fonts/raw/fonts/monofur/MonofurNerdFontMono-Regular.ttf \
       https://github.com/marslo/fonts/raw/fonts/monofur/MonofurNerdFontMono-Italic.ttf
```

![MonofurNFM](https://github.com/marslo/fonts/raw/fonts/monofur/MonofurNFM.png)

### Menlo Nerd Font Mono
```bash
$ curl --create-dirs -O --output-dir "${fontsPath}" -fsSL \
       https://github.com/marslo/fonts/raw/fonts/menlo/MenloNerdFontMono-Regular.otf
```

![MenloNFM-Regular](https://github.com/marslo/fonts/raw/fonts/menlo/MenloNFM-Regular.png)

## tips
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
