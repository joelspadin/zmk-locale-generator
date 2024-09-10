#!/usr/bin/env python3

import argparse
import logging
import sys
from pathlib import Path
from typing import Protocol, TextIO

from .generator import LayoutHeaderGenerator
from .keyboards import get_keyboards
from .update_codepoints import update_codepoints

REPO_PATH = Path(__file__).parent

KEYBOARDS_PATH = REPO_PATH / "keyboards/keyboards.yaml"


class GenerateAllArgs(Protocol):
    out: Path
    keyboards: Path
    zmk: Path | None


class GenerateSingleArgs(Protocol):
    prefix: str
    path: Path
    license: Path | None
    out: Path | None
    zmk: Path | None


class UpdateCodepointsArgs(Protocol):
    out: Path | None


def shorten_path(path: Path, base: Path):
    try:
        return path.relative_to(base)
    except ValueError:
        return path


def generate_all(args: GenerateAllArgs):
    args.out.mkdir(parents=True, exist_ok=True)
    base_path = args.keyboards.parent

    generator = LayoutHeaderGenerator(args.zmk)

    for keyboard in get_keyboards(args.keyboards):
        out_path = args.out / keyboard.filename

        print(f"{shorten_path(keyboard.path, base_path)} -> {out_path}")

        with keyboard.path.open("r", encoding="utf-8") as infile:
            with out_path.open("w", encoding="utf-8") as outfile:
                generator.write_header(
                    infile,
                    outfile,
                    prefix=keyboard.prefix,
                    license_path=keyboard.license,
                )


def generate_single(args: GenerateSingleArgs):
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


def update_codepoints_func(args: UpdateCodepointsArgs):
    update_codepoints(args.out)


def main():
    parser = argparse.ArgumentParser(
        description="Generate ZMK headers for different locale's keyboard layouts"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="print debug info")

    subparsers = parser.add_subparsers()

    batch = subparsers.add_parser("all", help="generate headers for all locales")
    batch.set_defaults(func=generate_all)
    batch.add_argument(
        "-k",
        "--keyboards",
        type=Path,
        default=KEYBOARDS_PATH,
        help="YAML file containing layout definitions",
    )
    batch.add_argument(
        "-o",
        "--out",
        type=Path,
        default="out",
        help="output directory (default: ./out)",
    )
    batch.add_argument(
        "-z", "--zmk", type=Path, help="path to ZMK repo to override keys.h"
    )

    single = subparsers.add_parser(
        "single", help="generate a header for a single locale"
    )
    single.set_defaults(func=generate_single)
    single.add_argument("prefix", help="prefix for key names")
    single.add_argument("path", type=Path, help="path to CLDR keyboard layout XML file")
    single.add_argument("--license", "-l", type=Path, help="path to license file")
    single.add_argument("-o", "--out", type=Path, help="output path (default: stdout)")
    single.add_argument(
        "-z", "--zmk", type=Path, help="path to ZMK repo to override keys.h"
    )

    update = subparsers.add_parser(
        "update_codepoints", help="update the file that assigns names to codepoints"
    )
    update.set_defaults(func=update_codepoints_func)
    update.add_argument(
        "out",
        type=Path,
        nargs="?",
        help="path to codepoints.yaml (default: embedded file)",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    args.func(args)


if __name__ == "__main__":
    main()
