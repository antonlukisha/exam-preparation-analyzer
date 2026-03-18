import logging
import sys

from .config import LOGGER_LEVEL


class Color:
    RESET = "\033[0m"
    DEBUG = "\033[36m"
    INFO = "\033[32m"
    WARNING = "\033[33m"
    ERROR = "\033[31m"
    CRITICAL = "\033[1m\033[31m"


class ColorFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record.

        :param record: Record to format.
        :type record: logging.LogRecord
        :return: The formatted log record.
        :rtype: str
        """
        orig_levelname = record.levelname
        color = getattr(Color, record.levelname, Color.RESET)
        record.levelname = f"{color}{record.levelname}{Color.RESET}"
        msg = super().format(record)
        record.levelname = orig_levelname
        return msg


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging.

    :param verbose: True to enable debug logging, False otherwise.
    :type verbose: bool
    :return: nothing
    :rtype: None
    """
    root_logger = logging.getLogger()

    if not verbose:
        root_logger.setLevel(logging.CRITICAL + 1)
        root_logger.disabled = True

        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).disabled = True
            logging.getLogger(name).setLevel(logging.CRITICAL + 1)
    else:
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        log_level = level_map.get(LOGGER_LEVEL.upper(), logging.INFO)

        root_logger.setLevel(log_level)
        root_logger.handlers.clear()
        root_logger.disabled = False

        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        formatter = ColorFormatter(log_format, date_format)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.handlers.clear()
        root_logger.addHandler(console_handler)


logger = logging.getLogger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    :param name: The name of the logger.
    :type name: str
    :return: The logger.
    :rtype: logging.Logger
    """
    return logging.getLogger(name)
