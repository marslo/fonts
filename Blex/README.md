# Blex — IBM Plex Mono + ligatures + Nerd Font

[IBM Plex Mono](https://fonts.google.com/specimen/IBM+Plex+Mono) with [Fira Code programming](https://github.com/tonsky/FiraCode) ligatures copied in, then [NerdFont patched](https://github.com/ryanoasis/nerd-fonts) — a reproducible three-stage build.

> [!TIP]
> - download the sources from google fonts: [IBM Plex Mono](https://fonts.google.com/specimen/IBM+Plex+Mono)
> - full from-scratch walkthrough: [Blex Ligature Runbook](https://claude.ai/code/artifact/c9643ca9-6da4-43d1-9404-4b6cced40058)

![Fira Code ligatures in IBMPlexMonoLig — arrows, comparisons, comments](./assets/ligatures.svg)

## pipeline

```bash
IBMPlexMono/  ──[ ligaturize.sh → Ligaturizer ]──▶  IBMPlexMonoLig/  ──[ font-patcher ]──▶  IBMPlexMonoLigNF/
# vendor             + Fira Code + calt                ligatures              + Nerd Font glyphs
```

```bash
Blex/
├── IBMPlexMono/        # vendor sources — IBMPlexMono-{Regular,Bold,Italic,…}.ttf
├── IBMPlexMonoLig/     # stage 2 — Fira Code ligatures added ( family: IBMPlexMonoLig )
├── IBMPlexMonoLigNF/   # stage 3 — NF patched; files are BlexMonoLigNerdFontMono-* ( font-patcher renames Plex→Blex, see below )
├── ligaturize.sh       # stage 2 driver ( wraps /opt/Ligaturizer )
└── preview.py          # renders assets/ligatures.svg
```

## build

```bash
# from the repo root ( fonts/ ) — one command does all three stages
bash build.sh --blex
```

Or run the stages by hand:

```bash
# stage 2 — ligaturize every face ( auto-clones/updates /opt/Ligaturizer )
bash Blex/ligaturize.sh --from ./Blex/IBMPlexMono --to ./Blex/IBMPlexMonoLig

# stage 3 — Nerd Font patch each ligaturized face into IBMPlexMonoLigNF/
```

> [!IMPORTANT]
> Needs **FontForge's python** ( `brew install fontforge` ) and, for the NF step, `font-patcher`. `ligaturize.sh` clones [Ligaturizer](https://github.com/ToxicFrog/Ligaturizer) to `/opt/Ligaturizer` on first run and `reset --hard`s it to the latest on later runs.

## how it works

Ligaturizer copies Fira Code's ligature glyphs and its `calt` rules into each face, scale-corrected to Plex's cell.<br>
`calt` never merges characters — each ligature is drawn as single-cell pieces ( `CR.n.0` … + `lig.n` ) that `calt` swaps in, so the advance width never changes and the font stays monospace.<br>
136 ligatures are copied.

```bash
fontforge -script Blex/preview.py     # regenerate assets/ligatures.svg ( needs hb-shape )
```

> [!NOTE]
> **Italic ligatures are upright.** Fira Code has no italic, so every face gets the same upright ligature glyphs — in italic code the letters slant but `->` / `==` stay vertical. ( The `lig.*` glyphs are byte-identical across Regular and Italic. )

## naming &amp; license

IBM Plex is under the SIL Open Font License 1.1 with **Reserved Font Name “Plex”**, so a modified font may not carry that name.

> [!CAUTION]
> font-patcher renames `IBM Plex` → `Blex` on output automatically. The stage-3 files are `BlexMonoLigNerdFontMono-*.ttf` ( RFN-safe ). Keep `IBMPlexMonoLig/` local; ship the `Blex…` Nerd Font faces.

- Output fonts are **OFL 1.1** ( IBM Plex OFL + Fira Code OFL ).
- Ligaturizer's *script* is GPL-3.0 — used as an external tool; the fonts it produces are not GPL.
- Ligatures via [Fira Code](https://github.com/tonsky/FiraCode) · [Ligaturizer](https://github.com/ToxicFrog/Ligaturizer) · Nerd Font glyphs via [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts).
