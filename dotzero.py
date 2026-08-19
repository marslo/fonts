#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Add a centered dot to the 'zero' glyph so 0 is distinguishable from o.

Run with fontforge's python:  fontforge -script dotzero.py [opts] <in.otf|dir>...
Keeps advance width (monospace-safe); originals are never modified.
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


def addDot( glyph, radius ):
    """ Add a filled circle of the given radius at the glyph bbox center. """
    x0, y0, x1, y1 = glyph.boundingBox()
    cx = ( x0 + x1 ) / 2.0
    cy = ( y0 + y1 ) / 2.0
    r = radius
    k = KAPPA * r
    c = fontforge.contour()
    c.is_quadratic = False
    # four on-curve extrema (E, N, W, S) joined by cubic arcs
    c.moveTo( cx + r, cy )
    c.cubicTo( ( cx + r, cy + k ), ( cx + k, cy + r ), ( cx, cy + r ) )
    c.cubicTo( ( cx - k, cy + r ), ( cx - r, cy + k ), ( cx - r, cy ) )
    c.cubicTo( ( cx - r, cy - k ), ( cx - k, cy - r ), ( cx, cy - r ) )
    c.cubicTo( ( cx + k, cy - r ), ( cx + r, cy - k ), ( cx + r, cy ) )
    c.closed = True
    # ttf glyphs are quadratic; adding a cubic contour to a quadratic layer is
    # silently dropped, so convert the circle to match the layer's spline order
    layer = glyph.layers[ 'Fore' ]
    if layer.is_quadratic:
        c.is_quadratic = True
    glyph.layers[ 'Fore' ] += c
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
    """ Open one font, dot its glyph, and generate into the output dir. """
    font = fontforge.open( path )
    try:
        if args.glyph not in font:
            print( f"skip (no '{args.glyph}'): {path}", file=sys.stderr )
            return False

        scale = ( font.em or 1000 ) / 1000.0
        base = args.bold_radius if isBoldFace( font ) else args.radius
        r = base * scale

        glyph = font[ args.glyph ]
        before = len( list( glyph.layers[ 'Fore' ] ) )
        if before > 2:
            print( f"warn: '{args.glyph}' already has {before} contours in {os.path.basename( path )} — adding anyway", file=sys.stderr )

        addDot( glyph, r )
        after = len( list( glyph.layers[ 'Fore' ] ) )
        if after != before + 1:
            sys.exit( f"error: dot was not added to '{args.glyph}' in {os.path.basename( path )} ( {before} -> {after} contours )" )
        if args.rename:
            rename( font, args.rename )

        out = os.path.join( args.out_dir, os.path.basename( path ) )
        if args.dry_run:
            print( f"[dry-run] {os.path.basename( path ):40s} r={r:.0f} -> {out}" )
        else:
            font.generate( out )
            print( f"{os.path.basename( path ):40s} r={r:.0f} -> {out}" )
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
