# ZMK Locale Generator

This Python module generates localized keyboard layout headers for [ZMK](https://zmk.dev) using data from [kbdlayout.info](https://kbdlayout.info/).

Python 3.10 or newer is required.

## Usage

```sh
python -m zmk_locale_generator --help
```

To print out the header for a locale:

```sh
python -m zmk_locale_generator <LOCALE>
```

To write the header to a file, use `--out`. For example:

```sh
python -m zmk_locale_generator DE --out keys_de.h
```

By default, this uses a version of ZMK's keys.h from the ZMK submodule. To use a different version of ZMK, specify `--zmk` with the path to ZMK.

If the locale code does not match the layout name on kbdlayout.info, specify `--layout` with the layout name.
