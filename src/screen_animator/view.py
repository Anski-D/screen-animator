import logging
from collections.abc import Mapping
from typing import Any

import pygame as pg

from screen_animator.model import Model

from .listener import Listener

log = logging.getLogger(__name__)


class View(Listener):
    """
    Display for the `screen_animator` model.

    Attributes
    ----------
    perimeter
        Defines outer perimeter of the display.

    Methods
    -------
    update
        Update the display.
    notify
        Tell the display to update.
    """

    perimeter: pg.Rect

    def __init__(
        self,
        model: Model,
        display: pg.Surface,
        settings: Mapping[str, Any],
        rotated: bool = False,
    ) -> None:
        """
        Set-up some initial parameters for the display.

        Parameters
        ----------
        model
            Model to be displayed.
        display
            `pygame` display.
        settings
            User-defined settings.
        rotated : optional
            Flips the display across the horizontal axis (default is False, not flipped).
        """
        self._model = model
        self._display = display
        self._settings = settings
        self._rotated = rotated
        log.info("Creating %s", self)

        self._set_bg()
        log.info("%s initialization complete", type(self).__name__)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._model}, {self._display}, {type(self._settings).__name__}(), {self._rotated})"

    def update(self) -> None:
        """Update the display."""
        self._set_bg()
        for group in self._model.item_groups:
            for item in group.sprites():
                self._display.blit(item.content, item.rect)

        if self._rotated:
            self._display.blit(pg.transform.rotate(self._display, 180), (0, 0))

        pg.display.flip()

    def notify(self) -> None:
        """Notify view of change to the model."""
        self.update()

    def _set_bg(self) -> None:
        self._display.fill(self._settings["bg"]["color"])
