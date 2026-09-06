import pytest

from screen_animator.controller import EventManager
from screen_animator.listener import Listener


@pytest.fixture
def example_listener() -> Listener:
    """Provide example `Oberserver` by removing abstract methods."""
    Listener.__abstractmethods__ = set()

    return Listener()


class TestEventManager:
    _num_listeners = 3

    @pytest.fixture
    def example_event_manager(self, example_listener: Listener) -> EventManager:
        """Set up EventManager for testing."""
        event_types = range(1, self._num_listeners + 1)
        listeners = [example_listener for _ in event_types]

        return EventManager(listeners, event_types)

    def test_init_listeners_len(self, example_event_manager: EventManager) -> None:
        """`EventManager` initialization, listeners registered."""
        event_manager = example_event_manager

        assert len(event_manager._listeners) == self._num_listeners

    def test_register_listener_keys(self, example_listener: Listener) -> None:
        """Keys register to EventManager."""
        event_manager = EventManager()
        key = 7, 77
        event_manager.register_listener(example_listener, key)

        assert key in event_manager._listeners

    def test_register_listener_key_as_tuple(self, example_listener: Listener) -> None:
        """`int` keys convert to tuple when registered."""
        event_manager = EventManager()
        key = 7
        event_manager.register_listener(example_listener, key)

        assert all(
            [key not in event_manager._listeners, (key,) in event_manager._listeners]
        )

    def test_register_listener_values(self, example_listener: Listener) -> None:
        """`Listener` values register to EventManager."""
        event_manager = EventManager()
        listener = example_listener
        event_manager.register_listener(listener, 1)

        assert listener in event_manager._listeners.values()

    def test_register_listener_len(self, example_listener: Listener) -> None:
        """Registered correct number of listeners."""
        num_listeners = 3
        event_manager = EventManager()
        for num in range(1, num_listeners + 1):
            event_manager.register_listener(example_listener, num)

        assert len(event_manager._listeners) == num_listeners

    def test_remove_listener_len(self, example_event_manager: EventManager) -> None:
        """Remove listener from EventManager."""
        event_manager = example_event_manager
        event_manager.remove_listener(2)

        assert len(event_manager._listeners) == self._num_listeners - 1

    def test_remove_listener_keys(self, example_event_manager: EventManager) -> None:
        """Remove listener from EventManager."""
        event_manager = example_event_manager
        key = 2
        event_manager.remove_listener(key)

        assert all(
            [
                key not in event_manager._listeners,
                (key,) not in event_manager._listeners,
            ]
        )
