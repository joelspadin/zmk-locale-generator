import logging
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import TextIO

from . import cldr
from .codepoints import get_codepoint_names, is_visible_character
from .keys import HidUsage, KeyAlias, Modifier, get_zmk_name, parse_zmk_keys
from .util import unique

DEFAULT_LICENSE = f"""\
Copyright (c) {date.today().year} The ZMK Contributors

SPDX-License-Identifier: MIT"""

UsageAndValue = tuple[HidUsage, str]


class LayoutHeaderGenerator:
    """
    Generates locale headers.
    """

    zmk_keys: dict[str, HidUsage | KeyAlias]
    codepoint_names: dict[str, str | list[str]]

    def __init__(self, zmk_path: Path | None):
        self.zmk_keys = parse_zmk_keys(zmk_path)
        self.codepoint_names = get_codepoint_names()

    def write_header(
        self,
        cldr_file: TextIO,
        out_file: TextIO,
        prefix: str,
        license_path: Path | None = None,
    ):
        """
        Write a locale header.

        :param cldr_file: CLDR keyboard XML file
        :param out_file: Output file
        :param prefix: Prefix for key names
        :param license_path: Path to license file to append to the generated header
        """
        layout = cldr.parse_cldr_keyboard(cldr_file)
        defs = self._get_key_definitions(layout)

        license_text = "\n * ".join(_get_license(license_path).splitlines())

        out_file.write(
            f"""\
/*
 * Localized Keys for {', '.join(layout.names)}
 *
 * This file was generated from data with the following license:
 *
 * {license_text}
 */

#pragma once

#include <dt-bindings/zmk/hid_usage.h>
#include <dt-bindings/zmk/hid_usage_pages.h>
#include <dt-bindings/zmk/modifiers.h>
"""
        )

        for usage, value in defs:
            if names := self._get_key_names(prefix, value):
                main, *aliases = names

                out_file.write("\n")
                if is_visible_character(value):
                    out_file.write(f"/* {value} */\n")

                out_file.write(f"#define {main} ({usage})\n")
                for alias in aliases:
                    out_file.write(f"#define {alias} ({main})\n")
            else:
                logging.debug("Skipped U+%04X (%s) = %s", ord(value), value, usage)

    def _lookup_usage(self, name: str) -> HidUsage:
        match self.zmk_keys[name]:
            case KeyAlias(alias=alias):
                return self._lookup_usage(alias)

            case HidUsage() as value:
                return value

        raise ValueError(f'Invalid type for "{name}"')

    def _get_key_definitions(self, keyboard: cldr.CldrKeyboard) -> list[UsageAndValue]:
        keys = list(self._get_raw_definitions(keyboard))

        keys = _dedupe_same_usage(keys)
        keys = _dedupe_uppercase(keys)
        keys = _dedupe_same_value(keys)

        keys.sort(key=lambda k: k[1].lower())
        return keys

    def _get_raw_definitions(self, keyboard: cldr.CldrKeyboard):
        for keymap in keyboard.keymaps:
            for key, value in keymap.keys.items():
                try:
                    usage = self._lookup_usage(get_zmk_name(key))

                    if keymap.modifiers:
                        modifiers = usage.modifiers | keymap.modifiers
                        usage = HidUsage(modifiers, usage.page, usage.id)

                    yield usage, value
                except KeyError:
                    logging.debug(
                        f'No ZMK defined name for key {key}. Ignoring "{value}"'
                    )

    def _get_key_names(self, locale: str, value: str):
        names = self.codepoint_names.get(value, [])

        if isinstance(names, str):
            names = [names]

        names += [
            k
            for k, v in self.zmk_keys.items()
            if isinstance(v, KeyAlias) and v.alias in names
        ]

        return [f"{locale.upper()}_{name}" for name in names]


def _get_license(path: Path | None):
    return path.read_text("utf-8-sig") if path else DEFAULT_LICENSE


def _has_shift(key: UsageAndValue):
    usage, _ = key
    return bool(usage.modifiers & {Modifier.LShift, Modifier.RShift})


def _remove_shift(key: UsageAndValue):
    usage, _ = key
    return usage.modifiers - {Modifier.LShift, Modifier.RShift}


def _dedupe_uppercase(keys: list[UsageAndValue]):
    # If we have two definitions a and b such that:
    # a.value.casefold() == b.value.casefold() and a.usage == LS(b.usage)
    # then the uppercase definition (a) is redundant.
    def is_duplicate_uppercase(a: UsageAndValue):
        a_value = a[1].casefold()
        a_mods = _remove_shift(a)
        return any(
            a_value == b_value.casefold() and a_mods == b_usage.modifiers
            for b_usage, b_value in base_defs
        )

    base_defs = [k for k in keys if not _has_shift(k)]
    shift_defs = [k for k in keys if _has_shift(k) and not is_duplicate_uppercase(k)]

    return base_defs + shift_defs


def _dedupe_same_usage(keys: list[UsageAndValue]):
    return list(unique(keys, lambda d: d[0]))


def _dedupe_same_value(keys: list[UsageAndValue]):
    # Keep the entry with the fewest modifiers
    d: defaultdict[str, list[HidUsage]] = defaultdict(list)
    for usage, value in keys:
        d[value].append(usage)

    def shortest_mods(seq: list[HidUsage]):
        return min(seq, key=lambda x: len(x.modifiers))

    return [(shortest_mods(v), k) for k, v in d.items()]
