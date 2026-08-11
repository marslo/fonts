#!/usr/bin/env python3
"""Repair single-chevron guillemets («/») on the upright faces.

Titillium's Regular *Upright* source draws guillemotleft/guillemotright with a
single chevron (one contour) instead of the usual double chevron (two
contours), so `»` shows as a lone `>`. Every other face (the normal
Titillium-<W>.otf and the other Upright weights) is fine.

Transplants the correct double-chevron outline from a same-weight donor
(FONT_ROOT/Titillium-<W>.otf, the upright non-italic face; weight read from the
target's usWeightClass) into any target whose guillemet is missing or has fewer
than two contours. The bug only affects upright faces -- every italic face
already ships a double chevron and is skipped -- so the upright donor is always
the right source; pass --donor=FILE to override. Idempotent: faces that already
carry a double chevron are left untouched (use --force to override). Only
CFF/OTF targets are handled.

Usage:
    ./04-fix-guillemet.py [DIR|FILE ...] [--root=FONT_ROOT] [--donor=FILE]
                          [--force] [--dry-run]
      # default target DIR=~/Desktop/titillium/up  (the staged upright sources)
      # default donor  --root=~/Desktop/titillium  (the normal Titillium faces)
"""
import os
import sys
import glob
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen

GUILLEMETS = (0x00AB, 0x00BB)   # « »
WCLASS = {250: "Thin", 300: "Light", 400: "Regular", 600: "Semibold", 700: "Bold"}


def weight_of(wc):
    return WCLASS.get(wc) or WCLASS[min(WCLASS, key=lambda k: abs(k - wc))]


def donor_for(font, donor_dir):
    return os.path.join(donor_dir, f"Titillium-{weight_of(font['OS/2'].usWeightClass)}.otf")


def contour_count(glyph_set, gname):
    pen = RecordingPen()
    glyph_set[gname].draw(pen)
    return sum(1 for op, _ in pen.value if op == "moveTo")


def transplant(target, donor, scale, force, dry):
    tcmap, dcmap = target.getBestCmap(), donor.getBestCmap()
    tgs, dgs = target.getGlyphSet(), donor.getGlyphSet()
    td = target["CFF "].cff[target["CFF "].cff.fontNames[0]]
    priv, gsubrs, cstrings = td.Private, td.GlobalSubrs, td.CharStrings

    changed = []
    for cp in GUILLEMETS:
        tname, dname = tcmap.get(cp), dcmap.get(cp)
        if tname is None or dname is None:
            continue
        n = contour_count(tgs, tname)
        if n >= 2 and not force:
            continue
        if dry:
            changed.append(f"{tname}({n}c->2c)")
            continue
        rp = RecordingPen()
        dgs[dname].draw(rp)
        w, lsb = donor["hmtx"][dname]
        w, lsb = round(w * scale), round(lsb * scale)
        # T2 width operand must be encoded relative to nominalWidthX
        pen = T2CharStringPen(w - priv.nominalWidthX, tgs)
        if scale != 1.0:
            rp.replay(TransformPen(pen, (scale, 0, 0, scale, 0, 0)))
        else:
            rp.replay(pen)
        cstrings[tname] = pen.getCharString(priv, gsubrs)
        target["hmtx"][tname] = (w, lsb)
        changed.append(f"{tname}({n}c->2c w={w})")
    return changed


def fix(path, donor_dir, donor_file, force, dry):
    font = TTFont(path)
    base = os.path.basename(path)
    if "CFF " not in font:
        print(f"skip  {base}  (not CFF/OTF)")
        return
    donor_path = donor_file or donor_for(font, donor_dir)
    if not os.path.isfile(donor_path):
        print(f"skip  {base}  (no donor {os.path.basename(donor_path)})")
        return
    donor = TTFont(donor_path)
    scale = font["head"].unitsPerEm / donor["head"].unitsPerEm
    changed = transplant(font, donor, scale, force, dry)
    donor.close()
    if not changed:
        print(f"ok    {base}  (guillemets already double-chevron)")
        return
    tag = os.path.basename(donor_path)
    if dry:
        print(f"[dry-run] {base} <- {tag}: {', '.join(changed)}")
        return
    font.save(path)
    print(f"fixed {base} <- {tag}: {', '.join(changed)}")


def iter_targets(args):
    for a in (args or ["~/Desktop/titillium/up"]):
        p = os.path.expanduser(a)
        if os.path.isdir(p):
            for f in sorted(glob.glob(os.path.join(p, "*.otf")) +
                            glob.glob(os.path.join(p, "*.ttf"))):
                yield f
        elif os.path.isfile(p):
            yield p
        else:
            print("not found:", a)


def main():
    dry = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    donor_dir = "~/Desktop/titillium"
    donor_file = None
    targets = []
    for a in sys.argv[1:]:
        if a.startswith("--root="):
            donor_dir = a.split("=", 1)[1]
        elif a.startswith("--donor="):
            donor_file = os.path.expanduser(a.split("=", 1)[1])
        elif a in ("--dry-run", "--force"):
            continue
        elif a.startswith("--"):
            print("unknown flag:", a)
            sys.exit(2)
        else:
            targets.append(a)

    donor_dir = os.path.expanduser(donor_dir)
    files = list(iter_targets(targets))
    if not files:
        print("no target fonts found")
        return
    for path in files:
        fix(path, donor_dir, donor_file, force, dry)


if __name__ == "__main__":
    main()
