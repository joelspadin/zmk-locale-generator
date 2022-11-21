#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import sys
from typing import TextIO


from zmk_locale_generator import LocaleGenerator


def main():
    parser = argparse.ArgumentParser(description="ZMK Locale Header Generator")
    parser.add_argument("locale", help="locale code (used as the prefix for key names)")
    parser.add_argument(
        "-l", "--layout", help="name on kbdlayout.info (default: locale)"
    )
    parser.add_argument("-o", "--out", type=Path, help="output path (default: stdout)")
    parser.add_argument("-v", "--verbose", action="store_true", help="print debug info")
    parser.add_argument("-z", "--zmk", type=Path, help="path to ZMK repo")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    keys_h_path = args.zmk / "app/include/dt-bindings/zmk/keys.h" if args.zmk else None

    def generate(outfile: TextIO):
        generator = LocaleGenerator(keys_h_path)
        generator.write_header(outfile, locale=args.locale, layout_name=args.layout)

    if args.out:
        with args.out.open("w", encoding="utf-8") as outfile:
            generate(outfile)
    else:
        generate(sys.stdout)


if __name__ == "__main__":
    main()
