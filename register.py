#!/usr/bin/env python3
"""
Flush the macOS CoreText font cache and (re)register fonts at .user scope.

Generic, standalone equivalent of fixnf.py's --install step -- works for any font, not just Titillium.
Point --input at a single font file or a directory of fonts (already placed wherever you want them, e.g. ~/Library/Fonts); it registers each face AT ITS GIVEN PATH (no copying), after dropping CoreText's parsed cache and restarting fontd so macOS / CoreText / browsers pick the fonts up at once.

Steps (mirror fixnf.py install()):
  1. resolve --input to a list of font paths (a file, or all fonts in a dir)
  2. rm -rf ~/Library/Caches/com.apple.FontRegistry ; killall fontd
  3. per font: CTFontManagerUnregisterFontsForURL(.user) then CTFontManagerRegisterFontsForURL(.user) -- unregister first avoids err -50

Idempotent and safe to re-run.

Usage:
    python3 register.py --input <file|dir> [--dry-run]
"""

import glob
import os
import subprocess
import sys
import tempfile

FONT_EXTS = {".otf", ".ttf", ".ttc", ".otc"}
USAGE = "usage: register-fonts.py --input <file|dir|glob> [--input ...] [--dry-run]"


def fonts_in(d):
    return sorted(
        os.path.join(d, n) for n in os.listdir(d)
        if os.path.splitext(n)[1].lower() in FONT_EXTS
        and os.path.isfile(os.path.join(d, n))
    )


def resolve_input(path):
    p = os.path.abspath(os.path.expanduser(path))
    if os.path.isdir(p):
        fonts = fonts_in(p)
        if not fonts:
            sys.exit(f"error: no fonts (.otf/.ttf/.ttc/.otc) found in {p}")
        return fonts
    if os.path.isfile(p):
        return [p]
    # not a plain file/dir -- treat as an ls-style glob (e.g. ~/Library/Fonts/Foo*.otf)
    if glob.has_magic(p):
        matches = sorted(
            m for m in glob.glob(p)
            if os.path.isfile(m)
            and os.path.splitext(m)[1].lower() in FONT_EXTS
        )
        if not matches:
            sys.exit(f"error: no fonts matched glob: {p}")
        return matches
    sys.exit(f"error: --input path does not exist: {p}")


def swift_str(p):
    return p.replace("\\", "\\\\").replace('"', '\\"')


def flush_and_register(paths, dry=False):
    home = os.path.expanduser("~")
    cache = os.path.join(home, "Library", "Caches", "com.apple.FontRegistry")

    if dry:
        print("[dry-run] planned actions:")
        for p in paths:
            print(f"  font: {p}")
        print(f"  flush cache: rm -rf {cache}")
        print("  restart daemon: killall fontd")
        for p in paths:
            print(f"  register (.user): {os.path.basename(p)}")
        print("  reminder: fully quit and reopen the browser/app afterwards")
        return

    subprocess.run( ["rm", "-rf", cache], check=False )
    subprocess.run( ["killall", "fontd"], stderr=subprocess.DEVNULL, check=False )

    arr = ",\n".join(f'  "{swift_str(p)}"' for p in paths)
    swift = (
        "import CoreText\nimport Foundation\n"
        f"let paths = [\n{arr}\n]\n"
        "for p in paths {\n"
        "  let u = URL(fileURLWithPath: p) as CFURL\n"
        "  CTFontManagerUnregisterFontsForURL(u, .user, nil)\n"
        "  var e: Unmanaged<CFError>?\n"
        "  let ok = CTFontManagerRegisterFontsForURL(u, .user, &e)\n"
        "  print(\"register \\((p as NSString).lastPathComponent): \\(ok)\")\n"
        "}\n"
    )
    with tempfile.NamedTemporaryFile( "w", suffix=".swift", delete=False ) as tf:
        tf.write(swift)
        tf_name = tf.name
    print( "--- flushing cache + registering (.user scope) ---" )
    try:
        subprocess.run( ["swift", tf_name], check=False )
    finally:
        os.unlink(tf_name)
    print( "done. Fully quit and reopen the browser/app to pick up the change." )


def parse_args(argv):
    inputs = []
    dry = False
    it = iter(argv)
    for a in it:
        if a == "--input":
            v = next(it, None)
            if v is not None:
                inputs.append(v)
        elif a.startswith("--input="):
            inputs.append(a.split("=", 1)[1])
        elif a == "--dry-run":
            dry = True
        elif a in ("-h", "--help"):
            print(USAGE)
            sys.exit(0)
        elif not a.startswith("-"):
            inputs.append(a)      # bare positional: file, dir, or glob
        else:
            print("unknown arg:", a)
            sys.exit(2)
    if not inputs:
        print(USAGE)
        sys.exit(2)
    return inputs, dry


def main():
    inputs, dry = parse_args(sys.argv[1:])
    paths = []
    seen = set()
    for inp in inputs:
        for p in resolve_input(inp):
            if p not in seen:
                seen.add(p)
                paths.append(p)
    flush_and_register(paths, dry=dry)


if __name__ == "__main__":
    main()
