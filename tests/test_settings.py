from collections.abc import Callable

import pygame as pg
import pytest

from screen_animator.settings import SettingsManager, Settings, convert_lists_to_tuples
from screen_animator.settings import ImageLoader


def test_convert_lists_to_tuples(dummy_settings_dict: dict, dummy_settings_dict_with_tuples: dict) -> None:
    """Lists with int values are converted to tuples."""

    assert convert_lists_to_tuples(dummy_settings_dict) == dummy_settings_dict_with_tuples


@pytest.fixture
def settings_manager(monkeypatch, mock_settings: Callable[[], Settings]) -> SettingsManager:
    def mock_set_initial_settings(*args, **kwargs) -> None:
        return None

    monkeypatch.setattr(SettingsManager, "_set_initial_settings", mock_set_initial_settings)

    return SettingsManager([""])


@pytest.fixture
def mock_image_load(monkeypatch) -> None:
    def mock_load_image(*args, **kwargs) -> pg.Surface:
        return pg.Surface((20, 10))

    monkeypatch.setattr(ImageLoader, "load_image", mock_load_image)


class TestSettingsManager:
    @pytest.mark.parametrize("group", ["bg", "messages"])
    def test_set_colors(
        self, group: str, settings_manager: SettingsManager
    ) -> None:
        """Colors are set to a color option provided in settings."""
        settings_manager.set_colors()
        settings = settings_manager.settings

        assert getattr(settings, group).color in settings.colors

    def test_set_outline_color(self, settings_manager: SettingsManager) -> None:
        """Outline color set to color option provided in settings."""
        settings_manager.set_colors()
        messages = settings_manager.settings.messages

        assert messages.outline_color in messages.outline_colors

    def test_set_font(self, settings_manager: SettingsManager) -> None:
        """`Font` instance created and added to settings."""
        settings_manager.set_font()

        assert isinstance(settings_manager.settings.messages.font, pg.Font)

    @pytest.mark.parametrize("sizes", [(10, 10), (20, 30), (50, 50), (80, 130)])
    def test_set_font_size(
        self, sizes: tuple[int, int], settings_manager: SettingsManager
    ) -> None:
        """Font size is between limits specified."""
        messages = settings_manager.settings.messages
        messages.sizes = list(sizes)
        settings_manager.set_font()

        assert min(sizes) <= messages.font.point_size <= max(sizes)

    @pytest.mark.parametrize("repeat", range(5))
    def test_generate_text(
        self,
        repeat: int,
        settings_manager: SettingsManager,
        dummy_settings_dict_with_tuples: dict,
    ) -> None:
        """Concatenated message strings are generated."""
        messages_dict = dummy_settings_dict_with_tuples["messages"]

        assert settings_manager.generate_message_text() in [
            f"{message}{messages_dict['separator']}"
            for message in messages_dict["messages"]
        ]

    def test_generate_text_return_type(
        self, settings_manager: SettingsManager
    ) -> None:
        """Message strings generated are of correct type."""
        assert isinstance(settings_manager.generate_message_text(), str)

    def test_load_images(
        self,
        mock_image_load,
        settings_manager: SettingsManager,
    ) -> None:
        """Images are loaded and stored in settings."""
        settings_manager._load_images()
        images = settings_manager.settings.images

        assert len(images.images) == len(images.sources)
