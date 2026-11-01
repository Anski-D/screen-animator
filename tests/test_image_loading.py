from collections.abc import Callable
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from screen_animator.image_loading import (
    ImageLoader,
    RasterImageTypeLoader,
    SvgImageTypeLoader,
)


@pytest.fixture
def mock_image_load(monkeypatch: MonkeyPatch) -> None:
    def mock_load_image(_, input_str: str, *args, **kwargs) -> str:
        image_types = {
            ".bmp": "raster",
            ".png": "raster",
            ".svg": "svg",
        }

        return image_types[Path(input_str).suffix]

    monkeypatch.setattr(RasterImageTypeLoader, "load_image", mock_load_image)
    monkeypatch.setattr(SvgImageTypeLoader, "load_image", mock_load_image)


class TestImageLoader:
    @pytest.mark.parametrize(
        "input_file, output",
        [
            ("test1.bmp", "raster"),
            ("test2.png", "raster"),
            ("test3.svg", "svg"),
            ("test4.svg", "svg"),
        ],
    )
    def test_load_image_file_type(
        self, mock_image_load: Callable[[], str], input_file: str, output: str
    ) -> None:
        """Correct loader function is used for loading images."""
        ImageLoader.register_loader(".svg", SvgImageTypeLoader)
        image_loader = ImageLoader()
        image = image_loader.load_image(input_file, -1)

        assert image == output


class TestRasterImageLoader:
    def test_load_raster_image_file_not_found(self) -> None:
        """`FileNotFoundError` not raised further when image files are not found."""
        image_loader = RasterImageTypeLoader()
        try:
            image_loader.load_image("test1.bmp", -1)
        except FileNotFoundError as error:
            assert False, f"{error}"


class TestSvgImageLoader:
    def test_load_svg_image_file_not_found(self) -> None:
        """`FileNotFoundError` not raised further when image files are not found."""
        image_loader = SvgImageTypeLoader()
        try:
            image_loader.load_image("test1.svg", -1)
        except FileNotFoundError as error:
            assert False, f"{error}"
