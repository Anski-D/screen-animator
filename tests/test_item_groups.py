import math
import time

import pygame as pg
import pytest
from pytest import MonkeyPatch

from screen_animator.item_groups import (
    ColorChangeItemGroup,
    LeftScrollingTextItemGroup,
    RandomImagesItemGroup,
    TimedItemGroup,
)
from screen_animator.settings import SettingsManager


# @pytest.fixture
# def settings_manager(
#     monkeypatch,
#     example_settings_manager: SettingsManager,
#     dummy_settings_dict_with_tuples: dict,
#     dummy_content: pg.Surface,
# ) -> SettingsManager:
#     """Provide example `SettingsManager`."""
#     settings_manager = example_settings_manager
#     settings_manager.settings["images"]["images"] = [
#         dummy_content
#         for _ in range(len(dummy_settings_dict_with_tuples["images"]["sources"]))
#     ]
#
#     return settings_manager


@pytest.fixture
def settings_manager(settings_manager: SettingsManager, dummy_content: pg.Surface) -> SettingsManager:
    """Provide example `SettingsManager`."""
    images = settings_manager.settings.images
    images.images = [
        dummy_content
        for _
        in images.sources
    ]

    return settings_manager


@pytest.fixture
def left_scrolling_text_item_group(settings_manager: SettingsManager, dummy_perimeter: pg.Rect) -> LeftScrollingTextItemGroup:
    """Provide example `LeftScrollingTextGroup`."""
    return LeftScrollingTextItemGroup(settings_manager, dummy_perimeter)


class TestLeftScrollingTextItemGroup:
    # @pytest.fixture
    # def left_scrolling_text_item_group(
    #     self, settings_manager: SettingsManager, dummy_perimeter: pg.Rect
    # ) -> LeftScrollingTextItemGroup:
    #     """Provide example `LeftScrollingTextGroup`."""
    #     return LeftScrollingTextItemGroup(settings_manager, dummy_perimeter)

    @pytest.mark.parametrize("num_of_items", [1, 2, 3, 5, 8])
    def test_create_no_outline(
        self,
        num_of_items: int,
        left_scrolling_text_item_group: LeftScrollingTextItemGroup,
    ) -> None:
        """No outlines are created."""
        item_group = left_scrolling_text_item_group
        item_group._settings.messages.outline_width = 0

        for _ in range(num_of_items):
            item_group.create()

        assert len(item_group.sprites()) == num_of_items

    @pytest.mark.parametrize("num_of_items", [1, 2, 3, 5, 8])
    def test_create_with_outline(
        self,
        num_of_items: int,
        left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        dummy_settings_dict_with_tuples: dict,
    ) -> None:
        """Outlines are created for each `Item`."""
        item_group = left_scrolling_text_item_group

        for _ in range(num_of_items):
            item_group.create()

        assert (
                len(item_group.sprites())
                == num_of_items * (1 +
                + dummy_settings_dict_with_tuples["messages"]["outline_copies"])
        )

    def test_create_position_x(
        self,
        left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        dummy_perimeter: pg.Rect,
        dummy_settings_dict_with_tuples: dict,
    ) -> None:
        """`Item` placed in correct starting x-position, dependent on outline settings."""
        item_group = left_scrolling_text_item_group
        item_group.create()

        assert (
                item_group.sprites()[-1].rect.left
                == dummy_perimeter.right
                + dummy_settings_dict_with_tuples["messages"]["outline_width"]
        )

    def test_create_position_y_start_middle(
        self,
        left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        dummy_perimeter: pg.Rect,
        dummy_settings_dict_with_tuples: dict,
    ) -> None:
        """`Item` placed in correct starting y-position, dependent on settings."""
        dummy_settings_dict_with_tuples["messages"]["start_middle"] = True
        item_group = left_scrolling_text_item_group
        item_group.create()

        assert item_group.sprites()[-1].rect.centery == dummy_perimeter.centery

    @pytest.mark.parametrize("repeat", range(5))
    def test_create_position_y_not_start_middle(
        self,
        repeat: int,
        left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        dummy_perimeter: pg.Rect,
        dummy_settings_dict_with_tuples: dict,
    ) -> None:
        """`Item` placed in correct starting y-position, dependent on settings."""
        dummy_settings_dict_with_tuples["messages"]["start_middle"] = False
        item_group = left_scrolling_text_item_group
        items = []
        for _ in range(5):
            item_group.create()
            item = item_group.sprites()[-1]
            items.append(item)

        assert all(
            [
                item.rect.top >= dummy_perimeter.top
                and item.rect.bottom <= dummy_perimeter.bottom
                for item in items
            ]
        )

    def test_update_create(
        self, left_scrolling_text_item_group: LeftScrollingTextItemGroup
    ) -> None:
        """New `Item` is created once previous has fully emerged."""
        item_group = left_scrolling_text_item_group
        item_group._settings["messages"]["outline_width"] = 0
        item_group.create()
        item = item_group.sprites()[0]
        width = item.rect.width
        speed = 100
        item._movement.speed = speed
        for _ in range(math.ceil(width / speed)):
            item_group.update()

        assert len(item_group.sprites()) == 2

    def test_update_delete(
        self,
        monkeypatch,
        left_scrolling_text_item_group: LeftScrollingTextItemGroup,
    ) -> None:
        """`Item` is deleted once fully off screen."""
        item_group = left_scrolling_text_item_group
        item_group.create()
        item = item_group.sprites()[0]
        width = item.rect.width + item_group._perimeter.width
        speed = 100
        item._movement.speed = speed
        monkeypatch.setattr(LeftScrollingTextItemGroup, "create", lambda x: None)
        for _ in range(math.ceil(width / speed)):
            item_group.update()

        assert len(item_group.sprites()) == 0

    def test_generate_message(
        self, left_scrolling_text_item_group: LeftScrollingTextItemGroup
    ) -> None:
        """Message is generated as `Surface`."""
        assert isinstance(
            left_scrolling_text_item_group._generate_message(
                "Test",
                left_scrolling_text_item_group._settings["messages"]["font"],
            ),
            pg.Surface,
        )

    def test_set_outline(
        self,
        left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        dummy_perimeter: pg.Rect,
        dummy_settings_dict_with_tuples: dict,
    ) -> None:
        """Outlines are created for `Item`."""
        item_group = left_scrolling_text_item_group
        item_group._set_outline("Test", dummy_perimeter.midright)

        assert (
                len(item_group.sprites())
                == dummy_settings_dict_with_tuples["messages"]["outline_copies"]
        )


