from dataclasses import dataclass, field
from itertools import chain
import re
from typing import IO
import unicodedata
import xml.etree.ElementTree as ET

from .keys import Modifier


@dataclass
class KeyMap:
    keys: dict[str, str]
    modifiers: set[Modifier] = field(default_factory=set)


@dataclass
class CldrKeyboard:
    locale: str
    names: list[str] = field(default_factory=list)
    keymaps: list[KeyMap] = field(default_factory=list)


def parse_cldr_keyboard(source: IO):
    tree = ET.parse(source)
    root = tree.getroot()

    locale = root.get("locale")
    try:
        names = [name.get("value") for name in root.find("names").findall("name")]
    except AttributeError:
        names = [locale]

    keymaps = list(
        chain.from_iterable(_parse_keymap(keymap) for keymap in root.findall("keyMap"))
    )

    return CldrKeyboard(locale=locale, names=names, keymaps=keymaps)


_ESCAPE_RE = re.compile(r"\\u\{([0-9a-fA-F]+)\}")


def _unescape(char: str):
    return _ESCAPE_RE.sub(lambda m: chr(int(m.group(1), 16)), char)


_INVALID_CATEGORIES = [
    "Cn",  # unassigned
    "Co",  # private use
    "Cs",  # lower surrogate
]


def _is_valid_character(c: str):
    # TODO: Layouts sometimes contain keys with a string of multiple characters.
    # Don't know what to do with those yet, so just ignore them.
    if len(c) > 1:
        return False

    return unicodedata.category(c) not in _INVALID_CATEGORIES


def _parse_keymap(keymap: ET.Element):
    keys = {
        key.get("iso"): v
        for key in keymap.findall("map")
        if _is_valid_character(v := _unescape(key.get("to")))
    }

    if modifiers := keymap.get("modifiers"):
        modifier_groups = _parse_modifiers(keymap.get("modifiers"))

        for modifiers in modifier_groups:
            yield KeyMap(keys=keys, modifiers=modifiers)
    else:
        yield KeyMap(keys=keys)


def _parse_modifiers(mods: str):
    for combo in mods.split():
        if parsed := _parse_modifier_combination(combo):
            yield parsed


class UnsupportedModifier(Exception):
    pass


def _parse_modifier_combination(combo: str):
    try:
        return {
            _parse_modifier_key(key)
            for key in combo.split("+")
            if not key.endswith("?")
        }
    except UnsupportedModifier:
        return None


_MODIFIERS = {
    "alt": Modifier.LAlt,
    "altL": Modifier.LAlt,
    "altR": Modifier.RAlt,
    "ctrl": Modifier.LCtrl,
    "ctrlL": Modifier.LCtrl,
    "ctrlR": Modifier.RCtrl,
    "shift": Modifier.LShift,
    "shiftL": Modifier.LShift,
    "shiftR": Modifier.RShift,
    "opt": Modifier.LAlt,
    "optL": Modifier.LAlt,
    "optR": Modifier.RAlt,
    "cmd": Modifier.LGui,
}


def _parse_modifier_key(key) -> Modifier:
    try:
        return _MODIFIERS[key]
    except KeyError:
        raise UnsupportedModifier()
