
> [!TIP]
> ## !! inhired from [ryanoasis/nerd-fonts](https://github.com/ryanoasis/nerd-fonts) [v3.4.0](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.4.0) !!
>
> this is a patched font-patcher tool with bash completion

```bash
# -- download the latest FontPatcher branch --
$ git clone --single-branch --branch FontPatcher git@github.com:marslo/fonts.git

# or
$ curl -o FontPatcher.zip \
       -fsSL https://github.com/marslo/fonts/releases/download/v3.4.0.2/FontPatcher-v3.4.0.2.zip &&
  unzip FontPatcher.zip
```

```bash
# -- install --
# osx
$ cp completion/font-patcher.sh $(brew --prefix)/etc/bash_completion.d/

# ubuntu/centos/wsl
$ cp completion/font-patcher.sh /usr/share/bash-completion/completions/
# or
$ cp completion/font-patcher.sh /etc/bash_completion.d/
```

---

# Nerd Fonts

This is font-patcher python script (and required source files) from a Nerd Fonts release.

## Running

* To execute run: `fontforge --script ./font-patcher --complete <YOUR FONT FILE>`
* For more CLI options and help: `fontforge --script ./font-patcher --help`

## Further info

For more information see:
* https://github.com/ryanoasis/nerd-fonts/
* https://github.com/ryanoasis/nerd-fonts/releases/latest/

## Version
This archive is created from

```bash
commit dc4e3309d6c1483532ccaefafd1e940d7c80dec1
Author: Fini Jastrow <ulf.fini.jastrow@desy.de>
Date:   Thu Apr 24 20:21:16 2025 +0200

    CI: Prepare for update casks workflow run [skip ci]

    Signed-off-by: Fini Jastrow <ulf.fini.jastrow@desy.de>
```
