import logging
import random
import tomllib
from collections.abc import Iterable
from pathlib import Path

import pygame as pg
from mergedeep import merge
from pydantic import BaseModel, ConfigDict

from screen_animator.image_loading import ImageLoader

log = logging.getLogger(__name__)


class Messages(BaseModel):
    messages: list[str]
    separator: str = "    "
    typeface: str = "freeserif"
    sizes: tuple[int, int]
    bold: bool = True
    italic: bool = False
    anti_aliasing: bool = False
    scroll_speed: int
    outline_width: int = 0
    outline_copies: int = 0
    outline_colors: list[tuple[int, int, int]] = [(0, 0, 0)]
    start_middle: bool = True
    sequential: bool = False


class Images(BaseModel):
    sources: list[tuple[str, int]]
    number: int
    reposition_attempts: int = -1


class Timings(BaseModel):
    fps: int = 30
    image_change_time: int
    color_change_time: int


class RuntimeSettings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    color: tuple[int, int, int] = (255, 255, 255)
    bg_color: tuple[int, int, int] = (0, 0, 0)
    outline_color: tuple[int, int, int] = (127, 127, 127)
    font: pg.Font | None = None
    images: list[pg.Surface] = []
    fps_actual: int = 0


class Settings(BaseModel):
    colors: list[tuple[int, int, int]]
    messages: Messages
    images: Images
    timings: Timings
    runtime: RuntimeSettings = RuntimeSettings()


def import_settings(settings_paths: Iterable[Path | str]) -> Settings:
    """Imports settings from defined files and validates input"""
    settings_dicts = []
    for settings_path in settings_paths:
        log.info("Reading settings from %s...", settings_path)
        with Path(settings_path).open("rb") as file:
            settings_dicts.append(tomllib.load(file))

    settings = merge(*settings_dicts)
    log.info("Collated settings:\n\t%s", settings)

    return Settings.model_validate(settings)


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

    _settings: Settings

    def __init__(self, settings_files: Iterable[Path | str]) -> None:
        """
        Import settings from specified file and set initial settings.

        Parameters
        ----------
        settings_files
            Paths to settings files.
        """
        self._settings_files = settings_files
        self._settings = import_settings(self._settings_files)
        self._messages = []
        self._set_initial_settings()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._settings_files})"

    @property
    def settings(self) -> Settings:
        """Dictionary of all settings."""
        return self._settings

    def set_colors(self) -> None:
        """Set background, text, and text outline colors from the available options
        in the settings provided."""
        self._settings.runtime.bg_color = random.choice(self._settings.colors)
        log.debug("Set background color to: %s", self._settings.runtime.bg_color)

        self._settings.runtime.color = random.choice(self._settings.colors)
        while self._settings.runtime.color == self._settings.runtime.bg_color:
            self._settings.runtime.color = random.choice(self._settings.colors)
        log.debug("Set text color to: %s", self._settings.runtime.color)

        self._settings.runtime.outline_color = random.choice(
            self._settings.messages.outline_colors
        )
        log.debug("Set outline color as: %s", self._settings.runtime.outline_color)

    def generate_message_text(self) -> str:
        """
        Get a message from the available options.

        Returns
        -------
        str
            The selected message.
        """
        if not self._messages:
            self._messages = list(self._settings.messages.messages)
            random.shuffle(self._messages)

        message = (
            self._messages.pop()
            if self._settings.messages.sequential
            else random.choice(self._messages)
        )

        return f"{message}{self._settings.messages.separator}"

    def set_font(self) -> None:
        """Create the `pygame` font instance for rendering messages."""
        log.debug("Setting `pygame` font for text rendering")
        size = random.randint(
            min(self._settings.messages.sizes), max(self._settings.messages.sizes)
        )
        self._settings.runtime.font = pg.font.Font(
            pg.font.match_font(
                self._settings.messages.typeface,
                self.settings.messages.bold,
                self.settings.messages.italic,
            ),
            size,
        )

    def _set_initial_settings(self) -> None:
        self.set_colors()
        self.set_font()
        self._load_images()

    def _load_images(self):
        if len(self._settings.images.sources) >= 1:
            log.info("Loading and scaling images for rendering")
            image_loader = ImageLoader()
            for source, width in self._settings.images.sources:
                image = image_loader.load_image(source, width)
                if image is not None:
                    self._settings.runtime.images.append(image)
