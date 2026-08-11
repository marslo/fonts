# Titillium Upright → Nerd Font toolkit (simplified)

One command turns the vendor Titillium zip into a clean **"Titillium Nerd Font Upright"** family whose upright faces render truly upright and whose italic faces slant correctly on macOS (CoreText) and in browsers.

```css
font-family: "Titillium Nerd Font Upright";              /* upright Regular     */
font-style:  italic;                                     /* the slanted Italic  */
font-weight: bold;                                       /* upright Bold        */
font-weight: bold; font-style: italic;                   /* slanted Bold Italic */
```

The family ships a complete **RIBBI** set — Regular / Italic / Bold / Bold Italic under one family name — plus the Thin / Light / Semibold weights as their own legacy families, each resolving to the correct face.

---

## What this is (and how it differs from the old 5-step `up/` toolkit)

Same result, fewer moving parts. The old toolkit had five ordered steps (`01`→`05`) with two separate "clean the metadata" passes. This one is **three stages** driven by one entry script:

```text
unzip  ->  prep.py (stage roman + upright-italic, repair «/»)  ->  font-patcher  ->  fixnf.py (unify metadata [+install])
```

Two old steps were removed once their assumptions were checked against the source:

- **Dropped** `01-gen-upright-italic.py`**.** The upright-italic's *outlines are just the vendor* `Titillium-<W>Italic.otf` — the old script copied those outlines verbatim and only borrowed a name table. `prep.py` now just copies the Italic under a new filename; all naming happens later in `fixnf.py`.
- **Dropped** `02-fix-upright-source.py` (the pre-patch metadata clean). It only existed because the old post-patch fixer *sniffed italic-ness from the font's own metadata*, and Titillium's upright sources ship a dirty `ItalicAngle = -13` that would fool it. `fixnf.py` instead learns italic-ness from **which folder** a face came out of (`nf/roman/` vs `nf/italic/`), so the dirty source metadata can never mislead anything — and every dirty field is overwritten anyway.

Why this is safe (verified, not assumed):

- **font-patcher never slants the glyphs it adds by the font's italic angle.** Its only per-glyph transforms are `psMat.scale` (size) and `psMat.translate` (alignment) — no `skew`/`shear`/`italicangle`. So pre-setting italic metadata before patching (what `01` did) changes nothing in the output; the Nerd Font symbols are upright on every face regardless.
- A full run was diffed against the vendor sources: for all 10 faces, **every non-Nerd-Font glyph is byte-for-byte identical to the patcher input** (font-patcher `--careful` and `fixnf.py` never touch existing outlines), the style bits/names match the spec exactly, and the Regular `«`/`»` come out as double chevrons.

Per-weight source → target:

| GENERATED (TARGET)                    | OUTLINES FROM                  | NAMING MIRRORED FROM            |
| ------------------------------------- | ------------------------------ | ------------------------------- |
| `Titillium-RegularUprightItalic.otf`  | `Titillium-RegularItalic.otf`  | `Titillium-RegularUpright.otf`  |
| `Titillium-ThinUprightItalic.otf`     | `Titillium-ThinItalic.otf`     | `Titillium-ThinUpright.otf`     |
| `Titillium-LightUprightItalic.otf`    | `Titillium-LightItalic.otf`    | `Titillium-LightUpright.otf`    |
| `Titillium-SemiboldUprightItalic.otf` | `Titillium-SemiboldItalic.otf` | `Titillium-SemiboldUpright.otf` |
| `Titillium-BoldUprightItalic.otf`     | `Titillium-BoldItalic.otf`     | `Titillium-BoldUpright.otf`     |

---

## Requirements


| TOOL                                                                                             | WHY                                                    | INSTALL                                    |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------ |
| macOS                                                                                            | CoreText / `fontd` registration                        | —                                          |
| Python 3.8+                                                                                      | runs the scripts                                       | `python3 --version`                        |
| `[fonttools](https://github.com/fonttools/fonttools)` 4.x                                        | read/edit OTF metadata                                 | `pip3 install fonttools`                   |
| `[fontforge](https://fontforge.org)` + `[font-patcher](https://github.com/ryanoasis/nerd-fonts)` | patch Nerd Font glyphs                                 | `brew install fontforge`; clone nerd-fonts |
| `swift` (Xcode CLT)                                                                              | `.user`-scope font registration (only for `--install`) | `xcode-select --install`                   |

