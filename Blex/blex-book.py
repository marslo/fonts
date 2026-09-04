#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Instance the IBM Plex Mono variable fonts into a Book ( ~350 ) weight.

For each of the roman / italic variable sources: instance at wght=<weight> with fontTools ( no glyph editing -- the font's own deltas ),
stamp the weight name records to mirror IBM Plex's own layout, then convert glyf -> CFF/OpenType via FontForge ( quadratic->cubic is exact ).
Output lands as <out>/IBMPlexMono-<name>{,Italic}.otf, monospaced.

Called by blex-book.sh ( which handles CLI / deps / fetching the sources ), but
runnable standalone ( invoke via the interpreter -- not marked executable ):
    python3 blex-book.py --roman VF-Roman.ttf --italic VF-Italic.ttf --out ./IBMPlexMono
i.e.:
    python3 blex-book.py --roman IBMPlexMonoVar/IBMPlexMonoVar-Roman.ttf --italic IBMPlexMonoVar/IBMPlexMonoVar-Italic.ttf --out IBMPlexMono
"""

import argparse
import os
import subprocess
import tempfile

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FAM = 'IBM Plex Mono'
PSFAM = 'IBMPlexMono'

# fontforge one-liner ( runs under fontforge's own python ): glyf -> CFF/OpenType
FF_CONVERT = (
    'import fontforge, sys; '
    'f = fontforge.open( sys.argv[1] ); '
    "f.generate( sys.argv[2], flags=( 'opentype', ) ); "
    'f.close()'
)


def setName( font, nid, value ):
    """ set a name record on both the windows and mac platforms. """
    font[ 'name' ].setName( value, nid, 3, 1, 0x409 )   # windows / unicode
    font[ 'name' ].setName( value, nid, 1, 0, 0 )       # mac / roman


def instance( src, weight, name, italic, out_ttf ):
    """ instance <src> at wght=<weight>, stamp weight names, save a glyf .ttf. """
    style = f'{name} Italic' if italic else name            # nameID 17
    ps    = f"{PSFAM}-{name}{'Italic' if italic else ''}"
    font  = TTFont( src )
    instantiateVariableFont( font, { 'wght': weight }, inplace=True )
    font[ 'OS/2' ].usWeightClass = weight
    setName( font, 1,  f'{FAM} {name}' )                    # family ( RIBBI-grouped )
    setName( font, 2,  'Italic' if italic else 'Regular' )  # subfamily
    setName( font, 3,  f'2.3;IBM ;{ps}' )                   # unique id
    setName( font, 4,  f'{FAM} {style}' )                   # full name
    setName( font, 6,  ps )                                 # postscript name
    setName( font, 16, FAM )                                # typographic family
    setName( font, 17, style )                              # typographic subfamily
    font.save( out_ttf )


def toOtf( glyf_path, otf_path ):
    """ convert a glyf font to CFF/OpenType via FontForge. """
    subprocess.run( [ 'fontforge', '-lang=py', '-c', FF_CONVERT, glyf_path, otf_path ],
                    check=True, stderr=subprocess.DEVNULL )


def build( src, weight, name, italic, out_dir, work ):
    """ instance <src> then emit IBMPlexMono-<name>[Italic].otf into out_dir. """
    ps  = f"{PSFAM}-{name}{'Italic' if italic else ''}"
    tmp = os.path.join( work, f'{ps}.ttf' )
    otf = os.path.join( out_dir, f'{ps}.otf' )
    instance( src, weight, name, italic, tmp )
    toOtf( tmp, otf )
    print( f'generated {otf} ( usWeightClass {weight} )' )


def main():
    parser = argparse.ArgumentParser( description='instance IBM Plex Mono variable fonts into a Book ( ~350 ) weight' )
    parser.add_argument( '--roman',  required=True, help='variable roman source ( .ttf )' )
    parser.add_argument( '--italic', required=True, help='variable italic source ( .ttf )' )
    parser.add_argument( '--out',    required=True, help='output directory for the .otf faces' )
    parser.add_argument( '--weight', type=int, default=350, help='wght instance / usWeightClass ( default 350 )' )
    parser.add_argument( '--name',   default='Book', help='weight name ( default Book )' )
    args = parser.parse_args()

    os.makedirs( args.out, exist_ok=True )
    with tempfile.TemporaryDirectory( prefix='blex-book.' ) as work:
        build( args.roman,  args.weight, args.name, False, args.out, work )
        build( args.italic, args.weight, args.name, True,  args.out, work )


if __name__ == '__main__':
    main()

# vim:tabstop=4:softtabstop=4:shiftwidth=4:expandtab:filetype=python:
