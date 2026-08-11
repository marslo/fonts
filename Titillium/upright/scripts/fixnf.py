#!/usr/bin/env python3
"""Unify font-patcher output into the "Titillium Nerd Font Upright" family.

font-patcher mangles naming/flags and carries over Titillium's dirty CFF
ItalicAngle. This rewrites every patched OTF to a clean, CoreText-friendly RIBBI
state so that, in a browser:

    font-family: "Titillium Nerd Font Upright";   -> upright Regular
    font-style:  italic;                          -> the slanted Italic

Key difference from the old 03-fix-nf.py: italic-ness is taken from *which input
folder* a face came from (--roman vs --italic), NOT sniffed from the font's own
metadata. That removes the need to pre-clean the upright sources (their leftover
ItalicAngle = -13 can no longer fool anything). Weight still comes from
usWeightClass. Output is written under canonical filenames into --out.

Usage:
    ./fixnf.py --roman DIR --italic DIR --out DIR [--install] [--dry-run]
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


def font_filename(weight, italic):
    style = (("" if weight == "Regular" else weight)
             + ("Italic" if italic else ("Regular" if weight == "Regular" else ""))) or "Regular"
    return f"TitilliumNerdFont-Upright{style}.otf"


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


def fix_one(path, italic, out_dir, dry=False):
    font = TTFont(path)
    weight = weight_of(font["OS/2"].usWeightClass)
    bold = font["OS/2"].usWeightClass >= 700
    role = "italic" if italic else "roman "

    n1, n2, n4, n6, n16, n17 = nf_names(weight, italic)
    dst = os.path.join(out_dir, font_filename(weight, italic))
    if dry:
        print(f"[dry-run] {os.path.basename(path):40s} [{role}] -> {n1} / {n2}  "
              f"[{n6}]  angle={-13.0 if italic else 0.0}  => {os.path.basename(dst)}")
        return dst

    set_name(font, 1, n1)
    set_name(font, 2, n2)
    set_name(font, 4, n4)
    set_name(font, 6, n6)
    set_name(font, 16, n16)
    set_name(font, 17, n17)
    apply_style(font, italic, bold)
    if "CFF " in font:
        font["CFF "].cff.fontNames[0] = n6

    font.save(dst)
    print(f"fixed {os.path.basename(path):40s} [{role}] -> {n1} / {n2}  [{n6}]  => {os.path.basename(dst)}")
    return dst


def install(paths):
    home = os.path.expanduser("~")
    fonts_dir = os.path.join(home, "Library", "Fonts")
    dests = []
    for p in paths:
        d = os.path.join(fonts_dir, os.path.basename(p))
        subprocess.run(["/bin/cp", "-f", p, d], check=True)
        dests.append(d)

    subprocess.run( ["rm", "-rf", os.path.join(home, "Library", "Caches", "com.apple.FontRegistry")], check=False )
    subprocess.run( ["killall", "fontd"], stderr=subprocess.DEVNULL, check=False )

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
    with tempfile.NamedTemporaryFile( "w", suffix=".swift", delete=False ) as tf:
        tf.write(swift)
        tf_name = tf.name
    print( "--- installing + registering (.user scope) ---" )
    try:
        subprocess.run( ["swift", tf_name], check=True )
    finally:
        os.unlink(tf_name)
    print("done. Fully quit and reopen the browser to pick up the change.")


def parse_args(argv):
    roman = italic = out = None
    dry = install_flag = False
    it = iter(argv)
    for a in it:
        if a == "--roman":
            roman = next(it, None)
        elif a == "--italic":
            italic = next(it, None)
        elif a == "--out":
            out = next(it, None)
        elif a.startswith("--roman="):
            roman = a.split("=", 1)[1]
        elif a.startswith("--italic="):
            italic = a.split("=", 1)[1]
        elif a.startswith("--out="):
            out = a.split("=", 1)[1]
        elif a == "--dry-run":
            dry = True
        elif a == "--install":
            install_flag = True
        else:
            print("unknown arg:", a)
            sys.exit(2)
    if not roman or not italic or not out:
        print("usage: fixnf.py --roman DIR --italic DIR --out DIR [--install] [--dry-run]")
        sys.exit(2)
    return (os.path.expanduser(roman), os.path.expanduser(italic),
            os.path.expanduser(out), dry, install_flag)


def faces(d):
    return sorted(glob.glob(os.path.join(d, "*.otf")) + glob.glob(os.path.join(d, "*.ttf")))


def main():
    roman, italic, out, dry, install_flag = parse_args(sys.argv[1:])
    if not dry:
        os.makedirs(out, exist_ok=True)

    jobs = [(p, False) for p in faces(roman)] + [(p, True) for p in faces(italic)]
    if not jobs:
        print(f"no patched fonts found in {roman} or {italic}")
        return

    produced = []
    for path, is_it in jobs:
        produced.append(fix_one(path, is_it, out, dry=dry))

    if install_flag:
        if dry:
            print("[dry-run] would copy to ~/Library/Fonts, flush fontd, register (.user)")
        else:
            install(produced)


if __name__ == "__main__":
    main()
