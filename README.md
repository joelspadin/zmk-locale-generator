# ZMK Locale Generator

This Python module generates localized keyboard layout headers for [ZMK](https://zmk.dev) using data from the [Unicode CLDR](https://github.com/unicode-org/cldr) or custom layouts in CLDR format.

Python 3.10 or newer is required.

## Using Generated Headers

First, determine what keyboard layout your OS is set to, then [download the matching header from the latest release](https://github.com/joelspadin/zmk-locale-generator/releases) or follow [Generating Headers](#generating-headers) to build the header yourself. Place the header in your ZMK config repo's `config/` directory alongside your `.keymap` file.

Next, edit your `.keymap` file and add an include statement near the top. For example, if the header is named `keys_dvorak.h`, you would add

```c
#include "keys_dvorak.h"
```

You can now use the key codes defined in the header in your keymap bindings. For example:

```dts
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>
#include "keys_dvorak.h"

/ {
  keymap {
    compatible = "zmk,keymap";

    default_layer {
      bindings = <
        &kp DV_GRAVE &kp DV_N1 &kp DV_N2      ...
        &kp TAB       &kp DV_SQT &kp DV_COMMA ...
        &kp CAPS       &kp DV_A &kp DV_O      ...
        &kp LSHIFT      &kp DV_SEMI &kp DV_Q  ...
        &kp LCTRL &kp LGUI &kp LALT           ...
      >;
    }
  };
};
```

## Generating Headers

### Setup

Install [Pipx](https://pipx.pypa.io/stable/), then use it to install ZMK Locale Generator:

```sh
pipx install https://github.com/joelspadin/zmk-locale-generator.git
```

### Usage

The following command will generate a header for every keyboard layout defined in [keyboards/keyboards.yaml](keyboards/keyboards.yaml) and write them to a directory named `out`:

```sh
zmk_locale_generator all
```

The following command will generate a header for a single locale:

```sh
zmk_locale_generator single <PREFIX> <CLDR_FILE>
```

Where:

- `<PREFIX>` is a prefix to attach to all key code names, e.g. `DE` for German.
- `<CLDR_FILE>` is the path to an XML file formatted similar to the ones from the [Unicode CLDR](https://github.com/unicode-org/cldr/tree/maint/maint-43/keyboards).

For example:

```sh
zmk_locale_generator single DE de-t-k0-windows.xml
```

This will print the generated header to stdout. To write the header to a file instead, use `--out`. For example:

```sh
zmk_locale_generator single DE de-t-k0-windows.xml --out keys_de.h
```

For more usage information, run

```sh
zmk_locale_generator --help
```

## Contributing

PRs are welcome, especially to add new keyboard layouts or improve key names.

### Setup

Optional: create a [venv](https://docs.python.org/3/library/venv.html) to ensure this project doesn't conflict with global packages:

```sh
python3 -m venv .venv
```

After creating the venv, [activate it](https://docs.python.org/3/library/venv.html#how-venvs-work) as necessary for the shell you are using.

Install the package in editable mode:

```sh
pip install -e .[dev]
```

Optional: install a Git pre-commit hooks and additional code checkers. This will check your code as you commit it, so you don't have to wait for feedback from GitHub when you make a pull request.

[Install Node.js](https://nodejs.org/en), then run:

```sh
npm install
```

### Add a Keyboard Layout

First, edit [zmk_locale_generator/keyboards/keyboards.yaml](zmk_locale_generator/keyboards/keyboards.yaml) and add a new item to the list:

1. Create a keyboard layout file in CLDR format and place it in the `keyboards` directory, or select an existing file from the `cldr` repo.
2. Add a new item to `keyboards.yaml` with a `path` key followed by the relative path from `keyboards.yaml` to the CLDR file.
3. If key names should be prefixed with something different than the first word of the file name, add a `prefix` key followed by the prefix.
4. If the generated header name should be different than the prefix or there is already another keyboard layout using the same prefix, add a `filename` key followed by a unique name. (The script will automatically add `keys_` to the beginning and `.h` to the end, so you should not include those in the name.)
5. If the layout has its own license, add a `license` key followed by the relative path to a text file containing the license.
   - If a license is not specified, it uses the Unicode CLDR license.

For example:

```yaml
- path: colemak.xml
  prefix: cm
  filename: colemak
  license: colemak-LICENSE.txt
```

### Update Codepoints

Next, run `zmk_locale_generator update_codepoints` to make sure [codepoints.yaml](zmk_locale_generator/codepoints.yaml) includes entries for all characters used in the keyboard layout:

```sh
zmk_locale_generator update_codepoints
```

Finally, edit [codepoints.yaml](zmk_locale_generator/codepoints.yaml) and assign names to any codepoints that were added. (New codepoints will have `''` for the name.)
