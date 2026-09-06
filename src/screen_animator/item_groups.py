import logging
import random
from abc import ABC, abstractmethod

import numpy as np
import pygame as pg

from screen_animator.items import Direction, Item, RandomMovement, ScrollingMovement
from screen_animator.settings import SettingsManager

log = logging.getLogger(__name__)


class ItemGroup(ABC, pg.sprite.Group):
    """
    Interface for `Item` groups.

    Methods
    -------
    create
        Create items in group (sublasses to implement).
    update
        Update items in group (sublasses to implement).
    """

    def __init__(self, settings_manager: SettingsManager, perimeter: pg.Rect) -> None:
        """
        Initialise group with settings and context perimeter.

        Parameters
        ----------
        settings_manager
            Dictionary of settings.
        perimeter
            Outer limit of 'canvas' in `pygame`.
        """
        super().__init__()
        self._settings_manager = settings_manager
        self._perimeter = perimeter

        self._settings = self._settings_manager.settings

    @abstractmethod
    def create(self) -> None:
        """Create item(s) in group, to be implemented by sublasses."""


class TimeableItemGroup(ItemGroup):
    """
    Interface for allowing ItemGroups to be controlled by time.
    """

    _time_diff: float

    @property
    def time_diff(self) -> float:
        """int or float: time difference"""
        return self._time_diff


class TimedItemGroup(ItemGroup):
    """
    Manages when wrapped groups are updated.

    Methods
    -------
    create
        Create items in wrapped `ItemGroup`, set the initial time tracked by `pygame`.
    update
        Change wrapped `ItemGroup`.
    """

    _time: int

    def __init__(
        self,
        settings_manager: SettingsManager,
        perimeter: pg.Rect,
        wrapped_group: type[TimeableItemGroup],
    ) -> None:
        """
        Initialise group with settings and context perimeter.

        Parameters
        ----------
        settings_manager
            Dictionary of settings.
        perimeter
            Outer limit of 'canvas' in `pygame`.
        """
        super().__init__(settings_manager, perimeter)
        self._wrapped_group_type = wrapped_group
        log.info("Creating %s", self)

        self._wrapped_group = wrapped_group(settings_manager, perimeter)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._settings_manager}, {self._perimeter}, {self._wrapped_group_type})"

    def sprites(self):
        """Sprites in wrapped group."""
        return self._wrapped_group.sprites()

    def create(self) -> None:
        """Run wrapped instance method, set the elapsed time according to `pygame`."""
        self._wrapped_group.create()
        self._time = pg.time.get_ticks()

    def update(self):
        """Check elapsed time, run wrapped instance update if ready."""
        time = pg.time.get_ticks()
        time_diff = time - self._time
        if time_diff >= self._wrapped_group.time_diff * 1000:
            log.debug(
                "%s milliseconds passed, updating %s", time_diff, type(self).__name__
            )
            self._wrapped_group.update()
            self._time = time


class LeftScrollingTextItemGroup(ItemGroup):
    """
    Group of items that will scroll messages to the left.

    Methods
    -------
    create
        Create a message with a set speed to the left.
    update
        Update messages depending on message position.
    """

    _movement = ScrollingMovement

    def __init__(self, settings_manager: SettingsManager, perimeter: pg.Rect) -> None:
        """
        Initialize group with a settings manager and defined perimeter.

        Parameters
        ----------
        settings_manager
            Manages settings.
        perimeter
            Defines outer perimeter.
        """
        super().__init__(settings_manager, perimeter)
        log.info("Creating %s", self)

        speed = (
            self._settings["messages"]["scroll_speed"]
            // self._settings["timings"]["fps"]
        )
        self._scrolling_movement = self._movement(speed, Direction.LEFT)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._settings_manager}, {self._perimeter})"

    @property
    def speed(self) -> float:
        """Speed of movement."""
        return self._scrolling_movement.speed

    @speed.setter
    def speed(self, speed: float) -> None:
        self._scrolling_movement.speed = speed

    def create(self) -> None:
        """
        Create a message `Item` that scrolls to the left with a set speed.

        Message is initially placed with middle-left set at the middle-right of the
        perimeter, i.e. off-screen to the right.
        """
        messages_dict = self._settings["messages"]
        self._settings_manager.set_font()
        message_text = self._settings_manager.generate_message_text()
        log.debug("Creating %s with text: %s", Item.__name__, message_text)
        start_position = self._calculate_start_position(message_text)
        self._set_outline(message_text, start_position)
        message = Item(
            self,
            self._generate_message(message_text, messages_dict["font"]),
            self._perimeter,
            self._scrolling_movement,
        )
        message.message_text = message_text
        message.font = messages_dict["font"]
        message.rect.midleft = start_position
        message.rect.x += messages_dict["outline_width"]

    def update(self):
        """
        Update messages in group.

        If the message has left the left side of the perimeter entirely, it will be
        deleted. If all messages are within the right-hand perimeter, a new message
        will be generated.
        """
        super().update()

        for message in self.sprites():
            if message.rect.right < self._perimeter.left:
                log.debug("%s has scrolled off screen, destroying", message)
                message.kill()
            else:
                try:
                    message.content = self._generate_message(
                        message.message_text, message.font
                    )
                except AttributeError:
                    pass

        if all(
            message.rect.right <= self._perimeter.right for message in self.sprites()
        ):
            self.create()

    def _generate_message(self, message_text: str, font: pg.Font) -> pg.Surface:
        messages_dict = self._settings["messages"]

        return font.render(
            message_text,
            messages_dict["anti-aliasing"],
            messages_dict["color"],
        )

    def _set_outline(self, message_text: str, start_position: tuple[int, int]) -> None:
        messages_dict = self._settings["messages"]
        log.debug("Setting text outline with width %s", messages_dict["outline_width"])
        outline_width = messages_dict["outline_width"]
        if outline_width > 0:
            outline_text = messages_dict["font"].render(
                message_text,
                messages_dict["anti-aliasing"],
                messages_dict["outline_color"],
            )
            angles = np.linspace(
                0, 360, messages_dict["outline_copies"], endpoint=False
            )
            x_shift = outline_width * np.cos(np.radians(angles - 90)) + outline_width
            y_shift = outline_width * np.sin(np.radians(angles - 90))
            xy_shifts = np.transpose(np.vstack((x_shift, y_shift)))
            for xy_shift in xy_shifts:
                outline = Item(
                    self, outline_text, self._perimeter, self._scrolling_movement
                )
                outline.rect.midleft = start_position
                outline.rect.x += xy_shift[0]
                outline.rect.y += xy_shift[1]

    def _calculate_start_position(self, message_text: str) -> tuple[int, int]:
        messages_dict = self._settings["messages"]
        if not messages_dict["start_middle"]:
            dummy_message = self._generate_message(message_text, messages_dict["font"])
            height = dummy_message.get_rect().height

            return (
                self._perimeter.right,
                random.randint(
                    height // 2 + messages_dict["outline_width"],
                    self._perimeter.bottom
                    - height // 2
                    - messages_dict["outline_width"],
                ),
            )

        return self._perimeter.midright


