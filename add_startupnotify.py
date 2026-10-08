#!/usr/bin/env python3
"""Add <startupnotify> to every launcher in an Openbox menu.xml file.

Openbox menu items that run a command look like:

    <item label="Firefox">
      <action name="Execute">
        <command>firefox</command>
      </action>
    </item>

This adds a <startupnotify><enabled>yes</enabled></startupnotify> child to
every <action name="Execute"> that doesn't already have one, so the cursor
shows a busy spinner while the app is launching.
"""
import argparse
import shutil
import sys
import xml.etree.ElementTree as ET


def localname(tag):
    """Return the tag's local name, or None for comments/PIs (non-string tags)."""
    if not isinstance(tag, str):
        return None
    return tag.rsplit('}', 1)[-1]


def namespace_of(tag):
    """Return '{uri}' for a namespaced tag, or '' otherwise."""
    if isinstance(tag, str) and tag.startswith('{'):
        return tag.split('}', 1)[0] + '}'
    return ''


def add_startupnotify(root, enabled="yes", force=False, verbose=False):
    parent_map = {child: parent for parent in root.iter() for child in parent}
    changed = 0
    skipped = 0

    for action in root.iter():
        if localname(action.tag) != 'action':
            continue
        if action.get('name', '').lower() != 'execute':
            continue

        ns = namespace_of(action.tag)
        existing = next(
            (c for c in action if localname(c.tag) == 'startupnotify'), None
        )

        item = parent_map.get(action)
        label = item.get('label') if item is not None and localname(item.tag) == 'item' else None

        if existing is not None:
            if force:
                enabled_el = next(
                    (c for c in existing if localname(c.tag) == 'enabled'), None
                )
                if enabled_el is None:
                    enabled_el = ET.SubElement(existing, ns + 'enabled')
                enabled_el.text = enabled
                changed += 1
                if verbose:
                    print(f"updated: {label!r}", file=sys.stderr)
            else:
                skipped += 1
                if verbose:
                    print(f"skipped (already has startupnotify): {label!r}", file=sys.stderr)
            continue

        startupnotify = ET.Element(ns + 'startupnotify')
        enabled_el = ET.SubElement(startupnotify, ns + 'enabled')
        enabled_el.text = enabled

        children = list(action)
        if children:
            last = children[-1]
            startupnotify.tail = last.tail
            last.tail = action.text
        else:
            startupnotify.tail = action.text
        action.append(startupnotify)

        changed += 1
        if verbose:
            print(f"added: {label!r}", file=sys.stderr)

    return changed, skipped


def register_default_namespace(path):
    """If the file declares a default xmlns, keep ET from inventing ns0: prefixes."""
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        head = f.read(4096)
    import re
    m = re.search(r'<[A-Za-z_][\w.-]*\s+[^>]*\bxmlns="([^"]+)"', head)
    if m:
        ET.register_namespace('', m.group(1))


def main():
    parser = argparse.ArgumentParser(
        description="Add startupnotify to every launcher (Execute action) in an Openbox menu.xml."
    )
    parser.add_argument("menu", help="path to menu.xml")
    out = parser.add_mutually_exclusive_group()
    out.add_argument("-o", "--output", help="write result to this file instead of stdout")
    out.add_argument("-i", "--in-place", action="store_true",
                      help="edit the file in place (keeps a .bak backup)")
    parser.add_argument("--disable", action="store_true",
                         help="set startupnotify enabled to 'no' instead of 'yes'")
    parser.add_argument("--force", action="store_true",
                         help="also update startupnotify blocks that already exist")
    parser.add_argument("-v", "--verbose", action="store_true",
                         help="print what changed, to stderr")
    args = parser.parse_args()

    register_default_namespace(args.menu)
    tree = ET.parse(args.menu, parser=ET.XMLParser(
        target=ET.TreeBuilder(insert_comments=True, insert_pis=True)
    ))
    root = tree.getroot()

    enabled = "no" if args.disable else "yes"
    changed, skipped = add_startupnotify(root, enabled=enabled, force=args.force, verbose=args.verbose)

    if args.verbose:
        print(f"{changed} launcher(s) updated, {skipped} already had startupnotify", file=sys.stderr)

    body = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    if not body.endswith(b"\n"):
        body += b"\n"

    if args.in_place:
        shutil.copy2(args.menu, args.menu + ".bak")
        with open(args.menu, "wb") as f:
            f.write(body)
    elif args.output:
        with open(args.output, "wb") as f:
            f.write(body)
    else:
        sys.stdout.buffer.write(body)


if __name__ == "__main__":
    main()
