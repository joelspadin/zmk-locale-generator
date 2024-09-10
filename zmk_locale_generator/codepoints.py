from pathlib import Path

from ruamel.yaml import YAML

from .typing import CommentedMap, CommentedSeq

CODEPOINTS_PATH = Path(__file__).parent / "codepoints.yaml"


CodepointNames = dict[str, str | list[str]]
CodepointNamesRaw = CommentedSeq[CommentedMap[str, str | list[str]]]


def get_codepoint_names() -> CodepointNames:
    """
    Get a mapping of codepoints to a single name or list of names from
    codepoints.yaml.
    """
    codepoints = get_codepoint_names_raw()

    flattened = (item for block in codepoints for item in block.items())

    return {k: v for k, v in flattened if v}


def get_codepoint_names_raw() -> CodepointNamesRaw:
    """
    Get the raw data from codepoints.yaml for round-trip editing.
    """
    with CODEPOINTS_PATH.open("r", encoding="utf-8") as f:
        yaml = YAML()
        return yaml.load(f)


# Characters for which str.isprintable() returns true, but which don't have a glyph.
# Determine by experimentation.
INVISIBLE_CHARACTERS = [
    "\u034f",  # Combining Grapheme Joiner
]


def is_visible_character(c: str):
    return c.isprintable() and not c.isspace() and c not in INVISIBLE_CHARACTERS
