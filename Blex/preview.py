#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Render assets/ligatures.svg — a showcase of the Fira Code ligatures in the
ligaturized IBM Plex Mono ( IBMPlexMonoLig ), straight from the font.

Ligatures are 'calt' substitutions, not plain code points, so each sample is
shaped with HarfBuzz ( hb-shape ) first, then the resulting glyphs are drawn as
outlines — GitHub loads README SVG via <img> and never applies @font-face.

Run with fontforge's python:  fontforge -script preview.py [-o out.svg]
"""

import argparse
import os
import subprocess
import sys

try:
    import fontforge
except ImportError:
    sys.exit( "error: run me via 'fontforge -script preview.py ...' (needs the fontforge module)" )

HERE = os.path.dirname( os.path.abspath( sys.argv[ 0 ] ) )
FONT = os.path.join( HERE, 'IBMPlexMonoLig', 'IBMPlexMonoLig-Regular.ttf' )
TITLE = 'IBMPlexMonoLig'
SUBTITLE = 'IBM Plex Mono + Fira Code ligatures ( rendered via calt )'
SAMPLES = [ '-> => <- <-> ->> =>>',
            '== === != !== <= >=',
            ':: := ::: ... |> <|',
            '/* */ // /// <!-- -->',
            'www ### ;;; && || ??' ]

# layout ( px )
PAD = 26
SAMPLE_PX = 30
ROW_H = 54
HEAD_H = 70
WIDTH = 720

STYLE = ( '<style>'
          '.pbg{fill:#21262d;stroke:#ffffff14}'
          '.cap{fill:#e6edf3;font-size:16px;font-weight:700}'
          '.cap2{fill:#8b98a5;font-size:12.5px}'
          '.ink{fill:#cbb994}'
          '</style>' )


def quadPath( contour ):
    """ TrueType ( quadratic ) contour -> SVG path 'd' in font units ( y up ). """
    pts = [ ( p.x, p.y, p.on_curve ) for p in contour ]
    if not pts:
        return ''
    exp = []
    n = len( pts )
    for i in range( n ):
        cur = pts[ i ]
        nxt = pts[ ( i + 1 ) % n ]
        exp.append( cur )
        if not cur[ 2 ] and not nxt[ 2 ]:
            exp.append( ( ( cur[ 0 ] + nxt[ 0 ] ) / 2.0, ( cur[ 1 ] + nxt[ 1 ] ) / 2.0, True ) )
    starts = [ i for i, p in enumerate( exp ) if p[ 2 ] ]
    if not starts:
        return ''
    s = starts[ 0 ]
    seq = exp[ s: ] + exp[ :s ]
    seq.append( seq[ 0 ] )
    d = f"M{seq[0][0]:.0f} {seq[0][1]:.0f}"
    i = 1
    while i < len( seq ):
        p = seq[ i ]
        if p[ 2 ]:
            d += f"L{p[0]:.0f} {p[1]:.0f}"
            i += 1
        else:
            on = seq[ i + 1 ]
            d += f"Q{p[0]:.0f} {p[1]:.0f} {on[0]:.0f} {on[1]:.0f}"
            i += 2
    return d + 'Z'


def shapeGlyphs( text ):
    """ hb-shape a string against FONT, returning the shaped glyph names ( ligatures applied ). """
    # '--' terminates options so a sample starting with '-' is not read as a flag
    out = subprocess.check_output( [ 'hb-shape', '--no-positions', FONT, '--', text ],
                                   text=True, stderr=subprocess.DEVNULL ).strip()
    out = out.strip( '[]' )
    return [ tok.split( '=' )[ 0 ] for tok in out.split( '|' ) ] if out else []


def renderRow( font, names, x, baseline ):
    """ Render shaped glyph names ( by name ) as outlines; y-flipped <g class="ink">. """
    em = font.em or 1000
    k = SAMPLE_PX / float( em )
    penx = 0
    parts = []
    for nm in names:
        if nm not in font:
            penx += em // 2
            continue
        glyph = font[ nm ]
        d = ''.join( quadPath( c ) for c in glyph.foreground )
        if d:
            parts.append( f'<path transform="translate({penx} 0)" d="{d}"/>' )
        penx += glyph.width
    return f'<g class="ink" transform="translate({x:.0f} {baseline:.0f}) scale({k:.4f} {-k:.4f})">{"".join( parts )}</g>'


def build():
    total_h = HEAD_H + len( SAMPLES ) * ROW_H + PAD - 10
    font = fontforge.open( FONT )
    try:
        out = [ ( f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {total_h}" '
                  f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">' ), STYLE,
                f'<rect class="pbg" x="0.5" y="0.5" width="{WIDTH - 1}" height="{total_h - 1}" rx="14"/>',
                f'<text class="cap" x="{PAD}" y="34">{TITLE}</text>',
                f'<text class="cap2" x="{PAD}" y="54">{SUBTITLE}</text>' ]
        for i, sample in enumerate( SAMPLES ):
            baseline = HEAD_H + i * ROW_H + ROW_H * 0.62
            out.append( renderRow( font, shapeGlyphs( sample ), PAD, baseline ) )
        out.append( '</svg>' )
        return '\n'.join( out )
    finally:
        font.close()


def main( argv ):
    p = argparse.ArgumentParser( prog='preview.py', description='render assets/ligatures.svg from IBMPlexMonoLig' )
    p.add_argument( '-o', '--out', default=os.path.join( HERE, 'assets', 'ligatures.svg' ), help='output svg path' )
    args = p.parse_args( argv )

    os.path.isfile( FONT ) or sys.exit( f"error: ligature font not found: {FONT} ( run ligaturize.sh first )" )
    try:
        subprocess.check_output( [ 'hb-shape', '--version' ], stderr=subprocess.DEVNULL )
    except ( OSError, subprocess.CalledProcessError ):
        sys.exit( 'error: hb-shape not found ( brew install harfbuzz )' )

    os.makedirs( os.path.dirname( args.out ), exist_ok=True )
    with open( args.out, 'w' ) as f:
        f.write( build() )
    print( f"wrote {args.out}" )


if __name__ == '__main__':
    main( sys.argv[ 1: ] )

# vim:tabstop=4:softtabstop=4:shiftwidth=4:expandtab:filetype=python:
