"""Typer extension for command aliases with grouped help display"""

from typer_extensions._version import __version__
from typer_extensions.core import Context, ExtendedTyper

__all__ = [
    # Core functionality
    "ExtendedTyper",
    "__version__",
    # Exported from Typer
    # "Abort",
    # "Argument",
    # "BadParameter",
    # "CallbackParam",
    "Context",
    # "Exit",
    # "FileBinaryRead",
    # "FileBinaryWrite",
    # "FileText",
    # "Option",
]


def __getattr__(name: str) -> str:
    """Fallback attribute access from Typer, provides forward compatibility.

    Args:
        name (str): The name of the attribute to access.

    Returns:
        str: The value of the requested attribute.
    """
    import typer

    return getattr(typer, name)