class TestRandomImagesItemGroup:
    @pytest.fixture
    def example_random_images_item_group(
        self, settings_manager: SettingsManager, dummy_perimeter: pg.Rect
    ) -> RandomImagesItemGroup:
        """Provide example `RandomImagesGroup`."""
        return RandomImagesItemGroup(settings_manager, dummy_perimeter)

    def test_create(
        self,
        example_random_images_item_group: RandomImagesItemGroup,
        dummy_settings_dict_with_tuples: dict,
    ) -> None:
        """Create correct number of images."""
        item_group = example_random_images_item_group
        item_group.create()
        image_settings = dummy_settings_dict_with_tuples["images"]

        assert (
            len(item_group.sprites())
            == len(image_settings["sources"]) * image_settings["number"]
        )

    @pytest.mark.parametrize("repeats", [1, 2, 3, 5, 8])
    def test_update(
        self, repeats: int, example_random_images_item_group: RandomImagesItemGroup
    ) -> None:
        """Images are confined to perimeter when positions update."""
        item_group = example_random_images_item_group
        item_group.create()
        for _ in range(repeats):
            item_group.update()

        assert all(
            [item_group._perimeter.contains(image) for image in item_group.sprites()]
        )


class TestColorChangeItemGroup:
    @pytest.fixture
    def example_color_change_item_group(
        self, settings_manager: SettingsManager, dummy_perimeter: pg.Rect
    ) -> TimedItemGroup:
        """Provide example `ColorChangeGroup`."""
        return TimedItemGroup(
            settings_manager, dummy_perimeter, ColorChangeItemGroup
        )

    def test_create(self, example_color_change_item_group: TimedItemGroup) -> None:
        """Time is saved."""
        item_group = example_color_change_item_group
        item_group.create()

        assert isinstance(item_group._time, int)

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "sleep, output", [(1, True), (2, True), (3, True), (5, False), (8, False)]
    )
    def test_update(
        self,
        sleep: int,
        output: bool,
        example_color_change_item_group: TimedItemGroup,
    ) -> None:
        """Time value updated after sufficient time elapsed."""
        item_group = example_color_change_item_group
        item_group._wrapped_group._time_diff = 4
        item_group.create()
        time1 = item_group._time
        time.sleep(sleep)
        item_group.update()
        time2 = item_group._time

        assert (time1 == time2) is output
