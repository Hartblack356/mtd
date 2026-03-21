"""Tests targeting mtd/api.py coverage.

Covers: convert_string branches (theme object, unsupported format),
and the __main__.py entry point via subprocess.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from mtd.themes.engine import Theme

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ===========================================================================
# __main__.py (lines 1-3) -- entry point via subprocess
# ===========================================================================


def test_main_module_version():
    """Running python -m mtd --version should print the version string."""
    result = subprocess.run(
        [sys.executable, "-m", "mtd", "--version"],
        capture_output=True,
        text=True,
        cwd=str(_PROJECT_ROOT),
    )
    assert result.returncode == 0
    assert "version" in result.stdout.lower() or result.stdout.strip()


# ===========================================================================
# api.py (lines 130, 141) -- convert_string branches
# ===========================================================================


def test_convert_string_with_theme_object(tmp_path):
    """convert_string with a Theme object directly hits the isinstance branch (line 130)."""
    from mtd.api import convert_string

    theme = Theme()
    out = tmp_path / "test.docx"
    result = convert_string("# Hello\n\nWorld\n", out, theme=theme)
    assert result == out
    assert out.exists()


def test_convert_string_unsupported_format(tmp_path):
    """convert_string raises ValueError for unsupported format (line 141)."""
    from mtd.api import convert_string

    out = tmp_path / "test.pdf"
    with pytest.raises(ValueError, match="Unsupported"):
        convert_string("# Hello\n", out)


def test_convert_string_unsupported_format_explicit(tmp_path):
    """convert_string raises ValueError when format kwarg is unsupported (line 141)."""
    from mtd.api import convert_string

    out = tmp_path / "output"
    with pytest.raises(ValueError, match="Unsupported"):
        convert_string("# Hello\n", out, format="pdf")
