"""
Tests for models.py - StudentRecord and StudentStatistics classes.
"""

import pytest
from datetime import datetime
from dataclasses import dataclass

from app.models import StudentRecord, StudentStatistics


class TestStudentRecord:
    """Tests for StudentRecord class."""

    def test_create_valid_record(self):
        """Test creating a StudentRecord with valid data."""
        record = StudentRecord(
            student="Иван Петров",
            date=datetime(2024, 6, 1),
            coffee_spent=450,
            sleep_hours=7.5,
            study_hours=8,
            mood="норм",
            exam="Математика"
        )

        assert record.student == "Иван Петров"
        assert record.date == datetime(2024, 6, 1)
        assert record.coffee_spent == 450
        assert record.sleep_hours == 7.5
        assert record.study_hours == 8
        assert record.mood == "норм"
        assert record.exam == "Математика"

    def test_from_dict_valid(self):
        """Test creating a StudentRecord from valid dictionary."""
        data = {
            "student": "Мария Сидорова",
            "date": "2024-06-02",
            "coffee_spent": "300",
            "sleep_hours": "8.0",
            "study_hours": "6",
            "mood": "отл",
            "exam": "Физика"
        }

        record = StudentRecord.from_dict(data)

        assert record.student == "Мария Сидорова"
        assert record.date == datetime(2024, 6, 2)
        assert record.coffee_spent == 300
        assert record.sleep_hours == 8.0
        assert record.study_hours == 6
        assert record.mood == "отл"
        assert record.exam == "Физика"

    @pytest.mark.parametrize("missing_field", [
        "student", "date", "coffee_spent", "sleep_hours",
        "study_hours", "mood", "exam"
    ])
    def test_from_dict_missing_field(self, missing_field):
        """Test from_dict with missing required fields."""
        data = {
            "student": "Иван Петров",
            "date": "2024-06-01",
            "coffee_spent": "450",
            "sleep_hours": "7.5",
            "study_hours": "8",
            "mood": "норм",
            "exam": "Математика"
        }
        del data[missing_field]

        with pytest.raises(KeyError) as excinfo:
            StudentRecord.from_dict(data)

        assert f"Expected required field {missing_field}" in str(excinfo.value)

    @pytest.mark.parametrize("field,invalid_value,expected_error", [
        ("date", "2024/06/01", "Incorrect value"),  # Wrong date format
        ("coffee_spent", "abc", "Incorrect value"),  # Not a number
        ("sleep_hours", "xyz", "Incorrect value"),  # Not a number
        ("study_hours", "7.5", "Incorrect value"),  # Float instead of int
    ])
    def test_from_dict_invalid_values(self, field, invalid_value, expected_error):
        """Test from_dict with invalid field values."""
        data = {
            "student": "Иван Петров",
            "date": "2024-06-01",
            "coffee_spent": "450",
            "sleep_hours": "7.5",
            "study_hours": "8",
            "mood": "норм",
            "exam": "Математика"
        }
        data[field] = invalid_value

        with pytest.raises(ValueError) as excinfo:
            StudentRecord.from_dict(data)

        assert expected_error in str(excinfo.value)

    def test_post_init_negative_coffee_spent(self):
        """Test validation of negative coffee_spent."""
        with pytest.raises(ValueError) as excinfo:
            StudentRecord(
                student="Иван Петров",
                date=datetime(2024, 6, 1),
                coffee_spent=-100,  # Negative
                sleep_hours=7.5,
                study_hours=8,
                mood="норм",
                exam="Математика"
            )

        assert "coffee_spent not be negative" in str(excinfo.value)

    @pytest.mark.parametrize("sleep_hours", [-1.0, 24.5, 25.0])
    def test_post_init_invalid_sleep_hours(self, sleep_hours):
        """Test validation of sleep_hours range."""
        with pytest.raises(ValueError) as excinfo:
            StudentRecord(
                student="Иван Петров",
                date=datetime(2024, 6, 1),
                coffee_spent=450,
                sleep_hours=sleep_hours,  # Invalid value
                study_hours=8,
                mood="норм",
                exam="Математика"
            )

        assert "sleep_hours must be in range [0, 24]" in str(excinfo.value)

    def test_post_init_negative_study_hours(self):
        """Test validation of negative study_hours."""
        with pytest.raises(ValueError) as excinfo:
            StudentRecord(
                student="Иван Петров",
                date=datetime(2024, 6, 1),
                coffee_spent=450,
                sleep_hours=7.5,
                study_hours=-5,  # Negative
                mood="норм",
                exam="Математика"
            )

        assert "study_hours not be negative" in str(excinfo.value)

    def test_edge_case_zero_values(self):
        """Test edge cases with zero values."""
        record = StudentRecord(
            student="Петр Иванов",
            date=datetime(2024, 6, 1),
            coffee_spent=0,  # Zero coffee
            sleep_hours=0,  # No sleep
            study_hours=0,  # No study
            mood="норм",
            exam="История"
        )

        assert record.coffee_spent == 0
        assert record.sleep_hours == 0
        assert record.study_hours == 0

    def test_edge_case_max_values(self):
        """Test edge cases with maximum values."""
        record = StudentRecord(
            student="Анна Петрова",
            date=datetime(2024, 6, 1),
            coffee_spent=10000,  # Large coffee amount
            sleep_hours=24.0,  # Max sleep
            study_hours=24,  # Max study
            mood="норм",
            exam="Литература"
        )

        assert record.coffee_spent == 10000
        assert record.sleep_hours == 24.0
        assert record.study_hours == 24


