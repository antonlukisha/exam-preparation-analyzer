from unittest.mock import MagicMock

from app.models import StudentStatistics
from app.processors import MedianCoffeeProcessor


class TestMedianCoffeeProcessor:

    def test_process_with_single_student(self) -> None:
        """
        Test that the processor returns the correct result for a single student.
        """
        stats = MagicMock(spec=StudentStatistics)
        stats.median_coffee = 450
        data = {"Иван Иванов": stats}
        processor = MedianCoffeeProcessor()
        result = processor.process(data)

        assert len(result) == 1
        assert result[0]["student"] == "Иван Иванов"
        assert result[0]["median_coffee"] == 450

    def test_process_with_multiple_students_sorts_descending(self) -> None:
        """
        Test that the processor returns the correct result for multiple students and sorts them descending.
        """
        ivan_stats = MagicMock(spec=StudentStatistics)
        ivan_stats.median_coffee = 450
        maria_stats = MagicMock(spec=StudentStatistics)
        maria_stats.median_coffee = 600
        petr_stats = MagicMock(spec=StudentStatistics)
        petr_stats.median_coffee = 300
        data = {
            "Иван Иванов": ivan_stats,
            "Мария Иванова": maria_stats,
            "Петр Сидоров": petr_stats,
        }
        processor = MedianCoffeeProcessor()
        result = processor.process(data)

        assert len(result) == 3
        assert result[0]["student"] == "Мария Иванова"
        assert result[0]["median_coffee"] == 600
        assert result[1]["student"] == "Иван Иванов"
        assert result[1]["median_coffee"] == 450
        assert result[2]["student"] == "Петр Сидоров"
        assert result[2]["median_coffee"] == 300
