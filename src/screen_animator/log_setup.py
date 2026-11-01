import logging
from pathlib import Path

LOG_DIR = "logs"
LOG_FILE = "screen-animator.log"


def setup_logging(logging_level: str = "") -> None:
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
        file_handler.setLevel(logging_level)
        log.addHandler(file_handler)

        log.info(50 * "=")
        log.info(
            "Logging to %s at %s level",
            log_path,
            logging.getLevelName(log.getEffectiveLevel()),
        )
