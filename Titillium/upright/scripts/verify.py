#!/usr/bin/env python3
"""Verify + display the key metadata of the built Titillium Nerd Font Upright faces.

Dumps the CoreText-relevant fields for each face (usWeightClass, head.macStyle,
OS/2.fsSelection, post / CFF ItalicAngle, name IDs 1/2/4/6/16/17, guillemet
contours, glyph counts) and checks them against the RIBBI spec. Weight is read
from usWeightClass; the intended italic-ness is taken from the canonical
filename (TitilliumNerdFont-Upright<Style>.otf), then every field is verified to
agree with it -- so one glance confirms the compile/fix produced correct upright
and italic faces.

Usage:
    python3 verify.py [--input FILE|DIR] [--strict] [--coretext] [--family NAME]
      # default --input = <script dir>/out/fonts
      # --strict   exit non-zero if any face fails
      # --coretext read faces' CoreText traits (macOS). given alone it reads the
      #            SYSTEM font cache and prints only installed faces (works from
      #            anywhere, no input dir needed); add --input FILE|DIR to instead
      #            spec-verify those files and read their traits straight from them.
      # --family   family name for the bare --coretext system-cache query
      #            (default "Titillium Nerd Font Upright"); ignored when --input is given.
"""
import glob
import os
import subprocess
import sys
import tempfile

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

FAMILY = "Titillium Nerd Font Upright"
RIBBI = {"Regular", "Bold"}
WCLASS = {250: "Thin", 300: "Light", 400: "Regular", 600: "Semibold", 700: "Bold"}

ITALIC_MS = 0x02      # head.macStyle italic bit (bit 1)
BOLD_MS = 0x01        # head.macStyle bold bit (bit 0)
ITALIC_FS = 0x01      # OS/2.fsSelection italic bit (bit 0)
BOLD_FS = 0x20
REGULAR_FS = 0x40
USE_TYPO = 0x80
WWS = 0x100

GUILLEMETS = ((0x00AB, "\u00AB"), (0x00BB, "\u00BB"))
PUA = ((0xE000, 0xF8FF), (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD))

GREEN, RED, DIM, RST = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = DIM = RST = ""


def get_name(font, nid):
    name = font["name"]
    rec = name.getName(nid, 3, 1, 0x409) or name.getName(nid, 1, 0, 0)
    return rec.toUnicode() if rec else None


def weight_of(wc):
    return WCLASS.get(wc) or WCLASS[min(WCLASS, key=lambda k: abs(k - wc))]


def italic_from_filename(base):
    return base[:-4].endswith("Italic") if base.lower().endswith(".otf") else base.endswith("Italic")


def decode_macstyle(ms):
    out = [n for bit, n in ((BOLD_MS, "Bold"), (ITALIC_MS, "Italic")) if ms & bit]
    return " ".join(out) or "-"


def decode_fsselection(fs):
    out = [n for bit, n in ((ITALIC_FS, "ITALIC"), (BOLD_FS, "BOLD"), (REGULAR_FS, "REGULAR"),
                            (USE_TYPO, "USE_TYPO"), (WWS, "WWS")) if fs & bit]
    return " ".join(out) or "-"


def expected(weight, italic):
    """The correct fields for (weight, italic), derived independently of fixnf.py."""
    bold = weight == "Bold"
    ms = (ITALIC_MS if italic else 0) | (BOLD_MS if bold else 0)
    if italic:
        fs_style = ITALIC_FS | (BOLD_FS if bold else 0)
    else:
        fs_style = BOLD_FS if bold else REGULAR_FS
    angle = -13 if italic else 0
    typo_sub = (("" if weight == "Regular" else weight) + (" Italic" if italic else "")).strip() or "Regular"
    if weight in RIBBI:
        n1 = FAMILY
        n2 = ("Bold Italic" if italic else "Bold") if bold else ("Italic" if italic else "Regular")
    else:
        n1 = f"{FAMILY} {weight}"
        n2 = "Italic" if italic else "Regular"
    n4 = FAMILY if (weight == "Regular" and not italic) else f"{FAMILY} {typo_sub}"
    ps_style = (("" if weight == "Regular" else weight)
                + ("Italic" if italic else ("Regular" if weight == "Regular" else ""))) or "Regular"
    n6 = f"TitilliumNF-Upright{ps_style}"
    return {"macStyle": ms, "fs_style": fs_style, "angle": angle,
            "n1": n1, "n2": n2, "n4": n4, "n6": n6, "n16": FAMILY, "n17": typo_sub}


def contour_count(gs, gname):
    pen = RecordingPen()
    gs[gname].draw(pen)
    return sum(1 for op, _ in pen.value if op == "moveTo")


def is_pua(cp):
    return any(lo <= cp <= hi for lo, hi in PUA)


def mark(ok):
    return f"{GREEN}OK{RST}" if ok else f"{RED}FAIL{RST}"


def check_face(path):
    base = os.path.basename(path)
    font = TTFont(path)
    wc = font["OS/2"].usWeightClass
    weight = weight_of(wc)
    italic = italic_from_filename(base)
    exp = expected(weight, italic)

    ms = font["head"].macStyle
    fs = font["OS/2"].fsSelection
    fs_style = fs & (ITALIC_FS | BOLD_FS | REGULAR_FS)
    ang = font["post"].italicAngle
    has_cff = "CFF " in font
    cff_ang = int(font["CFF "].cff.topDictIndex[0].ItalicAngle) if has_cff else None
    names = {nid: get_name(font, nid) for nid in (1, 2, 4, 6, 16, 17)}

    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    total = len(font.getGlyphOrder())
    uni = len(cmap)                              # encoded unicode codepoints
    pua = sum(1 for cp in cmap if is_pua(cp))    # of which private-use (nerd font icons)
    base_uni = uni - pua                         # real (non-PUA) unicode characters
    upm = font["head"].unitsPerEm

    checks = [
        ("head.macStyle", f"{hex(ms)} [{decode_macstyle(ms)}]",
         f"{hex(exp['macStyle'])} [{decode_macstyle(exp['macStyle'])}]", ms == exp["macStyle"]),
        ("OS/2.fsSelection", f"{hex(fs)} [{decode_fsselection(fs)}]",
         f"style={hex(exp['fs_style'])} +USE_TYPO+WWS",
         fs_style == exp["fs_style"] and bool(fs & USE_TYPO) and bool(fs & WWS)),
        ("post.italicAngle", f"{ang:g}", f"{exp['angle']}", int(ang) == exp["angle"]),
        ("CFF ItalicAngle", ("n/a" if not has_cff else str(cff_ang)),
         f"{exp['angle']}", (cff_ang == exp["angle"]) if has_cff else True),
        ("name 1 (family)", names[1], exp["n1"], names[1] == exp["n1"]),
        ("name 2 (subfamily)", names[2], exp["n2"], names[2] == exp["n2"]),
        ("name 4 (full)", names[4], exp["n4"], names[4] == exp["n4"]),
        ("name 6 (postscript)", names[6], exp["n6"], names[6] == exp["n6"]),
        ("name 16 (typo fam)", names[16], exp["n16"], names[16] == exp["n16"]),
        ("name 17 (typo sub)", names[17], exp["n17"], names[17] == exp["n17"]),
    ]

    guil = []
    guil_ok = True
    for cp, sym in GUILLEMETS:
        gname = cmap.get(cp)
        n = contour_count(gs, gname) if gname else -1
        guil.append((sym, gname, n))
        if n != 2:
            guil_ok = False
    checks.append(("guillemets « »", " ".join(f"{s}={n}c" for s, _, n in guil), "both 2c", guil_ok))

    passed = all(ok for *_, ok in checks)
    info = {"wc": wc, "weight": weight, "italic": italic, "upm": upm,
            "total": total, "uni": uni, "base_uni": base_uni, "pua": pua}
    return base, passed, checks, info


def _run_swift_columns(swift):
    # run a swift trait-dump program (tab-delimited rows) and print aligned columns
    with tempfile.NamedTemporaryFile( "w", suffix=".swift", delete=False ) as tf:
        tf.write("\n".join(swift) + "\n")
        tf_name = tf.name
    try:
        res = subprocess.run( ["swift", tf_name], capture_output=True, text=True, check=False )
    finally:
        os.unlink(tf_name)
    rows = [ln.split("\t") for ln in res.stdout.splitlines() if ln.strip()]
    if not rows:
        sys.stdout.write(res.stderr)
        return
    w = max(len(r[0]) for r in rows)
    for r in rows:
        if len(r) == 4:
            name, b, i, s = r
            print(f"  {name.ljust(w)}  bold={b}  italic={i}  slant={s}")
        else:
            print("  " + " ".join(r))


def coretext_traits(paths):
    # method b: read traits straight from the given font files (no install needed)
    swift = [
        "import CoreText", "import Foundation",
        f"let paths = [\n{','.join(chr(10) + '  ' + repr_swift(p) for p in paths)}\n]",
        "for p in paths {",
        "  let u = URL(fileURLWithPath: p) as CFURL",
        "  guard let ds = CTFontManagerCreateFontDescriptorsFromURL(u) as? [CTFontDescriptor], let d = ds.first else {",
        "    print(\"\\((p as NSString).lastPathComponent)\\t?\\t?\\t?\"); continue }",
        "  let f = CTFontCreateWithFontDescriptor(d, 13, nil)",
        "  let tr = CTFontCopyTraits(f) as NSDictionary",
        "  let sym = (tr[kCTFontSymbolicTrait] as? NSNumber)?.uint32Value ?? 0",
        "  let bold = (sym & CTFontSymbolicTraits.traitBold.rawValue) != 0",
        "  let ital = (sym & CTFontSymbolicTraits.traitItalic.rawValue) != 0",
        "  let slant = (tr[kCTFontSlantTrait] as? NSNumber)?.doubleValue ?? 0",
        "  let ps = CTFontCopyPostScriptName(f) as String",
        "  print(\"\\(ps)\\t\\(bold ? \"Y\" : \"n\")\\t\\(ital ? \"Y\" : \"n\")\\t\" + String(format: \"%.3f\", slant))",
        "}",
    ]
    _run_swift_columns(swift)


def coretext_cache(family):
    # method a: query the system font cache for installed families matching family
    swift = [
        "import CoreText", "import Foundation",
        f"let prefix = {repr_swift(family)}",
        "let fams = (CTFontManagerCopyAvailableFontFamilyNames() as? [String] ?? [])",
        "    .filter { $0 == prefix || $0.hasPrefix(prefix + \" \") }.sorted()",
        "if fams.isEmpty { print(\"(no installed family matching \\(prefix))\") }",
        "for fam in fams {",
        "  let base = CTFontDescriptorCreateWithAttributes([kCTFontFamilyNameAttribute: fam as CFString] as CFDictionary)",
        "  let coll = CTFontCollectionCreateWithFontDescriptors([base] as CFArray, nil)",
        "  for d in (CTFontCollectionCreateMatchingFontDescriptors(coll) as? [CTFontDescriptor] ?? []) {",
        "    let f = CTFontCreateWithFontDescriptor(d, 13, nil)",
        "    let tr = CTFontCopyTraits(f) as NSDictionary",
        "    let sym = (tr[kCTFontSymbolicTrait] as? NSNumber)?.uint32Value ?? 0",
        "    let bold = (sym & CTFontSymbolicTraits.traitBold.rawValue) != 0",
        "    let ital = (sym & CTFontSymbolicTraits.traitItalic.rawValue) != 0",
        "    let slant = (tr[kCTFontSlantTrait] as? NSNumber)?.doubleValue ?? 0",
        "    let ps = CTFontCopyPostScriptName(f) as String",
        "    print(\"\\(ps)\\t\\(bold ? \"Y\" : \"n\")\\t\\(ital ? \"Y\" : \"n\")\\t\" + String(format: \"%.3f\", slant))",
        "  }",
        "}",
    ]
    _run_swift_columns(swift)


