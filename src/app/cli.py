import sys
from argparse import ArgumentParser, Namespace

from .logging import get_logger, setup_logging
from .reporters import ReportGenerator
from .utils import read_csv_files, validate_files_exist

logger = get_logger(__name__)


def parse_arguments() -> Namespace:
    """
    Parse command-line arguments.

    :return: Parsed arguments
    :rtype: Namespace
    """
    parser = ArgumentParser(description="Analysis of data on student preparation for exams")
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="List of .csv files to analyze (can be multiple files separated by spaces)",
    )
    parser.add_argument(
        "--report",
        choices=["median-coffee"],
        required=True,
        help="Type of report to generate (e.g., median-coffee)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    return parser.parse_args()


def main() -> None:
    """
    Main function for the CLI.
    """
    try:
        args = parse_arguments()
        setup_logging(args.verbose)

        logger.info("Starting analysis")
        logger.debug(
            f"with CLI with arguments [files: {', '.join(args.files)}, report: {args.report}, verbose: {'DEBUG' if args.verbose else 'INFO'}]"
        )

        logger.debug(f"Checking files {', '.join(args.files)}...")
        files = validate_files_exist(args.files)

        logger.info("Reading files...")
        data = read_csv_files(files)

        if not data:
            logger.warning("No data found in the provided files.")
            return

        logger.info(f"Loaded {len(data)} records")

        logger.info("Generating report...")
        generator = ReportGenerator()
        generator.print_report(ReportGenerator.convert_to_report(data), args.report)
        logger.info("Report generated successfully")

    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Process stopped by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
