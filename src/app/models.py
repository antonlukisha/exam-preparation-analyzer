from dataclasses import dataclass, field
from datetime import datetime
from statistics import median


@dataclass
class StudentRecord:
    student: str
    date: datetime
    coffee_spent: int
    sleep_hours: float
    study_hours: int
    mood: str
    exam: str

    @classmethod
    def from_dict(cls, data: dict) -> "StudentRecord":
        try:
            return cls(
                student=data["student"],
                date=datetime.strptime(data["date"], "%Y-%m-%d"),
                coffee_spent=int(data["coffee_spent"]),
                sleep_hours=float(data["sleep_hours"]),
                study_hours=int(data["study_hours"]),
                mood=data["mood"],
                exam=data["exam"],
            )
        except KeyError as e:
            raise KeyError(f"Expected required field {str(e)}") from None
        except ValueError as e:
            raise ValueError(f"Incorrect value {str(e)}") from None

    def __post_init__(self) -> None:
        if self.coffee_spent < 0:
            raise ValueError("`coffee_spent` not be negative")
        if self.sleep_hours < 0 or self.sleep_hours > 24:
            raise ValueError("`sleep_hours` must be in range [0, 24]")
        if self.study_hours < 0:
            raise ValueError("`study_hours` not be negative")


@dataclass
class StudentStatistics:
    student: str
    coffee_spent_values: list[int] = field(default_factory=list)

    def add_record(self, record: StudentRecord) -> None:
        """
        Add a new record to the statistics.

        :param record: The new record to add
        :type record: StudentRecord
        :return: nothing
        :rtype: None
        """
        self.coffee_spent_values.append(record.coffee_spent)

    @property
    def median_coffee(self) -> int:
        """
        Median of coffee spent values.

        :return: median
        :rtype: int
        """
        return int(median(self.coffee_spent_values))
