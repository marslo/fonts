#!/usr/bin/env python3
"""Repair broken quote glyphs on upright faces: «/» ‹/› and ‚/„.

Titillium's Regular *Upright* source draws guillemotleft/guillemotright with a
single chevron (one contour) instead of the usual double chevron (two
contours), so `»` shows as a lone `>`. Every other face (the normal
Titillium-<W>.otf and the other Upright weights) already ships the double
chevron.

Transplants the correct double-chevron outline (CFF charstring + hmtx, metadata
untouched) from a same-weight donor Titillium-<W>.otf -- weight read from the
target's usWeightClass -- into any target whose guillemet is missing, has fewer
than two contours, or whose two chevrons overlap (Light / Semibold Upright draw
them ~40-90 units into each other; every correct face has a +38..+70 gap). The bug only affects upright faces; every italic face
already carries a double chevron and is skipped, so the upright donor is always
right. Idempotent: correct faces are left alone (use --force to override). Only
CFF/OTF targets are handled.

Also repairs the single guillemets (U+2039 ‹ / U+203A ›). On the Light / Regular
/ Semibold *Upright* sources `›` is squashed to ~20-50% of the height of `‹`
(Regular: a 66-unit sliver instead of a 330-unit chevron). `‹`/`›` are mirror
images, so the squashed one is rebuilt by mirroring its intact partner about the
advance-width centre (no donor needed). Detection is the bbox height ratio
(< SINGLE_MIN_RATIO); intact faces (Bold, Thin, all italics) are skipped.

Also repairs the low quotes (U+201A ‚ / U+201E „). The vendor draws them as the
face's own `’` / `”` moved down to the baseline, but in the Light / Regular /
Semibold *Upright* sources `‚` is shrunk to 20-50% (a barely visible dot),
Regular / Light `„` is a lone comma (1 contour instead of 2) and Semibold `„` is
squeezed narrow. Each broken glyph is rebuilt by translating the same face's
intact `’` / `”` outline down; the (dx, dy) offset is read from the same-weight
normal Titillium (`„` vs `”`), whose own `‚` is too small to use as reference.
Detected per glyph by contour-count mismatch or bbox height/width ratio against
its `’` / `”` partner (< LOWQUOTE_MIN_H / LOWQUOTE_MIN_W).

Importable: prep.py calls `fix()` directly. Standalone:

    python3 guillemet.py [DIR|FILE ...] [--root=DONOR_DIR] [--donor=FILE] [--force] [--dry-run]
      # default target DIR=. ; default donor --root=. (the normal Titillium faces)
"""
import glob
import itertools
import os
import sys

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

GUILLEMETS = (0x00AB, 0x00BB)   # « »
SINGLE = (0x2039, 0x203A)       # ‹ ›
SINGLE_MIN_RATIO = 0.9          # shorter / taller bbox height below this = broken
LOWQUOTES = ((0x201A, 0x2019), (0x201E, 0x201D))   # (‚ from ’), („ from ”)
LOWQUOTE_MIN_H = 0.9            # low quote / source bbox height below this = broken
LOWQUOTE_MIN_W = 0.85           # low quote / source bbox width below this = broken
WCLASS = {250: "Thin", 300: "Light", 400: "Regular", 600: "Semibold", 700: "Bold"}


def weight_of(wc):
    return WCLASS.get(wc) or WCLASS[min(WCLASS, key=lambda k: abs(k - wc))]


def donor_for(font, donor_dir):
    # always the upright (non-italic) donor; the bug never hits italic faces
    return os.path.join(donor_dir, f"Titillium-{weight_of(font['OS/2'].usWeightClass)}.otf")


def contour_count(glyph_set, gname):
    pen = RecordingPen()
    glyph_set[gname].draw(pen)
    return sum(1 for op, _ in pen.value if op == "moveTo")


def contour_gap(glyph_set, gname):
    """ Smallest x gap between consecutive contours (< 0 = overlapping); None if < 2 contours. """
    pen = RecordingPen()
    glyph_set[gname].draw(pen)
    boxes, cur = [], None
    for op, args in pen.value:
        if op == "moveTo":
            cur = RecordingPen()
        getattr(cur, op)(*args)
        if op in ("closePath", "endPath"):
            bp = BoundsPen(glyph_set)
            cur.replay(bp)
            boxes.append(bp.bounds)
    boxes.sort()
    if len(boxes) < 2:
        return None
    return min(b[0] - a[2] for a, b in itertools.pairwise(boxes))


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
        gap = contour_gap(tgs, tname)
        overlapped = gap is not None and gap < 0
        if n >= 2 and not overlapped and not force:
            continue
        note = f"{n}c->2c" if n < 2 else f"overlap {gap}->fixed"
        if dry:
            changed.append(f"{tname}({note})")
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
        changed.append(f"{tname}({note} w={w})")
    return changed


def bbox_of(glyph_set, gname):
    pen = BoundsPen(glyph_set)
    glyph_set[gname].draw(pen)
    return pen.bounds   # None for an empty glyph


