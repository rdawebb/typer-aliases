"""Core AliasedTyper class extending typer.Typer with alias support"""

from typing import Any

import typer


class AliasedTyper(typer.Typer):
    """Typer application with alias support"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise AliasedTyper

        Args:
            *args: Positional arguments for Typer.
            **kwargs: Keyword arguments for Typer.
        """
        super().__init__(*args, **kwargs)
        self._command_aliases: dict[str, list[str]] = {}
