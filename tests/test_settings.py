from itertools import pairwise
from string import ascii_letters

import pygame as pg
import pytest
from pytest import MonkeyPatch

from screen_animator.settings import ImageLoader, SettingsManager


@pytest.fixture
def mock_image_load(monkeypatch: MonkeyPatch) -> None:
    def mock_load_image(*args, **kwargs) -> pg.Surface:
        return pg.Surface((20, 10))

    monkeypatch.setattr(ImageLoader, "load_image", mock_load_image)


class TestSettingsManager:
    @pytest.mark.parametrize("key", ["color", "bg_color"])
    def test_set_colors(self, key: str, settings_manager: SettingsManager) -> None:
        """Colors are set to a color option provided in settings."""
        settings_manager.set_colors()
        settings = settings_manager.settings

        assert getattr(settings.runtime, key) in settings.colors

    def test_set_outline_color(self, settings_manager: SettingsManager) -> None:
        """Outline color set to color option provided in settings."""
        settings_manager.set_colors()
        settings = settings_manager.settings

        assert settings.runtime.outline_color in settings.messages.outline_colors

    def test_set_font(self, settings_manager: SettingsManager) -> None:
        """`Font` instance created and added to settings."""
        settings_manager.set_font()

        assert isinstance(settings_manager.settings.runtime.font, pg.Font)

    @pytest.mark.parametrize("sizes", [(10, 10), (20, 30), (50, 50), (80, 130)])
    def test_set_font_size(
        self, sizes: tuple[int, int], settings_manager: SettingsManager
    ) -> None:
        """Font size is between limits specified."""
        settings = settings_manager.settings
        settings.messages.sizes = sizes
        settings_manager.set_font()

        assert min(sizes) <= settings.runtime.font.point_size <= max(sizes)

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

    def test_generate_text_return_type(self, settings_manager: SettingsManager) -> None:
        """Message strings generated are of correct type."""
        assert isinstance(settings_manager.generate_message_text(), str)

    def test_generate_text_sequential_no_repeats(
        self, settings_manager: SettingsManager
    ) -> None:
        """Sequential strings are generated."""
        message_list = list(ascii_letters)
        message_settings = settings_manager.settings.messages
        message_settings.sequential = True
        message_settings.messages = message_list

        messages = [settings_manager.generate_message_text()]
        for _ in message_list[:-1]:
            messages.append(settings_manager.generate_message_text())

        assert all(message1 != message2 for message1, message2 in pairwise(messages))

    def test_generate_text_sequential_deplete_options(
        self, settings_manager: SettingsManager
    ) -> None:
        """Sequential string list gets exhausted."""
        message_list = list(ascii_letters)
        message_settings = settings_manager.settings.messages
        message_settings.sequential = True
        message_settings.messages = message_list

        settings_manager.generate_message_text()
        remaining_messages = len(settings_manager._messages)
        while remaining_messages > 0:
            settings_manager.generate_message_text()
            remaining_messages -= 1

        assert not settings_manager._messages

    def test_generate_text_non_sequential_no_deplete_options(
        self, settings_manager: SettingsManager
    ) -> None:
        """Non-sequential string list does not get exhausted."""
        message_list = list(ascii_letters)
        message_settings = settings_manager.settings.messages
        message_settings.sequential = False
        message_settings.messages = message_list

        list_lengths = []
        for _ in range(10):
            settings_manager.generate_message_text()
            list_lengths.append(len(settings_manager._messages))

        assert all(list_length == len(message_list) for list_length in list_lengths)

    def test_load_images(
        self,
        mock_image_load,
        settings_manager: SettingsManager,
    ) -> None:
        """Images are loaded and stored in settings."""
        settings_manager._load_images()
        settings = settings_manager.settings

        assert len(settings.runtime.images) == len(settings.images.sources)
