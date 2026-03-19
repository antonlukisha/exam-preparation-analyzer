from pathlib import Path
from typing import Final

from decouple import config

REQUIRED_COLUMNS: Final[set[str]] = {
    "student",
    "coffee_spent",
    "date",
    "sleep_hours",
    "study_hours",
    "mood",
    "exam",
}
CSV_ENCODING: Final[str] = "utf-8"
LOGGER_LEVEL: Final[str] = config("LOGGER_LEVEL", default="INFO")
DATA_PATH: Final[Path] = Path(config("DATA_PATH", default="data")).resolve()
FLOAT_ROUNDING: Final[int] = 2
