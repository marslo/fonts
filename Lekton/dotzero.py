#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Add a centered dot to the 'zero' glyph so 0 is distinguishable from o.

Symbol fixes ( enlarge •, add ^ / ` ) live in glyphfix.py — this script only touches the zero.

Run with fontforge's python:  fontforge -script dotzero.py [opts] <in.otf|dir>...
Keeps advance width (monospace-safe); originals are never modified.

USAGE
    fontforge -script dotzero.py -o Lekton Lekton/*NerdFont*.otf
    fontforge -script dotzero.py -r 62 -o Lekton Lekton/*NerdFont*.otf Lekton/*NerdFont*.ttf
"""

import argparse
import os
import sys

try:
    import fontforge
except ImportError:
    sys.exit( "error: run me via 'fontforge -script dotzero.py ...' (needs the fontforge python module)" )

FONT_EXTS = ( '.otf', '.ttf' )
KAPPA = 0.5522847498307936        # cubic-bezier circle handle ratio


def isBoldFace( font ):
    """ True when the face reads as bold (name or OS/2 weight). """
    name = ( font.fontname or '' ).lower()
    weight = ( font.weight or '' ).lower()
    heavy = 'bold' in name or 'bold' in weight or 'black' in weight
    return heavy or ( font.os2_weight or 0 ) >= 600


def circleContour( cx, cy, r, quadratic ):
    """ Build a closed circle contour of radius r centered at (cx, cy). """
    k = KAPPA * r
    c = fontforge.contour()
    c.is_quadratic = False
    # four on-curve extreme (E, N, W, S) joined by cubic arcs
    c.moveTo( cx + r, cy )
    c.cubicTo( ( cx + r, cy + k ), ( cx + k, cy + r ), ( cx, cy + r ) )
    c.cubicTo( ( cx - k, cy + r ), ( cx - r, cy + k ), ( cx - r, cy ) )
    c.cubicTo( ( cx - r, cy - k ), ( cx - k, cy - r ), ( cx, cy - r ) )
    c.cubicTo( ( cx + k, cy - r ), ( cx + r, cy - k ), ( cx + r, cy ) )
    c.closed = True
    # ttf glyphs are quadratic; a cubic contour on a quadratic layer is dropped, so match the layer
    if quadratic:
        c.is_quadratic = True
    return c


def addDot( glyph, radius ):
    """ Add a filled circle of the given radius at the glyph bbox center. """
    x0, y0, x1, y1 = glyph.boundingBox()
    cx = ( x0 + x1 ) / 2.0
    cy = ( y0 + y1 ) / 2.0
    layer = glyph.layers[ 'Fore' ]
    glyph.layers[ 'Fore' ] += circleContour( cx, cy, radius, layer.is_quadratic )
    glyph.correctDirection()


def rename( font, suffix ):
    """ Append suffix to family/full/ps names so the font can coexist with the original. """
    # setting these fields makes generate() rebuild the matching name-table strings
    font.familyname = ( font.familyname or font.fontname ) + suffix
    font.fullname = ( font.fullname or font.fontname ) + suffix
    font.fontname = ( font.fontname or 'Font' ) + suffix.replace( ' ', '' )


def collectInputs( paths ):
    """ Expand files and directories into a flat list of font paths. """
    out = []
    for p in paths:
        if os.path.isdir( p ):
            out += [ os.path.join( p, n ) for n in sorted( os.listdir( p ) )
                     if n.lower().endswith( FONT_EXTS ) ]
        elif p.lower().endswith( FONT_EXTS ):
            out.append( p )
        else:
            print( f"skip (not a font): {p}", file=sys.stderr )
    return out


def process( path, args ):
    """ Open one font, dot the zero, then generate into the output dir. """
    font = fontforge.open( path )
    try:
        scale = ( font.em or 1000 ) / 1000.0
        name = os.path.basename( path )

        if args.glyph not in font:
            print( f"skip (no '{args.glyph}'): {path}", file=sys.stderr )
            return False

        base = args.bold_radius if isBoldFace( font ) else args.radius
        r = base * scale
        glyph = font[ args.glyph ]
        before = len( list( glyph.layers[ 'Fore' ] ) )
        if before > 2:
            print( f"warn: '{args.glyph}' already has {before} contours in {name} — adding anyway", file=sys.stderr )
        addDot( glyph, r )
        after = len( list( glyph.layers[ 'Fore' ] ) )
        if after != before + 1:
            sys.exit( f"error: dot was not added to '{args.glyph}' in {name} ( {before} -> {after} contours )" )

        if args.rename:
            rename( font, args.rename )

        out = os.path.join( args.out_dir, name )
        tag = f"{args.glyph} r={r:.0f}"
        if args.dry_run:
            print( f"[dry-run] {name:40s} {tag} -> {out}" )
        else:
            font.generate( out )
            print( f"{name:40s} {tag} -> {out}" )
        return True
    finally:
        font.close()


def parseArgs( argv ):
    p = argparse.ArgumentParser(
        prog='dotzero.py',
        description='add a centered dot to the zero glyph (0 vs o)',
    )
    p.add_argument( 'inputs', nargs='+', help='font files or directories (*.otf, *.ttf)' )
    p.add_argument( '-o', '--out-dir', help='output dir (default: <first-input-parent>/nf-dotted)' )
    p.add_argument( '-r', '--radius', type=float, default=62.0, help='dot radius at em=1000 (default 62)' )
    p.add_argument( '--bold-radius', type=float, help='radius for bold faces (default: radius + 10)' )
    p.add_argument( '-g', '--glyph', default='zero', help="glyph to modify (default 'zero')" )
    p.add_argument( '--rename', metavar='SUFFIX', help="append SUFFIX to family name for coexistence, e.g. ' Dotted'" )
    p.add_argument( '-n', '--dry-run', action='store_true', help='report actions without writing files' )
    args = p.parse_args( argv )
    if args.bold_radius is None:
        args.bold_radius = args.radius + 10.0
    return args


def main( argv ):
    args = parseArgs( argv )
    fonts = collectInputs( args.inputs )
    if not fonts:
        sys.exit( 'error: no .otf/.ttf inputs found' )

    if not args.out_dir:
        first = args.inputs[ 0 ]
        parent = first if os.path.isdir( first ) else os.path.dirname( os.path.abspath( first ) )
        args.out_dir = os.path.join( os.path.dirname( parent.rstrip( '/' ) ) or '.',
                                     os.path.basename( parent.rstrip( '/' ) ) + '-dotted' )
    if not args.dry_run:
        os.makedirs( args.out_dir, exist_ok=True )

    ok = sum( process( f, args ) for f in fonts )
    print( f"\ndone: {ok}/{len( fonts )} font(s) -> {args.out_dir}" )


if __name__ == '__main__':
    # fontforge passes script args after the filename; argv[0] is this script
    main( sys.argv[ 1: ] )

# vim:tabstop=4:softtabstop=4:shiftwidth=4:expandtab:filetype=python:
