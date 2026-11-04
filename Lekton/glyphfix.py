#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix / add Lekton's symbol glyphs ( everything that isn't the '0' — that lives in dotzero.py ):

  •  U+2022  bullet   enlarge Lekton's tiny bullet, keeping its square outline ( or a round dot )
  ^  U+005E  circumflex  add it when the face lacks one ( Lekton ships without ^ )
  `  U+0060  grave       add it when the face lacks one ( Lekton ships without ` )
  ⌥  U+2325  option key  add it when the face lacks one ( Lekton ships without ⌥ )
  ← ↑ → ↓  U+2190-2193  arrows  add them when the face lacks them ( Lekton ships without arrows )
  ⌘ ⇧ ⌃ ⎋ ⏎ ⌫ ⌦ ⇥ ⇤ ↵ ⇪ ⏏ ␣     macOS key symbols  add them when the face lacks them

The ^ and ` are synthesized from the face's own diacritic accents ( the top contour of â / à ), so they match Lekton's stroke weight and style. This also makes the font ligaturizable: Ligaturizer aborts on a font missing ^ ( asciicircum ).
The ⌥ is drawn in Menlo's proportions ( top-left bar → diagonal → bottom-right bar, plus a detached top-right bar ) from the face's own minus ( − ) stroke, span and italic slant; the italics ship no minus, so they use the hyphen stroke and SPAN x advance.
The arrows take the face's own minus / hyphen stroke ( shaft + chevron head ) and its › ( guilsinglright ) width : height as the head proportion; ← ↑ ↓ are → mirrored / rotated, on the math axis.
The key symbols are centerlines stroked with the same weight ( capped at KEY_MAX x box ) inside the ⌥ box; ⌦ / ⇤ mirror ⌫ / ⇥. Arrows + keys are built upright and slanted on italics.
The arrows + key-symbol block is identical in Blex/glyphfix.py.

Run with fontforge's python:  fontforge -script glyphfix.py [opts] <in.otf|dir>...
Keeps advance width (monospace-safe); originals are never modified.

USAGE
    fontforge -script glyphfix.py -o OUT Lekton/*.ttf                 # == --square 100 + fill ^ `
    fontforge -script glyphfix.py --square 100 -o OUT Lekton/*.otf    # square bullet, width 200
    fontforge -script glyphfix.py --bullet 100 -o OUT Lekton/*.otf    # round bullet, diameter 200
    fontforge -script glyphfix.py --no-ascii -o OUT Lekton/*.ttf      # only touch the bullet ( + ⌥ )
    fontforge -script glyphfix.py --no-option -o OUT Lekton/*.ttf     # skip the ⌥
    fontforge -script glyphfix.py --no-arrows -o OUT Lekton/*.ttf     # skip ← ↑ → ↓
    fontforge -script glyphfix.py --no-keys -o OUT Lekton/*.ttf       # skip the macOS key symbols
"""

import argparse
import math
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

# ⌥ geometry, normalized from Menlo's uni2325 ( width = minus span, height = cap height )
OPTION = {
    'top'   : 573 / 698.0,         # top edge, fraction of cap height
    'bottom': 109 / 698.0,         # bottom edge, fraction of cap height
    'bend'  : 0.34,                # top-left bar end / diagonal start, fraction of width
    'foot'  : 0.732,               # diagonal end / bottom-right bar start, fraction of width
    'bar'   : 0.594,               # detached top-right bar start, fraction of width
}
SPAN = 0.86                        # ⌥ width / advance when the face has no minus ( upright Lekton minus: 430 / 500 )


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


def polygon( points, quadratic ):
    """ Closed straight-edged contour through the given points. """
    c = fontforge.contour()
    c.is_quadratic = quadratic
    c.moveTo( *points[ 0 ] )
    for p in points[ 1: ]:
        c.lineTo( *p )
    c.closed = True
    return c


def minusFrame( font ):
    """
    ( x0, x1, stroke, advance ) of the reference span and weight.

    minus ( U+2212 ) when present; else hyphen ( U+002D ) for the stroke, with the span = SPAN x advance centered ( the italics ship no minus ).
    """
    if hasGlyph( font, 0x2212 ):
        g = font[ 0x2212 ]
        x0, y0, x1, y1 = g.boundingBox()
        return x0, x1, y1 - y0, g.width
    if not hasGlyph( font, 0x2D ):
        return None
    g = font[ 0x2D ]
    _, y0, _, y1 = g.boundingBox()
    half = SPAN * g.width / 2.0
    return g.width / 2.0 - half, g.width / 2.0 + half, y1 - y0, g.width


def optionContours( font ):
    """ The two ⌥ contours, upright and centered on the minus, or None when the face has no reference glyph. """
    frame = minusFrame( font )
    if frame is None:
        return None
    x0, x1, t, _ = frame
    if font.italicangle:
        # italic minus is already slanted / shifted: rebuild the upright span around its center
        cx, half = ( x0 + x1 ) / 2.0, ( x1 - x0 ) / 2.0
        x0, x1 = cx - half, cx + half
    w = x1 - x0
    cap = font.capHeight if font.capHeight > 0 else 0.7 * ( font.em or 1000 )
    top, bottom = OPTION[ 'top' ] * cap, OPTION[ 'bottom' ] * cap
    xa = x0 + OPTION[ 'bend' ] * w
    xb = x0 + OPTION[ 'foot' ] * w
    xr = x0 + OPTION[ 'bar' ] * w
    # outer diagonal edge ( xa, top ) -> ( xb, bottom + t ); inner edge = outer shifted left by d, so the perpendicular thickness equals the bar stroke
    dx, dy = xb - xa, ( top - bottom ) - t
    d = t * math.hypot( dx, dy ) / dy

    def outer( y ):
        return xa + ( top - y ) * dx / dy

    quadratic = font.is_quadratic
    zigzag = polygon( [ ( x0, top ), ( xa, top ), ( xb, bottom + t ), ( x1, bottom + t ),
                        ( x1, bottom ), ( outer( bottom ) - d, bottom ), ( outer( top - t ) - d, top - t ), ( x0, top - t ) ], quadratic )
    bar = polygon( [ ( xr, top ), ( x1, top ), ( x1, top - t ), ( xr, top - t ) ], quadratic )
    return zigzag, bar


def addOption( font ):
    """ Draw U+2325 ⌥ into a face that lacks one; return True when the glyph was added. """
    if hasGlyph( font, 0x2325 ):
        return False
    contours = optionContours( font )
    if contours is None:
        return False
    width = minusFrame( font )[ 3 ]
    glyph = font.createChar( 0x2325, 'uni2325' )
    layer = fontforge.layer()
    layer.is_quadratic = glyph.layers[ 'Fore' ].is_quadratic
    for c in contours:
        layer += c
    glyph.layers[ 'Fore' ] = layer
    if font.italicangle:
        # slant about the glyph's vertical center so it stays aligned with the italic glyphs
        _, y0, _, y1 = glyph.boundingBox()
        cy = ( y0 + y1 ) / 2.0
        glyph.transform( psMat.compose( psMat.translate( 0, -cy ),
                                        psMat.compose( psMat.skew( math.radians( -font.italicangle ) ), psMat.translate( 0, cy ) ) ) )
    glyph.width = width                       # monospace advance from the reference glyph
    glyph.round()
    glyph.correctDirection()
    return True



# ── macOS key symbols + arrows ( identical block in Blex/glyphfix.py and Lekton/glyphfix.py ) ──
# centerline paths stroked with the face's minus weight inside the ⌥ box ( minus span x OPTION top / bottom ); italics are built upright then slanted
KEYS = {
    0x2318: ( 'uni2318', 'command'    ),   # ⌘
    0x21E7: ( 'uni21E7', 'shift'      ),   # ⇧
    0x2303: ( 'uni2303', 'control'    ),   # ⌃
    0x238B: ( 'uni238B', 'escape'     ),   # ⎋
    0x23CE: ( 'uni23CE', 'returnkey'  ),   # ⏎
    0x232B: ( 'uni232B', 'deleteleft' ),   # ⌫
    0x2326: ( 'uni2326', 'deleteright' ),  # ⌦
    0x21E5: ( 'uni21E5', 'tabright'   ),   # ⇥
    0x21E4: ( 'uni21E4', 'tableft'    ),   # ⇤
    0x21B5: ( 'uni21B5', 'enter'      ),   # ↵
    0x21EA: ( 'uni21EA', 'capslock'   ),   # ⇪
    0x23CF: ( 'uni23CF', 'eject'      ),   # ⏏
    0x2423: ( 'uni2423', 'openbox'    ),   # ␣
}
# arrows: codepoint -> ( glyph name, rotation in degrees applied to → )
ARROWS = {
    0x2192: ( 'arrowright',  0 ),
    0x2191: ( 'arrowup',    90 ),
    0x2190: ( 'arrowleft', 180 ),
    0x2193: ( 'arrowdown', -90 ),
}
HEAD_SRC = 'guilsinglright'        # › — arrowhead aspect donor
HEAD_H = 0.56                      # arrowhead height, fraction of the arrow length
AXIS = 0.432                       # math axis ( minus center ) / cap height, for faces without a minus
KEY_MAX = 0.14                     # key-symbol stroke cap, fraction of the box's short side ( keeps bold ⌘ ⇥ ⌫ open )


def capHeight( font ):
    """ Cap height, else 0.7 em. """
    return font.capHeight if font.capHeight > 0 else 0.7 * ( font.em or 1000 )


def mathAxis( font ):
    """ Vertical center of the minus, else AXIS x cap height ( the hyphen sits lower than the math axis ). """
    if hasGlyph( font, 0x2212 ):
        _, y0, _, y1 = font[ 0x2212 ].boundingBox()
        return ( y0 + y1 ) / 2.0
    return AXIS * capHeight( font )


def keyFrame( font ):
    """ ( L, R, B, T, stroke, advance ) of the key-symbol box: upright minus span, ⌥ top / bottom, minus stroke capped at KEY_MAX x short side. """
    frame = minusFrame( font )
    if frame is None:
        return None
    x0, x1, t, width = frame
    if font.italicangle:
        cx, half = ( x0 + x1 ) / 2.0, ( x1 - x0 ) / 2.0
        x0, x1 = cx - half, cx + half
    cap = capHeight( font )
    bottom, top = OPTION[ 'bottom' ] * cap, OPTION[ 'top' ] * cap
    return x0, x1, bottom, top, min( t, KEY_MAX * min( x1 - x0, top - bottom ) ), width


def headAspect( font ):
    """ Width / height of the face's › ( the arrowhead proportion ), else 0.5. """
    if HEAD_SRC not in font:
        return 0.5
    x0, y0, x1, y1 = font[ HEAD_SRC ].boundingBox()
    return ( x1 - x0 ) / ( y1 - y0 ) if y1 > y0 else 0.5


def path( points, closed=False ):
    """ Straight centerline as plain data: ( start, [ ( 'l', point ) ... ], closed ). """
    return points[ 0 ], [ ( 'l', p ) for p in points[ 1: ] ], closed


def arc( cx, cy, r, a0, a1 ):
    """ Open arc of radius r from angle a0 to a1 ( degrees, ccw when a1 > a0 ) as plain cubic data, in <= 90° pieces. """
    n = max( 1, math.ceil( abs( a1 - a0 ) / 90.0 ) )
    step = math.radians( ( a1 - a0 ) / n )
    k = 4.0 / 3.0 * math.tan( step / 4.0 ) * r
    a = math.radians( a0 )
    start = ( cx + r * math.cos( a ), cy + r * math.sin( a ) )
    segs = []
    for _ in range( n ):
        b = a + step
        p0 = ( cx + r * math.cos( a ), cy + r * math.sin( a ) )
        p3 = ( cx + r * math.cos( b ), cy + r * math.sin( b ) )
        segs.append( ( 'c', ( p0[ 0 ] - k * math.sin( a ), p0[ 1 ] + k * math.cos( a ) ),
                            ( p3[ 0 ] + k * math.sin( b ), p3[ 1 ] - k * math.cos( b ) ), p3 ) )
        a = b
    return start, segs, False


def drawShapes( glyph, shapes, replace ):
    """ Draw plain-data shapes into the glyph through its pen ( no contour / layer objects: fontforge 2025.10.9 corrupts memory with those ). """
    pen = glyph.glyphPen( replace=replace )
    for start, segs, closed in shapes:
        pen.moveTo( start )
        for seg in segs:
            if 'l' == seg[ 0 ]:
                pen.lineTo( seg[ 1 ] )
            else:
                pen.curveTo( seg[ 1 ], seg[ 2 ], seg[ 3 ] )
        if closed:
            pen.closePath()
        else:
            pen.endPath()
    pen = None                                # releasing the pen commits the outline


def rect( x0, y0, x1, y1 ):
    """ Closed filled rectangle. """
    return path( [ ( x0, y0 ), ( x0, y1 ), ( x1, y1 ), ( x1, y0 ) ], closed=True )


def chevron( tipx, cy, hw, hh ):
    """ Open → head centerline: arms of half-height hh and depth hw meeting at ( tipx, cy ). """
    return path( [ ( tipx - hw, cy + hh ), ( tipx, cy ), ( tipx - hw, cy - hh ) ] )


def rightArrowParts( x0, x1, cy, t, aspect ):
    """ → centerlines spanning x0..x1 on the axis cy: shaft + chevron head, tip kept inside x1 by the miter. """
    tip = x1 - 0.71 * t
    hh = HEAD_H * ( x1 - x0 ) / 2.0
    return [ path( [ ( x0, cy ), ( tip - 0.5 * t, cy ) ] ), chevron( tip, cy, aspect * 2 * hh, hh ) ]


def keyParts( font, kind ):
    """ ( stroked centerlines, filled contours ) of one key symbol, upright, or None when the face has no reference glyph. """
    frame = keyFrame( font )
    if frame is None:
        return None
    L, R, B, T, t, _ = frame
    l, r, b, tp = L + t / 2.0, R - t / 2.0, B + t / 2.0, T - t / 2.0      # centerline box ( stroke stays inside L..R x B..T )
    w, h = r - l, tp - b
    cx, cy = ( l + r ) / 2.0, ( b + tp ) / 2.0
    s = min( w, h )
    aspect = headAspect( font )
    strokes, fills = [], []

    if 'command' == kind:                                # square with four 3/4 loops at the corners
        q = s / 6.0
        for y in ( cy - q, cy + q ):
            strokes.append( path( [ ( cx - 2 * q, y ), ( cx + 2 * q, y ) ] ) )
        for x in ( cx - q, cx + q ):
            strokes.append( path( [ ( x, cy - 2 * q ), ( x, cy + 2 * q ) ] ) )
        for sx, sy in ( ( 1, 1 ), ( -1, 1 ), ( -1, -1 ), ( 1, -1 ) ):
            inward = math.degrees( math.atan2( -sy, -sx ) )
            strokes.append( arc( cx + sx * 2 * q, cy + sy * 2 * q, q, inward + 35, inward + 325 ) )   # 10° past each tangent point: overlap, not touch
    elif kind in ( 'shift', 'capslock' ):                # outlined up arrow ( ⇪ adds a bar below )
        base = b + 0.30 * h if 'capslock' == kind else b
        ym = base + 0.50 * ( tp - base )
        sw = 0.22 * w
        strokes.append( path( [ ( cx, tp ), ( r, ym ), ( cx + sw, ym ), ( cx + sw, base ), ( cx - sw, base ), ( cx - sw, ym ), ( l, ym ) ], closed=True ) )
        if 'capslock' == kind:
            strokes.append( path( [ ( cx - sw, b ), ( cx + sw, b ) ] ) )
    elif 'control' == kind:                              # up arrowhead in the upper half
        strokes.append( path( [ ( l + 0.08 * w, cy + 0.05 * h ), ( cx, tp ), ( r - 0.08 * w, cy + 0.05 * h ) ] ) )
    elif 'escape' == kind:                               # circle broken at the upper-left + NW corner arrow
        rad = 0.42 * s
        strokes.append( arc( cx, cy, rad, 160, 470 ) )
        d = 0.62 * s
        tx, ty = cx - d * math.sqrt( 0.5 ), cy + d * math.sqrt( 0.5 )
        hl = 0.30 * s
        strokes.append( path( [ ( cx, cy ), ( tx + 0.35 * t, ty - 0.35 * t ) ] ) )
        strokes.append( path( [ ( tx + hl, ty ), ( tx, ty ), ( tx, ty - hl ) ] ) )
    elif kind in ( 'returnkey', 'enter' ):               # down-then-left hook with a left arrowhead
        yb = b + 0.30 * h if 'returnkey' == kind else cy - 0.10 * h
        top = tp if 'returnkey' == kind else cy + 0.40 * h
        hd = 0.26 * s
        strokes.append( path( [ ( r, top ), ( r, yb ), ( l + 0.5 * t, yb ) ] ) )
        strokes.append( path( [ ( l + hd, yb + hd ), ( l, yb ), ( l + hd, yb - hd ) ] ) )
    elif kind in ( 'deleteleft', 'deleteright' ):        # left-pointing key outline with an × ( ⌦ is the mirror )
        px = l + 0.32 * w
        strokes.append( path( [ ( l, cy ), ( px, tp ), ( r, tp ), ( r, b ), ( px, b ) ], closed=True ) )
        xc, hx = ( px + r ) / 2.0 + 0.02 * w, 0.16 * s
        strokes.append( path( [ ( xc - hx, cy - hx ), ( xc + hx, cy + hx ) ] ) )
        strokes.append( path( [ ( xc - hx, cy + hx ), ( xc + hx, cy - hx ) ] ) )
    elif kind in ( 'tabright', 'tableft' ):              # → to a bar ( ⇤ is the mirror )
        strokes.extend( rightArrowParts( l, r - 1.6 * t, cy, t, aspect ) )
        strokes.append( path( [ ( r, cy - 0.32 * h ), ( r, cy + 0.32 * h ) ] ) )
    elif 'eject' == kind:                                # filled triangle over a filled bar
        bar = max( 1.4 * t, 0.14 * ( T - B ) )
        gap = 0.12 * ( T - B )
        fills.append( rect( L, B, R, B + bar ) )
        fills.append( path( [ ( L, B + bar + gap ), ( ( L + R ) / 2.0, T ), ( R, B + bar + gap ) ], closed=True ) )
    elif 'openbox' == kind:                              # ␣ on the baseline
        top = 0.22 * capHeight( font )
        strokes.append( path( [ ( l, top ), ( l, t / 2.0 ), ( r, t / 2.0 ), ( r, top ) ] ) )
    else:
        return None
    return strokes, fills


SCRATCH = {}                       # cubic scratch font: stroke / union / transform happen there, never on the target face


def scratchGlyph():
    """ A fresh glyph of a lazily created cubic ( CFF-style ) scratch font. """
    if 'font' not in SCRATCH:
        SCRATCH[ 'font' ] = fontforge.font()
        SCRATCH[ 'font' ].is_quadratic = False
        SCRATCH[ 'next' ] = 0xF0000
    SCRATCH[ 'next' ] += 1
    return SCRATCH[ 'font' ].createChar( SCRATCH[ 'next' ], f"scratch{SCRATCH[ 'next' ]:X}" )


def placeGlyph( font, cp, name, strokes, fills, t, width, cy, matrix=None ):
    """ Stroke the centerlines with weight t, merge the fills, transform / slant in a cubic scratch glyph, then copy the outline into the face. """
    # pen-drawn into a cubic scratch glyph: layer.stroke() / layer += contour corrupt memory and stroking a quadratic ( ttf ) glyph segfaults ( fontforge 2025.10.9 )
    work = scratchGlyph()
    if strokes:
        drawShapes( work, strokes, True )
        work.stroke( 'circular', t, 'butt', 'miter' )
    if fills:
        drawShapes( work, fills, not strokes )
    if matrix is not None:
        work.transform( matrix )
    work.removeOverlap()
    if font.italicangle:
        work.transform( psMat.compose( psMat.translate( 0, -cy ),
                                       psMat.compose( psMat.skew( math.radians( -font.italicangle ) ), psMat.translate( 0, cy ) ) ) )
    work.correctDirection()
    outline = work.foreground
    outline.is_quadratic = font.is_quadratic
    glyph = font.createChar( cp, name )
    glyph.foreground = outline
    glyph.width = width                       # monospace advance from the reference glyph
    glyph.round()
    glyph.correctDirection()


def addKeys( font ):
    """ Add the missing macOS key symbols ( ⌘ ⇧ ⌃ ⎋ ⏎ ⌫ ⌦ ⇥ ⇤ ↵ ⇪ ⏏ ␣ ); return the characters added. """
    frame = keyFrame( font )
    if frame is None:
        return []
    L, R, B, T, t, width = frame
    cx, cy = ( L + R ) / 2.0, ( B + T ) / 2.0
    mirror = psMat.compose( psMat.translate( -cx, 0 ), psMat.compose( psMat.scale( -1, 1 ), psMat.translate( cx, 0 ) ) )
    added = []
    for cp, ( name, kind ) in KEYS.items():
        if hasGlyph( font, cp ):
            continue
        base = { 'deleteright': 'deleteleft', 'tableft': 'tabright' }.get( kind, kind )
        parts = keyParts( font, base )
        if parts is None:
            continue
        placeGlyph( font, cp, name, parts[ 0 ], parts[ 1 ], t, width, cy, mirror if base != kind else None )
        added.append( chr( cp ) )
    return added


def addArrows( font ):
    """ Add the missing ← ↑ → ↓: minus-weight shaft + a chevron head in the face's › proportion, on the math axis. """
    missing = { cp: v for cp, v in ARROWS.items() if not hasGlyph( font, cp ) }
    frame = minusFrame( font )
    if not missing or frame is None:
        return []
    x0, x1, t, width = frame
    if font.italicangle:
        mid, half = ( x0 + x1 ) / 2.0, ( x1 - x0 ) / 2.0
        x0, x1 = mid - half, mid + half
    cy = mathAxis( font )
    cx = width / 2.0
    added = []
    for cp, ( name, angle ) in sorted( missing.items() ):
        rot = psMat.compose( psMat.translate( -cx, -cy ),
                             psMat.compose( psMat.rotate( math.radians( angle ) ), psMat.translate( cx, cy ) ) ) if angle else None
        placeGlyph( font, cp, name, rightArrowParts( x0, x1, cy, t, headAspect( font ) ), [], t, width, cy, rot )
        added.append( chr( cp ) )
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

        # draw the missing ⌥ from the face's own minus / hyphen stroke
        if not args.no_option and addOption( font ):
            notes.append( 'option U+2325' )

        # draw the missing ← ↑ → ↓ with the face's own minus stroke and › proportion
        if not args.no_arrows:
            got = addArrows( font )
            if got:
                notes.append( 'arrows ' + ''.join( got ) )

        # draw the missing macOS key symbols with the face's own minus stroke
        if not args.no_keys:
            got = addKeys( font )
            if got:
                notes.append( 'keys ' + ''.join( got ) )

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
        description='enlarge the bullet (•) and add the missing ^ / ` / ⌥ / ← ↑ → ↓ / macOS key glyphs',
    )
    p.add_argument( 'inputs', nargs='+', help='font files or directories (*.otf, *.ttf)' )
    p.add_argument( '-o', '--out-dir', help='output dir (default: <first-input-parent>/glyphfix)' )
    bullet = p.add_mutually_exclusive_group()
    bullet.add_argument( '--square', dest='square_half', nargs='?', const=100.0, type=float, default=None, metavar='N', help="enlarge the 'bullet' (•, U+2022) keeping its square shape, half-size N at em=1000 (default 100 -> 200 wide)" )
    bullet.add_argument( '--bullet', dest='bullet_radius', nargs='?', const=100.0, type=float, default=None, metavar='N', help="enlarge the 'bullet' (•, U+2022) as a round dot of radius N at em=1000 (default 100 -> diameter 200)" )
    p.add_argument( '--no-ascii', action='store_true', help='do not add the missing ^ / ` glyphs' )
    p.add_argument( '--no-option', action='store_true', help='do not add the missing ⌥ ( U+2325 ) glyph' )
    p.add_argument( '--no-arrows', action='store_true', help='do not add the missing ← ↑ → ↓ ( U+2190-2193 ) glyphs' )
    p.add_argument( '--no-keys', action='store_true', help='do not add the missing macOS key symbols ( ⌘ ⇧ ⌃ ⎋ ⏎ ⌫ ⌦ ⇥ ⇤ ↵ ⇪ ⏏ ␣ )' )
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