def repr_swift(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def collect(inp):
    p = os.path.expanduser(inp)
    if os.path.isfile(p):
        return [p]
    if os.path.isdir(p):
        return sorted(glob.glob(os.path.join(p, "*.otf")) + glob.glob(os.path.join(p, "*.ttf")))
    print(f"not found: {inp}", file=sys.stderr)
    return []


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    inp = os.path.join(here, "out", "fonts")
    family = FAMILY
    strict = coretext = input_given = False
    it = iter(sys.argv[1:])
    for a in it:
        if a == "--input":
            inp = next(it, inp)
            input_given = True
        elif a.startswith("--input="):
            inp = a.split("=", 1)[1]
            input_given = True
        elif a == "--family":
            family = next(it, family)
        elif a.startswith("--family="):
            family = a.split("=", 1)[1]
        elif a == "--strict":
            strict = True
        elif a == "--coretext":
            coretext = True
        elif a in ("-h", "--help"):
            print(__doc__)
            return
        else:
            print(f"unknown arg: {a}", file=sys.stderr)
            sys.exit(2)

    have_swift = subprocess.run( ["which", "swift"], capture_output=True, check=False ).returncode == 0

    # bare --coretext (no explicit --input): read the system font cache, print
    # only installed faces, skip directory collection + the per-face spec loop
    cache_only = coretext and not input_given
    if cache_only:
        print("=" * 72)
        print(f"CoreText traits from the system font cache for \"{family}\" (only installed faces shown):")
        print("  expect upright -> italic=n slant~0.000 ; real italic -> italic=Y slant>0\n")
        sys.stdout.flush()
        if have_swift:
            coretext_cache(family)
        else:
            print("  (swift not found; skipping CoreText read)")
        return

    files = collect(inp)
    if not files:
        print(f"no fonts in {inp}")
        sys.exit(2)

    print(f"verifying {len(files)} face(s) in {inp}\n")
    total = len(files)
    npass = 0
    for path in files:
        base, passed, checks, info = check_face(path)
        head = (f"{base}  {DIM}usWeightClass={info['wc']} ({info['weight']}"
                f"{', italic' if info['italic'] else ''})  upm={info['upm']}  "
                f"glyphs={info['total']}  unicode={info['uni']} "
                f"(base={info['base_uni']}, PUA/NF={info['pua']}){RST}")
        print(f"{'●' if passed else '✗'} {head}")
        for label, actual, want, ok in checks:
            line = f"    {label:22s}: {actual!s}"
            if not ok:
                line += f"   {RED}!= expected {want}{RST}"
            print(f"{mark(ok):>14}  {line}" if not ok else f"    {DIM}{mark(ok)}{RST} {line}")
        print(f"    => {mark(passed)}\n")
        npass += passed
    print("=" * 72)
    verdict = f"{GREEN}ALL PASS{RST}" if npass == total else f"{RED}{total - npass} FAILED{RST}"
    print(f"result: {npass}/{total} faces pass spec   {verdict}")

    if coretext:
        print("\n" + "=" * 72)
        print("CoreText traits read straight from each file (no install needed):")
        print("  expect roman -> italic=n slant~0.000 ; italic -> italic=Y slant~0.069\n")
        sys.stdout.flush()
        if have_swift:
            coretext_traits(files)
        else:
            print("  (swift not found; skipping CoreText read)")

    if strict and npass != total:
        sys.exit(1)


if __name__ == "__main__":
    main()