Quick check:

```bash
python3 -c "import fontTools; print('fonttools', fontTools.version)"
which fontforge
ls /opt/FontPatcher/font-patcher    # or your nerd-fonts clone
swift --version | head -1           # only needed for --install
```

---

## Usage

```bash
./run.sh --input path/to/titillium.zip --output path/to/dir [options]
```


| FLAG             | MEANING                                                                                                                    |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `--input FILE`   | source zip (the 16 flat `Titillium-*.otf`) — **required**                                                                  |
| `--output DIR`   | work + output directory — **required**                                                                                     |
| `--patcher PATH` | path to `font-patcher` (else `$FONT_PATCHER`, else autodetect `/opt/FontPatcher`, `~/git/nerd-fonts`, `~/code/nerd-fonts`) |
| `--install`      | copy the final faces to `~/Library/Fonts`, flush `fontd`, register at `.user` scope                                        |
| `--dry-run`      | print every step, write nothing, skip patch + install                                                                      |


```bash
# preview the whole plan, write nothing
./run.sh --input titillium.zip --output ~/temp/titillium/new/out --dry-run

# real build (no install) — inspect ~/temp/titillium/new/out/fonts
./run.sh --input titillium.zip --output ~/temp/titillium/new/out

# real build + install to ~/Library/Fonts and refresh the font cache
./run.sh --input titillium.zip --output ~/temp/titillium/new/out --patcher /opt/FontPatcher/font-patcher --install
```

`PYTHON=/path/to/python3 ./run.sh ...` overrides the interpreter. The scripts are called via `$PYTHON`, so the execute bit is not required.

---

## Output layout

Everything lives under `--output`:

```
<output>/
├── src/                                                 # unzipped vendor OTFs (16, flat)
├── build/
│   ├── roman/  Titillium-<W>Upright.otf                 # staged patcher input (Regular's «/» repaired)
│   └── italic/ Titillium-<W>UprightItalic.otf           # = vendor Italic, renamed only
├── nf/
│   ├── roman/                                           # font-patcher output for the roman faces
│   └── italic/                                          # font-patcher output for the italic faces
└── fonts/                                               # FINAL deliverables (renamed + metadata-fixed)
    ├── TitilliumNerdFont-UprightRegular.otf
    ├── TitilliumNerdFont-UprightItalic.otf
    ├── TitilliumNerdFont-UprightBold.otf
    ├── TitilliumNerdFont-UprightBoldItalic.otf
    └── TitilliumNerdFont-Upright{Thin,Light,Semibold}[Italic].otf
```

`<W>` = `Thin | Light | Regular | Semibold | Bold`. `Titillium-Black.otf` has no `Upright`/`Italic` pair, so it is reported `skip Black` and left out. The **role (roman vs italic) is carried by the folder** and read back by `fixnf.py`; nothing downstream sniffs italic-ness from (dirty) metadata.

---

## The scripts
### `prep.py` — stage sources by role, repair guillemets

```bash
./prep.py --src <output>/src --build <output>/build [--dry-run]
```

For each weight it copies two vendor faces into role subfolders, then repairs the single-chevron `«`/`»`:


| STAGED FILE                                   | COPIED FROM                    | NOTE                                 |
| --------------------------------------------- | ------------------------------ | ------------------------------------ |
| `build/roman/Titillium-<W>Upright.otf`        | `src/Titillium-<W>Upright.otf` | verbatim; Regular's `«`/`»` repaired |
| `build/italic/Titillium-<W>UprightItalic.otf` | `src/Titillium-<W>Italic.otf`  | renamed only — no metadata surgery   |


No metadata is touched here. The upright-italic is literally the vendor Italic under a new filename; its slant is real and its outlines are final. All naming/flags are set after patching by `fixnf.py`.

### `guillemet.py` — repair single-chevron `«` / `»`

Titillium's **Regular** `Upright` source draws `guillemotleft`/`guillemotright` with a **single** chevron (one contour) instead of the usual **double** chevron (two contours), so `»` shows as a lone `>`. Only the Regular-weight upright is affected — every other face already has the double chevron.

Transplants the correct double-chevron outline (CFF charstring + `hmtx`, metadata untouched) from the same-weight donor `Titillium-<W>.otf` — weight read from the target's `usWeightClass` — into any target whose guillemet is missing or has fewer than two contours. Idempotent: correct faces are skipped (use `--force` to override).

