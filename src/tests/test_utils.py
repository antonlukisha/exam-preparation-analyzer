from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from app.utils import (
    open_csv_file,
    read_csv_file,
    read_csv_files,
    validate_data,
    validate_file_exists,
    validate_files_exist,
)


class TestValidateFileExists:

    def test_valid_file_returns_path(self, tmp_path: Path) -> None:
        """
        Test that a valid file returns its Path object.

        :param tmp_path: Temporary path fixture
        :type tmp_path: Path
        :return: nothing
        :rtype: None
        """
        test_file = tmp_path / "test.csv"
        test_file.touch()
        result = validate_file_exists(test_file)
        assert isinstance(result, Path)
        assert result == test_file.resolve()

    def test_file_not_found_raises_error(self) -> None:
        """
        Test that a non-existent file raises a FileNotFoundError.
        """
        with pytest.raises(FileNotFoundError, match="File not found"):
            validate_file_exists("invalid.csv")

    def test_directory_raises_error(self, tmp_path: Path) -> None:
        """
        Test that a directory raises a RuntimeError.

        :param tmp_path: Temporary path fixture
        :type tmp_path: Path
        :return: nothing
        :rtype: None
        """
        with pytest.raises(RuntimeError, match="Path is not a file"):
            validate_file_exists(tmp_path)

    def test_all_files_valid(self, tmp_path: Path) -> None:
        """
        Test that all files in a list are valid.

        :param tmp_path: Temporary path fixture
        :type tmp_path: Path
        :return: nothing
        :rtype: None
        """
        file1 = tmp_path / "test1.csv"
        file2 = tmp_path / "test2.csv"
        file1.touch()
        file2.touch()

        result = validate_files_exist([file1, file2])

        assert len(result) == 2
        assert all(isinstance(p, Path) for p in result)

    def test_invalid_file_raises_error(self, tmp_path: Path) -> None:
        """
        Test that an invalid file raises an error.

        :param tmp_path: Temporary path fixture
        :type tmp_path: Path
        :return: nothing
        :rtype: None
        """
        file1 = tmp_path / "test1.csv"
        file1.touch()
        with pytest.raises(RuntimeError, match="File not found"):
            validate_files_exist([file1, "invalid.csv"])

        with pytest.raises(RuntimeError):
            validate_files_exist(["invalid1.csv", "invalid2.csv"])


class TestOpenCsvFile:

    @patch("builtins.open", new_callable=mock_open)
    def test_successful_open(self, mock_file: MagicMock) -> None:
        """
        Test successful opening of a CSV file.

        :param mock_file: Mocked open function
        :type mock_file: MagicMock
        :return: nothing
        :rtype: None
        """
        with open_csv_file("test.csv"):
            pass
        mock_file.assert_called_once_with(Path("test.csv"), "r", encoding="utf-8")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_file_not_found(self, mock_file: MagicMock) -> None:
        """
        Test file not found error handling.

        :param mock_file: Mocked open function
        :type mock_file: MagicMock
        :return: nothing
        :rtype: None
        """
        with pytest.raises(FileNotFoundError, match="File not found"), open_csv_file("missing.csv"):
            pass
        mock_file.assert_called_once_with(Path("missing.csv"), "r", encoding="utf-8")

    @patch("builtins.open", side_effect=PermissionError)
    def test_permission_error(self, mock_file: MagicMock) -> None:
        """
        Test permission error handling.

        :param mock_file: Mocked open function
        :type mock_file: MagicMock
        :return: nothing
        :rtype: None
        """
        with (
            pytest.raises(PermissionError, match="Not enough permissions"),
            open_csv_file("protected.csv"),
        ):
            pass
        mock_file.assert_called_once_with(Path("protected.csv"), "r", encoding="utf-8")

    @patch("builtins.open", side_effect=UnicodeDecodeError("", b"", 0, 0, ""))
    def test_unicode_decode_error(self, mock_file: MagicMock) -> None:
        """
        Test UnicodeDecodeError handling.

        :param mock_file: Mocked open function
        :type mock_file: MagicMock
        :return: nothing
        :rtype: None
        """
        with pytest.raises(RuntimeError, match="encoding"), open_csv_file("bad_encoding.csv"):
            pass
        mock_file.assert_called_once_with(Path("bad_encoding.csv"), "r", encoding="utf-8")

    @patch("builtins.open", side_effect=Exception("Any error"))
    def test_unknown_error(self, mock_file: MagicMock) -> None:
        """
        Test unknown error handling.

        :param mock_file: Mocked open function
        :type mock_file: MagicMock
        :return: nothing
        :rtype: None
        """
        with pytest.raises(Exception, match="Any error"), open_csv_file("unknown.csv"):
            pass
        mock_file.assert_called_once_with(Path("unknown.csv"), "r", encoding="utf-8")


