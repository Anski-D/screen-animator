import logging
import random
from collections.abc import Iterable, MutableMapping
from os import PathLike
from pathlib import Path
from typing import Any

import pygame as pg
from mergedeep import merge

from screen_animator.image_loading import ImageLoader

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

log = logging.getLogger(__name__)


class SettingsImporter:
    """
    Imports settings from TOML files and validates, ready for further use.

    Methods
    -------
    import_settings
        Imports the settings from specified files and validates imported values.
    """

    _settings: MutableMapping[str, Any]

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def import_settings(
        self, settings_files: Iterable[str | PathLike]
    ) -> MutableMapping[str, Any]:
        """
        Imports the settings from specified files, validates, and stores and
        returns a dictionary.

        Parameters
        ----------
        settings_files
            Paths to the TOML files containing settings.

        Returns
        -------
        dict
            The imported and validated settings.
        """
        self._read_settings(settings_files)
        self._validate_settings()
        log.info("Converting certain lists to tuples")
        self._settings = self._convert_colors_to_tuples(self._settings)

        return self._settings

    def _read_settings(self, settings_paths: Iterable[str | PathLike]) -> None:
        settings_dicts = []
        for settings_path in settings_paths:
            log.info("Reading settings from %s...", settings_path)
            with Path(settings_path).open("rb") as file:
                settings_dicts.append(tomllib.load(file))

        self._settings = merge(*settings_dicts)
        log.info("Collated settings:\n\t%s", self._settings)

    def _validate_settings(self) -> None:
        log.info("Validating input file matches expected format")
        match self._settings:
            case {
                "colors": list(),
                "messages": {
                    "messages": list() | str(),
                    "separator": str(),
                    "typeface": str(),
                    "sizes": list(),
                    "bold": bool(),
                    "italic": bool(),
                    "anti-aliasing": bool(),
                    "scroll_speed": int(),
                    "outline_width": int(),
                    "outline_copies": int(),
                    "outline_colors": list(),
                    "start_middle": bool(),
                },
                "images": {
                    "sources": list(),
                    "number": int(),
                    "reposition_attempts": int(),
                },
                "timings": {
                    "fps": int() | float(),
                    "image_change_time": int() | float(),
                    "color_change_time": int() | float(),
                },
            }:
                log.info("Validation successful")
            case _:
                raise ValueError(f"Invalid configuration {self._settings}")

    def _convert_colors_to_tuples(self, input_item):
        match input_item:
            case [int(), int(), int()] | [int(), int()] | [str(), int()]:
                return tuple(input_item)
            case list():
                return [self._convert_colors_to_tuples(item) for item in input_item]
            case MutableMapping():
                return {
                    key: self._convert_colors_to_tuples(value)
                    for key, value in input_item.items()
                }
            case _:
                return input_item


class SettingsManager:
    """
    Reads in settings, manipulates, and provides provisions for generating dynamic settings.

    Methods
    -------
    set_colors
        Randomly set the background, text, and text outline color.
    generate_message_text
        Create string with combined random message and separator
    set_font
        Create the `pygame` font instance for rendering text.
    """

    _settings: MutableMapping[str, Any]

    def __init__(self, settings_files: Iterable[str | PathLike]) -> None:
        """
        Import settings from specified file and set initial settings.

        Parameters
        ----------
        settings_files
            Paths to settings files.
        """
        self._settings_files = settings_files
        self._import_settings()
        self.set_colors()
        self.set_font()
        self._load_images()
        self._settings["timings"]["fps_actual"] = self._settings["timings"]["fps"]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._settings_files})"

    @property
    def settings(self) -> MutableMapping[str, Any]:
        """Dictionary of all settings."""
        return self._settings

    def set_colors(self) -> None:
        """Set background, text, and text outline colors from the available options
        in the settings provided."""
        if self._settings.get("bg") is None:
            self._settings["bg"] = {}
        self._settings["bg"]["color"] = random.choice(self._settings["colors"])
        log.debug("Set background color as: %s", self._settings["bg"]["color"])

        messages_dict = self._settings["messages"]
        messages_dict["color"] = random.choice(self._settings["colors"])
        while messages_dict["color"] == self._settings["bg"]["color"]:
            messages_dict["color"] = random.choice(self._settings["colors"])
        log.debug("Set text color as: %s", messages_dict["color"])

        match messages_dict["outline_colors"]:
            case (int(), int(), int()) as outline_color:
                pass
            case outline_colors:
                outline_color = random.choice(outline_colors)
        messages_dict["outline_color"] = outline_color
        log.debug("Set outline color as: %s", messages_dict["outline_color"])

    def generate_message_text(self) -> str:
        """
        Get a message from the available options.

        Returns
        -------
        str
            The selected message.
        """
        messages_dict = self._settings["messages"]

        return f"{random.choice(messages_dict['messages'])}{messages_dict['separator']}"

    def set_font(self) -> None:
        """Create the `pygame` font instance for rendering messages."""
        log.debug("Setting `pygame` font for text rendering")
        messages_dict = self._settings["messages"]
        messages_dict["size"] = random.randint(
            min(messages_dict["sizes"]), max(messages_dict["sizes"])
        )
        messages_dict["font"] = pg.font.Font(
            pg.font.match_font(
                messages_dict["typeface"],
                bold=messages_dict["bold"],
                italic=messages_dict["italic"],
            ),
            messages_dict["size"],
        )

    def _import_settings(self) -> None:
        importer = SettingsImporter()
        self._settings = importer.import_settings(self._settings_files)

    def _load_images(self):
        images_dict = self._settings["images"]
        if len(images_dict["sources"]) >= 1:
            log.info("Loading and scaling images for rendering")
            images_dict["images"] = []
            image_loader = ImageLoader()
            for image_src, width in images_dict["sources"]:
                image = image_loader.load_image(image_src, width)
                if image is not None:
                    images_dict["images"].append(image)
