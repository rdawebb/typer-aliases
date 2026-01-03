"""Smoke tests for basic package functionality."""

import typer_aliases


def test_package_imports():
    """Test that package imports successfully."""
    assert hasattr(typer_aliases, "AliasedTyper")
    assert hasattr(typer_aliases, "__version__")


def test_version_format():
    """Test that version string is properly formatted."""
    version = typer_aliases.__version__
    assert isinstance(version, str)
    assert len(version.split(".")) == 3  # semantic versioning


def test_aliased_typer_instantiation():
    """Test that AliasedTyper can be instantiated."""
    app = typer_aliases.AliasedTyper()
    assert isinstance(app, typer_aliases.AliasedTyper)

    # Verify it's also a Typer instance
    import typer

    assert isinstance(app, typer.Typer)
