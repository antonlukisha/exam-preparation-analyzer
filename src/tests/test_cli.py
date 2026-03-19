import sys
from argparse import Namespace
from unittest.mock import MagicMock, patch

from app.cli import main, parse_arguments


class TestParseArguments:

    def test_parse_arguments_valid(self) -> None:
        """
        Test the parse arguments function with valid arguments.
        """
        test_args = ["--files", "data1.csv", "data2.csv", "--report", "median-coffee"]

        with patch.object(sys, "argv", ["cli.py"] + test_args):
            args = parse_arguments()

            assert args.files == ["data1.csv", "data2.csv"]
            assert args.report == "median-coffee"
            assert args.verbose is False

    def test_parse_arguments_with_verbose(self) -> None:
        """
        Test the parse arguments function with verbose flag.
        """
        test_args = ["--files", "data.csv", "--report", "median-coffee", "--verbose"]

        with patch.object(sys, "argv", ["cli.py"] + test_args):
            args = parse_arguments()
            assert args.files == ["data.csv"]
            assert args.report == "median-coffee"
            assert args.verbose is True

    def test_parse_arguments_short_verbose(self) -> None:
        """
        Test the parse arguments function with short verbose flag.
        """
        test_args = ["--files", "data.csv", "--report", "median-coffee", "-v"]

        with patch.object(sys, "argv", ["cli.py"] + test_args):
            args = parse_arguments()

            assert args.verbose is True

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_arguments_calls_parser(self, mock_parse_args: MagicMock) -> None:
        """
        Test that parse_arguments calls the parser.

        :param mock_parse_args: Mocked parse_args method
        :type mock_parse_args: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_parse_args.return_value = Namespace(
            files=["test.csv"], report="median-coffee", verbose=False
        )
        result = parse_arguments()

        assert result.files == ["test.csv"]
        assert result.report == "median-coffee"


class TestMain:

    @patch("app.cli.validate_files_exist")
    @patch("app.cli.read_csv_files")
    @patch("app.cli.ReportGenerator")
    @patch("app.cli.setup_logging")
    def test_main_success_basic(
        self,
        mock_setup_logging: MagicMock,
        mock_report_generator_class: MagicMock,
        mock_read_csv: MagicMock,
        mock_validate_files: MagicMock,
    ) -> None:
        """
        Test the main function with basic success scenario.

        :param mock_setup_logging: Mocked setup_logging function
        :type mock_setup_logging: MagicMock
        :param mock_report_generator_class: Mocked ReportGenerator class
        :type mock_report_generator_class: MagicMock
        :param mock_read_csv: Mocked read_csv_files function
        :type mock_read_csv: MagicMock
        :param mock_validate_files: Mocked validate_files_exist function
        :type mock_validate_files: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate_files.return_value = ["file1.csv"]
        mock_read_csv.return_value = [{"student": "Иван Иванов", "coffee_spent": 100}]
        mock_generator = MagicMock()
        mock_report_generator_class.return_value = mock_generator
        mock_converted_data = {"student_data": "test"}
        mock_report_generator_class.convert_to_report.return_value = mock_converted_data

        with patch("app.cli.parse_arguments") as mock_parse_args:
            mock_parse_args.return_value = Namespace(
                files=["file1.csv"], report="median-coffee", verbose=False
            )

            with patch.object(sys, "exit") as mock_exit:
                main()
                mock_setup_logging.assert_called_once_with(False)
                mock_validate_files.assert_called_once_with(["file1.csv"])
                mock_read_csv.assert_called_once_with(["file1.csv"])
                mock_report_generator_class.convert_to_report.assert_called_once_with(
                    [{"student": "Иван Иванов", "coffee_spent": 100}]
                )
                mock_generator.print_report.assert_called_once_with(
                    mock_converted_data, "median-coffee"
                )
                mock_exit.assert_not_called()

    @patch("app.cli.validate_files_exist")
    @patch("app.cli.read_csv_files")
    @patch("app.cli.ReportGenerator")
    @patch("app.cli.setup_logging")
    def test_main_with_verbose(
        self,
        mock_setup_logging: MagicMock,
        mock_report_generator_class: MagicMock,
        mock_read_csv: MagicMock,
        mock_validate_files: MagicMock,
    ) -> None:
        """
        Test the main function with verbose logging.

        :param mock_setup_logging: Mocked setup_logging function
        :type mock_setup_logging: MagicMock
        :param mock_report_generator_class: Mocked ReportGenerator class
        :type mock_report_generator_class: MagicMock
        :param mock_read_csv: Mocked read_csv_files function
        :type mock_read_csv: MagicMock
        :param mock_validate_files: Mocked validate_files_exist function
        :type mock_validate_files: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate_files.return_value = ["file1.csv"]
        mock_read_csv.return_value = [{"student": "Иван Иванов", "coffee_spent": 100}]
        mock_generator = MagicMock()
        mock_report_generator_class.return_value = mock_generator

        with patch("app.cli.parse_arguments") as mock_parse_args:
            mock_parse_args.return_value = Namespace(
                files=["file1.csv"], report="median-coffee", verbose=True
            )

            with patch.object(sys, "exit") as mock_exit:
                main()

                mock_setup_logging.assert_called_once_with(True)
                mock_exit.assert_not_called()

    @patch("app.cli.validate_files_exist")
    @patch("app.cli.read_csv_files")
    @patch("app.cli.logger")
    def test_main_no_data(
        self, mock_logger: MagicMock, mock_read_csv: MagicMock, mock_validate_files: MagicMock
    ) -> None:
        """
        Test the main function when no data is found in the files.

        :param mock_logger: Mocked logger object
        :type mock_logger: MagicMock
        :param mock_read_csv: Mocked read_csv_files function
        :type mock_read_csv: MagicMock
        :param mock_validate_files: Mocked validate_files_exist function
        :type mock_validate_files: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate_files.return_value = ["file1.csv"]
        mock_read_csv.return_value = []

        with patch("app.cli.parse_arguments") as mock_parse_args:
            mock_parse_args.return_value = Namespace(
                files=["file1.csv"], report="median-coffee", verbose=False
            )

            with patch("app.cli.setup_logging"), patch.object(sys, "exit") as mock_exit:
                main()
                mock_logger.warning.assert_called_with("No data found in the provided files.")
                mock_exit.assert_not_called()

    @patch("app.cli.validate_files_exist")
    @patch("app.cli.logger")
    def test_main_file_not_found(
        self, mock_logger: MagicMock, mock_validate_files: MagicMock
    ) -> None:
        """
        Test the main function when a file is not found.

        :param mock_logger: Mocked logger object
        :type mock_logger: MagicMock
        :param mock_validate_files: Mocked validate_files_exist function
        :type mock_validate_files: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate_files.side_effect = FileNotFoundError("File not found: test.csv")

        with patch("app.cli.parse_arguments") as mock_parse_args:
            mock_parse_args.return_value = Namespace(
                files=["nonexistent.csv"], report="median-coffee", verbose=False
            )

            with patch("app.cli.setup_logging"), patch.object(sys, "exit") as mock_exit:
                main()
                mock_logger.error.assert_called_once()
                mock_exit.assert_called_once_with(1)

    @patch("app.cli.validate_files_exist")
    @patch("app.cli.read_csv_files")
    @patch("app.cli.logger")
    def test_main_value_error(
        self, mock_logger: MagicMock, mock_read_csv: MagicMock, mock_validate_files: MagicMock
    ) -> None:
        """
        Test the main function when a ValueError occurs.

        :param mock_logger: Mocked logger object
        :type mock_logger: MagicMock
        :param mock_read_csv: Mocked read_csv_files function
        :type mock_read_csv: MagicMock
        :param mock_validate_files: Mocked validate_files_exist function
        :type mock_validate_files: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate_files.return_value = ["file1.csv"]
        mock_read_csv.side_effect = ValueError("Invalid value in CSV")

        with patch("app.cli.parse_arguments") as mock_parse_args:
            mock_parse_args.return_value = Namespace(
                files=["file1.csv"], report="median-coffee", verbose=False
            )

            with patch("app.cli.setup_logging"), patch.object(sys, "exit") as mock_exit:
                main()
                mock_logger.error.assert_called_once()
                mock_exit.assert_called_once_with(1)

    @patch("app.cli.validate_files_exist")
    @patch("app.cli.read_csv_files")
    @patch("app.cli.logger")
    def test_main_keyboard_interrupt(
        self, mock_logger: MagicMock, mock_read_csv: MagicMock, mock_validate_files: MagicMock
    ) -> None:
        """
        Test the main function when a KeyboardInterrupt occurs.

        :param mock_logger: Mocked logger object
        :type mock_logger: MagicMock
        :param mock_read_csv: Mocked read_csv_files function
        :type mock_read_csv: MagicMock
        :param mock_validate_files: Mocked validate_files_exist function
        :type mock_validate_files: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate_files.return_value = ["file1.csv"]
        mock_read_csv.side_effect = KeyboardInterrupt()

        with patch("app.cli.parse_arguments") as mock_parse_args:
            mock_parse_args.return_value = Namespace(
                files=["file1.csv"], report="median-coffee", verbose=False
            )

            with patch("app.cli.setup_logging"), patch.object(sys, "exit") as mock_exit:
                main()
                mock_logger.info.assert_called_with("Process stopped by user")
                mock_exit.assert_called_once_with(0)

    @patch("app.cli.validate_files_exist")
    @patch("app.cli.read_csv_files")
    @patch("app.cli.logger")
    def test_main_unexpected_error(
        self, mock_logger: MagicMock, mock_read_csv: MagicMock, mock_validate_files: MagicMock
    ) -> None:
        """
        Test the main function when an unexpected error occurs.

        :param mock_logger: Mocked logger object
        :type mock_logger: MagicMock
        :param mock_read_csv: Mocked read_csv_files function
        :type mock_read_csv: MagicMock
        :param mock_validate_files: Mocked validate_files_exist function
        :type mock_validate_files: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate_files.return_value = ["file1.csv"]
        mock_read_csv.side_effect = Exception("Something unexpected")

        with patch("app.cli.parse_arguments") as mock_parse_args:
            mock_parse_args.return_value = Namespace(
                files=["file1.csv"], report="median-coffee", verbose=False
            )

            with patch("app.cli.setup_logging"), patch.object(sys, "exit") as mock_exit:
                main()
                mock_logger.error.assert_called_once()
                mock_exit.assert_called_once_with(1)

    @patch("app.cli.validate_files_exist")
    @patch("app.cli.read_csv_files")
    @patch("app.cli.ReportGenerator")
    def test_main_with_multiple_files(
        self,
        mock_report_generator_class: MagicMock,
        mock_read_csv: MagicMock,
        mock_validate_files: MagicMock,
    ) -> None:
        """
        Test the main function with multiple files.

        :param mock_report_generator_class: Mocked ReportGenerator class
        :type mock_report_generator_class: MagicMock
        :param mock_read_csv: Mocked read_csv_files function
        :type mock_read_csv: MagicMock
        :param mock_validate_files: Mocked validate_files_exist function
        :type mock_validate_files: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate_files.return_value = ["file1.csv", "file2.csv"]
        mock_read_csv.return_value = [
            {"student": "Иван Иванов", "coffee_spent": 100},
            {"student": "Алексей Смирнов", "coffee_spent": 200},
        ]
        mock_generator = MagicMock()
        mock_report_generator_class.return_value = mock_generator

        with patch("app.cli.parse_arguments") as mock_parse_args:
            mock_parse_args.return_value = Namespace(
                files=["file1.csv", "file2.csv"], report="median-coffee", verbose=False
            )

            with patch("app.cli.setup_logging"), patch.object(sys, "exit") as mock_exit:
                main()
                mock_validate_files.assert_called_once_with(["file1.csv", "file2.csv"])
                mock_exit.assert_not_called()
