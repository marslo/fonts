
> [!TIP]
> - [official download](https://fonts.google.com/specimen/Lekton)

## dotted zero ( `0` vs `o` )

Lekton's `0` and `o` look nearly identical. [`dotzero.py`](../dotzero.py) adds a
centered dot to the `0` glyph so the two are easy to tell apart — advance width is
kept ( monospace-safe ), the source `Lekton-*.ttf` are never touched.

> [!IMPORTANT]
> Needs FontForge's python. Run via `fontforge -script`, not plain `python3`.
> `brew install fontforge` ( macOS ) / `apt install fontforge` ( linux ).

### build ( recommended )

`build.sh --lekton` patches Lekton to Nerd Font Mono, then dots the `0` in place:

```bash
# from the repo root ( fonts/ )
bash build.sh --lekton              # build NF ( otf + ttf ) + dot the 0
bash build.sh --lekton --dry-run    # preview the commands only
```

`--all-mono` / `--all` include this step automatically.

### standalone ( dotzero.py )

```bash
# dot every already-built NerdFont face in place
fontforge -script dotzero.py -o Lekton Lekton/*NerdFont*.otf
```

| option | default | description |
|---|---|---|
| `-o, --out-dir DIR` | `<input-parent>/nf-dotted` | output dir |
| `-r, --radius N` | `62` | dot radius at em=1000 |
| `--bold-radius N` | `radius + 10` | radius for bold faces ( auto-detected ) |
| `-g, --glyph NAME` | `zero` | glyph to modify |
| `--rename SUFFIX` | — | append SUFFIX to family name, e.g. `' Dotted'`, to coexist with the original |
| `-n, --dry-run` | — | print actions without writing |

```bash
# smaller dot, keep as a separate family so both can be installed
fontforge -script dotzero.py -r 50 --rename ' Dotted' -o Lekton Lekton/*NerdFont*.otf
```

- inputs may be files or directories ( scans `*.otf` / `*.ttf` )
- radius auto-scales when `em != 1000`; bold faces use `--bold-radius`
