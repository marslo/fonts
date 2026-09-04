#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Synthesize Lekton 'Bold Italic' — italic letterforms from Lekton-Italic,
weight borrowed from Lekton-Bold.

Lekton ships Regular / Bold / Italic but no Bold Italic. This emboldens the
Italic face by the Regular->Bold stem delta ( auto-measured ), keeps the italic
slant and advance widths ( monospace-safe ), fixes the RIBBI name/style bits,
and writes Lekton-BoldItalic.ttf. build.sh --lekton then patches it into a NF
face automatically ( patchMono globs every non-NerdFont source under Lekton/ ).

Run with fontforge's python:  fontforge -script bolditalic.py [opts]
"""

import argparse
import math
import os
import sys

try:
    import fontforge
    import psMat
except ImportError:
    sys.exit( "error: run me via 'fontforge -script bolditalic.py ...' (needs the fontforge python module)" )

HERE = os.path.dirname( os.path.abspath( sys.argv[ 0 ] ) )
ROOT = os.path.dirname( HERE )
FAMILY = 'Lekton'
STEM_GLYPH = 0x6C                 # 'l' — a plain vertical stroke, good stem proxy
STEM_Y = 350                      # mid-height scanline, clear of the slab serifs


def defaultSrc( name ):
    """ Default source font path: next to the script, else in ../original. """
    for cand in ( os.path.join( HERE, name ), os.path.join( ROOT, 'original', name ) ):
        if os.path.isfile( cand ):
            return cand
    return os.path.join( ROOT, 'original', name )


def crossings( glyph, y ):
    """ x coordinates where the outline crosses the horizontal line at height y. """
    xs = []
    for contour in glyph.foreground:
        pts = [ ( p.x, p.y ) for p in contour ]
        n = len( pts )
        for i in range( n ):
            x1, y1 = pts[ i ]
            x2, y2 = pts[ ( i + 1 ) % n ]
            if ( y1 <= y <= y2 or y2 <= y <= y1 ) and y1 != y2:
                xs.append( x1 + ( x2 - x1 ) * ( y - y1 ) / ( y2 - y1 ) )
    xs.sort()
    return xs


def stemWidth( font, uni=STEM_GLYPH, y=STEM_Y ):
    """ Ink-run width of a vertical-stem glyph at height y ( scaled to em=1000 ). """
    xs = crossings( font[ uni ], y * ( font.em or 1000 ) / 1000.0 )
    if len( xs ) < 2:
        return None
    return ( xs[ -1 ] - xs[ 0 ] ) * 1000.0 / ( font.em or 1000 )


def autoAmount( italic, bold ):
    """ Embolden units = Bold stem - Italic stem ( the Regular->Bold weight delta ). """
    si = stemWidth( italic )
    sb = stemWidth( bold )
    if si is None or sb is None:
        sys.exit( "error: could not measure stem width from the reference faces" )
    return round( sb - si ), si, sb


def embolden( font, amount ):
    """
    Thicken every glyph by ~amount em units via an 8-way shift-union: overlay the
    outline shifted in 8 directions, then merge. Unlike changeWeight, this needs no
    stem detection, so it never collapses the italic's heavily-slanted stems ( i, k,
    X, % … ). Advance width is preserved ( monospace-safe ). Growth ~ 2 * ( amount / 2 ).
    """
    # integer offsets keep the shifted copies on the grid; snapping the union to
    # integers before removeOverlap avoids its near-zero-coordinate warnings
    # ( "Internal Error (overlap) ... Winding number did not return to 0" )
    d = round( amount / 2.0 )
    k = round( d / math.sqrt( 2.0 ) )
    offsets = [ ( d, 0 ), ( -d, 0 ), ( 0, d ), ( 0, -d ),
                ( k, k ), ( k, -k ), ( -k, k ), ( -k, -k ) ]
    for glyph in font.glyphs():
        if glyph.isWorthOutputting():
            width = glyph.width
            base = glyph.foreground.dup()
            for dx, dy in offsets:
                shifted = base.dup()
                shifted.transform( psMat.translate( dx, dy ) )
                glyph.foreground += shifted
            glyph.round()                # snap to integer grid before overlap removal
            glyph.removeOverlap()
            glyph.simplify()
            glyph.addExtrema()
            glyph.round()
            glyph.width = width          # the union widens the glyph; keep it monospace


def setBoldItalic( font ):
    """ Set family/style names and the bold+italic style bits ( keeps the italic angle ). """
    font.familyname = FAMILY
    font.fullname = FAMILY + ' Bold Italic'
    font.fontname = FAMILY + '-BoldItalic'
    font.weight = 'Bold'
    font.os2_weight = 700
    font.macstyle = 0x1 | 0x2         # head.macStyle: bit0 bold, bit1 italic
    font.os2_stylemap = 0x20 | 0x01   # OS/2 fsSelection: bold (0x20) + italic (0x01)
    lang = 'English (US)'
    for key, val in [ ( 'Family', FAMILY ),
                      ( 'SubFamily', 'Bold Italic' ),
                      ( 'Fullname', FAMILY + ' Bold Italic' ),
                      ( 'PostScriptName', FAMILY + '-BoldItalic' ),
                      ( 'Preferred Family', FAMILY ),
                      ( 'Preferred Styles', 'Bold Italic' ) ]:
        font.appendSFNTName( lang, key, val )


def parseArgs( argv ):
    p = argparse.ArgumentParser(
        prog='bolditalic.py',
        description='synthesize Lekton Bold Italic ( italic shapes + bold weight )',
    )
    italic = defaultSrc( 'Lekton-Italic.ttf' )
    p.add_argument( '--italic', default=italic,
                    help='source italic face ( shapes + slant )' )
    p.add_argument( '--bold', default=defaultSrc( 'Lekton-Bold.ttf' ),
                    help='reference bold face ( weight target )' )
    p.add_argument( '-o', '--out', default=os.path.join( os.path.dirname( italic ), 'Lekton-BoldItalic.ttf' ),
                    help='output path ( default: next to the italic source )' )
    p.add_argument( '-a', '--amount', type=int, default=None,
                    help='embolden units at em=1000 ( default: auto = bold stem - italic stem )' )
    p.add_argument( '-n', '--dry-run', action='store_true', help='report actions without writing' )
    return p.parse_args( argv )


def main( argv ):
    args = parseArgs( argv )
    for f in ( args.italic, args.bold ):
        test = os.path.isfile( f )
        test or sys.exit( f"error: missing source: {f}" )

    italic = fontforge.open( args.italic )
    bold = fontforge.open( args.bold )
    try:
        if args.amount is None:
            amount, si, sb = autoAmount( italic, bold )
            print( f"auto amount: bold stem {sb:.0f} - italic stem {si:.0f} = {amount}" )
        else:
            amount = args.amount
            print( f"amount: {amount} ( manual )" )

        if args.dry_run:
            print( f"[dry-run] embolden {os.path.basename( args.italic )} by {amount} -> {args.out}" )
            return

        # emboldening ( changeWeight / removeOverlap / addExtrema ) is unstable on
        # TrueType quadratic splines ( "Invalid 2nd order spline" ); do it in cubic,
        # then convert back to quadratic for the .ttf output
        italic.is_quadratic = 0
        embolden( italic, amount )
        italic.is_quadratic = 1
        # cubic ( PostScript ) and quadratic ( TrueType ) use opposite fill winding,
        # so fix every contour's direction after the conversion
        for glyph in italic.glyphs():
            if glyph.isWorthOutputting():
                glyph.correctDirection()
        setBoldItalic( italic )
        italic.generate( args.out )
        print( f"{os.path.basename( args.out ):28s} embolden={amount}  stem~{stemWidth( italic ):.0f} -> {args.out}" )
    finally:
        italic.close()
        bold.close()


if __name__ == '__main__':
    main( sys.argv[ 1: ] )

# vim:tabstop=4:softtabstop=4:shiftwidth=4:expandtab:filetype=python:
