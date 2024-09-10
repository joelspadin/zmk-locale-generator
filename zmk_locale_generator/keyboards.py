import re
from dataclasses import dataclass
from pathlib import Path

from ruamel.yaml import YAML

ROOT_PATH = Path(__file__).parent
CLDR_LICENSE_PATH = ROOT_PATH / "keyboards/cldr/unicode-license.txt"


@dataclass
class Keyboard:
    """Keyboard layout definition"""

    filename: str  # Header file name
    license: Path | None  # path to license file
    path: Path  # path to CLDR keyboard file
    prefix: str  # Locale prefix


def get_keyboards(keyboards_path: Path):
    """
    Get a list of keyboards from a YAML file.

    :param keyboards_path: Path to a YAML file containing an array of Keyboard objects.
    """

    yaml = YAML()
    locales: list[dict[str, str]] = yaml.load(keyboards_path)
    base_path = keyboards_path.parent

    for entry in locales:
        path = (base_path / entry["path"]).resolve()
        prefix = entry.get("prefix", _get_file_prefix(path))
        license_text = entry.get("license", CLDR_LICENSE_PATH)
        filename = f"keys_{entry.get('filename', prefix)}.h"

        if not isinstance(license_text, (str, Path)):
            raise TypeError(f"Failed to determine license for {path}")

        yield Keyboard(
            filename=filename, license=Path(license_text), path=path, prefix=prefix
        )


def _get_file_prefix(path: Path):
    if match := re.match(r"\w+", path.name):
        return match.group(0)

    raise ValueError(f'{path.name} must start with letters or have "locale" key')
