import pygame as pg
import pytest
from pytest import MonkeyPatch

from screen_animator.item_groups import ItemGroup
from screen_animator.model import Model
from screen_animator.settings import SettingsManager
from screen_animator.speed_changer import SpeedChanger


@pytest.fixture
def model(
    monkeypatch: MonkeyPatch,
    settings_manager: SettingsManager,
    dummy_perimeter: pg.Rect,
) -> Model:
    """Create example Model"""

    def mock_item_group_init(*args, **kwargs) -> None:
        """Patch ItemGroup so that its init dunder just returns None."""
        return

    def mock_speed_changer_init(*args, **kwargs) -> None:
        """Patch SpeedChanger so that its init dunder just returns None."""
        return

    monkeypatch.setattr(ItemGroup, "__init__", mock_item_group_init)
    ItemGroup.__abstractmethods__ = set()
    monkeypatch.setattr(SpeedChanger, "__init__", mock_speed_changer_init)

    return Model(settings_manager, [ItemGroup for _ in range(3)], dummy_perimeter)


class TestModel:
    def test_init_item_group(self, model: Model) -> None:
        """init dunder creates ItemGroup instances."""
        assert all(
            isinstance(item_group, ItemGroup) for item_group in model.item_groups
        )

    def test_init_event_type_int(self, model: Model) -> None:
        """Update event type is `int`."""
        assert isinstance(model.update_event_type, int)
