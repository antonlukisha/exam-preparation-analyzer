from typing import Final

REQUIRED_COLUMNS: Final[set[str]] = {"student", "coffee_spent", "date", "sleep_hours", "study_hours", "mood", "exam"}
CSV_ENCODING: Final[str] = 'utf-8'
LOGGER_LEVEL: Final[str] = 'DEBUG'
FLOAT_ROUNDING: Final[int] = 2