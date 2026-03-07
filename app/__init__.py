"""CarbSmart application package."""

from importlib.metadata import version, PackageNotFoundError
from pathlib import Path


def _get_version() -> str:
    try:
        return version("carbsmart")
    except PackageNotFoundError:
        pass
    # Fall back to reading pyproject.toml directly
    try:
        toml_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        for line in toml_path.read_text().splitlines():
            if line.strip().startswith("version"):
                return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return "unknown"


__version__ = _get_version()