> **Donor is always the upright (non-italic)** `Titillium-<W>.otf`**.** The bug only hits upright faces; every italic face already ships a double chevron and is skipped, so the upright donor is always right. `prep.py` imports this as a function; it also runs standalone on staged sources, on the patched `nf/`** faces, or on an already-installed `~/Library/Fonts/*.otf`:

```bash
./guillemet.py <output>/build/roman --root=<output>/src           # what prep.py does
./guillemet.py ~/Library/Fonts/TitilliumNerdFont-UprightRegular.otf --root=/path/to/sources
```

- `--root=DIR` donor folder (the normal `Titillium-<W>.otf` faces)
- `--donor=FILE` force one donor face (skips weight lookup)
- `--force` re-transplant even if the target already has ≥ 2 contours
- `--dry-run` print intended changes, write nothing

### `fixnf.py` — unify the patched Nerd Font metadata

```bash
./fixnf.py --roman <output>/nf/roman --italic <output>/nf/italic --out <output>/fonts [--install] [--dry-run]
```

font-patcher mangles naming/flags and carries over Titillium's dirty CFF `ItalicAngle`. This rewrites every patched OTF to a clean, CoreText-friendly RIBBI state, writing canonical filenames into `--out`:

- **italic-ness comes from the input folder** (`--roman` vs `--italic`), never from the font's own metadata — this is what lets the old pre-clean step disappear.
- **weight comes from** `usWeightClass` (250/300/400/600/700), so font-patcher's filename casing (e.g. `SemiBold`) is irrelevant.
- rewrites `name` IDs (1/2/4/6/16/17), `head.macStyle`, `OS/2.fsSelection`, `post`/CFF `ItalicAngle`, and the CFF font name. Regular/Bold share the typographic family `Titillium Nerd Font Upright` (RIBBI); Thin/Light/Semibold get their own legacy family for old apps.

`--install` performs the sequence that actually refreshes CoreText on macOS 14+: copy → `rm -rf ~/Library/Caches/com.apple.FontRegistry` → `killall fontd` → `CTFontManagerRegisterFontsForURL(..., .user, ...)`.

### `register-fonts.py` — flush the cache + register any font (generic `--install`)

```bash
./register-fonts.py --input <file|dir> [--dry-run]
```

Standalone, **font-agnostic** version of `fixnf.py --install`. Point `--input` at one font file or a directory of fonts already sitting where you want them (e.g. `~/Library/Fonts`); it registers each face **at its given path** — it never copies.


| FLAG           | MEANING                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------------------- |
| `--input FILE` | register that one font                                                                                  |
| `--input DIR`  | register every `*.otf` / `*.ttf` / `*.ttc` / `*.otc` in `DIR` (case-insensitive, sorted, non-recursive) |
| `--dry-run`    | print the planned font paths, cache flush, `killall`, and registrations; write nothing                  |


Runs the same CoreText refresh as `--install`, at `.user` scope: `rm -rf ~/Library/Caches/com.apple.FontRegistry` → `killall fontd` → per face `CTFontManagerUnregisterFontsForURL(.user)` then `CTFontManagerRegisterFontsForURL(.user)` (unregister first avoids err `-50`). Idempotent — safe to re-run. Needs `swift` (Xcode CLT). Fully quit and reopen the browser/app afterwards.

```bash
./register-fonts.py --input ~/Library/Fonts/MyFont.otf          # one file
./register-fonts.py --input ~/Library/Fonts --dry-run           # preview a whole dir
```

---

## Verify it worked

Resolve the family the way a browser does, via CoreText:

