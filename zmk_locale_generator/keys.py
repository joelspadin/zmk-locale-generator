import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
from typing import TextIO

_ZMK_KEYS_PATH = "app/include/dt-bindings/zmk/keys.h"
_DEFAULT_KEYS_H_PATH = Path(__file__).parent / "keys.h"

_DEFINE_RE = re.compile(r"^\s*#\s*define\s+([a-zA-Z_]\w*)\s+(.+?)\s*(?://\s*(.+))?$")
_LINE_CONTINUATION = "\\\n"


class Modifier(Enum):
    LAlt = "LA"
    LCtrl = "LC"
    LGui = "LG"
    LShift = "LS"
    RAlt = "RA"
    RCtrl = "RC"
    RGui = "RG"
    RShift = "RS"


@dataclass(eq=True, frozen=True)
class HidUsage:
    modifiers: frozenset[Modifier]
    page: str
    id: str

    def __str__(self):
        node = ast.Call(
            func=ast.Name(id="ZMK_HID_USAGE"),
            args=[ast.Name(id=self.page), ast.Name(id=self.id)],
            keywords=[],
        )
        for modifier in self.modifiers:
            node = ast.Call(func=ast.Name(id=modifier.value), args=[node], keywords=[])

        return ast.unparse(node)


@dataclass
class KeyAlias:
    alias: str


def parse_zmk_keys(zmk_path: Path = None) -> dict[str, HidUsage | KeyAlias]:
    """
    Parse ZMK's keys.h file.
    """
    keys_h_path = zmk_path / _ZMK_KEYS_PATH if zmk_path else _DEFAULT_KEYS_H_PATH

    with keys_h_path.open("r", encoding="utf-8") as f:
        defines = _get_defines(f)

        return {name: _parse_usage(value) for name, value in defines}


def _get_c_lines(io: TextIO):
    current_line = ""
    for line in io:
        if line.endswith(_LINE_CONTINUATION):
            current_line += line.removesuffix(_LINE_CONTINUATION)
            continue

        if current_line:
            yield current_line + line
            current_line = ""
        else:
            yield line


def _get_defines(io: TextIO):
    for line in _get_c_lines(io):
        if match := _DEFINE_RE.match(line):
            name = match.group(1)
            value = match.group(2)
            comment = match.group(3)
            if comment and "deprecated" in comment.lower():
                continue

            yield (name, value)


def _parse_usage(text: str):
    modifiers = set()

    def _parse_node(node):
        match node:
            case ast.Expression(body=body):
                return _parse_node(body)

            case ast.Name(id=symbol):
                return KeyAlias(symbol)

            case ast.Call(
                func=ast.Name(id="ZMK_HID_USAGE"),
                args=[ast.Name(id=page), ast.Name(id=id)],
            ):
                return HidUsage(frozenset(modifiers), page, id)

            case ast.Call(func=ast.Name(id=name), args=[arg]):
                modifiers.add(Modifier(name))
                return _parse_node(arg)

    return _parse_node(ast.parse(text, mode="eval"))


def get_zmk_name(iso_key: str):
    return _DEFAULT_MAP[iso_key]


_DEFAULT_MAP = {
    "E00": "GRAVE",
    "E01": "N1",
    "E02": "N2",
    "E03": "N3",
    "E04": "N4",
    "E05": "N5",
    "E06": "N6",
    "E07": "N7",
    "E08": "N8",
    "E09": "N9",
    "E10": "N0",
    "E11": "MINUS",
    "E12": "EQUAL",
    "D00": "TAB",
    "D01": "Q",
    "D02": "W",
    "D03": "E",
    "D04": "R",
    "D05": "T",
    "D06": "Y",
    "D07": "U",
    "D08": "I",
    "D09": "O",
    "D10": "P",
    "D11": "LEFT_BRACKET",
    "D12": "RIGHT_BRACKET",
    "D13": "BACKSLASH",
    "C01": "A",
    "C02": "S",
    "C03": "D",
    "C04": "F",
    "C05": "G",
    "C06": "H",
    "C07": "J",
    "C08": "K",
    "C09": "L",
    "C10": "SEMICOLON",
    "C11": "SINGLE_QUOTE",
    "C12": "BACKSLASH",
    "C13": "RETURN",
    "B00": "NON_US_BACKSLASH",
    "B01": "Z",
    "B02": "X",
    "B03": "C",
    "B04": "V",
    "B05": "B",
    "B06": "N",
    "B07": "M",
    "B08": "COMMA",
    "B09": "PERIOD",
    "B10": "SLASH",
    "B11": "INTERNATIONAL_1",
    "A03": "SPACE",
}
