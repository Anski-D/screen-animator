import pygame as pg
import pytest

from screen_animator.items import Direction, Item, RandomMovement, ScrollingMovement


@pytest.fixture
def example_item(example_content: pg.Surface, example_perimeter: pg.Rect) -> Item:
    """Provide example `Item` by removing abstract methods."""
    return Item(pg.sprite.Group(), example_content, example_perimeter)


class TestItem:
    def test_content_return_type(self, example_item) -> None:
        """Content is of correct type."""
        assert isinstance(example_item.content, pg.Surface)

    def test_content_setter(self, example_item) -> None:
        """Content setter sets correctly."""
        assert example_item.rect == pg.Rect(0, 0, 20, 10)


class TestScrollingMovement:
    @pytest.mark.parametrize(
        "direction, output",
        [
            (Direction.UP, ("y", -1)),
            (Direction.RIGHT, ("x", 1)),
            (Direction.DOWN, ("y", 1)),
            (Direction.LEFT, ("x", -1)),
            ("test", ("x", -1)),
        ],
    )
    def test_direction_setter(
        self, direction: Direction | str, output: tuple[str, int]
    ) -> None:
        """Direction set correctly."""
        movement = ScrollingMovement()
        movement.direction = direction

        assert (movement._axis, movement._sign) == output

    @pytest.mark.parametrize(
        "speed, direction, value",
        [
            (1, Direction.UP, 248),
            (2, Direction.RIGHT, 504),
            (3, Direction.DOWN, 256),
            (5, Direction.LEFT, 490),
        ],
    )
    def test_move(
        self, speed: int, direction: Direction, value: int, example_item: Item
    ) -> None:
        """Move in certain amount in correct direction."""
        item = example_item
        item.rect.topleft = item.perimeter.center
        movement = ScrollingMovement(speed, direction)
        movement.move(item)
        movement.move(item)
        axis = movement._directions[direction][0]

        assert getattr(item.rect, axis) == value


class TestRandomMovement:
    @pytest.mark.parametrize("repeat", range(5))
    def test_move_perimeter_contains(self, repeat: int, example_item: Item) -> None:
        """Random movement confined to perimeter."""
        item = example_item
        movement = RandomMovement()
        movement.move(item)

        assert item.perimeter.contains(item.rect)

    def test_move_repeat_move(self, example_item: Item) -> None:
        """Subsequent random movements result in different resulting locations."""
        item = example_item
        movement = RandomMovement()
        movement.move(item)
        rect1 = item.rect.copy()
        movement.move(item)

        assert item.rect != rect1
