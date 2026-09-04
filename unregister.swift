#!/usr/bin/env swift
//
// Unregister fonts at .user scope -- the mirror of register.py.
//
// Each arg is a font to drop from the CoreText .user registration DB:
//   - a bare name (BlexMonoLigNerdFontMono-Bold.otf) resolves under ~/Library/Fonts
//   - a path (absolute, ~-relative, or containing "/") is used as given
// Shell globs are expanded by the shell before they reach this script.
//
// Usage:
//   swift unregister.swift BlexMonoLigNerdFontMono-Bold.otf BlexMonoLigNerdFontMono-BoldItalic.otf
//   swift unregister.swift ~/Library/Fonts/Blex*Bold*.otf
//   ./unregister.swift <name|path> ...
//
// After running, also flush the cache and restart the daemon:
//   rm -rf ~/Library/Caches/com.apple.FontRegistry && killall fontd
//

import CoreText
import Foundation

// resolve an arg to an absolute font path
func resolve(_ arg: String) -> String {
    let expanded = (arg as NSString).expandingTildeInPath
    if expanded.contains("/") { return expanded }
    let dir = (NSHomeDirectory() as NSString).appendingPathComponent("Library/Fonts")
    return (dir as NSString).appendingPathComponent(expanded)
}

let args = Array(CommandLine.arguments.dropFirst())
guard !args.isEmpty else {
    FileHandle.standardError.write(
        Data("usage: unregister.swift <font-file|path> ...\n".utf8)
    )
    exit(2)
}

var failed = false
for arg in args {
    let path = resolve(arg)
    let url = URL(fileURLWithPath: path) as CFURL
    let name = (path as NSString).lastPathComponent
    var err: Unmanaged<CFError>?
    if CTFontManagerUnregisterFontsForURL(url, .user, &err) {
        print("unregister \(name): ok")
    } else {
        let msg = err?.takeRetainedValue().localizedDescription ?? "unknown error"
        print("unregister \(name): failed (\(msg))")
        failed = true
    }
}
exit(failed ? 1 : 0)
