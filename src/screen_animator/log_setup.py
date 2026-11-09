import logging

LOG_FILE = f".{__spec__.parent}.log"


def setup_logging(logging_level: str = "") -> None:
    log = logging.getLogger(__spec__.parent)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    log.addHandler(stream_handler)

    logging_level = logging_level.upper()
    if logging_level in logging.getLevelNamesMapping():
        log.setLevel(logging_level)
        file_handler = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] : %(message)s"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging_level)
        log.addHandler(file_handler)

        log.info(50 * "=")
        log.info(
            "Logging to %s at %s level",
            LOG_FILE,
            logging.getLevelName(log.getEffectiveLevel()),
        )
