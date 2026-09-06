import pygame as pg
import pytest

from screen_animator.item_groups import ItemGroup
from screen_animator.model import Model
from screen_animator.settings import SettingsManager
from screen_animator.speed_changer import SpeedChanger


class TestModel:
    @pytest.fixture
    def patch_item_group_init(self, monkeypatch) -> None:
        """Patch ItemGroup so that its init dunder just returns None."""
        monkeypatch.setattr(ItemGroup, "__init__", lambda *args, **kwargs: None)
        ItemGroup.__abstractmethods__ = set()

    @pytest.fixture
    def patch_speed_changer_init(self, monkeypatch) -> None:
        """Patch SpeedChanger so that its init dunder just returns None."""
        monkeypatch.setattr(SpeedChanger, "__init__", lambda *args, **kwargs: None)

    @pytest.fixture
    def example_model(
        self,
        example_settings_manager: SettingsManager,
        example_perimeter: pg.Rect,
        patch_item_group_init,
        patch_speed_changer_init,
    ) -> Model:
        """Create example Model"""
        return Model(
            example_settings_manager, [ItemGroup for _ in range(3)], example_perimeter
        )

    def test_init_item_group(self, example_model: Model) -> None:
        """init dunder creates ItemGroup instances."""
        model = example_model

        assert all(
            isinstance(item_group, ItemGroup) for item_group in model.item_groups
        )

    def test_init_event_type_int(self, example_model: Model) -> None:
        """Update event type is `int`."""
        model = example_model

        assert isinstance(model.update_event_type, int)
