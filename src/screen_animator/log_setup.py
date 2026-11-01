import logging
from pathlib import Path

from screen_animator import args

LOG_DIR = "logs"
LOG_FILE = f".screen-animator.log"


def _setup_logging(logging_level: str):
    log = logging.getLogger(__package__)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    log.addHandler(stream_handler)

    logging_level = logging_level.upper()
    if logging_level in logging.getLevelNamesMapping():
        log.setLevel(logging_level)
        Path(LOG_DIR).mkdir(exist_ok=True)
        log_path = Path(LOG_DIR, LOG_FILE)
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter(
            "[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s"
        )
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

        log.info(50 * "=")
        log.info(
            "Logging to %s at %s level",
            log_path,
            logging.getLevelName(log.getEffectiveLevel()),
        )


_setup_logging(args.logging)
