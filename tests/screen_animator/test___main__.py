import pytest
import pygame as pg

from screen_animator.__main__ import _set_display_size


class TestSetDisplaySize:
    def test_set_display_return_tuple_input(self) -> None:
        """Display returned when tuple input."""
        assert isinstance(_set_display_size((800, 400)), pg.Surface)

    def test_set_display_size_tuple_input(self) -> None:
        """Display size when tuple input."""
        display_size = (800, 400)

        assert _set_display_size(display_size).size == display_size

    def test_set_display_return_none_input(self) -> None:
        """Display returned when `None` input."""
        assert isinstance(_set_display_size(None), pg.Surface)

    def test_set_display_size_none_input(self) -> None:
        """Display size when `None` input."""
        assert _set_display_size(None).size in pg.display.get_desktop_sizes()
