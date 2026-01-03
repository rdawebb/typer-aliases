"""Pytest configuration for the typer-aliases tests"""

import pytest

from typer.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Fixture for the CLI test runner"""
    return CliRunner()
