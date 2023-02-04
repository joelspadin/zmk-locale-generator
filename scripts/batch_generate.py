#!/usr/bin/env python3

"""
Runs zmk_locale_generator for all locales in locales.yaml.
"""

import argparse
import logging
from pathlib import Path
import sys
from keyboards import get_keyboards, Keyboard

REPO_PATH = Path(__file__).parent.parent

sys.path.insert(0, str(REPO_PATH))

from zmk_locale_generator import LayoutHeaderGenerator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default="out",
        help="output directory (default: ./out)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="print debug info")
    parser.add_argument("-z", "--zmk", type=Path, help="path to ZMK repo")

    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    generator = LayoutHeaderGenerator(args.zmk)

    for keyboard in get_keyboards():
        out_path = args.out / keyboard.filename

        print(f"{shorten_path(keyboard.path)} -> {out_path}")

        with keyboard.path.open("r", encoding="utf-8") as infile:
            with out_path.open("w", encoding="utf-8") as outfile:
                generator.write_header(
                    infile,
                    outfile,
                    prefix=keyboard.prefix,
                    license_path=keyboard.license,
                )


def shorten_path(path: Path):
    try:
        return path.relative_to(Path.cwd())
    except ValueError:
        return path


if __name__ == "__main__":
    main()
