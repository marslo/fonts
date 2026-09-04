
> [!TIP]
> - [official download](https://fonts.google.com/specimen/Lekton)

## glyph tweaks ( dotted `0`, bigger `•` )

[`dotzero.py`](../dotzero.py) post-processes the built Nerd Font faces in place —
advance width is kept ( monospace-safe ) and the source `Lekton-*.ttf` are never touched.

- **dotted `0`** — Lekton's `0` and `o` look nearly identical; a centered dot is added to `0` so the two are easy to tell apart.
- **bigger `•`** — Lekton's bullet ( `•`, U+2022 ) is tiny ( bbox ⌀58 ≈ 5.8% of em, even smaller than the middot `·` ); `--bullet` redraws it as a centered circle ( default radius 100 → ⌀200 = 20% of em ).

> [!IMPORTANT]
> Needs FontForge's python. Run via `fontforge -script`, not plain `python3`.
> `brew install fontforge` ( macOS ) / `apt install fontforge` ( linux ).

### build ( recommended )

`build.sh --lekton` patches Lekton to Nerd Font Mono, then dots the `0` and
enlarges the `•` in place:

```bash
# from the repo root ( fonts/ )
bash build.sh --lekton              # build NF ( otf + ttf ) + dot 0 + enlarge •
bash build.sh --lekton --dry-run    # preview the commands only
```

`--all-mono` / `--all` include this step automatically.

### standalone ( dotzero.py )

```bash
# dot the 0 on every already-built NerdFont face in place
fontforge -script dotzero.py -o Lekton Lekton/*NerdFont*.otf

# dot the 0 and enlarge the • ( default radius 100 = ⌀200 = 20% of em )
fontforge -script dotzero.py --bullet -o Lekton Lekton/*NerdFont*.otf Lekton/*NerdFont*.ttf

# a slightly bigger bullet
fontforge -script dotzero.py --bullet 120 -o Lekton Lekton/*NerdFont*.otf
```

| OPTION              | DEFAULT                    | DESCRIPTION                                                                         |
| ------------------- | -------------------------- | ----------------------------------------------------------------------------------- |
| `-o, --out-dir DIR` | `<input-parent>/nf-dotted` | output dir                                                                          |
| `-r, --radius N`    | `62`                       | dot radius at em=1000                                                               |
| `--bold-radius N`   | `radius + 10`              | dot radius for bold faces ( auto-detected )                                         |
| `-g, --glyph NAME`  | `zero`                     | glyph to dot                                                                        |
| `--bullet [N]`      | off ( `100` when passed )  | enlarge `•` ( U+2022 ) to a circle of radius N at em=1000 ( `100` → ⌀200 = 20% em ) |
| `--rename SUFFIX`   | —                          | append SUFFIX to family name, e.g. `' Dotted'`, to coexist with the original        |
| `-n, --dry-run`     | —                          | print actions without writing                                                       |

```bash
# smaller dot, keep as a separate family so both can be installed
fontforge -script dotzero.py -r 50 --rename ' Dotted' -o Lekton Lekton/*NerdFont*.otf
```

- inputs may be files or directories ( scans `*.otf` / `*.ttf` )
- both radii auto-scale when `em != 1000`; the dot uses `--bold-radius` on bold faces, the bullet keeps one radius across weights

> [!WARNING]
> Re-running on an already-processed face adds a **second** dot to `0` ( it prints a `warn` and proceeds ). Dot from freshly built NF faces, or just use `build.sh --lekton` ( which rebuilds clean faces first ).
