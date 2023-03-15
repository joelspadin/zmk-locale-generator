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

```devicetree
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

Install dependencies with Pip:

```sh
pip3 install -r requirements.txt
```

### Usage

```sh
python3 -m zmk_locale_generator --help
```

To print out the header for a locale:

```sh
python3 -m zmk_locale_generator <PREFIX> <CLDR_FILE>
```

To write the header to a file, use `--out`. For example:

```sh
python3 -m zmk_locale_generator DE cldr/keyboards/windows/de-t-k0-windows.xml --out keys_de.h
```

By default, this uses a version of ZMK's keys.h from the ZMK submodule. To use a different version of ZMK, specify `--zmk` with the path to ZMK.

### Batch Generation

The following command will generate a header for every keyboard layout defined in [keyboards/keyboards.yaml](keyboards/keyboards.yaml):

```sh
./scripts/batch_generate.py
```

## Contributing

PRs are welcome, especially to add new keyboard layouts or improve key names.

### Add a Keyboard Layout

First, edit [keyboards/keyboards.yaml](keyboards/keyboards.yaml) and add a new item to the list:

1. Create a keyboard layout file in CLDR format and place it in the `keyboards` directory, or select an existing file from the `cldr` repo.
2. Add a new item to `keyboards.yaml` with a `path` key followed by the relative path from `keyboards.yaml` to the file.
3. If key names should be prefixed with something different than the first word of the file name, add a `prefix` key followed by the prefix.
4. If the generated header name should be different than the prefix or there is already another keyboard layout using the same prefix, add a `filename` key followed by a unique name. (The script will automatically add `keys_` to the beginning and `.h` to the end, so you should not include those in the name.)
5. If the layout has its own license, add a `license` key followed by the path to a text file containing the license.
   - Files from the `cldr` repo will automatically use the Unicode license.
   - If a license is not specified for a file in the `keyboards` directory, it uses the ZMK license.

For example:

```yaml
- path: colemak.xml
  prefix: cm
  filename: colemak
  license: colemak-LICENSE.txt
```

### Update Codepoints

Next, run [scripts/update_codepoints.py] to make sure [codepoints.yaml](zmk_locale_generator/codepoints.yaml) includes entries for all characters used in the keyboard layout:

```sh
./scripts/update_codepoints.py zmk_locale_generator/codepoints.yaml
```

Finally, edit [codepoints.yaml](zmk_locale_generator/codepoints.yaml) and assign names to any codepoints that were added. (New codepoints will have `''` for the name.)