def mirror_single(target, force, dry):
    """ Rebuild the squashed one of ‹/› by mirroring its intact partner. """
    cmap = target.getBestCmap()
    left, right = cmap.get(SINGLE[0]), cmap.get(SINGLE[1])
    if left is None or right is None:
        return []
    gs = target.getGlyphSet()
    heights = {}
    for name in (left, right):
        bb = bbox_of(gs, name)
        heights[name] = (bb[3] - bb[1]) if bb else 0
    src, dst = (left, right) if heights[left] >= heights[right] else (right, left)
    if not heights[src]:
        return []   # both empty: nothing to mirror from
    ratio = heights[dst] / heights[src]
    if ratio >= SINGLE_MIN_RATIO and not force:
        return []
    if dry:
        return [f"{dst}(h {heights[dst]}->{heights[src]})"]
    td = target["CFF "].cff[target["CFF "].cff.fontNames[0]]
    priv, gsubrs, cstrings = td.Private, td.GlobalSubrs, td.CharStrings
    w = target["hmtx"][dst][0]
    # x' = w - x about the advance centre; reverse restores CFF winding
    pen = T2CharStringPen(w - priv.nominalWidthX, gs)
    gs[src].draw(TransformPen(ReverseContourPen(pen), (-1, 0, 0, 1, w, 0)))
    cstrings[dst] = pen.getCharString(priv, gsubrs)
    bb = bbox_of(target.getGlyphSet(), src)
    target["hmtx"][dst] = (w, w - bb[2])   # mirrored xMin = w - src xMax
    return [f"{dst}(h {heights[dst]}->{heights[src]}, mirrored from {src})"]


def rebuild_lowquotes(target, donor, scale, force, dry):
    """ Rebuild a broken ‚/„ by translating the same face's ’/” down. """
    cmap = target.getBestCmap()
    gs = target.getGlyphSet()
    dcmap, dgs = donor.getBestCmap(), donor.getGlyphSet()
    ref_low, ref_src = bbox_of(dgs, dcmap[0x201E]), bbox_of(dgs, dcmap[0x201D])
    # donor offset of „ relative to ” (x: left edge, y: top edge), in target units
    dx = round((ref_low[0] - ref_src[0]) * scale)
    dy = round((ref_low[3] - ref_src[3]) * scale)

    td = target["CFF "].cff[target["CFF "].cff.fontNames[0]]
    priv, gsubrs, cstrings = td.Private, td.GlobalSubrs, td.CharStrings
    changed = []
    for low_cp, src_cp in LOWQUOTES:
        low, src = cmap.get(low_cp), cmap.get(src_cp)
        if low is None or src is None:
            continue
        sb, lb = bbox_of(gs, src), bbox_of(gs, low)
        if not sb:
            continue
        sh, sw = sb[3] - sb[1], sb[2] - sb[0]
        broken = (not lb
                  or contour_count(gs, low) != contour_count(gs, src)
                  or (lb[3] - lb[1]) < LOWQUOTE_MIN_H * sh
                  or (lb[2] - lb[0]) < LOWQUOTE_MIN_W * sw)
        if not broken and not force:
            continue
        label = f"{low}(h {lb[3] - lb[1] if lb else 0}->{sh}, from {src})"
        if dry:
            changed.append(label)
            continue
        adv = target["hmtx"][low][0]
        pen = T2CharStringPen(adv - priv.nominalWidthX, gs)
        gs[src].draw(TransformPen(pen, (1, 0, 0, 1, dx, dy)))
        cstrings[low] = pen.getCharString(priv, gsubrs)
        lsb = sb[0] + dx
        # keep the ink inside the advance box
        adv = max(adv, round(sb[2] + dx + lsb))
        target["hmtx"][low] = (adv, lsb)
        changed.append(label)
    return changed


def fix(path, donor_dir=".", donor_file=None, force=False, dry=False):
    font = TTFont(path)
    base = os.path.basename(path)
    if "CFF " not in font:
        print(f"skip  {base}  (not CFF/OTF)")
        return
    changed = []
    tag = ""
    donor_path = donor_file or donor_for(font, os.path.expanduser(donor_dir))
    if os.path.isfile(donor_path):
        donor = TTFont(donor_path)
        scale = font["head"].unitsPerEm / donor["head"].unitsPerEm
        changed += transplant(font, donor, scale, force, dry)
        changed += rebuild_lowquotes(font, donor, scale, force, dry)
        donor.close()
        tag = f" <- {os.path.basename(donor_path)}"
    else:
        print(f"warn  {base}  (no donor {os.path.basename(donor_path)}; « » ‚ „ not checked)")
    changed += mirror_single(font, force, dry)
    if not changed:
        print(f"ok    {base}  (« » ‹ › ‚ „ already correct)")
        return
    if dry:
        print(f"[dry-run] {base}{tag}: {', '.join(changed)}")
        return
    font.save(path)
    print(f"fixed {base}{tag}: {', '.join(changed)}")


def iter_targets(args):
    for a in (args or ["."]):
        p = os.path.expanduser(a)
        if os.path.isdir(p):
            yield from sorted(glob.glob(os.path.join(p, "*.otf")) +
                              glob.glob(os.path.join(p, "*.ttf")))
        elif os.path.isfile(p):
            yield p
        else:
            print("not found:", a)


def main():
    dry = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    donor_dir = "."
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

    files = list(iter_targets(targets))
    if not files:
        print("no target fonts found")
        return
    for path in files:
        fix(path, donor_dir, donor_file, force, dry)


if __name__ == "__main__":
    main()
