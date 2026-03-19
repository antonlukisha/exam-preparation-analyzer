import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from app.scripts import lint


class TestLint:

    @patch("app.scripts.subprocess.run")
    def test_lint_calls_all_tools(self, mock_run: MagicMock) -> None:
        """
        Test that lint calls all the tools in the correct order.

        :param mock_run: Mocked subprocess run
        :type mock_run: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_run.return_value = None

        lint()

        expected_calls = [
            call(["black", "."]),
            call(["isort", "."]),
            call(["ruff", "check", ".", "--fix"]),
            call(["mypy", "."]),
        ]

        assert mock_run.call_count == 4
        mock_run.assert_has_calls(expected_calls)

    @patch("app.scripts.subprocess.run")
    def test_lint_subprocess_errors(self, mock_run: MagicMock) -> None:
        """
        Test that lint raises an error if a subprocess call fails.

        :param mock_run: Mocked subprocess run
        :type mock_run: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_run.side_effect = [
            None,
            subprocess.CalledProcessError(1, ["isort", "."]),
        ]

        with pytest.raises(subprocess.CalledProcessError):
            lint()

        assert mock_run.call_count == 2
        mock_run.assert_has_calls(
            [
                call(["black", "."]),
                call(["isort", "."]),
            ]
        )
