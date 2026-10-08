# Openbox Menu startupnotify

A small script that adds `<startupnotify>` to every launcher in an Openbox
`menu.xml`, so the cursor shows a busy spinner while an app is launching
instead of looking like the click did nothing.

Turns this:

```xml
<item label="Firefox">
  <action name="Execute">
    <command>firefox</command>
  </action>
</item>
```

into this:

```xml
<item label="Firefox">
  <action name="Execute">
    <command>firefox</command>
    <startupnotify><enabled>yes</enabled></startupnotify>
  </action>
</item>
```

for every `<action name="Execute">` in the file — nested submenus included.

## Usage

```sh
# print the result to stdout
python3 add_startupnotify.py ~/.config/openbox/menu.xml

# write to a new file
python3 add_startupnotify.py ~/.config/openbox/menu.xml -o menu-new.xml

# edit in place (keeps a menu.xml.bak backup)
python3 add_startupnotify.py ~/.config/openbox/menu.xml -i -v

openbox --reconfigure
```

Options:

- `-i`, `--in-place` — edit the file in place, keeping a `.bak` backup
- `-o FILE` — write the result to `FILE` instead of stdout
- `--force` — also update launchers that already have a `<startupnotify>`
  block (default: leave them untouched)
- `--disable` — set `enabled` to `no` instead of `yes` (useful for undoing)
- `-v`, `--verbose` — print what was added/skipped, per item label

Re-running the script is safe: launchers that already have `startupnotify`
are left alone unless `--force` is given.

## Notes

- Requires only the Python 3 standard library.
- Preserves comments, XML namespace declaration, and the original
  indentation/formatting of everything it doesn't touch.
- Only comments *inside* the root `<openbox_menu>` element survive —
  Python's `ElementTree` drops anything outside the document element
  during parsing (not a concern for typical Openbox menu files).

## License

MIT
