"""Unit tests for AliasedTyper core functionality"""

import pytest

from typer_aliases import AliasedTyper


class TestAliasedTyperinitialisation:
    """Tests for AliasedTyper initialisation."""

    def test_default_initialisation(self):
        """Test that AliasedTyper initialises with default config"""
        app = AliasedTyper()
        assert app._alias_case_sensitive is True
        assert app._show_aliases_in_help is True
        assert app._command_aliases == {}
        assert app._alias_to_command == {}

    def test_custom_configuration(self):
        """Test that custom configuration is stored"""
        app = AliasedTyper(
            alias_case_sensitive=False,
            show_aliases_in_help=False,
        )
        assert app._alias_case_sensitive is False
        assert app._show_aliases_in_help is False


class TestNameNormalisation:
    """Tests for name normalisation based on case sensitivity"""

    def test_normalise_case_sensitive(self):
        """Test name normalisation with case sensitivity"""
        app = AliasedTyper(alias_case_sensitive=True)
        assert app._normalise_name("List") == "List"
        assert app._normalise_name("list") == "list"

    def test_normalise_case_insensitive(self):
        """Test name normalisation without case sensitivity"""
        app = AliasedTyper(alias_case_sensitive=False)
        assert app._normalise_name("List") == "list"
        assert app._normalise_name("LIST") == "list"


class TestAliasRegistration:
    """Tests for alias registration logic"""

    def test_register_single_alias(self):
        """Test registering a single alias"""
        app = AliasedTyper()
        app._register_alias("list", "ls")

        assert "list" in app._command_aliases
        assert "ls" in app._command_aliases["list"]
        assert app._alias_to_command["ls"] == "list"

    def test_register_multiple_aliases_same_command(self):
        """Test registering multiple aliases for same command"""
        app = AliasedTyper()
        app._register_alias("list", "ls")
        app._register_alias("list", "l")

        assert "list" in app._command_aliases
        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["l"] == "list"

    def test_register_duplicate_alias_raises(self):
        """Test that duplicate alias raises ValueError"""
        app = AliasedTyper()
        app._register_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app._register_alias("delete", "ls")

    def test_alias_same_as_primary_raises(self):
        """Test that alias matching primary name raises ValueError"""
        app = AliasedTyper()

        with pytest.raises(ValueError, match="cannot be the same as command name"):
            app._register_alias("list", "list")

    def test_case_insensitive_alias_conflict(self):
        """Test alias conflict detection with case insensitivity"""
        app = AliasedTyper(alias_case_sensitive=False)
        app._register_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app._register_alias("delete", "LS")  # Case-insensitive, should raise

    def test_case_sensitive_allows_different_case(self):
        """Test that case-sensitive mode allows different cases"""
        app = AliasedTyper(alias_case_sensitive=True)
        app._register_alias("list", "ls")
        app._register_alias("delete", "LS")  # Case-sensitive, should work

        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["LS"] == "delete"


class TestAliasResolution:
    """Tests for alias resolution"""

    def test_resolve_existing_alias(self):
        """Test resolving an existing alias"""
        app = AliasedTyper()
        app._register_alias("list", "ls")

        assert app._resolve_alias("ls") == "list"

    def test_resolve_nonexistent_alias(self):
        """Test resolving a non-existent alias returns None"""
        app = AliasedTyper()
        assert app._resolve_alias("nonexistent") is None

    def test_resolve_primary_name_returns_none(self):
        """Test that resolving primary name returns None"""
        app = AliasedTyper()
        app._register_alias("list", "ls")

        # Primary name is not an alias, should return None
        assert app._resolve_alias("list") is None

    def test_resolve_case_insensitive(self):
        """Test alias resolution with case insensitivity"""
        app = AliasedTyper(alias_case_sensitive=False)
        app._register_alias("list", "ls")

        assert app._resolve_alias("LS") == "list"
        assert app._resolve_alias("Ls") == "list"


class TestCommandWithAliases:
    """Tests for command registration with aliases"""

    def test_register_command_with_single_alias(self):
        """Test registering command with one alias"""
        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        assert "list" in app._command_aliases
        assert "ls" in app._command_aliases["list"]
        assert app._alias_to_command["ls"] == "list"

    def test_register_command_with_multiple_aliases(self):
        """Test registering command with multiple aliases"""
        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(
            list_items, "list", aliases=["ls", "l", "dir"]
        )

        assert app._command_aliases["list"] == ["ls", "l", "dir"]
        assert all(
            app._alias_to_command[alias] == "list" for alias in ["ls", "l", "dir"]
        )

    def test_register_command_without_aliases(self):
        """Test registering command without aliases"""
        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=None)

        # No aliases should be registered
        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_register_command_empty_alias_list(self):
        """Test registering command with empty alias list"""
        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=[])

        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_alias_conflicts_detected_during_registration(self):
        """Test that alias conflicts are detected during command registration"""
        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        with pytest.raises(ValueError, match="already registered"):
            app._register_command_with_aliases(delete_items, "delete", aliases=["ls"])


