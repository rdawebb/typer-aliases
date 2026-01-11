"""Help text formatting utilities"""

from typing import Optional


def truncate_aliases(
    aliases: list[str],
    max_num: int,
    separator: str = ", ",
) -> str:
    """Truncate the list of aliases to a maximum number, join with a separator, and truncate with '+ N more' if needed

    Args:
        aliases: The list of aliases to truncate
        max_num: The maximum number of aliases to display
        separator: The separator to use when joining aliases, defaults to ', '

    Returns:
        The formatted string of aliases, truncated if necessary
    """
    if not aliases:
        return ""

    # Handle negative max_num edge case
    if max_num < 0:
        max_num = 0

    if len(aliases) <= max_num:
        return separator.join(aliases)

    visible = aliases[:max_num]
    hidden = len(aliases) - max_num

    return f"{separator.join(visible)}{separator if visible else ''}+{hidden} more"


def format_command_with_aliases(
    command_name: str,
    aliases: list[str],
    *,
    display_format: str = "({aliases})",
    max_num: int = 3,
    separator: str = ", ",
) -> str:
    """Format a command with its aliases with specified format

    Args:
        command_name: The name of the command
        aliases: The list of aliases for the command
        display_format: The format string for displaying aliases
        max_num: The maximum number of aliases to display
        separator: The separator to use between aliases

    Returns:
        The formatted command string with aliases
    """
    if not aliases:
        return command_name

    aliases_str = truncate_aliases(aliases, max_num, separator)

    aliases_display = display_format.format(aliases=aliases_str)

    return f"{command_name} {aliases_display}"


def format_commands_section(
    commands: list[tuple[str, Optional[str]]],
    command_aliases: dict[str, list[str]],
    *,
    display_format: str = "({aliases})",
    max_num: int = 3,
    separator: str = ", ",
) -> list[tuple[str, Optional[str]]]:
    """Format a list of commands with their aliases

    Args:
        commands: The list of commands to format
        command_aliases: A dictionary mapping command names to their aliases
        display_format: The format string for displaying aliases
        max_num: The maximum number of aliases to display
        separator: The separator to use between aliases

    Returns:
        A list of (formatted_command, help text) tuples
    """
    formatted_commands = []

    for cmd_name, help_text in commands:
        if cmd_name in command_aliases:
            aliases = command_aliases[cmd_name]
            formatted_cmd = format_command_with_aliases(
                cmd_name,
                aliases,
                display_format=display_format,
                max_num=max_num,
                separator=separator,
            )
        else:
            formatted_cmd = cmd_name

        formatted_commands.append((formatted_cmd, help_text))

    return formatted_commands
