"""Tools for generating AI-assisted scripts for Reddit short-form videos."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("reddit_ai_shorts")
except PackageNotFoundError:  # pragma: no cover - during local development
    __version__ = "0.1.0"

__all__ = ["__version__"]
