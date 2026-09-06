import logging
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path

import cairosvg
import pygame as pg
from svgutils import transform as sg

log = logging.getLogger(__name__)


class TypeImageLoader(ABC):
    """
    Interface for loading images for `pygame`.

    Methods
    -------
    load_image
        Load an image (sublasses to implement).
    """

    def __init__(self) -> None:
        log.info("Creating %s", self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    @abstractmethod
    def load_image(self, image_loc: str, width: int = 0) -> pg.Surface | None:
        """
        Loads images for use in `pygame`.

        Parameters
        ----------
        image_loc
            Location of image file.
        width
            Required width in pixels of image when loaded.

        Returns
        -------
        pg.Surface
            Image loaded for use in `pygame`.
        """


class RasterTypeImageLoader(TypeImageLoader):
    """
    Load raster images.

    Methods
    -------
    load_image
        Load a raster image to `pygame` Surface.
    """

    def load_image(self, image_loc: str, width: int = 0) -> pg.Surface | None:
        """
        Loads raster images (e.g., BMP, JPG, PNG) for use in `pygame`.

        Parameters
        ----------
        image_loc
            Location of image file.
        width : Optional
            Desired width in pixels of image when loaded, 0 or lower results in no scaling.

        Returns
        -------
        pg.Surface
            Image loaded for use in `pygame`.
        """
        try:
            log.info("Loading %s...", image_loc)
            image = pg.image.load(image_loc)
        except FileNotFoundError:
            log.error("%s not found", Path(image_loc).absolute())
            return None

        if width > 0:
            width_old, height_old = image.get_size()
            height = width / (width_old / height_old)
            log.info(
                "Scaling image from (%s,%s) to (%s,%s)",
                width_old,
                height_old,
                width,
                height,
            )

            return pg.transform.scale(image, (width, height))

        log.info("No scaling required")
        return image


class SvgTypeImageLoader(TypeImageLoader):
    """
    Load SVG vector images.

    Methods
    -------
    load_image
        Load a raster image to `pygame` Surface.
    """

    def load_image(self, image_loc: str, width: int = 0) -> pg.Surface | None:
        """
        Loads SVG images for use in `pygame`.

        Parameters
        ----------
        image_loc
            Location of image file.
        width : Optional
            Desired width in pixels of image when loaded, 0 or lower results in no scaling.

        Returns
        -------
        pg.Surface
            Image loaded for use in `pygame`.
        """
        try:
            log.info("Loading %s...", image_loc)
            image = sg.fromfile(str(image_loc))
        except FileNotFoundError:
            log.error("%s not found", Path(image_loc).absolute())
            return None

        view_box = image.root.attrib["viewBox"]
        width_old, height_old = tuple(
            int(float(number)) for number in view_box.split(" ")[2:]
        )
        height = int(width / (width_old / height_old))
        log.info(
            "Scaling image from (%s,%s) to (%s,%s)",
            width_old,
            height_old,
            width,
            height,
        )
        image.set_size((str(width), str(height)))
        image_str = image.to_str()

        return pg.image.load(BytesIO(cairosvg.svg2png(image_str)))


class ImageLoader:
    """
    Loads images for use in `pygame`.

    Methods
    -------
    register_loader
        Add reference to class dictionary to image loading function.
    load_image
        Return a loaded image as a `pygame` Surface.
    """

    _loaders: dict = {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    @classmethod
    def register_loader(cls, image_format, loader) -> None:
        """Add image loader to class dictionary."""
        cls._loaders[image_format] = loader

    def load_image(self, image_loc: str, width: int) -> pg.Surface | None:
        """
        Load the image from location at specified width, dependent on file type.

        Parameters
        ----------
        image_loc
            Location of image file.
        width : Optional
            Desired width in pixels of image when loaded, 0 or lower results in no scaling.

        Returns
        -------
        pg.Surface
            Image loaded as `pygame` Surface.
        """
        loader = self._loaders.get(Path(image_loc).suffix, RasterTypeImageLoader)()

        return loader.load_image(image_loc, width)
