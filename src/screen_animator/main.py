from collections.abc import Callable
from functools import partial

import pygame as pg

from screen_animator import args
import screen_animator.log_setup
from screen_animator.controller import Controller, EventManager, QuitAction
from screen_animator.image_loading import ImageLoader, SvgImageTypeLoader
from screen_animator.item_groups import (
    ColorChangeItemGroup,
    FpsCounterItemGroup,
    ItemGroup,
    LeftScrollingTextItemGroup,
    RandomImagesItemGroup,
    TimedItemGroup,
)
from screen_animator.model import Model
from screen_animator.settings import SettingsManager
from screen_animator.speed_changer import (
    DecreaseSpeedAction,
    IncreaseSpeedAction,
    ResetSpeedAction,
)
from screen_animator.view import View

DEBUG_DISPLAY_SIZE = 800, 400
ITEM_GROUP_TYPES: list[Callable[[SettingsManager, pg.Rect], ItemGroup]] = [
    partial(TimedItemGroup, wrapped_group=ColorChangeItemGroup),
    partial(TimedItemGroup, wrapped_group=RandomImagesItemGroup),
    LeftScrollingTextItemGroup,
]
EVENT_TYPES: list[tuple[int, int] | int] = [
    pg.QUIT,
    (pg.KEYDOWN, pg.K_q),
    (pg.KEYDOWN, pg.K_DOWN),
    (pg.KEYDOWN, pg.K_LEFT),
    (pg.KEYDOWN, pg.K_RIGHT),
]


def run_app() -> None:
    """Main app function to run."""
    pg.init()

    ImageLoader.register_loader(".svg", SvgImageTypeLoader)

    item_group_types = (
        ITEM_GROUP_TYPES + [FpsCounterItemGroup] if args.fps else ITEM_GROUP_TYPES
    )

    display = _set_display_size(DEBUG_DISPLAY_SIZE if args.debug else None)
    settings_manager = SettingsManager(args.input)
    model = Model(settings_manager, item_group_types, display.get_rect())
    view = View(model, display, settings_manager.settings, args.rotate)

    event_types = EVENT_TYPES + [model.update_event_type]

    app = Controller(settings_manager.settings, model)
    listeners = [
        quit_action := QuitAction([app]),
        quit_action,
        ResetSpeedAction(model.speed_changer),
        IncreaseSpeedAction(model.speed_changer),
        DecreaseSpeedAction(model.speed_changer),
        view,
    ]
    event_manager = EventManager(listeners, event_types)

    try:
        app.run(event_manager)
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing app")


def _set_display_size(display_size: tuple[float, float] | None = None) -> pg.Surface:
    pg.display.set_caption("screen_animator")

    if display_size is None:
        return pg.display.set_mode((0, 0), pg.FULLSCREEN)

    return pg.display.set_mode(display_size)


if __name__ == "__main__":
    run_app()
