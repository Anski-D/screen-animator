import math
import time

import pygame as pg
import pytest

from screen_animator.item_groups import (
    ColorChangeItemGroup,
    LeftScrollingTextItemGroup,
    RandomImagesItemGroup,
    TimedItemGroup,
)
from screen_animator.settings import SettingsManager


@pytest.fixture
def example_settings_manager(
    monkeypatch,
    example_settings_manager: SettingsManager,
    example_settings_dict_with_tuples: dict,
    example_content: pg.Surface,
) -> SettingsManager:
    """Provide example `SettingsManager`."""
    settings_manager = example_settings_manager
    settings_manager.settings["images"]["images"] = [
        example_content
        for _ in range(len(example_settings_dict_with_tuples["images"]["sources"]))
    ]

    return settings_manager


class TestLeftScrollingTextItemGroup:
    @pytest.fixture
    def example_left_scrolling_text_item_group(
        self, example_settings_manager: SettingsManager, example_perimeter: pg.Rect
    ) -> LeftScrollingTextItemGroup:
        """Provide example `LeftScrollingTextGroup`."""
        return LeftScrollingTextItemGroup(example_settings_manager, example_perimeter)

    @pytest.mark.parametrize("num_of_items", [1, 2, 3, 5, 8])
    def test_create_no_outline(
        self,
        num_of_items: int,
        example_left_scrolling_text_item_group: LeftScrollingTextItemGroup,
    ) -> None:
        """No outlines are created."""
        item_group = example_left_scrolling_text_item_group
        item_group._settings["messages"]["outline_width"] = 0

        for _ in range(num_of_items):
            item_group.create()

        assert len(item_group.sprites()) == num_of_items

    @pytest.mark.parametrize("num_of_items", [1, 2, 3, 5, 8])
    def test_create_with_outline(
        self,
        num_of_items: int,
        example_left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        example_settings_dict_with_tuples: dict,
    ) -> None:
        """Outlines are created for each `Item`."""
        item_group = example_left_scrolling_text_item_group

        for _ in range(num_of_items):
            item_group.create()

        assert (
            len(item_group.sprites())
            == num_of_items
            + example_settings_dict_with_tuples["messages"]["outline_copies"]
            * num_of_items
        )

    def test_create_position_x(
        self,
        example_left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        example_perimeter: pg.Rect,
        example_settings_dict_with_tuples: dict,
    ) -> None:
        """`Item` placed in correct starting x-position, dependent on outline settings."""
        item_group = example_left_scrolling_text_item_group
        item_group.create()

        assert (
            item_group.sprites()[-1].rect.left
            == example_perimeter.right
            + example_settings_dict_with_tuples["messages"]["outline_width"]
        )

    def test_create_position_y_start_middle(
        self,
        example_left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        example_perimeter: pg.Rect,
        example_settings_dict_with_tuples: dict,
    ) -> None:
        """`Item` placed in correct starting y-position, dependent on settings."""
        example_settings_dict_with_tuples["messages"]["start_middle"] = True
        item_group = example_left_scrolling_text_item_group
        item_group.create()

        assert item_group.sprites()[-1].rect.centery == example_perimeter.centery

    @pytest.mark.parametrize("repeat", range(5))
    def test_create_position_y_not_start_middle(
        self,
        repeat: int,
        example_left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        example_perimeter: pg.Rect,
        example_settings_dict_with_tuples: dict,
    ) -> None:
        """`Item` placed in correct starting y-position, dependent on settings."""
        example_settings_dict_with_tuples["messages"]["start_middle"] = False
        item_group = example_left_scrolling_text_item_group
        items = []
        for _ in range(5):
            item_group.create()
            item = item_group.sprites()[-1]
            items.append(item)

        assert all(
            [
                item.rect.top >= example_perimeter.top
                and item.rect.bottom <= example_perimeter.bottom
                for item in items
            ]
        )

    def test_update_create(
        self, example_left_scrolling_text_item_group: LeftScrollingTextItemGroup
    ) -> None:
        """New `Item` is created once previous has fully emerged."""
        item_group = example_left_scrolling_text_item_group
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
        example_left_scrolling_text_item_group: LeftScrollingTextItemGroup,
    ) -> None:
        """`Item` is deleted once fully off screen."""
        item_group = example_left_scrolling_text_item_group
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
        self, example_left_scrolling_text_item_group: LeftScrollingTextItemGroup
    ) -> None:
        """Message is generated as `Surface`."""
        assert isinstance(
            example_left_scrolling_text_item_group._generate_message(
                "Test",
                example_left_scrolling_text_item_group._settings["messages"]["font"],
            ),
            pg.Surface,
        )

    def test_set_outline(
        self,
        example_left_scrolling_text_item_group: LeftScrollingTextItemGroup,
        example_perimeter: pg.Rect,
        example_settings_dict_with_tuples: dict,
    ) -> None:
        """Outlines are created for `Item`."""
        item_group = example_left_scrolling_text_item_group
        item_group._set_outline("Test", example_perimeter.midright)

        assert (
            len(item_group.sprites())
            == example_settings_dict_with_tuples["messages"]["outline_copies"]
        )


class TestRandomImagesItemGroup:
    @pytest.fixture
    def example_random_images_item_group(
        self, example_settings_manager: SettingsManager, example_perimeter: pg.Rect
    ) -> RandomImagesItemGroup:
        """Provide example `RandomImagesGroup`."""
        return RandomImagesItemGroup(example_settings_manager, example_perimeter)

    def test_create(
        self,
        example_random_images_item_group: RandomImagesItemGroup,
        example_settings_dict_with_tuples: dict,
    ) -> None:
        """Create correct number of images."""
        item_group = example_random_images_item_group
        item_group.create()
        image_settings = example_settings_dict_with_tuples["images"]

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
        self, example_settings_manager: SettingsManager, example_perimeter: pg.Rect
    ) -> TimedItemGroup:
        """Provide example `ColorChangeGroup`."""
        return TimedItemGroup(
            example_settings_manager, example_perimeter, ColorChangeItemGroup
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
