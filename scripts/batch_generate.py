#!/usr/bin/env python3

"""
Runs zmk_locale_generator for all locales in locales.yaml.
"""

import argparse
import logging
from multiprocessing import Pool
from pathlib import Path
import sys
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent))

from batch_locales import get_locales, Locale


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

    extra_args = []
    if args.verbose:
        extra_args.append("-v")
    if args.zmk:
        extra_args += ["--zmk", args.zmk]

    args.out.mkdir(parents=True, exist_ok=True)

    with Pool() as pool:
        output = pool.starmap(generate, ((entry, args) for entry in get_locales()))

    for locale, text in output:
        if text:
            print(f"===== {locale.upper()} =====")
            print(text)


def generate(entry: Locale, args):
    command = [sys.executable, "-m", "zmk_locale_generator", entry.locale]
    command += ["--layout", entry.layout]
    command += ["--out", args.out / entry.filename]
    if args.verbose:
        command.append("-v")
    if args.zmk:
        command += ["--zmk", args.zmk]

    return entry.locale, subprocess.check_output(
        command, stderr=subprocess.STDOUT, encoding="utf-8"
    )


if __name__ == "__main__":
    main()
