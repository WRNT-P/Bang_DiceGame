
import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.absolute()


def get_resource_path(relative_path: str) -> str:

    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))
