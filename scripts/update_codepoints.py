#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path
import re
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
import sys
import unicodedata
import urllib.request

sys.path.insert(0, str(Path(__file__).parent.parent))

from batch_locales import get_locales
from zmk_locale_generator.locales import get_layout
from zmk_locale_generator.codepoints import (
    get_codepoint_names_raw,
    is_visible_character,
)

yaml = YAML()

UNICODE_BLOCKS_URL = "https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt"
UNICODE_BLOCK_RE = re.compile(r"^([0-9A-F]+)..([0-9A-F]+); (.+)")

YAML_HEADER = """\
%YAML 1.2
# This document maps Unicode codepoints to key names for ZMK.
# Do not manually add new codepoitns to this file. Instead, add locales to
# /scripts/locales.yaml and run /scripts/update_codepoints.py. Then you can
# edit this file to assign names to the codepoints it adds.
#
# Each value is either a single string or a list of strings. The locale
# abbreviation will prefix each name, e.g. A -> DE_A for a German layout.
# If a name matches a name from ZMK's keys.h, any aliases for that key will
# automatically be added.
---
"""


def upper_bound(seq, val, gt=lambda a, b: a > b):
    """
    Return the index of the first item in seq which is greater than val.
    """
    for i, x in enumerate(seq):
        if gt(x, val):
            return i
    return len(seq)


@dataclass
class UnicodeBlock:
    start: str
    end: str
    name: str


def get_unicode_blocks():
    """
    Get the list of blocks into which Unicode codepoints are grouped.
    """
    with urllib.request.urlopen(UNICODE_BLOCKS_URL) as response:
        text = response.read().decode("utf-8")
        for line in text.splitlines():
            if match := UNICODE_BLOCK_RE.match(line):
                start = chr(int(match.group(1), 16))
                end = chr(int(match.group(2), 16))
                name = match.group(3)
                yield UnicodeBlock(start=start, end=end, name=name)


def codepoint_to_block(c: str, blocks: list[UnicodeBlock]):
    """
    Get the UnicodeBlock containing a character.
    """
    return next(block for block in blocks if c >= block.start and c <= block.end)


def first_key(map: CommentedMap):
    return list(map.keys())[0]


def find_block(codepoints: CommentedSeq, block: UnicodeBlock):
    """
    Find the YAML object for a Unicode block, creating it if necessary.
    """
    try:
        return next(b for b in codepoints if block.start <= first_key(b) <= block.end)
    except StopIteration:

        def compare_blocks(a: CommentedMap, b: UnicodeBlock):
            return first_key(a) > b.end

        index = upper_bound(codepoints, block, compare_blocks)
        item = CommentedMap()
        codepoints.insert(index, item)
        return item


# Ignore control codes aside from these
CONTROL_CODES = [
    "\u0007",  # Bell
    "\t",  # Tab
    "\r",  # Enter
    "\u001B",  # Escape character
]


def filter_codepoint(c):
    return ord(c) >= 0x20 or c in CONTROL_CODES


def get_used_codepoints():
    """
    Get the list of codepoints that are used by the selected keyboard layouts.
    """
    locales = list(get_locales())

    with Pool(processes=len(locales)) as pool:
        layouts = pool.map(get_layout, (x.layout for x in locales))

    codepoints: set[str] = set()
    for layout in layouts:
        for keymap in layout.keymaps:
            codepoints.update(v for v in keymap.keys.values() if filter_codepoint(v))

    return sorted(codepoints)


def remove_unused_codepoints(codepoints: CommentedSeq, used: list[str]):
    """
    Remove codepoints that are no longer used by any locale.
    """
    for block in codepoints:
        for c in list(block.keys()):
            if not c in used:
                del block[c]


def add_new_codepoint_placeholders(
    codepoints: CommentedSeq, blocks: list[UnicodeBlock], used: list[str]
):
    """
    Add a placeholder name for new codepoints to indicate they need to be named.
    """
    for c in used:
        block = find_block(codepoints, codepoint_to_block(c, blocks))
        if not c in block:
            pos = upper_bound(block.keys(), c)
            block.insert(pos, c, "")


def add_codepoint_comments(codepoints: CommentedSeq, blocks: list[UnicodeBlock]):
    """
    Add a comment to show the character for every printable character.
    """
    for item in codepoints:
        block = codepoint_to_block(first_key(item), blocks)

        # ruamel.yaml parses the first block's comment as being a start comment
        # for the whole sequence, so don't set it on the list item too or it
        # will duplicate the comment.
        if block.start == "\0":
            codepoints.yaml_set_start_comment("# " + block.name)
        else:
            item.yaml_set_start_comment("\n# " + block.name)

        for c in item.keys():
            comments = []
            if not item[c]:
                try:
                    name = re.sub(r"[^\w]+", "_", unicodedata.name(c).upper())
                    comments.append(f"# {name}")
                except ValueError:
                    pass

            if is_visible_character(c):
                comments.append(f"# {c}")

            if comments:
                item.yaml_add_eol_comment(" ".join(comments), key=c)


# Matches "foo:", "'foo':", or '"foo":' if preceded by "  " or "- ".
KEY_RE = re.compile(r"(?<=^(?:- |  ))(([\"']?).+\2)(?=:)")
COMMENT_PAD_RE = re.compile(" +#")


def transform(text: str):
    # ruamel.yaml will try to format keys in the shortest way possible, but we
    # want everything as Unicode escapes for consistency.
    # Also, because it shortens many keys but tries to keep comments on the same
    # column, it ends up padding out comments, so undo that.
    def escape_key(match):
        c = yaml.load(match.group(1))
        return f'"\\u{ord(c):04X}"'

    def transform_line(line: str):
        line = KEY_RE.sub(escape_key, line)
        line = COMMENT_PAD_RE.sub(" #", line)

        return line

    return "\n".join(transform_line(line) for line in text.splitlines())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "out",
        type=Path,
        nargs="?",
        default=Path("./codepoints.yaml"),
        help="Output file name (default: codepoints.yaml)",
    )

    args = parser.parse_args()

    blocks = list(get_unicode_blocks())
    codepoints = get_codepoint_names_raw()

    print("Fetching locales...")
    used = get_used_codepoints()

    print(f"Writing {args.out}")
    remove_unused_codepoints(codepoints, used)
    add_new_codepoint_placeholders(codepoints, blocks, used)
    add_codepoint_comments(codepoints, blocks)

    with args.out.open(mode="w", encoding="utf-8") as f:
        f.write(YAML_HEADER)
        yaml.dump(codepoints, f, transform=transform)


if __name__ == "__main__":
    main()
