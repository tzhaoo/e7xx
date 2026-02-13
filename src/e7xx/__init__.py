from importlib.metadata import PackageNotFoundError, version as _version

from .device import e7xx

__all__ = ["e7xx"]
try:
    __version__ = _version("e7xx")
except PackageNotFoundError:
    __version__ = "0+unknown"