```bash
cat > /tmp/ctcheck.swift <<'SWIFT'
import CoreText
import Foundation
func resolve(_ family: String, _ bold: Bool, _ italic: Bool) -> String {
    var s: CTFontSymbolicTraits = []
    if bold { s.insert(.traitBold) }
    if italic { s.insert(.traitItalic) }
    let t: [CFString: Any] = [kCTFontSymbolicTrait: NSNumber(value: s.rawValue)]
    let a: [CFString: Any] = [kCTFontFamilyNameAttribute: family as CFString,
                              kCTFontTraitsAttribute: t as CFDictionary]
    let f = CTFontCreateWithFontDescriptor(CTFontDescriptorCreateWithAttributes(a as CFDictionary), 13, nil)
    return (CTFontCopyPostScriptName(f) as String) + " slant=" + String(format: "%.1f", CTFontGetSlantAngle(f))
}
// the RIBBI family holds Regular/Italic/Bold/Bold Italic; Thin/Light/Semibold are their own families
let ribbi = "Titillium Nerd Font Upright"
print("[\(ribbi)]")
print("  normal      -> " + resolve(ribbi, false, false))
print("  italic      -> " + resolve(ribbi, false, true))
print("  bold        -> " + resolve(ribbi, true,  false))
print("  bold italic -> " + resolve(ribbi, true,  true))
for w in ["Thin", "Light", "Semibold"] {
    let fam = "\(ribbi) \(w)"
    print("[\(fam)]")
    print("  normal      -> " + resolve(fam, false, false))
    print("  italic      -> " + resolve(fam, false, true))
}
SWIFT
swift /tmp/ctcheck.swift
```

Expected (each request resolves to its own face — bold/bold-italic must **not** fall back to another slant):

```
[Titillium Nerd Font Upright]
  normal      -> TitilliumNF-UprightRegular        slant=0.0
  italic      -> TitilliumNF-UprightItalic         slant=-13.0
  bold        -> TitilliumNF-UprightBold           slant=0.0
  bold italic -> TitilliumNF-UprightBoldItalic     slant=-13.0
[Titillium Nerd Font Upright Thin]
  normal      -> TitilliumNF-UprightThin           slant=0.0
  italic      -> TitilliumNF-UprightThinItalic     slant=-13.0
[Titillium Nerd Font Upright Light]
  normal      -> TitilliumNF-UprightLight          slant=0.0
  italic      -> TitilliumNF-UprightLightItalic    slant=-13.0
[Titillium Nerd Font Upright Semibold]
  normal      -> TitilliumNF-UprightSemibold       slant=0.0
  italic      -> TitilliumNF-UprightSemiboldItalic slant=-13.0
```

`fontconfig` (independent of CoreText) should agree:

```bash
fc-match 'Titillium Nerd Font Upright'              # -> ...Regular
fc-match 'Titillium Nerd Font Upright:italic'       # -> ...Italic
fc-match 'Titillium Nerd Font Upright:bold'         # -> ...Bold
fc-match 'Titillium Nerd Font Upright:bold:italic'  # -> ...Bold Italic
```

### `verify.py` — inspect + check the built faces (no install needed)

```bash
./verify.py [--input FILE|DIR] [--strict] [--coretext]
```

Dumps the CoreText-relevant metadata for each built face and checks it against the RIBBI spec, so a fresh `--output` build can be confirmed without touching the system. Weight is read from `usWeightClass`; the intended italic-ness is taken from the canonical filename, then every field is verified to agree.


| FLAG               | MEANING                                                              |
| ------------------ | -------------------------------------------------------------------- |
| `--input FILE|DIR` | face(s) to check (default `<toolkit>/out/fonts`)                     |
| `--strict`         | exit non-zero if any face fails the spec (for CI)                    |
| `--coretext`       | read CoreText traits (macOS). **given alone** it reads the system font cache and prints only the installed faces (works from anywhere); add `--input FILE\|DIR` to spec-verify those files and read their traits straight from them |
| `--family FAMILY`  | family name for the bare `--coretext` system-cache query (default `Titillium Nerd Font Upright`); only affects bare `--coretext`, ignored when `--input` is given |