class TestValidateData:

    def test_valid_data_returns_true(self) -> None:
        """
        Test that valid data returns true.
        """
        data = {
            "student": "Ивана Иванов",
            "date": "2026-01-01",
            "coffee_spent": "100",
            "sleep_hours": "7.5",
            "study_hours": "8",
            "mood": "норм",
            "exam": "Математика",
        }

        assert validate_data(data) is True
        assert data["coffee_spent"] == 100
        assert data["sleep_hours"] == 7.5
        assert data["study_hours"] == 8

    def test_missing_data_returns_false(self) -> None:
        """
        Test that missing data returns false.
        """
        data_missing_student = {
            "date": "2026-01-01",
            "coffee_spent": "100",
            "sleep_hours": "7.5",
            "study_hours": "8",
        }

        data_missing_date = {
            "student": "Ивана Иванов",
            "coffee_spent": "100",
            "sleep_hours": "7.5",
            "study_hours": "8",
        }
        assert validate_data(data_missing_student) is False
        assert validate_data(data_missing_date) is False

    @pytest.mark.parametrize(
        "field, value",
        [
            ("coffee_spent", "invalid"),
            ("sleep_hours", "bad"),
            ("study_hours", "not_int"),
        ],
    )
    def test_invalid_numeric_values_return_false(self, field: str, value: str) -> None:
        """
        Test that invalid numeric values return false.

        :param field: Field name
        :type field: str
        :param value: Invalid value
        :type value: str
        :return: nothing
        :rtype: None
        """
        data = {
            "student": "Ивана Иванов",
            "date": "2026-01-01",
            "coffee_spent": "100",
            "sleep_hours": "7.5",
            "study_hours": "8",
            field: value,
        }
        assert validate_data(data) is False

    @pytest.mark.parametrize(
        "field, value",
        [
            ("coffee_spent", -10),
            ("sleep_hours", -1.0),
            ("study_hours", -5),
        ],
    )
    def test_negative_values_return_false(self, field: str, value: str) -> None:
        """
        Test that negative values return false.

        :param field: Field name
        :type field: str
        :param value: Invalid value
        :type value: str
        :return: nothing
        :rtype: None
        """
        data = {
            "student": "Ивана Иванов",
            "date": "2026-01-01",
            "coffee_spent": 100,
            "sleep_hours": 7.5,
            "study_hours": 8,
            field: value,
        }
        assert validate_data(data) is False

    @pytest.mark.parametrize("sleep_hours", [-0.1, 24.1, 25.0])
    def test_sleep_hours_out_of_range_returns_false(self, sleep_hours: float) -> None:
        """
        Test that sleep hours out of range returns false.

        :param sleep_hours: Invalid sleep hours value
        :type sleep_hours: float
        :return: nothing
        :rtype: None
        """
        data = {
            "student": "Ивана Иванов",
            "date": "2026-01-01",
            "coffee_spent": 100,
            "sleep_hours": sleep_hours,
            "study_hours": 8,
        }
        assert validate_data(data) is False


