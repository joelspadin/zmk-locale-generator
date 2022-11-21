import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
import re

from .keys import Modifier

LAYOUT_URL = "https://kbdlayout.info/{name}/download/cldr"


@dataclass
class KeyMap:
    keys: dict[str, str]
    modifiers: set[Modifier] = field(default_factory=set)


@dataclass
class LocaleLayout:
    locale: str
    names: list[str] = field(default_factory=list)
    keymaps: list[KeyMap] = field(default_factory=list)
    # TODO: do we need anything from the <transforms> element?
    # transforms: list = field(default_factory=list)


def get_layout(locale: str) -> LocaleLayout:
    """
    Fetch a layout from kbdlayout.info
    """
    url = _get_layout_url(locale)
    with urllib.request.urlopen(url) as response:
        tree = ET.parse(response)
        return _parse_layout(locale, tree)


_ESCAPE_RE = re.compile(r"\\u\{([0-9a-fA-F]+)\}")


def _unescape(char: str):
    return _ESCAPE_RE.sub(lambda m: chr(int(m.group(1), 16)), char)


def _get_layout_url(locale: str):
    return LAYOUT_URL.format(name=locale.lower())


def _parse_layout(locale: str, tree: ET.ElementTree):
    root = tree.getroot()
    try:
        names = [name.attrib["value"] for name in root.find("names").findall("name")]
    except:
        names = [locale]

    layout = LocaleLayout(locale=locale, names=names)

    for keymap in root.findall("keyMap"):
        layout.keymaps.extend(_parse_keymap(keymap))

    return layout


def _parse_keymap(keymap: ET.Element):
    keys = {
        key.attrib["iso"]: _unescape(key.attrib["to"]) for key in keymap.findall("map")
    }

    try:
        modifier_groups = keymap.attrib["modifiers"].split(" ")
        for group in modifier_groups:
            try:
                yield KeyMap(keys=keys, modifiers=_parse_modifiers(group))
            except KeyError:
                pass
    except KeyError:
        yield KeyMap(keys=keys)


def _parse_modifiers(text: str):
    return {_MODIFIERS[name] for name in text.split("+")}


_MODIFIERS = {
    "alt": Modifier.LAlt,
    "altR": Modifier.RAlt,
    "ctrl": Modifier.LCtrl,
    "shift": Modifier.LShift,
}