class TestGetCommand:
    """Tests for get_command with alias support

    Note: These tests focus on multi-command scenarios, as single-command
    apps don't meaningfully support aliases (the command becomes the default)
    """

    def test_get_command_multiple_commands_by_primary_name(self):
        """Test getting command by primary name in multi-command app"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete items."""
            pass

        ctx = MagicMock()

        cmd = app.get_command(ctx, "list")
        assert cmd is not None
        assert cmd.name == "list"

    def test_get_command_by_alias_in_multi_command_app(self):
        """Test getting command by alias in multi-command app"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        # Register commands with aliases
        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        app._register_command_with_aliases(delete_items, "delete", aliases=["del"])

        ctx = MagicMock()

        # Test getting by alias
        cmd_ls = app.get_command(ctx, "ls")
        cmd_list = app.get_command(ctx, "list")

        assert cmd_ls is not None, "Failed to get command by alias 'ls'"
        assert cmd_list is not None, "Failed to get command by name 'list'"
        assert cmd_ls.callback == cmd_list.callback, (
            "Alias and primary command should have same callback"
        )

    def test_get_command_nonexistent_in_multi_command_app(self):
        """Test getting non-existent command returns None"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete items."""
            pass

        ctx = MagicMock()

        cmd = app.get_command(ctx, "nonexistent")
        assert cmd is None

    def test_get_command_case_insensitive_alias(self):
        """Test getting command by case-insensitive alias"""
        from unittest.mock import MagicMock

        app = AliasedTyper(alias_case_sensitive=False)

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        app._register_command_with_aliases(delete_items, "delete", aliases=["del"])

        ctx = MagicMock()

        # Should work with different case
        cmd = app.get_command(ctx, "LS")
        assert cmd is not None

    def test_get_command_multiple_aliases_same_command(self):
        """Test getting command by different aliases"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls", "l"])
        app._register_command_with_aliases(
            delete_items, "delete", aliases=["del", "rm"]
        )

        ctx = MagicMock()

        # Test all aliases point to same command
        cmd_list = app.get_command(ctx, "list")
        cmd_ls = app.get_command(ctx, "ls")
        cmd_l = app.get_command(ctx, "l")

        assert cmd_list is not None
        assert cmd_ls is not None
        assert cmd_l is not None
        assert cmd_ls.callback == cmd_list.callback
        assert cmd_l.callback == cmd_list.callback

    def test_get_command_single_command_app(self):
        """Test getting command returns the default command"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        ctx = MagicMock()

        # Should return the command
        cmd = app.get_command(ctx, "list")
        assert cmd is not None
        assert cmd.name == "list"

        # Should not resolve an alias
        cmd_alias = app.get_command(ctx, "ls")
        assert cmd_alias is None

    def test_get_command_with_unknown_command(self):
        """Test None is returned for unknown commands"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        ctx = MagicMock()

        assert app.get_command(ctx, "unknown") is None


class TestAliasedGroup:
    """Tests for AliasedGroup get_command"""

    def test_get_command_by_alias(self):
        """Test AliasedGroup resolves a command by alias"""
        from click import Context
        from typer_aliases.core import AliasedGroup

        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        group = AliasedGroup(aliased_typer=app)
        ctx = Context(group)

        cmd = app.get_command(ctx, "list")
        assert cmd is not None
        group.add_command(cmd, name="list")

        assert group.get_command(ctx, "ls") is not None

    def test_get_command_with_unknown_command(self):
        """Test AliasedGroup returns None for unknown command/alias"""
        from click import Context
        from typer_aliases.core import AliasedGroup

        app = AliasedTyper()
        group = AliasedGroup(aliased_typer=app)
        ctx = Context(group)

        assert group.get_command(ctx, "unknown") is None

    def test_get_command_without_aliased_typer(self):
        """Test AliasedGroup.get_command when aliased_typer is None"""
        from click import Context
        from typer_aliases.core import AliasedGroup

        group = AliasedGroup(aliased_typer=None)
        ctx = Context(group)

        # Should fall back to parent's get_command
        result = group.get_command(ctx, "unknown")
        # Should return None as no commands are registered
        assert result is None


class TestRegisterAliasValidation:
    """Tests for alias registration input validation"""

    def test_register_alias_empty_string(self):
        """Test that empty string alias raises ValueError"""
        app = AliasedTyper()

        with pytest.raises(ValueError, match="Alias must be a non-empty string"):
            app._register_alias("list", "")

    def test_register_alias_none_value(self):
        """Test that None alias raises ValueError"""
        app = AliasedTyper()

        with pytest.raises(ValueError, match="Alias must be a non-empty string"):
            app._register_alias("list", None)  # type: ignore[arg-type]

    def test_register_alias_non_string_type(self):
        """Test that non-string alias raises ValueError"""
        app = AliasedTyper()

        with pytest.raises(ValueError, match="Alias must be a non-empty string"):
            app._register_alias("list", 123)  # type: ignore[arg-type]

    def test_register_alias_with_whitespace(self):
        """Test that alias with whitespace raises ValueError"""
        app = AliasedTyper()

        with pytest.raises(ValueError, match="Alias cannot contain whitespace"):
            app._register_alias("list", "l s")

    def test_register_alias_with_tabs(self):
        """Test that alias with tabs raises ValueError"""
        app = AliasedTyper()

        with pytest.raises(ValueError, match="Alias cannot contain whitespace"):
            app._register_alias("list", "l\ts")

    def test_register_alias_with_invalid_characters(self):
        """Test that alias with invalid characters raises ValueError"""
        app = AliasedTyper()

        with pytest.raises(
            ValueError,
            match="Alias must only contain alphanumeric characters, dashes, and underscores",
        ):
            app._register_alias("list", "l@s")

    def test_register_alias_with_special_characters(self):
        """Test that alias with special characters raises ValueError"""
        app = AliasedTyper()

        with pytest.raises(
            ValueError,
            match="Alias must only contain alphanumeric characters, dashes, and underscores",
        ):
            app._register_alias("list", "l$s")

    def test_register_alias_valid_with_dashes(self):
        """Test that alias with dashes is valid"""
        app = AliasedTyper()
        app._register_alias("list", "list-all")

        assert app._alias_to_command["list-all"] == "list"

    def test_register_alias_valid_with_underscores(self):
        """Test that alias with underscores is valid"""
        app = AliasedTyper()
        app._register_alias("list", "list_all")

        assert app._alias_to_command["list_all"] == "list"

    def test_register_alias_valid_with_unicode(self):
        """Test that alias with unicode characters is valid"""
        app = AliasedTyper()
        app._register_alias("list", "liés")

        assert app._alias_to_command["liés"] == "list"


class TestAddAliasToSingleCommandApp:
    """Tests for add_alias with single-command applications"""

    def test_add_alias_to_single_command_app_raises(self):
        """Test that adding alias to single-command app raises ValueError"""
        app = AliasedTyper()

        @app.command()
        def main():
            """Main command."""
            pass

        with pytest.raises(
            ValueError, match="Cannot add aliases to single-command applications"
        ):
            app.add_alias("main", "m")

    def test_add_alias_to_nonexistent_command_raises(self):
        """Test that adding alias to non-existent command raises ValueError"""
        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete items."""
            pass

        with pytest.raises(ValueError, match="Command 'nonexistent' does not exist"):
            app.add_alias("nonexistent", "nx")


