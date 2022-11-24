from dataclasses import dataclass
from pathlib import Path
from ruamel.yaml import YAML

LOCALES_PATH = Path(__file__).parent / "locales.yaml"


@dataclass
class Locale:
    locale: str  # Locale prefix
    layout: str  # kbdlayout.info layout name
    filename: str  # Header file name


def get_locales():
    """
    Get the list of locales from locales.yaml.
    """
    yaml = YAML()
    locales = yaml.load(LOCALES_PATH)

    for entry in locales:
        locale = entry.get("locale")
        layout = entry.get("layout", locale)
        filename = f"keys_{entry.get('filename', locale)}.h"

        yield Locale(locale, layout, filename)