Per face it prints and verifies `head.macStyle`, `OS/2.fsSelection` (both decoded), `post` / CFF `ItalicAngle`, `name` IDs 1/2/4/6/16/17, and the Regular `«`/`»` contour count (must be **2**), plus `unitsPerEm` and glyph / PUA counts. `--coretext` confirms roman faces read `italic=n slant≈0.000` and italic faces `italic=Y slant≈0.069`, matching the [Correct style bits](#correct-style-bits-after-the-fix) table — reading straight from the file bytes only when `--input` is given, while bare `--coretext` reflects the installed system cache.

```bash
./verify.py                                                        # spec-check all 10 faces in out/fonts
./verify.py --coretext                                             # read the system font cache; only installed faces
./verify.py --coretext --family "OperatorMonoLig Nerd Font Mono"   # inspect another installed family's cache
./verify.py --coretext --input out/fonts                           # spec-check + per-file CoreText read (all files in dir)
./verify.py --strict                                               # exit 1 on any spec violation
```

#### What the reported fields mean

A sample header line and the meaning of every term it prints:

```
● TitilliumNerdFont-UprightRegular.otf  usWeightClass=400 (Regular)  upm=1000  glyphs=10864  unicode=10805 (base=407, PUA/NF=10398)
```


| FIELD                           | MEANING                                                                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `usWeightClass`                 | OS/2 numeric weight — 250 Thin, 300 Light, 400 Regular, 600 Semibold, 700 Bold; the weight is read from here, never from the filename                  |
| `upm` (`unitsPerEm`)            | the font's design-grid resolution: coordinate units per em (Titillium = `1000`). All glyph outlines / metrics are expressed in these units             |
| `glyphs`                        | total glyph count in the font, **including unencoded** entries (`.notdef`, composite components, alternates)                                           |
| `unicode`                       | number of Unicode codepoints mapped in the `cmap` — i.e. how many characters the font can actually display                                             |
| `base`                          | the **non-PUA** Unicode characters (real text: Latin, punctuation, symbols, incl. `«`/`»`)                                                             |
| `PUA/NF`                        | Private Use Area codepoints (`U+E000–F8FF`, `U+F0000–FFFFD`, `U+100000–10FFFD`) — the Nerd Font icons added by font-patcher. `base + PUA/NF = unicode` |
| `head.macStyle`                 | `head`-table style bits: `0x01` Bold, `0x02` Italic (CoreText reads the italic bit)                                                                    |
| `OS/2.fsSelection`              | OS/2 style bits: `0x01` ITALIC, `0x20` BOLD, `0x40` REGULAR, `0x80` USE_TYPO_METRICS, `0x100` WWS                                                      |
| `post` / CFF `ItalicAngle`      | slant in **degrees** — `0` upright, `-13` italic (CoreText reads the CFF one to judge OTF slant)                                                       |
| `name 1/2/4/6/16/17`            | name-table IDs: family / subfamily / full name / PostScript name / typographic family / typographic subfamily                                          |
| `guillemets « »`                | contour count of `«` / `»` — must be **2** (double chevron); `1` is the broken single chevron                                                          |
| CoreText `slant` (`--coretext`) | CoreText's own **normalized** slant estimate — `~0.000` upright, `~0.069` real italic; a different quantity from the degree-based `italicAngle`        |


---

## Flush the font cache

`./fixnf.py --install` (and `run.sh --install`) already does this end-to-end. For **any** font (not just this family) that is already in place, the standalone `[register-fonts.py](#the-scripts)` is the generic equivalent of `--install` — one command:

```bash
./register-fonts.py --input ~/Library/Fonts/MyFont.otf   # a file, or --input a whole dir
```

Use the manual sequence below when the faces are **already** in `~/Library/Fonts` (edited in place, or copied by hand) and you just need CoreText / `fontd` to notice — on macOS 14+, moving files in/out does **not** reliably refresh the parsed cache.

```bash
# 1) drop CoreText's parsed font DB, then restart the daemon (it auto-respawns)
rm -rf ~/Library/Caches/com.apple.FontRegistry
killall fontd

# 2) re-register the faces at .user scope (unregister first to avoid err -50)
cat > /tmp/reg.swift <<'SWIFT'
import CoreText
import Foundation
let files = [
    "TitilliumNerdFont-UprightRegular.otf",
    "TitilliumNerdFont-UprightItalic.otf",
    "TitilliumNerdFont-UprightBold.otf",
    "TitilliumNerdFont-UprightBoldItalic.otf",
]
let dir = (NSHomeDirectory() as NSString).appendingPathComponent("Library/Fonts")
for f in files {
    let u = URL(fileURLWithPath: (dir as NSString).appendingPathComponent(f)) as CFURL
    CTFontManagerUnregisterFontsForURL(u, .user, nil)
    var err: Unmanaged<CFError>?
    let ok = CTFontManagerRegisterFontsForURL(u, .user, &err)
    print("register \(f): \(ok)")
}
SWIFT
swift /tmp/reg.swift

# 3) fully quit and reopen the browser/app (per-process font cache; a reload isn't enough)
```

Then re-check with [Verify it worked](#verify-it-worked). If a face **still** reads wrong afterwards, the dirt is in the **file**, not the cache — jump to [Diagnose a false italic reading](#diagnose-a-false-italic-reading). Truly stuck cache: log out / log back in.

---

## Troubleshooting

- **Still all italic after editing files** — the file is fine but `fontd`'s parsed cache is stale. Moving files in/out of `~/Library/Fonts` does **not** reliably refresh it on macOS 14+. Use `run.sh --install` / `./fixnf.py --install` (it clears the cache, restarts `fontd`, and re-registers at `.user` scope) — or the manual [Flush the font cache](#flush-the-font-cache) steps if the files are already installed — then fully quit/relaunch the app. Last resort: log out / log back in.
- `CTFontManagerRegisterFontsForURL` **returns** `false` **with err** `-50` — that scope is already occupied; the script unregisters at `.user` scope first, then registers, which works from a CLI process.
- **Browser still shows the old face** — browsers cache fonts per process; do a full **Quit**, not a tab reload.
- `fc-match` **is right but the browser is wrong** — that's the CoreText/`fontd` layer, not fontconfig. Re-run `--install`.
- `<b>` **/** `font-weight: bold` **renders un-bold (and isn't slanted)** — that upright Bold face is being reported *italic* by CoreText (signature `italic=Y slant≈0.08x`), so `bold` resolves to Bold Italic. Diagnose with [Diagnose a false italic reading](#diagnose-a-false-italic-reading); the usual culprit is a stray `head.macStyle` italic bit (`0x02`).
- `»` **shows as a single** `>` **(Regular only)** — the Regular upright `«`/`»` glyphs ship as a single chevron (one contour). `prep.py` already runs `guillemet.py` before patching; to repair an already-installed face, run `./guillemet.py ~/Library/Fonts/TitilliumNerdFont-UprightRegular.otf --root=/path/to/sources` then flush the font cache.
- `run.sh: Permission denied` — the execute bit isn't set (e.g. `chmod` is aliased to `sudo chmod` in your shell). Run via the interpreter instead: `bash run.sh ...` (and `python3 prep.py ...`), or set the bit with the real binary: `/bin/chmod +x *.sh *.py`.
- **font-patcher not found** — pass `--patcher /path/to/font-patcher`, or set `FONT_PATCHER`, or place your nerd-fonts clone at one of the autodetected paths.
- `WARNING: Possible problem with the weight metadata detected` **(Thin)** — harmless font-patcher notice for the 250-weight Thin; `fixnf.py` reads the real `usWeightClass` and names it correctly.

---

## Pitfalls and dirty-data analysis

Even though the flow is shorter, the underlying font-data traps are unchanged — they are just handled differently (see [What this is](#what-this-is-and-how-it-differs-from-the-old-5-step-up-toolkit)).

### Why the family is needed at all

Titillium's upright OTFs ship with **leftover italic metadata** — a `-13` `ItalicAngle` in both the `post` and **CFF** tables, plus stray style bits. CoreText reads the **CFF** `ItalicAngle` to decide whether a CFF/OTF face is slanted, so an "upright" that still says `-13` is treated as italic. With only the upright installed it still looks fine (it's the only candidate), but once a real italic sibling exists CoreText picks the italic for *normal* text — the italic appears to "replace" the regular. This trap applies to **every weight**, not just Regular; the upright **Bold** source is dirty the same way, so `font-weight: bold` can resolve to the slanted *Bold Italic*.

`fixnf.py` overwrites `post`/CFF `ItalicAngle`, `head.macStyle`, `OS/2.fsSelection`, and the whole name table for every face, so whatever dirt the sources carried is gone in the output. Because italic-ness is decided by the **input folder**, the dirty `-13` on the upright sources can no longer be mistaken for a real slant (this is exactly what the old `02` pre-clean guarded against).

### The `head.macStyle` swapped-bit trap (the real root cause of "bold looks italic")

In `head.macStyle` the bits are **bit0 =** `0x01` **Bold** and **bit1 =** `0x02` **Italic**. In `OS/2.fsSelection` the italic bit is `0x01` and bold is `0x20`. The two tables put the italic bit in *different* positions. An early version of the fixer reused the `fsSelection` layout for `macStyle` (`ITALIC = 0x01`), which is exactly inverted there: **the bold face got the italic bit and the italic face got the bold bit**. CoreText reads the `macStyle` italic bit, so it treated the upright Bold as slanted (`slant ≈ 0.083`) and handed back Bold Italic for plain bold; an `is_italic()` that tested `macStyle & 0x01` was actually testing the *bold* bit, compounding the confusion. (This was originally misattributed to font-patcher corrupting `macStyle` — it was the swapped constants.)

`fixnf.py` keeps the constants separate and correct:

```python
ITALIC_MS = 0x02   # head.macStyle italic bit (bit 1)
BOLD_MS   = 0x01   # head.macStyle bold  bit (bit 0)
ITALIC_FS = 0x01   # OS/2.fsSelection italic bit (bit 0)
BOLD_FS   = 0x20
```

> [!NOTE]
> A stale artifact from the old toolkit made this concrete: diffing this build's `TitilliumNerdFont-UprightItalic.otf` against an old `up/nf` copy showed identical outlines but `macStyle` `0x02` (new, correct italic) vs `0x01` (old, the swapped-bit bug). The new output is the correct one.

### font-patcher rewrites the family name

font-patcher can change the family (e.g. the Bold Italic's family became `Titillium Nerd Font`, dropping `Upright`), splitting a face into a separate family. `fixnf.py` rewrites the `name` table (IDs 1/2/4/6/16/17) to unify everything back under `Titillium Nerd Font Upright`.

### How a false italic was pinned down (diagnostic evidence)

CoreText resolution (tried both through the family database and through `CTFontManagerCreateFontDescriptorsFromURL` reading the file directly, to rule out the `fontd` cache) reported the upright Bold as `italic=Y`, `slant ≈ 0.083`; yet the outlines are genuinely upright (median stem shear `0.0000` across 21 glyphs, CFF `FontMatrix` is identity), and `fsSelection` / `post.italicAngle` / CFF `ItalicAngle` were all clean. A single-field experiment (change one field at a time, save, re-read) showed the only change that flipped the result back to `italic=n slant=0.0` was clearing the `head.macStyle` italic bit (`0x02`). fontTools also warns on open: `fsSelection bit 5 (bold) and head table macStyle bit 0 (bold) should match`.

### Correct style bits after the fix

| FACE        | USWEIGHTCLASS | HEAD.MACSTYLE        | OS/2.FSSELECTION   | POST / CFF ITALICANGLE |
| ----------- | ------------- | -------------------- | ------------------ | ---------------------- |
| Regular     | 400           | `0x00`               | REGULAR `0x40`     | `0`                    |
| Italic      | 400           | `0x02` (Italic)      | ITALIC `0x01`      | `-13`                  |
| Bold        | 700           | `0x01` (Bold)        | BOLD `0x20`        | `0`                    |
| Bold Italic | 700           | `0x03` (Bold+Italic) | ITALIC+BOLD `0x21` | `-13`                  |

> [!NOTE]
> `fsSelection` additionally always carries `USE_TYPO_METRICS 0x80` + `WWS 0x100`; the table lists only the style-related bits. Thin/Light/Semibold follow the same rule as Regular/Italic (no bold bit): roman → `macStyle 0x00`, `fsSelection 0x40`; italic → `macStyle 0x02`, `fsSelection 0x01`.
> Key difference: the italic bit is `0x02` in `head.macStyle` but `0x01` in `fsSelection` — the bit positions differ between the two tables, which is the direct source of the "swap".

### Diagnose a false italic reading

Browsers pick a face by CoreText's symbolic traits (bold / italic) + slant, **not by filename**. A face with genuinely upright outlines can still be reported `italic=Y` if any style bit says so. The signature of this bug: the upright **Bold** reported `italic=Y`, `slant ≈ 0.083`.

**Method A — list every face CoreText sees in the family**

```bash
cat > /tmp/ctfaces.swift <<'SWIFT'
import CoreText
import Foundation
let fam = "Titillium Nerd Font Upright"
let base = CTFontDescriptorCreateWithAttributes([kCTFontFamilyNameAttribute: fam as CFString] as CFDictionary)
let coll = CTFontCollectionCreateWithFontDescriptors([base] as CFArray, nil)
for d in (CTFontCollectionCreateMatchingFontDescriptors(coll) as? [CTFontDescriptor] ?? []) {
    let f = CTFontCreateWithFontDescriptor(d, 13, nil)
    let tr = CTFontCopyTraits(f) as NSDictionary
    let sym = (tr[kCTFontSymbolicTrait] as? NSNumber)?.uint32Value ?? 0
    let bold = (sym & CTFontSymbolicTraits.traitBold.rawValue) != 0
    let italic = (sym & CTFontSymbolicTraits.traitItalic.rawValue) != 0
    let slant = (tr[kCTFontSlantTrait] as? NSNumber)?.doubleValue ?? 0
    print(String(format: "%-30@ bold=%@ italic=%@ slant=%.3f",
                 (CTFontCopyPostScriptName(f) as String) as NSString,
                 bold ? "Y" : "n", italic ? "Y" : "n", slant))
}
SWIFT
swift /tmp/ctfaces.swift
```

After the fix (each face in its slot):

```
TitilliumNF-UprightRegular     bold=n italic=n slant=0.000
TitilliumNF-UprightItalic      bold=n italic=Y slant=0.069
TitilliumNF-UprightBold        bold=Y italic=n slant=0.000
TitilliumNF-UprightBoldItalic  bold=Y italic=Y slant=0.069
```

With the bug (the upright Bold classified as italic):

```
TitilliumNF-UprightBold        bold=Y italic=Y slant=0.083   <- should be italic=n slant=0.000
```

**Method B — read traits straight from the file (bypassing the** `fontd` **database / cache)**

Use this to tell whether the dirt is in the file bytes or just a stale cache:

```bash
cat > /tmp/ctfile.swift <<'SWIFT'
import CoreText
import Foundation
let u = URL(fileURLWithPath: (NSHomeDirectory() as NSString)
    .appendingPathComponent("Library/Fonts/TitilliumNerdFont-UprightBold.otf"))
let d = (CTFontManagerCreateFontDescriptorsFromURL(u as CFURL) as! [CTFontDescriptor])[0]
let f = CTFontCreateWithFontDescriptor(d, 13, nil)
let tr = CTFontCopyTraits(f) as NSDictionary
let sym = (tr[kCTFontSymbolicTrait] as? NSNumber)?.uint32Value ?? 0
let italic = (sym & CTFontSymbolicTraits.traitItalic.rawValue) != 0
let slant = (tr[kCTFontSlantTrait] as? NSNumber)?.doubleValue ?? 0
print("italic=\(italic ? "Y" : "n") slant=\(slant)")
SWIFT
swift /tmp/ctfile.swift
```

**Reading the numbers**

| OUTPUT                                         | MEANING                                                                                    |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `italic=n slant=0.000`                         | Upright — how Regular / Bold should read                                                   |
| `italic=Y slant≈0.069`                         | Real italic — Italic / Bold Italic (genuinely sheared outlines)                            |
| An upright face reading `italic=Y slant≈0.08x` | **bug** — a style bit marks it italic even though the outlines / `ItalicAngle` are upright |

- `slant ≈ 0.083` is CoreText's own **normalized** slant estimate, not derived from `italicAngle` (which is `0`). It is even larger than the real italic's `≈ 0.069` — being "anomalously larger than the actual italic" is the tell that this is a style-bit flag, not a real slant.
- The two "slant" values are different quantities: `kCTFontSlantTrait` is a normalized value (`0.069` / `0.083`), whereas `CTFontGetSlantAngle` in [Verify it worked](#verify-it-worked) is an **angle in degrees** (`-13.0`).

**Decision flow**

1. `fc-match` is correct but the browser is wrong → the problem is at the CoreText / `fontd` layer (fontconfig keeps its own separate cache; see Troubleshooting).
2. Method B (direct file read) still shows `italic=Y` → the dirt is in the **file bytes**, not a stale cache. If Method B is clean and only Method A is dirty → stale cache, so re-run `--install` (or log out / log back in).
3. Re-save under a brand-new PostScript / family name and read again; if it still shows `italic=Y` → it is not a name-keyed cache. Then run a **single-variable experiment** (change one field at a time, save, read the traits directly) to isolate the offending field — here it was the `head.macStyle` italic bit (`0x02`).

---

## Notes

- Weight mapping: `usWeightClass` 250→Thin, 300→Light, 400→Regular, 600→Semibold, 700→Bold.
- `Titillium-Black.otf` has no upright/italic pair and is skipped.
- All edits are idempotent — safe to re-run; `guillemet.py` leaves already-correct faces untouched.
- font-patcher is invoked as `--complete --careful`; `--careful` means it never overwrites glyphs the font already has, so `U+00BB` (and every other base glyph) is preserved exactly — which is why the `«`/`»` repair is done on the source, before patching.
