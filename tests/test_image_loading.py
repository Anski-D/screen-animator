import pytest

from screen_animator.image_loading import (
    ImageLoader,
    RasterTypeImageLoader,
    SvgTypeImageLoader,
)


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
        self, input_file: str, output: str, monkeypatch
    ) -> None:
        """Correct loader function is used for loading images."""
        monkeypatch.setattr(
            RasterTypeImageLoader, "load_image", lambda *args, **kwargs: "raster"
        )
        monkeypatch.setattr(
            SvgTypeImageLoader, "load_image", lambda *args, **kwargs: "svg"
        )
        ImageLoader.register_loader(".svg", SvgTypeImageLoader)
        image_loader = ImageLoader()
        image = image_loader.load_image(input_file, -1)

        assert image == output


class TestRasterImageLoader:
    def test_load_raster_image_file_not_found(self) -> None:
        """`FileNotFoundError` not raised further when image files are not found."""
        image_loader = RasterTypeImageLoader()
        try:
            image_loader.load_image("test1.bmp", -1)
        except FileNotFoundError as error:
            assert False, f"{error}"


class TestSvgImageLoader:
    def test_load_svg_image_file_not_found(self) -> None:
        """`FileNotFoundError` not raised further when image files are not found."""
        image_loader = SvgTypeImageLoader()
        try:
            image_loader.load_image("test1.svg", -1)
        except FileNotFoundError as error:
            assert False, f"{error}"
