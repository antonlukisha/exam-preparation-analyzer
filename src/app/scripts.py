import subprocess


def lint() -> None:
    """
    Run linters.
    """
    subprocess.run(["black", "."])
    subprocess.run(["isort", "."])
    subprocess.run(["ruff", "check", ".", "--fix"])
    subprocess.run(["mypy", "."])
