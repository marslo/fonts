#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Canonicalize a Nerd-Font-patched Blex face's name table + filename.

font-patcher names output by usWeightClass and folds the non-standard Book ( 350 )
onto Regular ( so Book collides with the real Regular and is lost ), and it can
leak ligaturize's abbreviated weights ( ExtLt / Medm / SmBld ) into the family of
some italics. This restamps names purely from usWeightClass + the italic bit, to
the exact convention font-patcher already uses for the faces it gets right:

  RIBBI ( 400 / 700 ): family 'BlexMonoLig Nerd Font Mono', style in nameID 2
  others  ( incl 350 ): family '<base> <Weight>', nameID 2 Regular/Italic,
                        typographic family/subfamily ( 16 / 17 ) carry the weight

Run one patched .otf into an output dir under its canonical filename:
    python3 blex-fixnames.py --in patched.otf --out-dir IBMPlexMonoLigNF
"""

import argparse
import os

from fontTools.ttLib import TTFont

# usWeightClass -> weight name ( 350 = the synthesized Book )
WEIGHTS = {
    100: 'Thin', 200: 'ExtraLight', 300: 'Light', 350: 'Book', 400: 'Regular',
    450: 'Text', 500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold',
    900: 'Black',
}
RIBBI = { 400, 700 }                 # weights that stay in the base family
BASE_FAM = 'BlexMonoLig Nerd Font Mono'
BASE_PS = 'BlexMonoLigNFM'
FNAME_BASE = BASE_FAM.replace( ' ', '' )   # BlexMonoLigNerdFontMono


def isItalic( font ):
    """ true when the face is italic ( macStyle bit or a non-zero italic angle ). """
    return bool( font[ 'head' ].macStyle & 0b10 ) or font[ 'post' ].italicAngle != 0


def names( weight, italic ):
    """ ( family1, sub2, full4, ps6, typo16, typo17, file_style ) for a weight. """
    if weight in RIBBI:
        core = '' if 400 == weight else 'Bold'
        sub  = ' '.join( x for x in ( core, 'Italic' if italic else '' ) if x ) or 'Regular'
        fam  = BASE_FAM
        full = f'{BASE_FAM} {sub}' if 'Regular' != sub else BASE_FAM
        ps   = f'{BASE_PS}-{sub.replace( " ", "" )}'
        return fam, sub, full, ps, '', '', sub.replace( ' ', '' )
    wname = WEIGHTS[ weight ]
    style = f'{wname} Italic' if italic else wname               # nameID 17
    fam   = f'{BASE_FAM} {wname}'                                # weight in family
    return ( fam,
             'Italic' if italic else 'Regular',
             f'{fam} Italic' if italic else fam,
             f'{BASE_PS}-{wname}{"Italic" if italic else ""}',
             BASE_FAM,
             style,
             f'{wname}{"Italic" if italic else ""}' )


def setName( font, nid, value ):
    """ set ( non-empty ) or drop ( empty ) a name record on windows + mac. """
    if value:
        font[ 'name' ].setName( value, nid, 3, 1, 0x409 )
        font[ 'name' ].setName( value, nid, 1, 0, 0 )
    else:
        font[ 'name' ].removeNames( nameID=nid )


def fix( src, out_dir ):
    font   = TTFont( src )
    weight = font[ 'OS/2' ].usWeightClass
    if weight not in WEIGHTS:
        raise SystemExit( f'error: unmapped usWeightClass {weight} in {src}' )
    fam, sub, full, ps, typo16, typo17, file_style = names( weight, isItalic( font ) )
    for nid, value in ( ( 1, fam ), ( 2, sub ), ( 4, full ), ( 6, ps ), ( 16, typo16 ), ( 17, typo17 ) ):
        setName( font, nid, value )
    out = os.path.join( out_dir, f'{FNAME_BASE}-{file_style}.otf' )
    os.makedirs( out_dir, exist_ok=True )
    font.save( out )
    font.close()
    print( f'{os.path.basename( src )} -> {os.path.basename( out )} ( {weight} )' )


def main():
    parser = argparse.ArgumentParser( description='canonicalize a patched Blex face name table + filename' )
    parser.add_argument( '--in',      dest='src', required=True, help='the patched .otf to canonicalize' )
    parser.add_argument( '--out-dir', required=True, help='destination directory' )
    args = parser.parse_args()
    fix( args.src, args.out_dir )


if __name__ == '__main__':
    main()

# vim:tabstop=4:softtabstop=4:shiftwidth=4:expandtab:filetype=python:
