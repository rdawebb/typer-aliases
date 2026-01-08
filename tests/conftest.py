"""Pytest configuration for the typer-aliases tests"""

import re

import pytest

from typer.testing import CliRunner


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text for consistent assertion testing

    This is needed because different environments (local vs CI runners) may
    have different color output settings, but the actual text content should
    be the same

    Args:
        text: The text potentially containing ANSI escape codes

    Returns:
        The text with all ANSI escape codes removed
    """
    ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_pattern.sub("", text)


@pytest.fixture
def cli_runner() -> CliRunner:
    """Fixture for the CLI test runner"""
    return CliRunner()


@pytest.fixture
def clean_output():
    """Fixture providing the strip_ansi_codes function for use in tests"""
    return strip_ansi_codes
