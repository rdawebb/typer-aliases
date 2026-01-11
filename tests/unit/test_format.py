"""Unit tests for formatters module."""

from typer_extensions.format import (
    format_command_with_aliases,
    format_commands_section,
    truncate_aliases,
)


class TestTruncateAliases:
    """Tests for truncate_aliases function."""

    def test_empty_list(self):
        """Test that empty list returns empty string."""
        result = truncate_aliases([], 3)
        assert result == ""

    def test_within_limit(self):
        """Test aliases within limit show all."""
        result = truncate_aliases(["a", "b"], 3)
        assert result == "a, b"

    def test_at_exact_limit(self):
        """Test aliases at exact limit show all."""
        result = truncate_aliases(["a", "b", "c"], 3)
        assert result == "a, b, c"

    def test_over_limit(self):
        """Test aliases over limit truncate with +N more."""
        result = truncate_aliases(["a", "b", "c", "d"], 2)
        assert result == "a, b, +2 more"

    def test_custom_separator(self):
        """Test custom separator between aliases."""
        result = truncate_aliases(["a", "b", "c"], 3, separator=" | ")
        assert result == "a | b | c"

    def test_truncate_with_custom_separator(self):
        """Test truncation with custom separator."""
        result = truncate_aliases(["a", "b", "c", "d"], 2, separator="; ")
        assert result == "a; b; +2 more"

    def test_single_alias(self):
        """Test single alias returns just that alias."""
        result = truncate_aliases(["only"], 3)
        assert result == "only"

    def test_many_aliases_truncated(self):
        """Test many aliases show correct count."""
        aliases = ["a", "b", "c", "d", "e", "f"]
        result = truncate_aliases(aliases, 2)
        assert result == "a, b, +4 more"


class TestFormatCommandWithAliases:
    """Tests for format_command_with_aliases function."""

    def test_no_aliases(self):
        """Test command with no aliases shows name only."""
        result = format_command_with_aliases("list", [])
        assert result == "list"

    def test_single_alias(self):
        """Test command with single alias."""
        result = format_command_with_aliases("list", ["ls"])
        assert result == "list (ls)"

    def test_multiple_aliases(self):
        """Test command with multiple aliases."""
        result = format_command_with_aliases("list", ["ls", "l"])
        assert result == "list (ls, l)"

    def test_many_aliases_default_truncation(self):
        """Test that many aliases truncate at default limit."""
        aliases = ["a", "b", "c", "d"]
        result = format_command_with_aliases("cmd", aliases, max_num=3)
        assert result == "cmd (a, b, c, +1 more)"

    def test_custom_display_format_brackets(self):
        """Test custom display format with brackets."""
        result = format_command_with_aliases(
            "list", ["ls", "l"], display_format="[{aliases}]"
        )
        assert result == "list [ls, l]"

    def test_custom_display_format_pipe(self):
        """Test custom display format with pipe."""
        result = format_command_with_aliases(
            "list", ["ls"], display_format="| {aliases}"
        )
        assert result == "list | ls"

    def test_custom_separator(self):
        """Test custom separator between aliases."""
        result = format_command_with_aliases("list", ["a", "b", "c"], separator=" / ")
        assert result == "list (a / b / c)"

    def test_custom_max_num(self):
        """Test custom max num limit."""
        aliases = ["a", "b", "c", "d", "e"]
        result = format_command_with_aliases("cmd", aliases, max_num=2)
        assert result == "cmd (a, b, +3 more)"

    def test_combined_custom_params(self):
        """Test all custom parameters together."""
        result = format_command_with_aliases(
            "cmd",
            ["a", "b", "c"],
            display_format="[{aliases}]",
            max_num=2,
            separator="; ",
        )
        assert result == "cmd [a; b; +1 more]"

    def test_long_command_name(self):
        """Test with long command name."""
        result = format_command_with_aliases("very-long-command-name", ["short"])
        assert result == "very-long-command-name (short)"

    def test_unicode_aliases(self):
        """Test with unicode characters in aliases."""
        result = format_command_with_aliases("list", ["ls", "列表"])
        assert result == "list (ls, 列表)"


