import importlib.resources
import logging
import shutil
from pathlib import Path

from screen_animator import example

log = logging.getLogger(__name__)


def copy_examples() -> None:
    """Copies `example` files to working directory."""
    for file_path in importlib.resources.files(example).iterdir():
        print(f"Copying {file_path.name} to {Path.cwd().joinpath(file_path.name)}")
        shutil.copy2(
            str(file_path), file_path.name
        )  # `str` is used purely for type-checking
