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

### Batch Generation

The following command will generate a header for every locale defined in [scripts/locales.yaml](scripts/locales.yaml):

```sh
./scripts/batch_generate.py
```

## Contributing

PRs are welcome, especially to add new locales or improve key names.

### Add a Locale/Layout

Currently, all layout data comes from [kbdlayout.info](https://kbdlayout.info). If you'd like to add support for a layout which isn't defined there, please submit an issue on GitHub and we can discuss options for including it.

First, edit [scripts/locales.yaml](scripts/locales.yaml) and add a new item to the list:

1. Add a new line with `- locale: ` followed by an abbreviation for the locale which will prefix all key names. Typically this should be an [ISO 639](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) two or three-letter code.
1. Open `https://kbdlayout.info/{locale}` in a web browser (replacing `{locale}` with the abbreviation from the previous step). If this does _not_ open a page for the layout you want to add, go back to the [home page](https://kbdlayout.info), find the page for the correct layout, and then add `layout: ` followed by the part of the URL after the last slash. For example, if the URL is [https://kbdlayout.info/kbdus](https://kbdlayout.info/kbdus), add `layout: kbdus`.
1. If the abbreviation from step 1 is used by multiple locales (e.g. layout variations for the same language) or is not descriptive enough, you can add `filename: ` followed by a new name for the header file. The script will automatically add `keys_` to the beginning and `.h` to the end, so you should not include those in the name.

Next, run [scripts/update_codepoints.py] to make sure [codepoints.yaml](zmk_locale_generator/codepoints.yaml) includes entries for all characters used in the keyboard layout:

```sh
./scripts/update_codepoints.py zmk_locale_generator/codepoints.yaml
```

Finally, edit [codepoints.yaml](zmk_locale_generator/codepoints.yaml) and assign names to any codepoints that were added.
