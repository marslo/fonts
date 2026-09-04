#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix / add Lekton's symbol glyphs ( everything that isn't the '0' — that lives in dotzero.py ):

  •  U+2022  bullet   enlarge Lekton's tiny bullet, keeping its square outline ( or a round dot )
  ^  U+005E  circumflex  add it when the face lacks one ( Lekton ships without ^ )
  `  U+0060  grave       add it when the face lacks one ( Lekton ships without ` )

The ^ and ` are synthesized from the face's own diacritic accents ( the top contour of â / à ), so they match Lekton's stroke weight and style. This also makes the font ligaturizable: Ligaturizer aborts on a font missing ^ ( asciicircum ).

Run with fontforge's python:  fontforge -script glyphfix.py [opts] <in.otf|dir>...
Keeps advance width (monospace-safe); originals are never modified.

USAGE
    fontforge -script glyphfix.py -o OUT Lekton/*.ttf                 # == --square 100 + fill ^ `
    fontforge -script glyphfix.py --square 100 -o OUT Lekton/*.otf    # square bullet, width 200
    fontforge -script glyphfix.py --bullet 100 -o OUT Lekton/*.otf    # round bullet, diameter 200
    fontforge -script glyphfix.py --no-ascii -o OUT Lekton/*.ttf      # only touch the bullet
"""

import argparse
import os
import sys

try:
    import fontforge
    import psMat
except ImportError:
    sys.exit( "error: run me via 'fontforge -script glyphfix.py ...' (needs the fontforge python module)" )

FONT_EXTS = ( '.otf', '.ttf' )
KAPPA = 0.5522847498307936        # cubic-bezier circle handle ratio

# codepoint -> ( glyph name, donor composite ) — the accent is the donor's top contour
ASCII_FILL = {
    0x5E: ( 'asciicircum', 'acircumflex' ),   # ^  <- circumflex accent of â
    0x60: ( 'grave',       'agrave'      ),   # `  <- grave accent of à
}


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


def hasGlyph( font, cp ):
    """ True when the code point maps to a real ( worth-outputting ) glyph. """
    try:
        return font[ cp ].isWorthOutputting()
    except TypeError:
        return False                          # font[cp] raises TypeError 'No such glyph' for an empty slot


def topAccent( glyph ):
    """ Dup of the glyph's highest contour — the accent sitting above a diacritic composite's base. """
    best = None
    besty = None
    for c in glyph.foreground:
        ys = [ p.y for p in c ]
        if not ys:
            continue
        lo = min( ys )
        if besty is None or lo > besty:
            besty, best = lo, c
    return best.dup() if best is not None else None


def addAscii( font ):
    """ Add ^ and ` from the face's own circumflex/grave accents when the face lacks them. """
    added = []
    for cp, ( name, donor ) in sorted( ASCII_FILL.items() ):
        if hasGlyph( font, cp ) or donor not in font:
            continue
        accent = topAccent( font[ donor ] )
        if accent is None:
            continue
        glyph = font.createChar( cp, name )
        accent.is_quadratic = glyph.layers[ 'Fore' ].is_quadratic
        glyph.layers[ 'Fore' ] += accent
        glyph.width = font[ donor ].width     # monospace advance from the donor
        glyph.round()
        glyph.correctDirection()
        added.append( name )
    return added


def rename( font, suffix ):
    """ Append suffix to family/full/ps names so the font can coexist with the original. """
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
    """ Open one font, enlarge/create the bullet and fill ^ `, then generate into the output dir. """
    font = fontforge.open( path )
    try:
        scale = ( font.em or 1000 ) / 1000.0
        name = os.path.basename( path )
        notes = []

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

        # fill the missing ^ and ` from the face's own accents
        if not args.no_ascii:
            got = addAscii( font )
            if got:
                notes.append( 'ascii ' + '+'.join( got ) )

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
        prog='glyphfix.py',
        description='enlarge the bullet (•) and add the missing ^ / ` glyphs',
    )
    p.add_argument( 'inputs', nargs='+', help='font files or directories (*.otf, *.ttf)' )
    p.add_argument( '-o', '--out-dir', help='output dir (default: <first-input-parent>/glyphfix)' )
    bullet = p.add_mutually_exclusive_group()
    bullet.add_argument( '--square', dest='square_half', nargs='?', const=100.0, type=float, default=None, metavar='N', help="enlarge the 'bullet' (•, U+2022) keeping its square shape, half-size N at em=1000 (default 100 -> 200 wide)" )
    bullet.add_argument( '--bullet', dest='bullet_radius', nargs='?', const=100.0, type=float, default=None, metavar='N', help="enlarge the 'bullet' (•, U+2022) as a round dot of radius N at em=1000 (default 100 -> diameter 200)" )
    p.add_argument( '--no-ascii', action='store_true', help='do not add the missing ^ / ` glyphs' )
    p.add_argument( '--rename', metavar='SUFFIX', help="append SUFFIX to family name for coexistence, e.g. ' Fixed'" )
    p.add_argument( '-n', '--dry-run', action='store_true', help='report actions without writing files' )
    args = p.parse_args( argv )
    # default action when neither bullet mode is given: square 100
    if args.square_half is None and args.bullet_radius is None:
        args.square_half = 100.0
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
                                     os.path.basename( parent.rstrip( '/' ) ) + '-glyphfix' )
    if not args.dry_run:
        os.makedirs( args.out_dir, exist_ok=True )

    ok = sum( process( f, args ) for f in fonts )
    print( f"\ndone: {ok}/{len( fonts )} font(s) -> {args.out_dir}" )


if __name__ == '__main__':
    # fontforge passes script args after the filename; argv[0] is this script
    main( sys.argv[ 1: ] )

# vim:tabstop=4:softtabstop=4:shiftwidth=4:expandtab:filetype=python:
