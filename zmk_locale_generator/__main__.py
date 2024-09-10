#!/usr/bin/env python3

import argparse
import logging
import sys
from pathlib import Path
from typing import TextIO

from zmk_locale_generator import LayoutHeaderGenerator


def main():
    parser = argparse.ArgumentParser(description="ZMK Locale Header Generator")
    parser.add_argument("prefix", help="prefix for key names")
    parser.add_argument("path", type=Path, help="path to CLDR keyboard layout XML file")
    parser.add_argument("--license", "-l", type=Path, help="path to license file")
    parser.add_argument("-o", "--out", type=Path, help="output path (default: stdout)")
    parser.add_argument("-v", "--verbose", action="store_true", help="print debug info")
    parser.add_argument("-z", "--zmk", type=Path, help="path to ZMK repo")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    def generate(infile: TextIO, outfile: TextIO):
        generator = LayoutHeaderGenerator(args.zmk)
        generator.write_header(
            infile, outfile, prefix=args.prefix, license_path=args.license
        )

    with args.path.open("r", encoding="utf-8") as infile:
        if args.out:
            with args.out.open("w", encoding="utf-8") as outfile:
                generate(infile, outfile)
        else:
            generate(infile, sys.stdout)


if __name__ == "__main__":
    main()
