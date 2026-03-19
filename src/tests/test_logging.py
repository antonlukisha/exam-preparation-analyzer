import logging
from unittest.mock import MagicMock, patch

import pytest

from app.logging import Color, ColorFormatter, get_logger, setup_logging
from app.logging import logger as root_logger


class TestLogger:

    def test_colors_base(self) -> None:
        """
        Test colors base.
        """
        assert hasattr(Color, "RESET")
        assert hasattr(Color, "DEBUG")
        assert hasattr(Color, "INFO")
        assert hasattr(Color, "WARNING")
        assert hasattr(Color, "ERROR")
        assert hasattr(Color, "CRITICAL")

        assert isinstance(Color.RESET, str)
        assert isinstance(Color.DEBUG, str)
        assert isinstance(Color.INFO, str)
        assert isinstance(Color.WARNING, str)
        assert isinstance(Color.ERROR, str)
        assert isinstance(Color.CRITICAL, str)

        assert Color.RESET == "\033[0m"
        assert Color.DEBUG == "\033[36m"
        assert Color.INFO == "\033[32m"
        assert Color.WARNING == "\033[33m"
        assert Color.ERROR == "\033[31m"
        assert Color.CRITICAL == "\033[1m\033[31m"

    def test_formatter(self) -> None:
        """
        Test formatter.
        """
        formatter = ColorFormatter("%(levelname)s - %(message)s", "%Y-%m-%d")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        assert isinstance(formatter, logging.Formatter)
        assert Color.INFO in formatted
        assert "INFO" in formatted
        assert Color.RESET in formatted

    def test_format_unknown_level_uses_reset(self) -> None:
        """
        Test format unknown level uses reset.
        """
        formatter = ColorFormatter("%(levelname)s")

        record = logging.LogRecord(
            name="test", level=999, pathname="", lineno=0, msg="test", args=(), exc_info=None
        )
        record.levelname = "UNKNOWN"

        formatted = formatter.format(record)

        assert Color.RESET in formatted

    @pytest.mark.parametrize(
        "level,color_attr",
        [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ],
    )
    def test_format_all_levels(self, level: int, color_attr: str) -> None:
        """
        Test format all levels.

        :param level: Logging level.
        :type level: int
        :param color_attr: Color attribute.
        :type color_attr: str
        :return: nothing
        :rtype: None
        """
        formatter = ColorFormatter("%(levelname)s")

        record = logging.LogRecord(
            name="test", level=level, pathname="", lineno=0, msg="test", args=(), exc_info=None
        )

        formatted = formatter.format(record)
        color = getattr(Color, color_attr)

        assert color in formatted
        assert Color.RESET in formatted

    def test_setup_logging_disabled_when_not_verbose(self) -> None:
        """
        Test setup_logging disabled when not verbose.
        """
        with patch("logging.getLogger") as mock_get_logger:
            mock_root = MagicMock()
            mock_get_logger.return_value = mock_root

            with patch("logging.root.manager.loggerDict", {"test": MagicMock()}):
                setup_logging(verbose=False)

                mock_root.setLevel.assert_called_with(logging.CRITICAL + 1)
                mock_root.disabled = True

    def test_setup_logging_enabled_when_verbose(self) -> None:
        """
        Test setup_logging enabled when verbose.
        """
        with patch("logging.getLogger") as mock_get_logger:
            mock_root = MagicMock()
            mock_get_logger.return_value = mock_root

            with patch("app.logging.LOGGER_LEVEL", "DEBUG"), patch("logging.StreamHandler"):
                setup_logging(verbose=True)
                mock_root.setLevel.assert_called()
                mock_root.handlers.clear.assert_called()
                mock_root.addHandler.assert_called_once()

    @patch("app.logging.LOGGER_LEVEL", "INVALID")
    def test_setup_logging_invalid_level_defaults_to_info(self) -> None:
        """
        Test setup_logging invalid level defaults to info.
        """
        with patch("logging.getLogger") as mock_get_logger:
            mock_root = MagicMock()
            mock_get_logger.return_value = mock_root

            with patch("logging.StreamHandler"):
                setup_logging(verbose=True)

                mock_root.setLevel.assert_called_with(logging.INFO)

    @patch("app.logging.LOGGER_LEVEL", "DEBUG")
    def test_setup_logging_creates_color_formatter(self) -> None:
        """
        Test setup_logging creates color formatter.
        """
        with patch("logging.getLogger") as mock_get_logger:
            mock_root = MagicMock()
            mock_get_logger.return_value = mock_root

            with patch("logging.StreamHandler") as mock_handler_class:
                mock_handler = MagicMock()
                mock_handler_class.return_value = mock_handler

                with patch("app.logging.ColorFormatter") as mock_formatter_class:
                    mock_formatter = MagicMock()
                    mock_formatter_class.return_value = mock_formatter

                    setup_logging(verbose=True)

                    mock_formatter_class.assert_called_once()
                    mock_handler.setFormatter.assert_called_with(mock_formatter)

    def test_get_logger(self) -> None:
        """
        Test get_logger.
        """
        logger = get_logger("test_module")
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        logger_same = get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 is not logger2
        assert logger is logger_same

    @patch("logging.getLogger")
    def test_get_logger_calls_logging_getlogger(self, mock_get_logger: MagicMock) -> None:
        """
        Test get_logger calls logging.getLogger.

        :param mock_get_logger: Mock of logging.getLogger.
        :type mock_get_logger: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_get_logger.return_value = MagicMock()

        result = get_logger("test")

        mock_get_logger.assert_called_once_with("test")
        assert result == mock_get_logger.return_value

    def test_root_logger(self) -> None:
        """
        Test root logger.
        """
        assert root_logger is not None
        assert isinstance(root_logger, logging.Logger)
        assert root_logger.name == "root" or root_logger.name == ""
