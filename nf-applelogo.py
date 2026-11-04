#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Alias U+F8FF ( the Apple logo PUA code point ) to the Nerd Font apple icon ( nf-fa-apple, U+F179 ) in patched fonts.

cmap-only: U+F8FF points at the existing nf-fa-apple glyph — no outline is added or copied.
Skips a font that already maps U+F8FF, or that has no U+F179 ( i.e. not Nerd-Font patched ).

USAGE
    python3 nf-applelogo.py Lekton/LektonLigNF                     # every *.otf / *.ttf in the dir, in place
    python3 nf-applelogo.py --newer MARKER Monaco/MonacoNF/otf     # only files modified after MARKER ( build.sh )
    python3 nf-applelogo.py -n path/to/*NerdFont*.ttf              # report only
"""

import argparse
import logging
import os
import sys

from fontTools.ttLib import TTFont

logging.getLogger( 'fontTools' ).setLevel( logging.ERROR )   # silence "'created' timestamp seems very low" on font-patcher output

FONT_EXTS = ( '.otf', '.ttf' )
APPLE_PUA = 0xF8FF                 # Apple logo ( private use area; Apple fonts only )
NF_APPLE = 0xF179                  # nf-fa-apple


def collectInputs( paths, newer=None ):
    """ Expand files and directories into a flat list of font paths, optionally only those modified after `newer` ( mtime ). """
    out = []
    for p in paths:
        if os.path.isdir( p ):
            out += [ os.path.join( p, n ) for n in sorted( os.listdir( p ) ) if n.lower().endswith( FONT_EXTS ) ]
        elif p.lower().endswith( FONT_EXTS ) and os.path.isfile( p ):
            out.append( p )
    if newer is not None:
        out = [ f for f in out if os.path.getmtime( f ) > newer ]
    return out


def alias( path, dry_run ):
    """ Map U+F8FF to the glyph of U+F179 in every unicode cmap subtable; return a short status. """
    font = TTFont( path, lazy=False )
    try:
        cmap = font.getBestCmap() or {}
        if APPLE_PUA in cmap:
            return 'skip ( has U+F8FF )'
        glyph = cmap.get( NF_APPLE )
        if glyph is None:
            return 'skip ( no U+F179 )'
        if dry_run:
            return f'[dry-run] U+F8FF -> {glyph}'
        for table in font[ 'cmap' ].tables:
            if table.isUnicode():
                table.cmap[ APPLE_PUA ] = glyph
        tmp = path + '.tmp'
        font.save( tmp )
    finally:
        font.close()
    os.replace( tmp, path )
    return f'U+F8FF -> {glyph}'


def parseArgs( argv ):
    p = argparse.ArgumentParser( prog='nf-applelogo.py', description='alias U+F8FF ( Apple logo ) to nf-fa-apple ( U+F179 ) in Nerd-Font-patched fonts' )
    p.add_argument( 'inputs', nargs='+', help='font files or directories (*.otf, *.ttf)' )
    p.add_argument( '--newer', metavar='FILE', help='only fonts modified after FILE ( a marker touched before font-patcher ran )' )
    p.add_argument( '-n', '--dry-run', action='store_true', help='report actions without writing files' )
    return p.parse_args( argv )


def main( argv ):
    args = parseArgs( argv )
    newer = os.path.getmtime( args.newer ) if args.newer else None
    fonts = collectInputs( args.inputs, newer )
    for f in fonts:
        print( f'   {os.path.basename( f ):50s} {alias( f, args.dry_run )}' )
    return 0


if __name__ == '__main__':
    sys.exit( main( sys.argv[ 1: ] ) )

# vim:tabstop=4:softtabstop=4:shiftwidth=4:expandtab:filetype=python:
