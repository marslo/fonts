#!/usr/bin/env python3
"""Stage per-weight upright + upright-italic sources for font-patcher.

For each weight it copies two vendor faces into role subfolders of the build
dir, then repairs the single-chevron «/» on the upright (Regular) face:

    <build>/roman/Titillium-<W>Upright.otf         <- src/Titillium-<W>Upright.otf   (verbatim)
    <build>/italic/Titillium-<W>UprightItalic.otf  <- src/Titillium-<W>Italic.otf    (renamed only)

No metadata is touched here. The upright-italic is just the vendor Italic under
a new filename -- its slant is real and its outlines are final; all naming and
style flags are set *after* patching by fixnf.py. This is safe because
font-patcher never slants the glyphs it adds by the font's italic angle (it only
scales + translates them), so pre-setting italic metadata would be pointless.
The role (roman vs italic) is carried by the build subfolder and read back by
fixnf.py, so no italic detection from (possibly dirty) metadata is ever needed.

Usage:
    ./prep.py --src DIR --build DIR [--dry-run]
"""
import os
import sys
import glob
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guillemet import fix as fix_guillemet   # reusable double-chevron transplant

WEIGHTS = ["Thin", "Light", "Regular", "Semibold", "Bold"]


def parse_args(argv):
    src = build = None
    dry = False
    it = iter(argv)
    for a in it:
        if a == "--src":
            src = next(it, None)
        elif a == "--build":
            build = next(it, None)
        elif a == "--dry-run":
            dry = True
        elif a.startswith("--src="):
            src = a.split("=", 1)[1]
        elif a.startswith("--build="):
            build = a.split("=", 1)[1]
        else:
            print("unknown arg:", a)
            sys.exit(2)
    if not src or not build:
        print("usage: prep.py --src DIR --build DIR [--dry-run]")
        sys.exit(2)
    return os.path.expanduser(src), os.path.expanduser(build), dry


def main():
    src, build, dry = parse_args(sys.argv[1:])
    roman_dir = os.path.join(build, "roman")
    italic_dir = os.path.join(build, "italic")
    if not dry:
        os.makedirs(roman_dir, exist_ok=True)
        os.makedirs(italic_dir, exist_ok=True)

    staged_roman = []
    for w in WEIGHTS:
        up = os.path.join(src, f"Titillium-{w}Upright.otf")
        ita = os.path.join(src, f"Titillium-{w}Italic.otf")
        if not (os.path.exists(up) and os.path.exists(ita)):
            print(f"skip {w}: missing {os.path.basename(up)} or {os.path.basename(ita)}")
            continue
        dst_roman = os.path.join(roman_dir, f"Titillium-{w}Upright.otf")
        dst_italic = os.path.join(italic_dir, f"Titillium-{w}UprightItalic.otf")
        if dry:
            print(f"[dry-run] roman  {os.path.basename(up):32s} -> roman/{os.path.basename(dst_roman)}")
            print(f"[dry-run] italic {os.path.basename(ita):32s} -> italic/{os.path.basename(dst_italic)}")
            staged_roman.append(up)   # preview guillemet against the source
            continue
        shutil.copyfile(up, dst_roman)
        shutil.copyfile(ita, dst_italic)
        print(f"staged {w}: roman/{os.path.basename(dst_roman)} + italic/{os.path.basename(dst_italic)}")
        staged_roman.append(dst_roman)

    print("--- repairing guillemets on roman faces ---")
    for f in sorted(staged_roman):
        fix_guillemet(f, donor_dir=src, dry=dry)


if __name__ == "__main__":
    main()
