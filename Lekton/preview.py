#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Render a comparison matrix ( preview.svg ) + a 0-vs-o graphic ( zero.svg )
straight from the repo's own fonts, so the README graphics stay in sync.

Two presets, auto-detected from the directory layout ( override with --preset ):
  font-lekton    3 columns: original / optimized / NerdFonts  ( repo has those dirs )
  fonts-lekton   2 columns: original / nerd font              ( fonts next to the script )

Sample text is emitted as glyph outlines ( <path> ), not <text> in the font,
because GitHub loads README SVG via <img> and never applies @font-face.

Run with fontforge's python:  fontforge -script preview.py [--preset NAME] [-d out-dir]
"""

import argparse
import os
import sys

try:
    import fontforge
except ImportError:
    sys.exit( "error: run me via 'fontforge -script preview.py ...' (needs the fontforge module)" )

HERE = os.path.dirname( os.path.abspath( sys.argv[ 0 ] ) )
ROOT = os.path.dirname( HERE )
SAMPLE = 'Il1 ilL 0Oo •'      # programming confusables + the enlarged bullet
ROWS = [ ( 'Regular', 'Regular' ), ( 'Italic', 'Italic' ),
         ( 'Bold', 'Bold' ), ( 'Bold Italic', 'BoldItalic' ) ]


def esc( s ):
    """ escape XML text content ( &, <, > ). """
    return str( s ).replace( '&', '&amp;' ).replace( '<', '&lt;' ).replace( '>', '&gt;' )

# each preset: base dir · columns ( header, path template relative to base, {} = style
# token ) · the two faces for the 0-vs-o graphic · caption
PRESETS = {
    'font-lekton': {
        'base': ROOT,
        'title': 'Lekton, optimized',
        'subtitle': 'no Bold Italic · 0 looks like o · tiny bullet — the optimized & Nerd Font builds fix all three',
        'columns': [ ( 'original', 'original/Lekton-{}.ttf' ),
                     ( 'optimized', 'optimized/Lekton-{}.ttf' ),
                     ( 'NerdFonts', 'NerdFonts/LektonNerdFontMono-{}.ttf' ) ],
        'zero': ( 'original/Lekton-Regular.ttf', 'optimized/Lekton-Regular.ttf' ),
    },
    'fonts-lekton': {
        'base': HERE,
        'title': 'Lekton, patched',
        'subtitle': 'no Bold Italic · 0 ≈ o · tiny bullet — all fixed in the Nerd Font build',
        'columns': [ ( 'original', 'Lekton-{}.ttf' ),
                     ( 'nerd font', 'LektonNerdFontMono-{}.ttf' ) ],
        'zero': ( 'Lekton-Regular.ttf', 'LektonNerdFontMono-Regular.ttf' ),
        'omit': { ( 'original', 'BoldItalic' ) },   # vendor Lekton ships no Bold Italic
    },
}


def detectPreset():
    """ 'font-lekton' when an optimized/ dir sits under the repo root, else 'fonts-lekton'. """
    return 'font-lekton' if os.path.isdir( os.path.join( ROOT, 'optimized' ) ) else 'fonts-lekton'


# ── layout ( px ) ──
OUT_PAD = 20
BOX_PAD = 18
CAPTION_H = 46
HEAD_H = 40
ROW_H = 64
LABEL_W = 118
COL_W = 250
CELL_PAD = 18
SAMPLE_PX = 34


def quadPath( contour ):
    """ TrueType ( quadratic ) contour -> SVG path 'd' in font units ( y up ). """
    pts = [ ( p.x, p.y, p.on_curve ) for p in contour ]
    if not pts:
        return ''
    # insert implied on-curve midpoints between consecutive off-curve points
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


def sampleWidth( font, text ):
    """ Advance width of the sample in font units. """
    em = font.em or 1000
    return sum( font[ ord( c ) ].width if ord( c ) in font else em // 2 for c in text )


def renderGlyphs( font, text, x, baseline, px ):
    """ Lay out text as outlines at the given cap size; y-flipped <g class="ink">. """
    em = font.em or 1000
    k = px / float( em )
    penx = 0
    parts = []
    for ch in text:
        code = ord( ch )
        if code in font:
            glyph = font[ code ]
            d = ''.join( quadPath( c ) for c in glyph.foreground )
            if d:
                parts.append( f'<path transform="translate({penx} 0)" d="{d}"/>' )
            penx += glyph.width
        else:
            penx += em // 2
    return f'<g class="ink" transform="translate({x:.0f} {baseline:.0f}) scale({k:.4f} {-k:.4f})">{"".join( parts )}</g>'


def sampleGroup( font, text, x, baseline, avail ):
    """ Render text as outlines, shrunk to fit avail px ( cap SAMPLE_PX ). """
    em = font.em or 1000
    adv = sampleWidth( font, text ) or em
    px = min( float( SAMPLE_PX ), avail * em / adv )
    return renderGlyphs( font, text, x, baseline, px )


STYLE = ( '<style>'
          '.pbg{fill:#21262d;stroke:#ffffff14}'
          '.cap{fill:#e6edf3;font-size:16px;font-weight:700}'
          '.cap2{fill:#8b98a5;font-size:12.5px}'
          '.col{fill:#e6edf3;font-size:13.5px;font-weight:700}'
          '.lbl{fill:#8b98a5;font-size:13.5px}'
          '.ink{fill:#cbb994}'
          '.dash{fill:#5b636c;font-size:20px}'
          '.rule{stroke:#ffffff12}'
          '.vrule{stroke:#ffffff0d}'
          '.tag{fill:#e6edf3;font-size:12px;font-weight:700}'
          '.sub{fill:#8b98a5;font-size:10.5px}'
          '</style>' )


def build( preset ):
    """ The comparison matrix for the given preset ( 2 or 3 columns ). """
    cols = preset[ 'columns' ]
    ncols = len( cols )
    width = 2 * OUT_PAD + 2 * BOX_PAD + LABEL_W + ncols * COL_W
    inner_w = width - 2 * OUT_PAD
    panel_top = OUT_PAD + CAPTION_H
    table_h = HEAD_H + len( ROWS ) * ROW_H
    panel_h = table_h + 2 * BOX_PAD
    total_h = panel_top + panel_h + OUT_PAD
    tx = OUT_PAD + BOX_PAD                     # table left ( inside panel )
    ty = panel_top + BOX_PAD                   # table top

    def col_x( i ):
        return tx + LABEL_W + i * COL_W

    out = [ ( f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_h:.0f}" '
              f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">' ), STYLE ]
    out.append( f'<text class="cap" x="{OUT_PAD}" y="{OUT_PAD + 16}">{esc( preset[ "title" ] )}</text>' )
    out.append( f'<text class="cap2" x="{OUT_PAD}" y="{OUT_PAD + 36}">{esc( preset[ "subtitle" ] )}</text>' )
    out.append( f'<rect class="pbg" x="{OUT_PAD}" y="{panel_top}" width="{inner_w}" height="{panel_h}" rx="14"/>' )

    for i, ( header, _ ) in enumerate( cols ):
        cx = col_x( i ) + COL_W / 2
        out.append( f'<text class="col" x="{cx:.0f}" y="{ty + 24:.0f}" text-anchor="middle">{esc( header )}</text>' )
    for i in range( 1, ncols ):
        vx = col_x( i )
        out.append( f'<line class="vrule" x1="{vx:.0f}" y1="{ty + HEAD_H - 8}" x2="{vx:.0f}" y2="{ty + table_h}"/>' )

    for r, ( label, token ) in enumerate( ROWS ):
        rtop = ty + HEAD_H + r * ROW_H
        out.append( f'<line class="rule" x1="{tx}" y1="{rtop}" x2="{tx + LABEL_W + ncols * COL_W:.0f}" y2="{rtop}"/>' )
        out.append( f'<text class="lbl" x="{tx}" y="{rtop + ROW_H / 2 + 4:.0f}">{esc( label )}</text>' )
        omit = preset.get( 'omit', () )
        for i, ( header, tmpl ) in enumerate( cols ):
            path = os.path.join( preset[ 'base' ], tmpl.format( token ) )
            if ( header, token ) not in omit and os.path.isfile( path ):
                font = fontforge.open( path )
                try:
                    out.append( sampleGroup( font, SAMPLE, col_x( i ) + CELL_PAD,
                                             rtop + ROW_H * 0.64, COL_W - 2 * CELL_PAD ) )
                finally:
                    font.close()
            else:
                out.append( f'<text class="dash" x="{col_x( i ) + COL_W / 2:.0f}" '
                            f'y="{rtop + ROW_H / 2 + 8:.0f}" text-anchor="middle">–</text>' )

    out.append( '</svg>' )
    return '\n'.join( out )


def buildZero( preset ):
    """ Small before/after: original 0 ( ≈ o ) vs patched dotted 0 ( ≠ o ). """
    w, h, pad, px = 320, 104, 16, 52
    half = w / 2.0
    before, after = preset[ 'zero' ]
    faces = [ ( before, 'before', '0 looks like o' ), ( after, 'after', 'dotted 0' ) ]
    out = [ ( f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
              f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">' ), STYLE,
            f'<rect class="pbg" x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12"/>',
            f'<line class="vrule" x1="{half:.0f}" y1="12" x2="{half:.0f}" y2="{h - 12}"/>' ]
    for i, ( rel, tag, sub ) in enumerate( faces ):
        gx = i * half + pad
        out.append( f'<text class="tag" x="{gx:.0f}" y="26">{esc( tag )}</text>' )
        out.append( f'<text class="sub" x="{gx + 44:.0f}" y="26">{esc( sub )}</text>' )
        font = fontforge.open( os.path.join( preset[ 'base' ], rel ) )
        try:
            out.append( renderGlyphs( font, '0o', gx + 12, h - 22, px ) )
        finally:
            font.close()
    out.append( '</svg>' )
    return '\n'.join( out )


def main( argv ):
    p = argparse.ArgumentParser( prog='preview.py', description='render preview.svg + zero.svg from the repo fonts' )
    p.add_argument( '--preset', choices=sorted( PRESETS ), default=None, help='column layout ( default: auto-detect )' )
    p.add_argument( '-d', '--out-dir', default=None, help='output dir ( default: <base>/assets )' )
    args = p.parse_args( argv )

    name = args.preset or detectPreset()
    preset = PRESETS[ name ]
    out_dir = args.out_dir or os.path.join( preset[ 'base' ], 'assets' )
    os.makedirs( out_dir, exist_ok=True )
    for fname, fn in [ ( 'preview.svg', build ), ( 'zero.svg', buildZero ) ]:
        dst = os.path.join( out_dir, fname )
        with open( dst, 'w' ) as f:
            f.write( fn( preset ) )
        print( f"[{name}] wrote {dst}" )


if __name__ == '__main__':
    main( sys.argv[ 1: ] )

# vim:tabstop=4:softtabstop=4:shiftwidth=4:expandtab:filetype=python:
