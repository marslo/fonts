<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [macOS Font Cleanup Tips](#macos-font-cleanup-tips)
  - [1. Clear the CoreText font cache](#1-clear-the-coretext-font-cache)
  - [2. Clear the `.user` registration DB](#2-clear-the-user-registration-db)
    - [with `unregister.swift` ( recommended )](#with-unregisterswift--recommended-)
    - [inline ( no script file )](#inline--no-script-file-)
  - [3. Check / verify](#3-check--verify)
  - [Quick reference](#quick-reference)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# macOS Font Cleanup Tips

Cleanup for user-scope fonts registered via CoreText (`CTFontManagerRegisterFontsForURL(url, .user, …)`, as `register.py` does). No `sudo` needed — the mirror of a `.user` registration is a `.user` unregistration, **not** `atsutil`.

> [!NOTE]
> Example font below: `BlexMonoLig*` under `~/Library/Fonts`. Swap the name/glob for your own.

## 1. Clear the CoreText font cache

Drop CoreText's parsed cache, then restart the `fontd` daemon so it rebuilds:

```bash
rm -rf ~/Library/Caches/com.apple.FontRegistry && killall fontd
```

After this, **fully quit and reopen** any app that loaded the font (terminal, browser, editor) — a running app may still hold the old glyphs.

## 2. Clear the `.user` registration DB

If files were already deleted, a stale registration may still point at the missing path. Unregister the exact URLs at `.user` scope (mirror of `register.py`).

### with `unregister.swift` ( recommended )

[`unregister.swift`](./unregister.swift) takes font **names or paths** as args — a bare name resolves under `~/Library/Fonts`, a path (absolute / `~` / containing `/`) is used as-is, and the shell expands globs before they reach it. No editing, reusable for any family:

```bash
# by name ( resolved under ~/Library/Fonts )
swift unregister.swift BlexMonoLigNerdFontMono-Bold.otf BlexMonoLigNerdFontMono-BoldItalic.otf

# by glob ( the shell expands it first )
swift unregister.swift ~/Library/Fonts/BlexMonoLig*Bold*.otf
```

It prints `unregister <face>: ok` / `failed (…)` per file and exits non-zero if any failed. `./unregister.swift …` also works ( the file is executable ).

### inline ( no script file )

The same call without the script — edit the `paths` list:

```bash
swift - <<'EOF'
import CoreText
import Foundation
let paths = [
  "\(NSHomeDirectory())/Library/Fonts/BlexMonoLigNerdFontMono-Bold.otf",
  "\(NSHomeDirectory())/Library/Fonts/BlexMonoLigNerdFontMono-BoldItalic.otf",
]
for p in paths {
  let u = URL(fileURLWithPath: p) as CFURL
  var e: Unmanaged<CFError>?
  let ok = CTFontManagerUnregisterFontsForURL(u, .user, &e)
  print("unregister \((p as NSString).lastPathComponent): \(ok)")
}
EOF
```

- Returns `false` / `failed` when the file is already gone — harmless; it still drops the persistent record.
- Deleting the file only removes those faces; the family survives if other faces (Regular/Italic/…) remain.
- Then flush the cache ( [step 1](#1-clear-the-coretext-font-cache) ) so any running app picks up the change.

## 3. Check / verify

List whatever the system still recognizes for the family:

```bash
system_profiler SPFontsDataType 2>/dev/null | command grep -i 'BlexMonoLig.*Bold'
```

Sample output (SemiBold + SemiBoldItalic still installed; plain Bold/BoldItalic removed):

```bash
    BlexMonoLigNerdFontMono-SemiBold.otf:
      Location: /Users/marslo/Library/Fonts/BlexMonoLigNerdFontMono-SemiBold.otf
        BlexMonoLigNFM-SemiBold:
          Full Name: BlexMonoLig Nerd Font Mono SemiBold
          Unique Name: BlexMonoLig Nerd Font Mono SemiBold 3.5.0.1-1
    BlexMonoLigNerdFontMono-SemiBoldItalic.otf:
      Location: /Users/marslo/Library/Fonts/BlexMonoLigNerdFontMono-SemiBoldItalic.otf
        BlexMonoLigNFM-SemiBoldItalic:
          Full Name: BlexMonoLig Nerd Font Mono SemiBold Italic
          Unique Name: BlexMonoLig Nerd Font Mono SemiBold Italic 3.5.0.1-1
```

- Empty output → fully removed.
- The removed faces (Bold / BoldItalic) no longer appear; the remaining faces (SemiBold / SemiBoldItalic) still list their `Location`.

Cross-check the files on disk:

```bash
command ls ~/Library/Fonts/BlexMonoLig*Bold* 2>/dev/null
```

## Quick reference

| GOAL                         | COMMAND                                                                     |
| ---------------------------- | --------------------------------------------------------------------------- |
| Flush cache + restart daemon | `rm -rf ~/Library/Caches/com.apple.FontRegistry && killall fontd`           |
| Unregister `.user` face      | `swift unregister.swift <name\|glob> …` ( or the inline `swift -` snippet ) |
| Verify via system            | `system_profiler SPFontsDataType \| command grep -i '<NAME>'`               |
| Verify on disk               | `command ls ~/Library/Fonts/<GLOB>`                                         |

> [!WARNING]
> `atsutil` targets the legacy ATS path and its system scope needs `sudo`. For fonts registered at `.user` scope, prefer the cache flush + `.user` unregister above.
