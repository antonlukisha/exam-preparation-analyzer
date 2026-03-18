import csv
from pathlib import Path
from typing import Generator
from contextlib import contextmanager

from .config import CSV_ENCODING, REQUIRED_COLUMNS
from .logging import get_logger

logger = get_logger(__name__)

def validate_file_exists(file_path: str | Path) -> Path:
    """
    Checks if the file exists and is a file.

    :param file_path: The path to the file
    :type file_path: str | Path
    :return: The resolved Path object
    :rtype: Path
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found {str(path)}")
    if not path.is_file():
        raise RuntimeError(f"Path is not a file `{str(path)}`")
    return path

def validate_files_exist(file_paths: list[str | Path]) -> list[Path]:
    """
    Checks if all files exist and are files.

    :param file_paths: List of file paths
    :type file_paths: list[str | Path]
    :return: List of resolved Path objects
    :rtype: list[Path]
    """
    paths = []
    errors = []

    for file_path in file_paths:
        try:
            paths.append(validate_file_exists(file_path))
        except Exception as e:
            errors.append(str(e))

    if errors:
        error_message = "; ".join(errors)
        if len(errors) == 1:
            raise RuntimeError(f"{error_message} for file {str(file_paths[0])}")
        else:
            raise RuntimeError(error_message)
    return paths

@contextmanager
def open_csv_file(file_path: str | Path, mode: str = "r") -> Generator:
    """
    Opens a CSV file with context manager.

    :param file_path: Path to the file
    :type file_path: str | Path
    :param mode: File open mode
    :type mode: str
    :return: File object
    :rtype: Generator
    """
    path = Path(file_path)
    try:
        with open(path, mode, encoding=CSV_ENCODING) as f:
            yield f
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found `{str(path)}`")
    except PermissionError:
        raise PermissionError(f"Not enough permissions to read the file `{str(path)}`")
    except UnicodeDecodeError:
        raise RuntimeError(f"File is not have needed encoding (expected {CSV_ENCODING})")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}", str(path))

def read_csv_file(file_path: str | Path) -> list[dict]:
    """
    Reads a CSV file and returns a list of dictionaries.

    :param file_path: Path to the file
    :type file_path: str | Path
    :return: List of dictionaries
    :rtype: list[dict]
    """
    path = validate_file_exists(file_path)
    data = []

    logger.debug(f"Reading file: {str(path)}")

    with open_csv_file(path, 'r') as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise RuntimeError("File is empty")

        fieldnames_set = set(reader.fieldnames)
        missing_columns = REQUIRED_COLUMNS - fieldnames_set
        if missing_columns:
            raise RuntimeError(f"Expected required columns: {', '.join(missing_columns)}")

        for row_num, row in enumerate(reader, start=2):
            try:
                if not validate_data(row):
                    logger.warning(f"Skipping row {row_num} in file `{path.name}` (invalid data)")
                    continue

                data.append(row)

            except Exception as e:
                logger.warning(f"Error processing row {row_num} файла `{path.name}`: {e}")
                continue

    logger.debug(f"Loaded {len(data)} records from file `{path.name}`")
    return data


def read_csv_files(file_paths: list[str | Path]) -> list[dict]:
    """
    Reads multiple CSV files and returns a list of dictionaries.

    :param file_paths: List of file paths
    :type file_paths: list[str | Path]
    :return: List of dictionaries
    :rtype: list[dict]
    """
    all_data = []
    errors = []

    for file_path in file_paths:
        try:
            file_data = read_csv_file(file_path)
            all_data.extend(file_data)
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Error processing file `{file_path}`: {str(e)}")

    if errors and not all_data:
        error_message = "; ".join(errors)
        raise RuntimeError(f"No valid data found {error_message}")
    elif errors:
        logger.warning(f"Bypassed {len(errors)} files with errors")

    return all_data

def validate_data(data: dict) -> bool:
    """
    Validates the data in the row.

    :param data: The data to validate
    :type data: dict
    :return: True if valid, False otherwise
    :rtype: bool
    """
    if not data.get("student") or not data.get("date"):
        return False
    try:
        data["coffee_spent"] = int(data["coffee_spent"])
        data["sleep_hours"] = float(data["sleep_hours"])
        data["study_hours"] = int(data["study_hours"])
    except (ValueError, TypeError):
        return False

    if any(v < 0 for v in [data["coffee_spent"], data["sleep_hours"], data["study_hours"]]):
        return False

    if not 0 <= data["sleep_hours"] <= 24:
        return False
    return True