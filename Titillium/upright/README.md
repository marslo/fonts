# Titillium Upright → Nerd Font toolkit

Scripts to build a clean **"Titillium Nerd Font Upright"** family whose upright faces render truly upright and whose italic faces slant correctly on macOS (CoreText) and in browsers.

The whole point: make this work as expected —

```css
font-family: "Titillium Nerd Font Upright";              /* upright Regular     */
font-style:  italic;                                     /* the slanted Italic  */
font-weight: bold;                                       /* upright Bold        */
font-weight: bold; font-style: italic;                   /* slanted Bold Italic */
```

The family ships a complete **RIBBI** set — Regular / Italic / Bold / Bold Italic — all under the one family name, each resolving to the correct face.

## Why this is needed

Titillium's upright OTFs ship with **leftover italic metadata** (a `-13` `ItalicAngle` in both the `post` and **CFF** tables, plus stray style bits).
CoreText reads the **CFF `ItalicAngle`** to decide whether a CFF/OTF face is slanted, so an "upright" that still says `-13` is treated as italic. With only the upright installed it still looks fine (it's the only candidate), but once a
real italic sibling exists CoreText picks the italic for *normal* text — the italic appears to "replace" the regular.

This trap applies to **every weight**, not just Regular. The upright **Bold** source is dirty in the same way, so `font-weight: bold` can resolve to the slanted *Bold Italic* instead of the upright *Bold*. Bold also has a **second** italic signal that matters — `head.macStyle` (bit0 = Bold, bit1 = Italic); if the upright Bold carries the italic bit, CoreText slants it (`slant ≈ 0.083`) and hands back Bold Italic for plain bold (see [Pitfalls and dirty-data analysis](#pitfalls-and-dirty-data-analysis)).

These scripts strip that dirt, generate matching upright-italics, and fix the metadata that `font-patcher` mangles — producing all four RIBBI faces (Regular / Italic / Bold / Bold Italic).

## Requirements

| Tool | Why | Install |
| --- | --- | --- |
| macOS | CoreText / `fontd` registration | — |
| Python 3.8+ | runs the scripts | `python3 --version` |
| [`fonttools`](https://github.com/fonttools/fonttools) 4.x | read/edit OTF metadata | `pip3 install fonttools` |
| [`fontforge`](https://fontforge.org) + [`font-patcher`](https://github.com/ryanoasis/nerd-fonts) | patch Nerd Font glyphs | `brew install fontforge`; clone nerd-fonts |
| `swift` (Xcode CLT) | `.user`-scope font registration | `xcode-select --install` |

Quick check:

```bash
python3 -c "import fontTools; print('fonttools', fontTools.version)"
swift --version | head -1
which fontforge font-patcher
```

## Step 0 — prepare the sources

The source faces ship as a zip — 16 OTFs: `Regular / Thin / Light / Semibold / Bold`, each with its `Italic` + `Upright`, plus `Black`. Extract them **flat** into `FONT_ROOT`; the scripts read `Titillium-<W>Upright.otf` and `Titillium-<W>Italic.otf` from there.

```bash
mkdir -p ~/Desktop/titillium
unzip titillium.zip -d ~/Desktop/titillium      # 16 .otf files, flat, into FONT_ROOT

cd /Users/marslo/iMarslo/tools/fonts/sans/titillium/titillium.fix/up   # this toolkit (where the scripts live)
FONT_ROOT=~/Desktop/titillium \
FONT_PATCHER=~/git/nerd-fonts/font-patcher \
  ./00-run-all.sh --dry-run                      # dry-run preview: confirm Bold is picked up, Black is skipped
# once the dry-run looks right, drop --dry-run and add --install to build + refresh the font cache
```

`FONT_ROOT` holds the sources; generated faces land in `FONT_ROOT/up/` (patched ones in `FONT_ROOT/up/nf/`). The zip contains **only** the source OTFs — the scripts themselves are this `up/` toolkit. `Black` has no `Upright`/`Italic` pair, so it is reported as `skip Black` and left untouched. Steps 1 → 5 then run automatically (see below).

## Directory layout

```
~/Desktop/titillium/
├── Titillium-<W>.otf            # original family (Thin/Light/Regular/Semibold/Bold[/Black])
├── Titillium-<W>Italic.otf      # original italics (slanted outlines)
├── Titillium-<W>Upright.otf     # upright faces (dirty metadata)
└── up/
    ├── 00-run-all.sh            # one-shot orchestrator (steps 1-5)
    ├── 01-gen-upright-italic.py
    ├── 02-fix-upright-source.py
    ├── 03-fix-nf.py
    ├── 04-fix-guillemet.py      # repair single-chevron «/» on upright faces
    ├── README.md
    ├── Titillium-<W>Upright.otf        # staged pairs (after step 1/2)
    ├── Titillium-<W>UprightItalic.otf  # generated (step 1)
    └── nf/                             # font-patcher output (fixed by step 3)
```

`<W>` = `Thin | Light | Regular | Semibold | Bold`.

All three Python scripts accept `--dry-run` to print intended changes and write nothing.

## One-shot pipeline: `00-run-all.sh`

Runs steps 1 → 5 in order (generate → clean → repair guillemets → font-patcher → fix [+ install]).

```bash
cd ~/Desktop/titillium/up

# preview everything, write nothing, skip patch + install
./00-run-all.sh --dry-run

# real run + install (set FONT_PATCHER to your nerd-fonts clone)
FONT_PATCHER=~/git/nerd-fonts/font-patcher ./00-run-all.sh --install
```

Config via env:
- `FONT_ROOT` (default `~/Desktop/titillium`)
- `FONT_PATCHER` (default `~/git/nerd-fonts/font-patcher`)
- `PYTHON` (default `python3`)
It calls the Python scripts via `$PYTHON`, so the execute bit is not required.

## The scripts

### `01-gen-upright-italic.py` — generate the upright-italics

Takes the slanted outlines from `Titillium-<W>Italic.otf`, dresses them with the naming of `Titillium-<W>Upright.otf` + italic flags (`ItalicAngle = -13`), and writes `Titillium-<W>UprightItalic.otf` into `up/` (also stages a copy of each upright face so `up/` holds complete pairs).

> **The outline source is the *Italic*, not the *Upright*.** The upright faces have upright outlines, so the slant has to come from the real `Titillium-<W>Italic.otf`; the upright face only lends its `name` table (family/subfamily/full/PostScript, IDs 1/2/4/6/16/17) so the generated italic joins the same family and forms a proper upright/italic pair. `Titillium-<W>Upright.otf` itself is copied into `up/` **unchanged** (staged for patching), not converted.

Per-weight source → target:

| generated (target) | outlines from | naming mirrored from |
| --- | --- | --- |
| `Titillium-RegularUprightItalic.otf`  | `Titillium-RegularItalic.otf`  | `Titillium-RegularUpright.otf`  |
| `Titillium-ThinUprightItalic.otf`     | `Titillium-ThinItalic.otf`     | `Titillium-ThinUpright.otf`     |
| `Titillium-LightUprightItalic.otf`    | `Titillium-LightItalic.otf`    | `Titillium-LightUpright.otf`    |
| `Titillium-SemiboldUprightItalic.otf` | `Titillium-SemiboldItalic.otf` | `Titillium-SemiboldUpright.otf` |
| `Titillium-BoldUprightItalic.otf`     | `Titillium-BoldItalic.otf`     | `Titillium-BoldUpright.otf`     |

```bash
./01-gen-upright-italic.py                 # default ROOT=~/Desktop/titillium
./01-gen-upright-italic.py /path/to/root   # custom source folder
```

### `02-fix-upright-source.py` — clean the upright sources (before patching)

In place on every `up/Titillium-*Upright.otf` (skips `*UprightItalic`): clears the macStyle italic bit, sets `post.italicAngle = 0` **and CFF `ItalicAngle = 0`**, and normalises `fsSelection` to REGULAR/BOLD by weight.

```bash
./02-fix-upright-source.py                 # default DIR=~/Desktop/titillium/up
./02-fix-upright-source.py /path/to/dir
```

### `03-fix-nf.py` — fix the patched Nerd Font metadata
In place on every `up/nf/*.otf|*.ttf`. Detects weight + italic from the font's own metadata (not the filename), then rewrites `name` IDs (1/2/4/6/16/17), `macStyle`/`fsSelection`, `post`/CFF `ItalicAngle`, and the CFF font name to the clean target. All weights share the typographic family `Titillium Nerd Font Upright`.

```bash
./03-fix-nf.py                  # default DIR=~/Desktop/titillium/up/nf, edit only
./03-fix-nf.py /path/to/nf
./03-fix-nf.py --install        # + copy to ~/Library/Fonts, flush fontd, register (.user)
```

`--install` performs the sequence that actually refreshes CoreText on macOS 14+: copy → `rm -rf ~/Library/Caches/com.apple.FontRegistry` → `killall fontd` →`CTFontManagerRegisterFontsForURL(..., .user, ...)`.

### `04-fix-guillemet.py` — repair single-chevron `«` / `»`

Titillium's **Regular** `Upright` source draws `guillemotleft` / `guillemotright` with a **single** chevron (one contour) instead of the usual **double** chevron (two contours), so `»` shows as a lone `>`. Only the Regular-weight upright is affected — every other face (the normal `Titillium-<W>.otf` and the other `Upright` weights) already has the double chevron.

Transplants the correct double-chevron outline (CFF charstring + `hmtx`, metadata untouched) from the same-weight upright donor `FONT_ROOT/Titillium-<W>.otf` — weight read from the target's `usWeightClass` — into any target whose guillemet is missing or has fewer than two contours. Idempotent: faces that already carry a double chevron are left alone.

> **Donor is always the upright (non-italic) face.** The bug only ever hits upright faces; every italic face already ships a double chevron and is skipped, so the upright donor is always right. Use `--donor=FILE` to force a specific donor.

Runs in the pipeline as step 3 (after `02` cleans metadata, before `font-patcher`), so the patched output is already correct. It also works standalone on the patched `up/nf/` faces or on an installed `~/Library/Fonts/*.otf`.

```bash
./04-fix-guillemet.py                             # default DIR=~/Desktop/titillium/up
./04-fix-guillemet.py ~/Desktop/titillium/up/nf   # fix patched output in place
./04-fix-guillemet.py /path/to/Font.otf --root=/path/to/sources --dry-run
```

- `--root=DIR` donor folder (default `~/Desktop/titillium`)
- `--donor=FILE` force one donor face (skips weight lookup)
- `--force` re-transplant even if the target already has ≥ 2 contours
- `--dry-run` print intended changes, write nothing

## Full pipeline (manual / step-by-step)

Equivalent to `00-run-all.sh`, if you'd rather run each stage yourself.

### Workflow — what each step does

```text
[1/5] 01-gen-upright-italic.py   generate the upright-italics
        Titillium-<W>Italic.otf    (outlines / slant)
      + Titillium-<W>Upright.otf   (name table only)
      -> up/Titillium-<W>UprightItalic.otf   <- deliberately written with correct italic flags (italicAngle = -13, etc.)
      also stages Titillium-<W>Upright.otf into up/ unchanged

[2/5] 02-fix-upright-source.py   clean the dirty metadata on the UPRIGHT sources   (* BEFORE patching)
        up/Titillium-<W>Upright.otf:
          post / CFF ItalicAngle -13 -> 0, clear the macStyle italic bit, set REGULAR/BOLD fsSelection by weight
        (skips *UprightItalic -- those are supposed to stay italic)

[3/5] 04-fix-guillemet.py        repair single-chevron «/» on the UPRIGHT sources  (* BEFORE patching)
        up/Titillium-<W>Upright.otf:
          if guillemotleft/right have < 2 contours (single chevron), transplant the
          double-chevron outline + hmtx from FONT_ROOT/Titillium-<W>.otf (idempotent)

[4/5] font-patcher               add the Nerd Font glyphs
        up/Titillium-<W>Upright.otf + up/Titillium-<W>UprightItalic.otf -> up/nf/

[5/5] 03-fix-nf.py               fix the metadata that font-patcher mangled   (* AFTER patching)
        detect weight + italic from metadata; rewrite name (1/2/4/6/16/17), macStyle/fsSelection,
        post / CFF ItalicAngle, and the CFF font name -> unify under family "Titillium Nerd Font Upright"
        [+ --install: copy to ~/Library/Fonts, flush fontd, register at .user scope]
```

- **Step 1 — generate.** The upright faces are upright, so the *slant* must come from the real `Titillium-<W>Italic.otf`; the upright face only lends its `name` table so the two share a family and form an upright/italic pair. The generated `*UprightItalic.otf` is given the correct italic flags on purpose (this is not dirt). The upright face is also copied into `up/` unchanged, ready for patching.
- **Step 2 — clean the sources (before patch).** Titillium's upright OTFs ship with leftover italic metadata (`ItalicAngle = -13`, a stray BOLD bit, etc.). This strips it so the upright is genuinely upright by the time font-patcher sees it.
- **Step 3 — repair guillemets (before patch).** The Regular upright's `«`/`»` are drawn as a single chevron; this transplants the correct double chevron from `Titillium-<W>.otf` so the fix is baked in before patching. Idempotent, so the other weights pass through untouched.
- **Step 4 — patch.** font-patcher adds the Nerd Font glyph set to *both* the upright and the upright-italic, writing the results to `up/nf/`.
- **Step 5 — fix (after patch).** font-patcher re-mangles names/flags (and can drop `Upright` from the family), so this rewrites them to the clean target, deciding weight + italic from the **metadata**, not the filename. `--install` then deploys and refreshes the cache.

> **Why clean twice (before *and* after the patch)?** Step 4 decides italic-ness from metadata, not the filename. If Step 2 were skipped, the upright's leftover `ItalicAngle = -13` would survive patching and Step 4's `is_italic()` would misclassify the upright as italic. Step 2 removes that misleading signal *before* font-patcher runs; Step 4 then repairs whatever font-patcher itself mangles.

Then run the four stages yourself:

```bash
cd ~/Desktop/titillium/up

# 1) generate upright-italics + stage upright pairs
./01-gen-upright-italic.py

# 2) clean the upright sources' dirty italic metadata
./02-fix-upright-source.py

# 3) repair single-chevron «/» on the upright sources
./04-fix-guillemet.py . --root=..

# 4) patch Nerd Font glyphs into up/nf/  (adjust path to your nerd-fonts clone)
PATCHER=~/git/nerd-fonts/font-patcher
mkdir -p nf
for f in Titillium-*Upright.otf Titillium-*UprightItalic.otf; do
  fontforge -script "$PATCHER" "$f" --complete --careful --outputdir nf
done

# 5) fix patched metadata, then install + register
./03-fix-nf.py --install
```

After installing, **fully quit and reopen the browser** (not just reload) so it
picks up the refreshed `.user` font registration.

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
let fam = "Titillium Nerd Font Upright"
print("normal      -> " + resolve(fam, false, false))
print("italic      -> " + resolve(fam, false, true))
print("bold        -> " + resolve(fam, true,  false))
print("bold italic -> " + resolve(fam, true,  true))
SWIFT
swift /tmp/ctcheck.swift
```

Expected (each request resolves to its own face — bold/bold-italic must **not** fall back to another slant):

```
normal      -> TitilliumNF-UprightRegular    slant=0.0
italic      -> TitilliumNF-UprightItalic     slant=-13.0
bold        -> TitilliumNF-UprightBold       slant=0.0
bold italic -> TitilliumNF-UprightBoldItalic slant=-13.0
```

`fontconfig` (independent of CoreText) should agree:

```bash
fc-match 'Titillium Nerd Font Upright'              # -> ...Regular
fc-match 'Titillium Nerd Font Upright:italic'       # -> ...Italic
fc-match 'Titillium Nerd Font Upright:bold'         # -> ...Bold
fc-match 'Titillium Nerd Font Upright:bold:italic'  # -> ...Bold Italic
```

## Flush the font cache

`./03-fix-nf.py --install` already does this end-to-end. Use the manual sequence below when the faces are **already** in `~/Library/Fonts` (edited in place, or copied by hand) and you just need CoreText / `fontd` to notice — on macOS 14+, moving files in/out does **not** reliably refresh the parsed cache.

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

## Troubleshooting

- **Still all italic after editing files** — the file is fine but `fontd`'s parsed cache is stale. Moving files in/out of `~/Library/Fonts` does **not** reliably refresh it on macOS 14+. Use `./03-fix-nf.py --install` (it clears the cache, restarts `fontd`, and re-registers at `.user` scope) — or the manual [Flush the font cache](#flush-the-font-cache) steps if the files are already installed — then fully quit/relaunch the app. Last resort: log out / log back in.
- **`CTFontManagerRegisterFontsForURL` returns `false` with err `-50`** — that scope is already occupied; the script unregisters at `.user` scope first, then registers, which works from a CLI process.
- **Browser still shows the old face** — browsers cache fonts per process; do a full **Quit**, not a tab reload.
- **`fc-match` is right but the browser is wrong** — that's the CoreText/`fontd` layer, not fontconfig. Re-run `--install`.
- **`<b>` / `font-weight: bold` renders un-bold (and isn't slanted)** — that upright Bold face is being reported *italic* by CoreText (signature `italic=Y slant≈0.08x`), so `bold` resolves to Bold Italic. Diagnose with [Diagnose a false italic reading](#diagnose-a-false-italic-reading); the usual culprit is the `head.macStyle` italic bit (`0x02`) set by mistake.
- **`./00-run-all.sh: Permission denied`** — the execute bit isn't set (e.g. `chmod` is aliased to `sudo chmod` in your shell). Either run via the interpreter (`bash 00-run-all.sh ...`, `python3 03-fix-nf.py ...`) or set the bit with the real binary: `/bin/chmod +x *.sh *.py`.
- **`»` shows as a single `>` (Regular only)** — the Regular upright `«`/`»` glyphs ship as a single chevron (one contour). Run `04-fix-guillemet.py` (pipeline step 3) to transplant the double chevron from `Titillium-Regular.otf`; it also fixes an already-installed face in place (`./04-fix-guillemet.py ~/Library/Fonts/TitilliumNerdFont-UprightRegular.otf --root=/path/to/sources`, then flush the font cache).

## Pitfalls and dirty-data analysis

Pitfalls hit while generating the upright Bold / Bold Italic faces, with the cause and remedy for each piece of dirty metadata.

- **Dirty metadata in the upright-Bold source** (`post` / CFF `ItalicAngle = -13`, subfamily name `Italic`, plus a stray BOLD `fsSelection` bit) — the same dirt the upright Regular carries. CoreText reads the CFF `ItalicAngle` to judge slant, so `-13` makes the upright Bold be treated as italic. Run `02-fix-upright-source.py` before patching to clean it (→ `post` / CFF `ItalicAngle = 0`, set the REGULAR/BOLD `fsSelection` bit by weight, clear the macStyle italic bit).
- **Swapped `head.macStyle` bit constants (the real root cause)** — in `head.macStyle` the bits are bit0 = `0x01` **Bold** and bit1 = `0x02` **Italic**; but the scripts defined `ITALIC = 0x01` / `BOLD_MS = 0x02` following the `fsSelection` layout (where the italic bit really is `0x01`). Applied to `macStyle` this is exactly inverted: **the bold face got the italic bit and the italic face got the bold bit**. CoreText reads the `macStyle` italic bit, so it treats the upright Bold as slanted (`slant ≈ 0.083`), and `font-weight: bold` resolves to Bold Italic instead of Bold; `is_italic()` (`macStyle & 0x01`) was actually testing the bold bit, which is why it also misclassified the bold as italic (previously blamed on font-patcher corrupting `macStyle`, but it was the swapped constants). → `macStyle` now has its own constants `ITALIC_MS = 0x02` / `BOLD_MS = 0x01`, kept separate from `fsSelection`'s `ITALIC_FS = 0x01` (see `02` / `03`; `01` line 66 also changed from `0x01` to `0x02`). After the fix all four RIBBI faces sit in their correct slots, with no need to hand-normalise `macStyle`.
- **font-patcher rewrites the family name** — the Bold Italic's family was changed to `Titillium Nerd Font` (dropping `Upright`), i.e. a full-name mismatch that split it into a separate family. `03-fix-nf.py` rewrites the `name` table (IDs 1/2/4/6/16/17) to unify everything back to `Titillium Nerd Font Upright`.
- **How it was pinned down (diagnostic evidence)** — CoreText resolution (tried both through the family database and through `CTFontManagerCreateFontDescriptorsFromURL` reading the file directly, to rule out the `fontd` cache) reported the upright Bold as `italic=Y`, `slant ≈ 0.083`; yet the outlines are genuinely upright (median stem shear of `0.0000` across 21 glyphs, and the CFF `FontMatrix` is the identity matrix), and `fsSelection` / `post.italicAngle` / CFF `ItalicAngle` are all clean. A single-field experiment (changing one field at a time) showed the only change that flipped the result back to `italic=n slant=0.0` was clearing the `head.macStyle` italic bit (`0x02`). fontTools also warns on open: `fsSelection bit 5 (bold) and head table macStyle bit 0 (bold) should match`.

Correct style bits for the four faces after the fix (each RIBBI slot in place):

| face | usWeightClass | head.macStyle | OS/2.fsSelection | post / CFF ItalicAngle |
| --- | --- | --- | --- | --- |
| Regular     | 400 | `0x00`               | REGULAR `0x40`     | `0`   |
| Italic      | 400 | `0x02` (Italic)      | ITALIC `0x01`      | `-13` |
| Bold        | 700 | `0x01` (Bold)        | BOLD `0x20`        | `0`   |
| Bold Italic | 700 | `0x03` (Bold+Italic) | ITALIC+BOLD `0x21` | `-13` |

> `fsSelection` additionally always carries `USE_TYPO_METRICS 0x80` + `WWS 0x100`; the table lists only the style-related bits.
> Key difference: the italic bit is `0x02` in `head.macStyle` but `0x01` in `fsSelection` — the bit positions differ between the two tables, which is the direct source of this "swap".

### Diagnose a false italic reading

Reads whether a face is reported as italic by CoreText (`italic=Y/N`) and its `slant`. Browsers pick a face by CoreText's symbolic traits (bold / italic) + slant, **not by filename**. A face with genuinely upright outlines can still be reported `italic=Y` if any style bit says it is italic. The signature of this bug: the upright **Bold** was reported `italic=Y`, `slant ≈ 0.083`.

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

**Method B — read traits straight from the file (bypassing the `fontd` database / cache)**

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

| Output | Meaning |
| --- | --- |
| `italic=n slant=0.000` | Upright — this is how Regular / Bold should read |
| `italic=Y slant≈0.069` | Real italic — Italic / Bold Italic (with genuinely sheared outlines) |
| An upright face reading `italic=Y slant≈0.08x` | **bug** — some style bit marks it italic even though the outlines / `ItalicAngle` are upright |

- `slant ≈ 0.083` is CoreText's own **normalized** slant estimate, not derived from `italicAngle` (which is `0`). It is even larger than the real italic's `≈ 0.069` — being "anomalously larger than the actual italic" is the tell that this is not a real slant but a face flagged italic by a style bit.
- Note the two "slant" values are different quantities: `kCTFontSlantTrait` in the traits is a normalized value (`0.069` / `0.083`), whereas `CTFontGetSlantAngle` used in [Verify it worked](#verify-it-worked) is an **angle in degrees** (`-13.0`).

**Decision flow**

1. `fc-match` is correct but the browser is wrong → the problem is at the CoreText / `fontd` layer (fontconfig keeps its own separate cache; see Troubleshooting).
2. Method B (direct file read) still shows `italic=Y` → the dirt is in the **file bytes**, not a stale cache; if Method B is clean and only Method A is dirty → it is a stale cache, so re-run `./03-fix-nf.py --install` (or log out / log back in).
3. Re-save the file under a brand-new PostScript / family name and read again; if it still shows `italic=Y` → it is not a name-keyed cache. Then run a **single-variable experiment** (change one field at a time, save, and read the traits directly) to isolate the offending field — here it was the `head.macStyle` italic bit (`0x02`).

## Notes

- Weight mapping: `usWeightClass` 250→Thin, 300→Light, 400→Regular, 600→Semibold, 700→Bold.
- `Titillium-Black.otf` has no upright/italic pair and is left untouched.
- All edits are idempotent — safe to re-run.
