#!/usr/bin/env python3
"""Normalise font-patcher (Nerd Font) output metadata for the Upright family.

font-patcher mangles naming/flags (especially for the italic face) and carries
over Titillium's dirty CFF ItalicAngle. This rewrites every patched OTF to a
clean, CoreText-friendly state so that, in a browser:

    font-family: "Titillium Nerd Font Upright";   -> upright Regular
    font-style:  italic;                          -> the slanted Italic

Weight and italic-ness are detected from the font's own metadata, so it does
not depend on font-patcher's filenames. All weights share the typographic
family "Titillium Nerd Font Upright"; Regular/Bold use RIBBI grouping, the rest
get their own legacy family for old apps.

Usage:
    ./03-fix-nf.py [DIR]                # default DIR=~/Desktop/titillium/up/nf
    ./03-fix-nf.py [DIR] --install      # also copy to ~/Library/Fonts, flush
                                        # fontd, and register at .user scope
    ./03-fix-nf.py [DIR] --dry-run      # print intended changes, write nothing
"""
import os
import sys
import glob
import subprocess
import tempfile
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


def set_name(font, nid, value):
    name = font["name"]
    name.setName(value, nid, 3, 1, 0x409)
    name.setName(value, nid, 1, 0, 0)


def get_name(font, nid):
    name = font["name"]
    rec = name.getName(nid, 3, 1, 0x409) or name.getName(nid, 1, 0, 0)
    return rec.toUnicode() if rec else None


def weight_of(wc):
    return WCLASS.get(wc) or WCLASS[min(WCLASS, key=lambda k: abs(k - wc))]


def is_italic(font):
    if font["head"].macStyle & ITALIC_MS:
        return True
    if abs(font["post"].italicAngle) > 0.01:
        return True
    sub = (get_name(font, 17) or get_name(font, 2) or "").lower()
    return "italic" in sub or "oblique" in sub


def nf_names(weight, italic):
    typo_sub = (("" if weight == "Regular" else weight)
                + (" Italic" if italic else "")).strip() or "Regular"
    if weight in RIBBI:
        n1 = FAMILY
        if weight == "Bold":
            n2 = "Bold Italic" if italic else "Bold"
        else:
            n2 = "Italic" if italic else "Regular"
    else:
        n1 = f"{FAMILY} {weight}"
        n2 = "Italic" if italic else "Regular"
    n4 = FAMILY if (weight == "Regular" and not italic) else f"{FAMILY} {typo_sub}"
    ps_style = (("" if weight == "Regular" else weight)
                + ("Italic" if italic else ("Regular" if weight == "Regular" else ""))) or "Regular"
    n6 = f"TitilliumNF-Upright{ps_style}"
    return n1, n2, n4, n6, FAMILY, typo_sub


def apply_style(font, italic, bold):
    ms = font["head"].macStyle
    ms = (ms | ITALIC_MS) if italic else (ms & ~ITALIC_MS)
    ms = (ms | BOLD_MS) if bold else (ms & ~BOLD_MS)
    font["head"].macStyle = ms

    fs = font["OS/2"].fsSelection & ~(ITALIC_FS | BOLD_FS | REGULAR_FS)
    if italic:
        fs |= ITALIC_FS
    if bold:
        fs |= BOLD_FS
    if not italic and not bold:
        fs |= REGULAR_FS
    fs |= USE_TYPO | WWS
    font["OS/2"].fsSelection = fs

    angle = -13.0 if italic else 0.0
    font["post"].italicAngle = angle
    if "CFF " in font:
        font["CFF "].cff.topDictIndex[0].ItalicAngle = int(angle)


def fix(path, dry=False):
    font = TTFont(path)
    weight = weight_of(font["OS/2"].usWeightClass)
    italic = is_italic(font)
    bold = font["OS/2"].usWeightClass >= 700

    n1, n2, n4, n6, n16, n17 = nf_names(weight, italic)
    if dry:
        print(f"[dry-run] {os.path.basename(path):42s} -> {n1} / {n2}  [{n6}]  "
              f"angle={-13.0 if italic else 0.0}")
        return n6

    set_name(font, 1, n1)
    set_name(font, 2, n2)
    set_name(font, 4, n4)
    set_name(font, 6, n6)
    set_name(font, 16, n16)
    set_name(font, 17, n17)
    apply_style(font, italic, bold)
    if "CFF " in font:
        font["CFF "].cff.fontNames[0] = n6

    font.save(path)
    print(f"fixed {os.path.basename(path):42s} -> {n1} / {n2}  [{n6}]")
    return n6


def install(paths):
    home = os.path.expanduser("~")
    fonts_dir = os.path.join(home, "Library", "Fonts")
    dests = []
    for p in paths:
        d = os.path.join(fonts_dir, os.path.basename(p))
        subprocess.run(["/bin/cp", "-f", p, d], check=True)
        dests.append(d)

    subprocess.run(["rm", "-rf", os.path.join(home, "Library", "Caches", "com.apple.FontRegistry")])
    subprocess.run(["killall", "fontd"], stderr=subprocess.DEVNULL)

    arr = ",\n".join(f'  "{d}"' for d in dests)
    swift = (
        "import CoreText\nimport Foundation\n"
        f"let paths = [\n{arr}\n]\n"
        "for p in paths {\n"
        "  let u = URL(fileURLWithPath: p) as CFURL\n"
        "  CTFontManagerUnregisterFontsForURL(u, .user, nil)\n"
        "  var e: Unmanaged<CFError>?\n"
        "  let ok = CTFontManagerRegisterFontsForURL(u, .user, &e)\n"
        "  print(\"register \\((p as NSString).lastPathComponent): \\(ok)\")\n"
        "}\n"
    )
    tf = tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False)
    tf.write(swift)
    tf.close()
    print("--- installing + registering (.user scope) ---")
    subprocess.run(["swift", tf.name])
    os.unlink(tf.name)
    print("done. Fully quit and reopen the browser to pick up the change.")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    target = os.path.expanduser(args[0] if args else "~/Desktop/titillium/up/nf")

    dry = "--dry-run" in flags

    files = sorted(glob.glob(os.path.join(target, "*.otf")) + glob.glob(os.path.join(target, "*.ttf")))
    if not files:
        print("no patched fonts found in", target)
        return

    fixed = []
    for path in files:
        fix(path, dry=dry)
        fixed.append(path)

    if "--install" in flags:
        if dry:
            print("[dry-run] would copy to ~/Library/Fonts, flush fontd, register (.user)")
        else:
            install(fixed)


if __name__ == "__main__":
    main()
