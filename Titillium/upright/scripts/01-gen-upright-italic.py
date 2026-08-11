#!/usr/bin/env python3
"""Generate the full set of upright-italic source faces.

For each weight it takes the slanted outlines from `Titillium-<W>Italic.otf`
and dresses them with naming mirrored from `Titillium-<W>Upright.otf`, so the
result (`Titillium-<W>UprightItalic.otf`) forms a proper Regular/Italic pair
with the upright face. A copy of the upright face is staged alongside it so the
`up/` folder holds complete pairs ready for font-patcher.

Usage:
    ./01-gen-upright-italic.py [ROOT_DIR] [--dry-run]   # default ROOT_DIR=~/Desktop/titillium
Output goes to ROOT_DIR/up/.
"""
import os
import sys
import shutil
from fontTools.ttLib import TTFont

WEIGHTS = ["Thin", "Light", "Regular", "Semibold", "Bold"]
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
_flags = {a for a in sys.argv[1:] if a.startswith("--")}
DRY = "--dry-run" in _flags
ROOT = os.path.expanduser(_args[0] if _args else "~/Desktop/titillium")
OUT = os.path.join(ROOT, "up")


def set_name(font, nid, value):
    name = font["name"]
    name.setName(value, nid, 3, 1, 0x409)   # Windows / Unicode BMP / en-US
    name.setName(value, nid, 1, 0, 0)       # Mac / Roman / English


def get_name(font, nid):
    name = font["name"]
    rec = name.getName(nid, 3, 1, 0x409) or name.getName(nid, 1, 0, 0)
    return rec.toUnicode() if rec else None


def main():
    if not DRY:
        os.makedirs(OUT, exist_ok=True)
    for w in WEIGHTS:
        up = os.path.join(ROOT, f"Titillium-{w}Upright.otf")
        ita = os.path.join(ROOT, f"Titillium-{w}Italic.otf")
        dst = os.path.join(OUT, f"Titillium-{w}UprightItalic.otf")
        if not (os.path.exists(up) and os.path.exists(ita)):
            print(f"skip {w}: missing {os.path.basename(up)} or {os.path.basename(ita)}")
            continue
        if DRY:
            print(f"[dry-run] would write {os.path.relpath(dst, ROOT)} (from {w}Italic, naming from {w}Upright)")
            continue

        font = TTFont(ita)          # slanted outlines live here
        ref = TTFont(up)            # naming pattern of the upright pair

        for nid in (1, 16):                         # family / typographic family
            value = get_name(ref, nid)
            if value:
                set_name(font, nid, value)
        for nid in (2, 4, 17):                      # subfamily / full / typo subfamily
            base = get_name(ref, nid) or get_name(font, nid) or ""
            set_name(font, nid, f"{base} Italic".strip())
        ps = (get_name(ref, 6) or f"Titillium-{w}Upright") + "Italic"
        set_name(font, 6, ps)

        font["head"].macStyle |= 0x02                       # macStyle italic bit (bit 1)
        font["OS/2"].fsSelection = (font["OS/2"].fsSelection & ~0x40) | 0x01
        font["post"].italicAngle = -13.0
        if "CFF " in font:
            font["CFF "].cff.fontNames[0] = ps
            font["CFF "].cff.topDictIndex[0].ItalicAngle = -13

        font.save(dst)
        shutil.copyfile(up, os.path.join(OUT, os.path.basename(up)))
        print("wrote", os.path.relpath(dst, ROOT), "(+ staged upright)")


if __name__ == "__main__":
    main()
