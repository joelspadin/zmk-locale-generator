from dataclasses import dataclass
from pathlib import Path
import re
from typing import Optional
from ruamel.yaml import YAML

REPO_PATH = Path(__file__).parent.parent

KEYBOARDS_PATH = REPO_PATH / "keyboards/keyboards.yaml"
CLDR_PATH = REPO_PATH / "cldr"
CLDR_LICENSE_PATH = CLDR_PATH / "unicode-license.txt"


@dataclass
class Keyboard:
    filename: str  # Header file name
    license: Optional[Path]  # path to license file
    path: Path  # path to CLDR keyboard file
    prefix: str  # Locale prefix


def get_keyboards():
    """
    Get the list of keyboards from keyboards.yaml.
    """
    yaml = YAML()
    locales: list[dict[str, str]] = yaml.load(KEYBOARDS_PATH)
    base_path = KEYBOARDS_PATH.parent

    for entry in locales:
        path = (base_path / entry["path"]).resolve()
        prefix = entry.get("prefix", _get_file_prefix(path))
        license = entry.get("license", None)
        filename = f"keys_{entry.get('filename', prefix)}.h"

        if license is None and path.is_relative_to(CLDR_PATH):
            license = CLDR_LICENSE_PATH

        yield Keyboard(filename=filename, license=license, path=path, prefix=prefix)


def _get_file_prefix(path: Path):
    if match := re.match("\w+", path.name):
        return match.group(0)

    raise Exception(f'{path.name} must start with letters or have "locale" key')
