from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq, CommentedMap


CODEPOINTS_PATH = Path(__file__).parent / "codepoints.yaml"


def get_codepoint_names() -> dict[str, str | list[str]]:
    """
    Get a mapping of codepoints to a single name or list of names from
    codepoints.yaml.
    """
    codepoints = get_codepoint_names_raw()

    flattened = (item for block in codepoints for item in block.items())

    return {k: v for k, v in flattened if v}


def get_codepoint_names_raw() -> CommentedSeq[CommentedMap[str, str | list[str]]]:
    """
    Get the raw data from codepoints.yaml for round-trip editing.
    """
    with CODEPOINTS_PATH.open("r", encoding="utf-8") as f:
        yaml = YAML()
        return yaml.load(f)
