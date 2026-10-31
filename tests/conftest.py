import pygame as pg
import pytest

from screen_animator import settings
from screen_animator.settings import Settings

pg.init()


@pytest.fixture
def dummy_settings_dict() -> dict:
    """Provide example settings dict prior to conversion to tuples."""
    return {
        "colors": [
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255],
        ],
        "messages": {
            "messages": [
                "TEST MESSAGE 1!",
                "TEST MESSAGE 2!",
                "TEST MESSAGE 3!",
                "TEST MESSAGE 4!",
            ],
            "separator": "    ",
            "typeface": "freeserif",
            "sizes": [350, 350],
            "bold": True,
            "italic": False,
            "anti-aliasing": False,
            "scroll_speed": 240,
            "outline_width": 3,
            "outline_copies": 12,
            "outline_colors": [
                [0, 0, 0],
                [255, 255, 255],
            ],
            "start_middle": True,
        },
        "images": {
            "sources": [
                ["pic1.svg", 64],
                ["pic2.bmp", -1],
                ["pic3.bmp", 64],
            ],
            "number": 10,
            "reposition_attempts": -1,
        },
        "timings": {
            "fps": 30,
            "image_change_time": 2,
            "color_change_time": 15,
        },
    }


@pytest.fixture
def dummy_settings_dict_with_tuples(dummy_settings_dict: dict) -> dict:
    """Provide example settings dict after conversion to tuples."""
    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
    ]
    sizes = (350, 350)
    outline_colors = [
        (0, 0, 0),
        (255, 255, 255),
    ]
    sources = [
        ("pic1.svg", 64),
        ("pic2.bmp", -1),
        ("pic3.bmp", 64),
    ]
    dummy_settings_dict["colors"] = colors
    dummy_settings_dict["messages"]["sizes"] = sizes
    dummy_settings_dict["messages"]["outline_colors"] = outline_colors
    dummy_settings_dict["images"]["sources"] = sources

    return dummy_settings_dict


@pytest.fixture
def dummy_settings(dummy_settings_dict_with_tuples: dict) -> Settings:
    return Settings.model_validate(dummy_settings_dict_with_tuples)


@pytest.fixture
def dummy_perimeter() -> pg.Rect:
    """Provide example perimeter."""
    return pg.Rect(0, 0, 1000, 500)


@pytest.fixture
def dummy_content() -> pg.Surface:
    """Provide example content surface."""
    return pg.Surface((20, 10))


@pytest.fixture
def mock_settings(monkeypatch, dummy_settings_dict_with_tuples: dict) -> None:
    def mock_import_settings(*args, **kwargs) -> Settings:
        return Settings.model_validate(dummy_settings_dict_with_tuples)

    monkeypatch.setattr(settings, "import_settings", mock_import_settings)