class RandomImagesItemGroup(TimeableItemGroup):
    """
    Group of items that will remove randomly within the specified perimeter.

    Methods
    -------
    create
        Create all the image items.
    update
        Update the position of all image items.
    """

    _movement = RandomMovement

    def __init__(self, settings_manager: SettingsManager, perimeter: pg.Rect) -> None:
        """
        Initialize group with a settings manager and defined perimeter.

        Parameters
        ----------
        settings_manager
            Manages settings.
        perimeter
            Defines outer perimeter.
        """
        super().__init__(settings_manager, perimeter)
        log.info("Creating %s", self)

        self._random_movement = self._movement()
        self._time_diff = self._settings["timings"]["image_change_time"]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._settings_manager}, {self._perimeter})"

    def create(self) -> None:
        """Create all the image items, set to move randomly within the perimeter."""
        image_settings = self._settings["images"]
        for _ in range(image_settings["number"]):
            for image in image_settings["images"]:
                log.debug("Creating `pygame` image: %s", image)
                Item(self, image, self._perimeter, self._random_movement)

    def update(self):
        """
        Update the position, randomly, of all the images in the group.

        Image position is updated sequentially, and each is compared to the position
        of newly positioned images to ensure no collisions.
        """
        log.debug("Repositioning all images")
        group = []
        reattempts_taken_total = 0
        num_items = len(self.sprites())
        for image_idx, image in enumerate(self.sprites(), 1):
            self.remove(image)
            image.update()
            reattempts_allowed = self._settings["images"]["reposition_attempts"]
            while abs(reattempts_allowed) > 0 and pg.sprite.spritecollideany(
                image, group
            ):
                image.update()
                reattempts_allowed -= 1
                reattempts_taken_total += 1
                if reattempts_taken_total >= 1000 and reattempts_allowed <= 0:
                    log.debug(
                        "Limit of image reposition attempts reached for image %s/%s",
                        image_idx,
                        num_items,
                    )
                elif reattempts_taken_total % 10000 == 0:
                    log.debug(
                        "%s total reattempts so far, currently on image %s of %s",
                        reattempts_taken_total,
                        image_idx,
                        num_items,
                    )
            group.append(image)
        log.debug(
            "All images (%s total) repositioned with %s total reattempts",
            num_items,
            reattempts_taken_total,
        )
        random.shuffle(group)
        self.add(group)


class ColorChangeItemGroup(TimeableItemGroup):
    """
    Manages when colors are changed.

    Methods
    -------
    update
        Change colors if time threshold reached.
    """

    def __init__(self, settings_manager: SettingsManager, perimeter: pg.Rect) -> None:
        """
        Initialize group with a settings manager and defined perimeter.

        Parameters
        ----------
        settings_manager
            Manages settings.
        perimeter
            Defines outer perimeter.
        """
        super().__init__(settings_manager, perimeter)
        log.info("Creating %s", self)

        self._time_diff = self._settings["timings"]["color_change_time"]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._settings_manager}, {self._perimeter})"

    def create(self) -> None:
        pass

    def update(self):
        """Update colors."""
        self._settings_manager.set_colors()


class FpsCounterItemGroup(ItemGroup):
    """
    Counter for fps.

    Methods
    -------
    create
        Create the fps counter.
    update
        Update the fps counter.
    """

    def __init__(self, settings_manager: SettingsManager, perimeter: pg.Rect) -> None:
        """
        Initialize group with a settings manager and defined perimeter.

        Parameters
        ----------
        settings_manager
            Manages settings.
        perimeter
            Defines outer perimeter.
        """
        super().__init__(settings_manager, perimeter)
        log.info("Creating %s", self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._settings_manager}, {self._perimeter})"

    def create(self) -> None:
        """Create the fps counter."""
        fps_font = pg.font.SysFont(None, 36)
        fps_actual = self._settings["timings"]["fps_actual"]
        content = fps_font.render(f"{fps_actual:.2f}", False, (0, 0, 0))
        fps = Item(self, content, self._perimeter)
        fps.rect.x = 10
        fps.rect.y = 10

    def update(self):
        """Update the fps counter."""
        self.empty()
        self.create()