class TestFormatCommandsSection:
    """Tests for format_commands_section function."""

    def test_no_commands(self):
        """Test empty command list."""
        result = format_commands_section([], {})
        assert result == []

    def test_commands_without_aliases(self):
        """Test commands without any aliases."""
        commands = [("list", "List items"), ("delete", "Delete items")]
        result = format_commands_section(commands, {})

        assert result == commands

    def test_all_commands_with_aliases(self):
        """Test all commands have aliases."""
        commands = [("list", "List items"), ("delete", "Delete items")]
        aliases = {"list": ["ls", "l"], "delete": ["rm"]}
        result = format_commands_section(commands, aliases)

        assert result == [
            ("list (ls, l)", "List items"),
            ("delete (rm)", "Delete items"),
        ]

    def test_mixed_aliased_and_non_aliased(self):
        """Test mix of commands with and without aliases."""
        commands = [
            ("list", "List items"),
            ("delete", "Delete items"),
            ("create", "Create item"),
        ]
        aliases = {"list": ["ls"], "delete": ["rm"]}
        result = format_commands_section(commands, aliases)

        assert result == [
            ("list (ls)", "List items"),
            ("delete (rm)", "Delete items"),
            ("create", "Create item"),
        ]

    def test_custom_format_applied(self):
        """Test custom display format is applied."""
        commands = [("list", "List items")]
        aliases = {"list": ["ls"]}
        result = format_commands_section(
            commands, aliases, display_format="[{aliases}]"
        )

        assert result == [("list [ls]", "List items")]

    def test_truncation_applied(self):
        """Test truncation is applied to long alias lists."""
        commands = [("list", "List items")]
        aliases = {"list": ["a", "b", "c", "d"]}
        result = format_commands_section(commands, aliases, max_num=2)

        assert result == [("list (a, b, +2 more)", "List items")]

    def test_custom_separator_applied(self):
        """Test custom separator is applied."""
        commands = [("list", "List items")]
        aliases = {"list": ["a", "b"]}
        result = format_commands_section(commands, aliases, separator=" | ")

        assert result == [("list (a | b)", "List items")]

    def test_none_help_text(self):
        """Test commands with None help text."""
        commands = [("list", None), ("delete", "Delete items")]
        aliases = {"list": ["ls"]}
        result = format_commands_section(commands, aliases)

        assert result == [("list (ls)", None), ("delete", "Delete items")]

    def test_preserves_command_order(self):
        """Test that command order is preserved."""
        commands = [
            ("zzz", "Last alphabetically"),
            ("aaa", "First alphabetically"),
            ("mmm", "Middle"),
        ]
        aliases = {"zzz": ["z"], "aaa": ["a"]}
        result = format_commands_section(commands, aliases)

        # Order should be preserved, not alphabetised
        assert result[0][0].startswith("zzz")
        assert result[1][0].startswith("aaa")
        assert result[2][0] == "mmm"


class TestFormattersEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_very_long_alias_list(self):
        """Test with very long list of aliases."""
        aliases = [f"alias{i}" for i in range(100)]
        result = truncate_aliases(aliases, 3)
        assert result == "alias0, alias1, alias2, +97 more"

    def test_alias_with_spaces(self):
        """Test aliases containing spaces."""
        result = format_command_with_aliases("cmd", ["alias one", "alias two"])
        assert result == "cmd (alias one, alias two)"

    def test_alias_with_special_chars(self):
        """Test aliases with special characters."""
        result = format_command_with_aliases("cmd", ["alias-1", "alias_2", "alias.3"])
        assert result == "cmd (alias-1, alias_2, alias.3)"

    def test_empty_string_alias(self):
        """Test handling of empty string in alias list."""
        # Should be prevented in practice, but tested defensively
        result = truncate_aliases(["a", "", "b"], 3)
        assert result == "a, , b"

    def test_max_num_zero(self):
        """Test max_num of 0 shows +N more immediately."""
        result = truncate_aliases(["a", "b"], 0)
        assert result == "+2 more"

    def test_max_num_negative(self):
        """Test negative max_num (edge case, treat as 0)."""
        result = truncate_aliases(["a", "b"], -1)
        # Should return empty, so only +N more
        assert "+2 more" in result