class TestReadCsvFile:

    @patch("app.utils.validate_file_exists")
    @patch("app.utils.open_csv_file")
    @patch("csv.DictReader")
    def test_successful_read(
        self, mock_dict_reader: MagicMock, mock_open_csv: MagicMock, mock_validate: MagicMock
    ) -> None:
        """
        Test successful CSV file reading.

        :param mock_dict_reader: Mock DictReader
        :type mock_dict_reader: MagicMock
        :param mock_open_csv: Mock open_csv_file
        :type mock_open_csv: MagicMock
        :param mock_validate: Mock validate_file_exists
        :type mock_validate: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate.return_value = Path("test.csv")
        mock_reader = MagicMock()
        mock_reader.fieldnames = [
            "student",
            "coffee_spent",
            "date",
            "sleep_hours",
            "study_hours",
            "mood",
            "exam",
        ]
        mock_reader.__iter__.return_value = [
            {"student": "Ивана Иванов", "coffee_spent": "100", "date": "2026-01-01"},
        ]
        mock_dict_reader.return_value = mock_reader
        mock_file = MagicMock()
        mock_open_csv.return_value.__enter__.return_value = mock_file

        with patch("app.utils.validate_data", return_value=True):
            result = read_csv_file("test.csv")

        assert len(result) == 1
        assert result[0]["student"] == "Ивана Иванов"

    @patch("app.utils.validate_file_exists")
    @patch("app.utils.open_csv_file")
    @patch("csv.DictReader")
    def test_empty_file_raises_error(
        self, mock_dict_reader: MagicMock, mock_open_csv: MagicMock, mock_validate: MagicMock
    ) -> None:
        """
        Test that an empty file raises an error.

        :param mock_dict_reader: Mock DictReader
        :type mock_dict_reader: MagicMock
        :param mock_open_csv: Mock open_csv_file
        :type mock_open_csv: MagicMock
        :param mock_validate: Mock validate_file_exists
        :type mock_validate: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate.return_value = Path("test.csv")
        mock_reader = MagicMock()
        mock_reader.fieldnames = None
        mock_dict_reader.return_value = mock_reader
        mock_file = MagicMock()
        mock_open_csv.return_value.__enter__.return_value = mock_file

        with pytest.raises(RuntimeError, match="File is empty"):
            read_csv_file("test.csv")

    @patch("app.utils.validate_file_exists")
    @patch("app.utils.open_csv_file")
    @patch("csv.DictReader")
    def test_missing_columns_raises_error(
        self, mock_dict_reader: MagicMock, mock_open_csv: MagicMock, mock_validate: MagicMock
    ) -> None:
        """
        Test that missing required columns raises an error.

        :param mock_dict_reader: Mock DictReader
        :type mock_dict_reader: MagicMock
        :param mock_open_csv: Mock open_csv_file
        :type mock_open_csv: MagicMock
        :param mock_validate: Mock validate_file_exists
        :type mock_validate: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate.return_value = Path("test.csv")
        mock_reader = MagicMock()
        mock_reader.fieldnames = ["student", "coffee_spent"]
        mock_dict_reader.return_value = mock_reader
        mock_file = MagicMock()
        mock_open_csv.return_value.__enter__.return_value = mock_file

        with (
            patch("app.config.REQUIRED_COLUMNS", {"student", "coffee_spent", "date"}),
            pytest.raises(RuntimeError, match="Expected required columns"),
        ):
            read_csv_file("test.csv")

    @patch("app.utils.validate_file_exists")
    @patch("app.utils.open_csv_file")
    @patch("csv.DictReader")
    @patch("app.utils.validate_data")
    @patch("app.utils.logger")
    def test_exception_during_row_processing_is_caught(
        self,
        mock_logger: MagicMock,
        mock_validate_data: MagicMock,
        mock_dict_reader: MagicMock,
        mock_open_csv: MagicMock,
        mock_validate: MagicMock,
    ) -> None:
        """
        Test that exceptions during row processing are caught.

        :param mock_logger: Mock logger
        :type mock_logger: MagicMock
        :param mock_validate_data: Mock validate_data
        :type mock_validate_data: MagicMock
        :param mock_dict_reader: Mock DictReader
        :type mock_dict_reader: MagicMock
        :param mock_open_csv: Mock open_csv_file
        :type mock_open_csv: MagicMock
        :param mock_validate: Mock validate_file_exists
        :type mock_validate: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_validate.return_value = Path("test.csv")
        mock_reader = MagicMock()
        mock_reader.fieldnames = [
            "student",
            "coffee_spent",
            "date",
            "sleep_hours",
            "study_hours",
            "mood",
            "exam",
        ]
        mock_reader.__iter__.return_value = [
            {"student": "Ивана Иванов", "coffee_spent": "100", "date": "2024-01-01"},
            {"student": "Михаил Павлов", "coffee_spent": "200", "date": "2024-01-01"},
        ]
        mock_dict_reader.return_value = mock_reader
        mock_file = MagicMock()
        mock_open_csv.return_value.__enter__.return_value = mock_file
        mock_validate_data.side_effect = [True, ValueError("Test error")]

        result = read_csv_file("test.csv")

        assert len(result) == 1
        assert result[0]["student"] == "Ивана Иванов"
        mock_logger.warning.assert_called_once()
        assert "Test error" in mock_logger.warning.call_args[0][0]

    @patch("app.utils.read_csv_file")
    def test_single_file_success(self, mock_read: MagicMock) -> None:
        """
        Test single file read successfully.

        :param mock_read: Mock read_csv_file
        :type mock_read: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_read.return_value = [{"student": "Ивана Иванов"}]
        result = read_csv_files(["test1.csv"])

        assert len(result) == 1
        mock_read.assert_called_once_with("test1.csv")

    @patch("app.utils.read_csv_file")
    def test_multiple_files_success(self, mock_read: MagicMock) -> None:
        """
        Test multiple files read successfully.

        :param mock_read: Mock read_csv_file
        :type mock_read: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_read.side_effect = [
            [{"student": "Ивана Иванов"}],
            [{"student": "Михаил Павлов"}],
        ]
        result = read_csv_files(["test1.csv", "test2.csv"])

        assert len(result) == 2
        assert mock_read.call_count == 2

    @patch("app.utils.read_csv_file")
    def test_one_file_fails_continues(self, mock_read: MagicMock) -> None:
        """
        Test that one file fails but continues.

        :param mock_read: Mock read_csv_file
        :type mock_read: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_read.side_effect = [
            [{"student": "Ивана Иванов"}],
            RuntimeError("File error"),
            [{"student": "Михаил Павлов"}],
        ]

        with patch("app.utils.logger") as mock_logger:
            result = read_csv_files(["test1.csv", "invalid.csv", "test3.csv"])

        assert len(result) == 2
        assert result[0]["student"] == "Ивана Иванов"
        assert result[1]["student"] == "Михаил Павлов"
        mock_logger.error.assert_called_once()
        mock_logger.warning.assert_called_once()

    @patch("app.utils.read_csv_file")
    def test_all_files_fail_raises_error(self, mock_read: MagicMock) -> None:
        """
        Test that all files fail raises an error.

        :param mock_read: Mock read_csv_file
        :type mock_read: MagicMock
        :return: nothing
        :rtype: None
        """
        mock_read.side_effect = [
            RuntimeError("Error 1"),
            RuntimeError("Error 2"),
        ]

        with pytest.raises(RuntimeError, match="No valid data found"):
            read_csv_files(["invalid1.csv", "invalid2.csv"])


class TestUtilsIntegration:

    def test_read_csv_file_integration(self, tmp_path: Path) -> None:
        """
        Test the read_csv_file function with a valid CSV file.

        :param tmp_path: Temporary path fixture
        :type tmp_path: Path
        :return: nothing
        :rtype: None
        """
        csv_path = tmp_path / "test.csv"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("student,coffee_spent,date,sleep_hours,study_hours,mood,exam\n")
            f.write("Ивана Иванов,100,2026-01-01,7.5,8,зомби,Математика\n")
            f.write("Елена Волкова,invalid,2026-01-01,8.0,6,норм,Физика\n")
            f.write("Михаил Павлов,200,2026-01-01,7.0,7,хор,История\n")

        with patch("app.utils.validate_data") as mock_validate:
            mock_validate.side_effect = [True, False, True]

            result = read_csv_file(csv_path)

        assert len(result) == 2
        assert result[0]["student"] == "Ивана Иванов"
        assert result[1]["student"] == "Михаил Павлов"