class TestRemoveAliasEdgeCases:
    """Tests for edge cases in remove_alias"""

    def test_remove_alias_when_primary_command_has_no_aliases_dict(self):
        """Test remove_alias when primary command is not in _command_aliases dict"""
        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        # Manually add an alias without registering the command
        app._alias_to_command["orphan"] = "delete"

        # Should return True, but not crash when primary isn't in _command_aliases
        result = app.remove_alias("orphan")
        assert result is True


class TestGetCommandEdgeCases:
    """Tests for edge cases in get_command"""

    def test_get_command_with_fresh_app_single_command(self):
        """Test get_command on fresh single-command app"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        def main():
            """Main command."""
            pass

        app._register_command_with_aliases(main, "main", aliases=["m"])

        ctx = MagicMock()

        # First call should trigger CLI build
        cmd = app.get_command(ctx, "main")
        assert cmd is not None
        assert cmd.name == "main"

    def test_get_command_returns_none_for_invalid_command(self):
        """Test that get_command returns None for truly invalid commands"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        ctx = MagicMock()

        # Get a valid command first to initialise _group
        app.get_command(ctx, "list")

        # Invalid command, should return None
        cmd = app.get_command(ctx, "invalid_command_xyz")
        assert cmd is None

    def test_get_command_with_no_group_or_command_initialised(self):
        """Test get_command when neither _group nor _command are set"""
        from unittest.mock import MagicMock, patch

        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        ctx = MagicMock()

        # Patch get_command to return an object without attributes
        with patch("typer.main.get_command") as mock_get_cmd:
            # Return a mock that doesn't have 'commands' attribute
            mock_obj = MagicMock()
            del mock_obj.commands  # Remove the commands attribute
            mock_get_cmd.return_value = mock_obj

            # Delete cached attributes to force re-initialisation
            if hasattr(app, "_group"):
                delattr(app, "_group")
            if hasattr(app, "_command"):
                delattr(app, "_command")

            # Should return None when neither condition is met
            result = app.get_command(ctx, "unknown")
            assert result is None
