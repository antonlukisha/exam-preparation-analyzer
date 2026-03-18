from tabulate import tabulate

from .config import FLOAT_ROUNDING
from .logging import get_logger
from .models import StudentStatistics, StudentRecord
from .processors import DataProcessor, PROCESSORS

logger = get_logger(__name__)

class ReportGenerator:

    def __init__(self):
        self._processors = PROCESSORS


    @staticmethod
    def convert_to_report(data: list[dict]) -> dict[str, StudentStatistics]:
        """
        Convert data to report

        :params data: list of data
        :type data: list[dict]
        :return: report data
        :rtype: dict[str, StudentStatistics]
        """
        student_stats = {}

        try:
            for item in data:
                record = StudentRecord.from_dict(item)
                if record.student not in student_stats:
                    student_stats[record.student] = StudentStatistics(record.student)
                student_stats[record.student].add_record(record)
        except Exception as e:
            raise ValueError(f"Error converting data to report {str(e)}")

        return student_stats

    def get_available_reports(self) -> list[str]:
        """
        Get available reports

        :return: list of available reports
        :rtype: list[str]
        """
        return list(self._processors.keys())

    def generate_report(self, data: dict[str, StudentStatistics], report_type: str) -> list[dict] | None:
        """
        Generate report

        :param data: list of data
        :type data: dict[str, StudentStatistics]
        :param report_type: report type
        :type report_type: str
        :return: report data
        :rtype: list[dict] | None
        """
        if report_type not in self._processors:
            raise ValueError(f"Unknown report type `{report_type}` (available reports: {', '.join(self.get_available_reports())})")

        processor_cls = self._processors[report_type]['cls']
        processor: DataProcessor = processor_cls()
        return processor.process(data)

    def print_report(self, data: dict[str, StudentStatistics], report_type: str) -> None:
        """
        Print report

        :param data: list of data
        :type data: dict[str, StudentStatistics]
        :param report_type: report type
        :type report_type: str
        :return: nothing
        :rtype: None
        """
        try:
            report_data = self.generate_report(data, report_type)

            if not report_data:
                logger.error(f"No data to generate report for `{report_type}`")
                return

            logger.debug(f"Report data: {len(report_data)} records")
            logger.debug("Generating table...")

            table = tabulate(
                report_data,
                headers=self._processors[report_type]['headers'],
                tablefmt='grid',
                floatfmt=f'.{FLOAT_ROUNDING}f'
            )

            print(table)

        except ValueError as e:
            logger.error(f"Error generating report: {str(e)}")