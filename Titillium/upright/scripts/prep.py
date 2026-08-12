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
    ./prep.py --src DIR [--src DIR ...] --build DIR [--dry-run]

--src is repeatable; each weight's Upright/Italic face is looked up across the
given dirs in order (first match wins).
"""
import os
import sys
import glob
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guillemet import fix as fix_guillemet   # reusable double-chevron transplant

WEIGHTS = ["Thin", "Light", "Regular", "Semibold", "Bold"]


def parse_args(argv):
    srcs = []
    build = None
    dry = False
    it = iter(argv)
    for a in it:
        if a == "--src":
            v = next(it, None)
            if v is not None:
                srcs.append(v)
        elif a.startswith("--src="):
            srcs.append(a.split("=", 1)[1])
        elif a == "--build":
            build = next(it, None)
        elif a.startswith("--build="):
            build = a.split("=", 1)[1]
        elif a == "--dry-run":
            dry = True
        else:
            print("unknown arg:", a)
            sys.exit(2)
    if not srcs or not build:
        print("usage: prep.py --src DIR [--src DIR ...] --build DIR [--dry-run]")
        sys.exit(2)
    return [os.path.expanduser(s) for s in srcs], os.path.expanduser(build), dry


def find_in(srcs, name):
    """ Return the first <src>/<name> that exists across the src dirs, else None. """
    for d in srcs:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


def donor_dir_of(srcs):
    """ The src dir holding the normal Titillium-<W>.otf faces (guillemet donor). """
    for d in srcs:
        if os.path.exists(os.path.join(d, "Titillium-Regular.otf")):
            return d
    return srcs[0]


def main():
    srcs, build, dry = parse_args(sys.argv[1:])
    roman_dir = os.path.join(build, "roman")
    italic_dir = os.path.join(build, "italic")
    if not dry:
        os.makedirs(roman_dir, exist_ok=True)
        os.makedirs(italic_dir, exist_ok=True)

    staged_roman = []
    for w in WEIGHTS:
        up = find_in(srcs, f"Titillium-{w}Upright.otf")
        ita = find_in(srcs, f"Titillium-{w}Italic.otf")
        if not (up and ita):
            missing = []
            if not up:
                missing.append(f"Titillium-{w}Upright.otf")
            if not ita:
                missing.append(f"Titillium-{w}Italic.otf")
            print(f"skip {w}: missing {' + '.join(missing)} in {', '.join(srcs)}")
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
        rseg = f"roman/{os.path.basename(dst_roman)}"
        print(f"staged {w + ':':<10}{rseg:<38}+ italic/{os.path.basename(dst_italic)}")
        staged_roman.append(dst_roman)

    donor_dir = donor_dir_of(srcs)
    print("--- repairing guillemets on roman faces ---")
    for f in sorted(staged_roman):
        fix_guillemet(f, donor_dir=donor_dir, dry=dry)


if __name__ == "__main__":
    main()
