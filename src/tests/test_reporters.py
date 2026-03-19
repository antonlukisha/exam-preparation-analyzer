from unittest.mock import MagicMock, patch

import pytest

from app.reporters import ReportGenerator


class TestConvertToReport:

    def test_convert_empty_data(self) -> None:
        """
        Test converting empty data returns empty dict.
        """
        result = ReportGenerator.convert_to_report([])
        assert result == {}

    def test_convert_invalid_data_raises_error(self) -> None:
        """
        Test converting invalid data raises ValueError.
        """
        invalid_data = [{"invalid": "data"}]

        with pytest.raises(ValueError, match="Error converting data to report"):
            ReportGenerator.convert_to_report(invalid_data)

    def test_convert_data_with_multiple_records_for_same_student(self) -> None:
        """
        Test converting multiple records for the same student.
        """
        data = [
            {
                "student": "Иван Петров",
                "date": "2026-01-01",
                "coffee_spent": "100",
                "sleep_hours": "8",
                "study_hours": "6",
                "mood": "норм",
                "exam": "История",
            },
            {
                "student": "Иван Петров",
                "date": "2026-01-02",
                "coffee_spent": "150",
                "sleep_hours": "7",
                "study_hours": "8",
                "mood": "норм",
                "exam": "Физика",
            },
            {
                "student": "Иван Петров",
                "date": "2026-01-03",
                "coffee_spent": "200",
                "sleep_hours": "6",
                "study_hours": "10",
                "mood": "устал",
                "exam": "Математика",
            },
        ]

        result = ReportGenerator.convert_to_report(data)

        assert len(result) == 1
        assert "Иван Петров" in result
        assert len(result["Иван Петров"].coffee_spent_values) == 3
        assert result["Иван Петров"].coffee_spent_values == [100, 150, 200]

    def test_convert_data_with_multiple_students(self) -> None:
        """
        Test converting data with multiple students.
        """
        data = [
            {
                "student": "Иван Петров",
                "date": "2026-01-01",
                "coffee_spent": "100",
                "sleep_hours": "8",
                "study_hours": "6",
                "mood": "норм",
                "exam": "Математика",
            },
            {
                "student": "Мария Иванова",
                "date": "2026-01-01",
                "coffee_spent": "200",
                "sleep_hours": "9",
                "study_hours": "4",
                "mood": "отл",
                "exam": "Physics",
            },
            {
                "student": "Петр Сидоров",
                "date": "2026-01-01",
                "coffee_spent": "150",
                "sleep_hours": "7",
                "study_hours": "8",
                "mood": "зомби",
                "exam": "История",
            },
        ]

        result = ReportGenerator.convert_to_report(data)

        assert len(result) == 3
        assert "Иван Петров" in result
        assert "Мария Иванова" in result
        assert "Петр Сидоров" in result
        assert len(result["Иван Петров"].coffee_spent_values) == 1
        assert len(result["Мария Иванова"].coffee_spent_values) == 1
        assert len(result["Петр Сидоров"].coffee_spent_values) == 1


class TestReportGenerator:

    def test_get_available_reports(self) -> None:
        """
        Test getting available report types.
        """
        generator = ReportGenerator()
        reports = generator.get_available_reports()
        assert isinstance(reports, list)

    @patch("app.reporters.PROCESSORS", {"test": {"cls": MagicMock()}})
    def test_generate_report_valid_type(self) -> None:
        """
        Test generating report with valid type.
        """
        generator = ReportGenerator()
        mock_processor = MagicMock()
        generator._processors["test"]["cls"].return_value = mock_processor
        mock_processor.process.return_value = [{"result": "data"}]
        data = {"student": MagicMock()}
        result = generator.generate_report(data, "test")

        assert result == [{"result": "data"}]
        mock_processor.process.assert_called_once_with(data)

    def test_generate_report_invalid_type_raises_error(self) -> None:
        """
        Test generating report with invalid type raises ValueError.
        """
        generator = ReportGenerator()
        data = {"student": MagicMock()}

        with pytest.raises(ValueError, match="Unknown report type `invalid`"):
            generator.generate_report(data, "invalid")

    @patch("app.reporters.tabulate")
    def test_print_report_success(self, mock_tabulate: MagicMock) -> None:
        """
        Test successful report printing.
        """
        generator = ReportGenerator()
        mock_tabulate.return_value = "formatted table"

        with patch.object(generator, "generate_report") as mock_generate:
            mock_generate.return_value = [{"student": "Test", "median_coffee": 100}]

            with patch("builtins.print") as mock_print:
                generator.print_report({}, "median-coffee")

                mock_print.assert_called_once_with("formatted table")
                mock_tabulate.assert_called_once()
                mock_generate.assert_called_once_with({}, "median-coffee")

    @patch("app.reporters.logger")
    def test_print_report_no_data(self, mock_logger: MagicMock) -> None:
        """
        Test printing report with no data.
        """
        generator = ReportGenerator()

        with patch.object(generator, "generate_report") as mock_generate:
            mock_generate.return_value = None
            generator.print_report({}, "median-coffee")
            mock_logger.error.assert_called_once_with(
                "No data to generate report for `median-coffee`"
            )

    @patch("app.reporters.logger")
    def test_print_report_generation_error(self, mock_logger: MagicMock) -> None:
        """
        Test error handling during report generation.
        """
        generator = ReportGenerator()

        with patch.object(generator, "generate_report") as mock_generate:
            mock_generate.side_effect = ValueError("Test error")
            generator.print_report({}, "median-coffee")
            mock_logger.error.assert_called_once_with("Error generating report: Test error")