class TestStudentStatistics:
    """Tests for StudentStatistics class."""

    def test_create_empty_statistics(self):
        """Test creating empty StudentStatistics."""
        stats = StudentStatistics("Иван Петров")

        assert stats.student == "Иван Петров"
        assert stats.coffee_spent_values == []

    def test_add_record(self):
        """Test adding records to statistics."""
        stats = StudentStatistics("Иван Петров")

        # Create some test records
        record1 = StudentRecord(
            student="Иван Петров",
            date=datetime(2024, 6, 1),
            coffee_spent=450,
            sleep_hours=7.5,
            study_hours=8,
            mood="норм",
            exam="Математика"
        )

        record2 = StudentRecord(
            student="Иван Петров",
            date=datetime(2024, 6, 2),
            coffee_spent=500,
            sleep_hours=6.5,
            study_hours=10,
            mood="устал",
            exam="Математика"
        )

        stats.add_record(record1)
        assert stats.coffee_spent_values == [450]

        stats.add_record(record2)
        assert stats.coffee_spent_values == [450, 500]

    def test_median_coffee_with_single_value(self):
        """Test median calculation with single value."""
        stats = StudentStatistics("Иван Петров")

        record = StudentRecord(
            student="Иван Петров",
            date=datetime(2024, 6, 1),
            coffee_spent=450,
            sleep_hours=7.5,
            study_hours=8,
            mood="норм",
            exam="Математика"
        )

        stats.add_record(record)
        assert stats.median_coffee == 450

    def test_median_coffee_with_multiple_values(self):
        """Test median calculation with multiple values."""
        stats = StudentStatistics("Иван Петров")
        values = [450, 500, 350, 600, 550]

        for i, value in enumerate(values):
            record = StudentRecord(
                student="Иван Петров",
                date=datetime(2024, 6, i + 1),
                coffee_spent=value,
                sleep_hours=7.5,
                study_hours=8,
                mood="норм",
                exam="Математика"
            )
            stats.add_record(record)

        # Median of [350, 450, 500, 550, 600] is 500
        assert stats.median_coffee == 500

    def test_median_coffee_even_number_of_values(self):
        """Test median calculation with even number of values."""
        stats = StudentStatistics("Иван Петров")
        values = [450, 500, 350, 600]

        for i, value in enumerate(values):
            record = StudentRecord(
                student="Иван Петров",
                date=datetime(2024, 6, i + 1),
                coffee_spent=value,
                sleep_hours=7.5,
                study_hours=8,
                mood="норм",
                exam="Математика"
            )
            stats.add_record(record)

        # Median of [350, 450, 500, 600] is 475 (average of 450 and 500)
        assert stats.median_coffee == 475

    def test_median_coffee_returns_int(self):
        """Test that median_coffee returns int."""
        stats = StudentStatistics("Иван Петров")

        record = StudentRecord(
            student="Иван Петров",
            date=datetime(2024, 6, 1),
            coffee_spent=450,
            sleep_hours=7.5,
            study_hours=8,
            mood="норм",
            exam="Математика"
        )

        stats.add_record(record)
        result = stats.median_coffee

        assert isinstance(result, int)
        assert result == 450

    def test_add_multiple_students_separately(self):
        """Test statistics for multiple students."""
        ivan_stats = StudentStatistics("Иван Петров")
        maria_stats = StudentStatistics("Мария Сидорова")

        # Ivan's records
        ivan_record1 = StudentRecord(
            student="Иван Петров",
            date=datetime(2024, 6, 1),
            coffee_spent=450,
            sleep_hours=7.5,
            study_hours=8,
            mood="норм",
            exam="Математика"
        )

        ivan_record2 = StudentRecord(
            student="Иван Петров",
            date=datetime(2024, 6, 2),
            coffee_spent=500,
            sleep_hours=6.5,
            study_hours=10,
            mood="устал",
            exam="Математика"
        )

        # Maria's records
        maria_record1 = StudentRecord(
            student="Мария Сидорова",
            date=datetime(2024, 6, 1),
            coffee_spent=200,
            sleep_hours=8.0,
            study_hours=5,
            mood="отл",
            exam="Физика"
        )

        ivan_stats.add_record(ivan_record1)
        ivan_stats.add_record(ivan_record2)
        maria_stats.add_record(maria_record1)

        assert ivan_stats.median_coffee == 475  # median of [450, 500]
        assert maria_stats.median_coffee == 200
        assert ivan_stats.coffee_spent_values == [450, 500]
        assert maria_stats.coffee_spent_values == [200]

    def test_realistic_scenario(self):
        """Test with realistic data scenario."""
        # Create statistics for a student with 5 days of data
        stats = StudentStatistics("Алексей Смирнов")

        daily_data = [
            (1, 450, 7.5, 8),
            (2, 500, 6.5, 10),
            (3, 550, 5.5, 12),
            (4, 480, 7.0, 9),
            (5, 600, 4.5, 14),
        ]

        for day, coffee, sleep, study in daily_data:
            record = StudentRecord(
                student="Алексей Смирнов",
                date=datetime(2024, 6, day),
                coffee_spent=coffee,
                sleep_hours=sleep,
                study_hours=study,
                mood="норм",
                exam="Математика"
            )
            stats.add_record(record)

        # Expected median of [450, 480, 500, 550, 600] is 500
        assert stats.median_coffee == 500
        assert len(stats.coffee_spent_values) == 5
        assert sum(stats.coffee_spent_values) == 2580