import subprocess


def lint() -> None:
    """
    Run linters.
    """
    subprocess.run(["black", "."])
    subprocess.run(["isort", "."])
    subprocess.run(["ruff", "check", "."])
    subprocess.run(["mypy", "."])
