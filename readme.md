
# Nerd Fonts

This is the font-patcher python script (and required source files) from a Nerd Fonts release.

## Running

* To execute run: `fontforge --script ./font-patcher --complete <YOUR FONT FILE>`
* For more CLI options and help: `fontforge --script ./font-patcher --help`

## Further info

For more information see:
* https://github.com/ryanoasis/nerd-fonts/
* https://github.com/ryanoasis/nerd-fonts/releases/latest/

# font-patcher bash completion

Bash completion for the Nerd Fonts `font-patcher` command.

## Install

### bash-completion@2 (lazy load)

```bash
dir="${BASH_COMPLETION_USER_DIR:-$HOME/.local/share/bash-completion}"
dir="${dir%%:*}/completions"
mkdir -p "${dir}"
curl -fsSL https://github.com/marslo/fonts/raw/FontPatcher/completion/font-patcher.bash -o "${dir}/font-patcher"
```

### bash-completion@1

```bash
dir="${BASH_COMPLETION_USER_DIR:-$HOME/.local/share/bash-completion}"
dir="${dir%%:*}"
mkdir -p "${dir}"
curl -fsSL https://github.com/marslo/fonts/raw/FontPatcher/completion/font-patcher.bash -o "${dir}/font-patcher.bash"

echo 'source "${BASH_COMPLETION_USER_DIR:-$HOME/.local/share/bash-completion}/font-patcher.bash"' >> ~/.bashrc
```

Reload your shell (`exec bash`), then `font-patcher --<Tab>` to use it.

## Uninstall

### bash-completion@2

```bash
dir="${BASH_COMPLETION_USER_DIR:-$HOME/.local/share/bash-completion}"
rm -f "${dir%%:*}/completions/font-patcher"
```

### bash-completion@1

```bash
dir="${BASH_COMPLETION_USER_DIR:-$HOME/.local/share/bash-completion}"
rm -f "${dir%%:*}/font-patcher"
```

## Licensing

This script has an MIT license.

The added icons' authors and licenses can be found in the `src/` subdirectory.
