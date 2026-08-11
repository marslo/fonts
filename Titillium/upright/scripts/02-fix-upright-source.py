#!/usr/bin/env python3
"""Strip dirty italic metadata from the upright (non-italic) source faces.

Titillium's upright OTFs ship with leftover italic traits (macStyle italic bit,
post.italicAngle = -13, CFF ItalicAngle = -13, and a stray BOLD fsSelection
bit). CoreText reads the CFF ItalicAngle to decide a CFF face is slanted, so an
upright that still says -13 gets treated as italic and loses to a real italic
sibling. This neutralises those traits before patching.

Runs in place on every `Titillium-*Upright.otf` (NOT the *UprightItalic ones).

Usage:
    ./02-fix-upright-source.py [DIR] [--dry-run]      # default DIR=~/Desktop/titillium/up
"""
import os
import sys
import glob
from fontTools.ttLib import TTFont

_args = [a for a in sys.argv[1:] if not a.startswith("--")]
_flags = {a for a in sys.argv[1:] if a.startswith("--")}
DRY = "--dry-run" in _flags
DIR = os.path.expanduser(_args[0] if _args else "~/Desktop/titillium/up")

ITALIC_MS = 0x02      # head.macStyle italic bit (bit 1)
BOLD_MS = 0x01        # head.macStyle bold bit (bit 0)
ITALIC_FS = 0x01      # OS/2.fsSelection italic bit (bit 0)
BOLD_FS = 0x20
REGULAR_FS = 0x40


def fix(path):
    font = TTFont(path)
    bold = font["OS/2"].usWeightClass >= 700
    if DRY:
        print(f"[dry-run] would clean {os.path.basename(path)} "
              f"(italicAngle->0, CFF->0, fsSelection->{'BOLD' if bold else 'REGULAR'})")
        return

    ms = font["head"].macStyle & ~ITALIC_MS
    ms = (ms | BOLD_MS) if bold else (ms & ~BOLD_MS)
    font["head"].macStyle = ms

    fs = font["OS/2"].fsSelection & ~(ITALIC_FS | BOLD_FS | REGULAR_FS)
    fs |= BOLD_FS if bold else REGULAR_FS
    font["OS/2"].fsSelection = fs

    font["post"].italicAngle = 0.0
    if "CFF " in font:
        font["CFF "].cff.topDictIndex[0].ItalicAngle = 0

    font.save(path)
    print("fixed", os.path.basename(path))


def main():
    files = [p for p in glob.glob(os.path.join(DIR, "Titillium-*Upright.otf"))
             if not p.endswith("UprightItalic.otf")]
    if not files:
        print("no Titillium-*Upright.otf found in", DIR)
        return
    for path in sorted(files):
        fix(path)


if __name__ == "__main__":
    main()
