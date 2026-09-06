from collections.abc import Callable

import pytest

from screen_animator.items import ScrollingMovement, Speeder
from screen_animator.speed_changer import (
    DecreaseSpeedAction,
    IncreaseSpeedAction,
    MaintainSpeedAction,
    ResetSpeedAction,
    Speed,
    SpeedAction,
    SpeedChanger,
)


@pytest.fixture
def example_speeder() -> ScrollingMovement:
    """Create example `Speeder`."""
    speeder = ScrollingMovement()
    speeder.speed = 400

    return speeder


@pytest.fixture
def example_speed_changer(example_speeder: Speeder) -> SpeedChanger:
    """Create example `SpeedChanger`."""
    return SpeedChanger(example_speeder)


class TestSpeedChanger:
    @pytest.mark.parametrize("repeat", [1, 2, 3, 5, 8, 13])
    def test_increase_speed(self, repeat, example_speed_changer: SpeedChanger) -> None:
        """Speed of `Speeder` is increased."""
        speed_changer = example_speed_changer
        speed_initial = speed_changer._speeder.speed
        for _ in range(repeat):
            speed_changer.increase()

        assert speed_changer._speeder.speed == speed_initial + int(
            repeat * speed_changer._speed_change * speed_initial
        )

    @pytest.mark.parametrize(
        "repeats, result", [(1, 1), (2, 2), (3, 3), (5, 5), (8, 8), (10, 0), (13, 0)]
    )
    def test_decrease_speed(
        self, repeats: int, result: int, example_speed_changer: SpeedChanger
    ) -> None:
        """Speed of `Speeder` is decreased."""
        speed_changer = example_speed_changer
        speed_initial = speed_changer._speeder.speed
        for _ in range(repeats):
            speed_changer.decrease()

        assert speed_changer._speeder.speed == (
            (result and 1 * speed_initial)
            - int(result * speed_changer._speed_change * speed_initial)
        )

    def test_reset_speed(self, example_speed_changer: SpeedChanger) -> None:
        """Speed of `Speeder` is reset."""
        speed_changer = example_speed_changer
        speed_initial = speed_changer._speeder.speed
        for _ in range(10):
            speed_changer.increase()

        speed_interim = speed_changer._speeder.speed
        speed_changer.reset()

        assert all(
            [
                speed_interim != speed_initial,
                speed_changer._speeder.speed == speed_initial,
            ]
        )

    @pytest.mark.parametrize(
        "speed_input, check_method",
        [(Speed.FASTER, int.__gt__), (Speed.SLOWER, int.__lt__)],
    )
    def test_change_speed_changes(
        self,
        speed_input: Speed,
        check_method: Callable[[float | int, float | int], bool],
        example_speed_changer: SpeedChanger,
    ) -> None:
        """Speed of `Speeder` is changed."""
        speed_changer = example_speed_changer
        speed_initial = speed_changer._speeder.speed
        speed_changer.change_speed(speed_input)

        assert check_method(speed_changer._speeder.speed, speed_initial)

    def test_change_speed_reset(self, example_speed_changer: SpeedChanger) -> None:
        """Speed of `Speeder` is reset."""
        speed_changer = example_speed_changer
        speed_initial = speed_changer._speeder.speed
        for _ in range(10):
            speed_changer.increase()

        speed_interim = speed_changer._speeder.speed
        speed_changer.change_speed(Speed.RESET)

        assert all(
            [
                speed_interim != speed_initial,
                speed_changer._speeder.speed == speed_initial,
            ]
        )

    @pytest.mark.parametrize("speed_input", [Speed.MAINTAIN, ""])
    def test_change_speed_do_nothing(
        self, speed_input: Speed | str, example_speed_changer: SpeedChanger
    ) -> None:
        """Speed of `Speeder` is left as-is."""
        speed_changer = example_speed_changer
        speed_initial = speed_changer._speeder.speed
        for _ in range(10):
            speed_changer.increase()

        speed_interim = speed_changer._speeder.speed
        speed_changer.change_speed(speed_input)

        assert all(
            [
                speed_changer._speeder.speed != speed_initial,
                speed_changer._speeder.speed == speed_interim,
            ]
        )


class TestMaintainSpeedAction:
    def test_maintain_speed(self, example_speed_changer: SpeedChanger) -> None:
        """Speed action does not change speed."""
        speed_changer = example_speed_changer
        speed_initial = speed_changer._speeder.speed
        for _ in range(10):
            speed_changer.increase()

        speed_interim = speed_changer._speeder.speed
        speed_action = MaintainSpeedAction(speed_changer)
        speed_action.notify()

        assert all(
            [
                speed_changer._speeder.speed != speed_initial,
                speed_changer._speeder.speed == speed_interim,
            ]
        )


@pytest.mark.parametrize(
    "speed_action, check_method",
    [(IncreaseSpeedAction, int.__gt__), (DecreaseSpeedAction, int.__lt__)],
)
def test_speed_action_changes_speed(
    speed_action: type[SpeedAction],
    check_method: Callable[[float | int, float | int], bool],
    example_speed_changer: SpeedChanger,
) -> None:
    """Speed of `Speeder` is changed."""
    speed_changer = example_speed_changer
    speed_initial = speed_changer._speeder.speed
    speed_action = speed_action(speed_changer)
    speed_action.notify()

    assert check_method(speed_changer._speeder.speed, speed_initial)


class TestResetSpeedAction:
    def test_reset_speed(self, example_speed_changer: SpeedChanger) -> None:
        """Speed action resets speed."""
        speed_changer = example_speed_changer
        speed_initial = speed_changer._speeder.speed
        for _ in range(10):
            speed_changer.increase()

        speed_interim = speed_changer._speeder.speed
        speed_action = ResetSpeedAction(speed_changer)
        speed_action.notify()

        assert all(
            [
                speed_interim != speed_initial,
                speed_changer._speeder.speed == speed_initial,
            ]
        )
