#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Add a centered dot to the 'zero' glyph so 0 is distinguishable from o, and optionally enlarge the tiny 'bullet' (•, U+2022) glyph.

The bullet can grow two ways ( mutually exclusive ):
  --square  keep Lekton's original square outline, just scaled up ( default )
  --bullet  replace it with a round dot

Run with fontforge's python:  fontforge -script dotzero.py [opts] <in.otf|dir>...
Keeps advance width (monospace-safe); originals are never modified.

USAGE
    fontforge -script dotzero.py -o Lekton Lekton/*NerdFont*.otf
    fontforge -script dotzero.py --square -o Lekton Lekton/*NerdFont*.otf Lekton/*NerdFont*.ttf   # == --square 100 ( square )
    fontforge -script dotzero.py --bullet -o Lekton Lekton/*NerdFont*.otf                          # == --bullet 100 ( round )
"""

import argparse
import os
import sys

try:
    import fontforge
    import psMat
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
    # ttf glyphs are quadratic; a cubic contour added to a quadratic layer is silently dropped, so match the circle to the layer's spline order
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


def setCircle( glyph, radius ):
    """ Replace the glyph outline with one circle of the given radius, keeping center and advance width. """
    x0, y0, x1, y1 = glyph.boundingBox()
    cx = ( x0 + x1 ) / 2.0
    cy = ( y0 + y1 ) / 2.0
    width = glyph.width
    quadratic = glyph.layers[ 'Fore' ].is_quadratic
    layer = fontforge.layer()
    layer.is_quadratic = quadratic
    layer += circleContour( cx, cy, radius, quadratic )
    glyph.layers[ 'Fore' ] = layer          # replace outline; width restored below
    glyph.width = width
    glyph.correctDirection()


def scaleBullet( glyph, target_w ):
    """ Scale the existing bullet outline about its center to target width, keeping shape and advance width. """
    x0, y0, x1, y1 = glyph.boundingBox()
    w = x1 - x0
    if w <= 0:
        return
    cx = ( x0 + x1 ) / 2.0
    cy = ( y0 + y1 ) / 2.0
    width = glyph.width
    m = psMat.compose( psMat.translate( -cx, -cy ),
                       psMat.compose( psMat.scale( target_w / w ), psMat.translate( cx, cy ) ) )
    glyph.transform( m )
    glyph.width = width                      # transform may shift the advance; keep it monospace
    glyph.round()
    glyph.correctDirection()


def bulletHome( font ):
    """ ( center x, center y, advance width ) for a freshly created bullet on a face that lacks one. """
    em = font.em or 1000
    ref = 'period' if 'period' in font else ( 'zero' if 'zero' in font else None )
    width = font[ ref ].width if ref else round( em / 2 )
    return width / 2.0, 0.30 * em, width      # cy ~ middot height; upright Lekton centers the dot at 299/1000


def makeCircle( font, radius ):
    """ Create a U+2022 'bullet' as a centered round dot for faces that lack one ( monospace-safe ). """
    cx, cy, width = bulletHome( font )
    glyph = font.createChar( 0x2022, 'bullet' )
    glyph.width = width
    quadratic = glyph.layers[ 'Fore' ].is_quadratic
    layer = fontforge.layer()
    layer.is_quadratic = quadratic
    layer += circleContour( cx, cy, radius, quadratic )
    glyph.layers[ 'Fore' ] = layer
    glyph.correctDirection()


def makeSquare( font, half ):
    """ Create a U+2022 'bullet' as a centered square ( Lekton bullet aspect ) for faces that lack one. """
    cx, cy, width = bulletHome( font )
    hw = half
    hh = half * 64.0 / 58.0                  # original Lekton bullet is 58 wide x 64 tall
    glyph = font.createChar( 0x2022, 'bullet' )
    glyph.width = width
    quadratic = glyph.layers[ 'Fore' ].is_quadratic
    c = fontforge.contour()
    c.is_quadratic = quadratic
    c.moveTo( cx - hw, cy - hh )
    c.lineTo( cx - hw, cy + hh )
    c.lineTo( cx + hw, cy + hh )
    c.lineTo( cx + hw, cy - hh )
    c.closed = True
    layer = fontforge.layer()
    layer.is_quadratic = quadratic
    layer += c
    glyph.layers[ 'Fore' ] = layer
    glyph.round()
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
    """ Open one font, dot the zero and/or enlarge the bullet, then generate into the output dir. """
    font = fontforge.open( path )
    try:
        scale = ( font.em or 1000 ) / 1000.0
        name = os.path.basename( path )
        notes = []

        # dot the zero ( primary action )
        if args.glyph in font:
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
            notes.append( f"{args.glyph} r={r:.0f}" )
        else:
            print( f"skip (no '{args.glyph}'): {path}", file=sys.stderr )

        # enlarge the bullet, creating it when the face lacks one ( --square or --bullet )
        if args.square_half is not None:
            half = args.square_half * scale
            if 'bullet' in font:
                scaleBullet( font[ 'bullet' ], 2 * half )
                notes.append( f"square w={2 * half:.0f}" )
            else:
                makeSquare( font, half )
                notes.append( f"square w={2 * half:.0f} (created)" )
        elif args.bullet_radius is not None:
            r = args.bullet_radius * scale
            if 'bullet' in font:
                setCircle( font[ 'bullet' ], r )
                notes.append( f"bullet r={r:.0f}" )
            else:
                makeCircle( font, r )
                notes.append( f"bullet r={r:.0f} (created)" )

        if not notes:
            return False
        if args.rename:
            rename( font, args.rename )

        out = os.path.join( args.out_dir, name )
        tag = ', '.join( notes )
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
    bullet = p.add_mutually_exclusive_group()
    bullet.add_argument( '--square', dest='square_half', nargs='?', const=100.0, type=float, default=None, metavar='N', help="enlarge the 'bullet' (•, U+2022) keeping its square shape, half-size N at em=1000 (default 100 -> 200 wide)" )
    bullet.add_argument( '--bullet', dest='bullet_radius', nargs='?', const=100.0, type=float, default=None, metavar='N', help="enlarge the 'bullet' (•, U+2022) as a round dot of radius N at em=1000 (default 100 -> diameter 200)" )
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
