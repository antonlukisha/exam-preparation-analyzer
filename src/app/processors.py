from abc import ABC, abstractmethod

from app.models import StudentStatistics


class DataProcessor(ABC):

    @abstractmethod
    def process(self, data: dict[str, StudentStatistics]) -> list[dict]:
        """
        Process the data and return the result.

        :param data: Dictionary of student records
        :type data: dict[str, StudentStatistics]
        :return: List of processed data
        :rtype: list[dict]
        """
        pass


class MedianCoffeeProcessor(DataProcessor):

    def process(self, data: dict[str, StudentStatistics]) -> list[dict]:
        """
        Calculates the median coffee consumption for each student.

        :param data: Dictionary of student records
        :type data: dict[str, StudentStatistics]
        :return: List of dictionaries containing student and median coffee consumption
        :rtype: list[dict]
        """
        result = [
            {"student": student, "median_coffee": stats.median_coffee}
            for student, stats in data.items()
        ]
        result.sort(key=lambda x: x["median_coffee"], reverse=True)
        return result


PROCESSORS = {
    "median-coffee": {
        "cls": MedianCoffeeProcessor,
        "headers": {"student": "student", "median_coffee": "median_coffee"},
    }
}
