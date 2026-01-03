"""Typer extension for command aliases with grouped help display"""

from typer_aliases._version import __version__
from typer_aliases.core import AliasedTyper

__all__ = [
    "AliasedTyper",
    "__version__",
]
