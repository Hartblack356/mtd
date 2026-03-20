"""Unit tests for the theme engine (mtd.themes.engine)."""

import pytest

from mtd.themes.engine import Theme, list_themes, load_theme

# ---------------------------------------------------------------------------
# test_load_default_theme
# ---------------------------------------------------------------------------


def test_load_default_theme():
    """load_theme('default') returns a Theme with the documented defaults."""
    theme = load_theme("default")
    assert isinstance(theme, Theme)
    assert theme.name == "default"
    assert theme.font_heading == "Arial"
    assert theme.font_body == "Calibri"
    assert theme.font_code == "Courier New"
    assert theme.body_size == 11
    assert theme.line_spacing == 1.15
    assert theme.page_size == "A4"


# ---------------------------------------------------------------------------
# test_load_academic_theme
# ---------------------------------------------------------------------------


def test_load_academic_theme():
    """load_theme('academic') returns Times New Roman fonts and 2.0 line spacing."""
    theme = load_theme("academic")
    assert isinstance(theme, Theme)
    assert theme.name == "academic"
    assert theme.font_heading == "Times New Roman"
    assert theme.font_body == "Times New Roman"
    assert theme.line_spacing == 2.0
    # Academic theme uses larger margins
    assert theme.margin_top == "3cm"
    assert theme.margin_bottom == "3cm"


# ---------------------------------------------------------------------------
# test_load_modern_theme
# ---------------------------------------------------------------------------


def test_load_modern_theme():
    """load_theme('modern') returns Helvetica fonts and accent colors."""
    theme = load_theme("modern")
    assert isinstance(theme, Theme)
    assert theme.name == "modern"
    assert theme.font_heading == "Helvetica"
    assert theme.font_body == "Helvetica"
    # Modern theme uses an indigo accent color
    assert theme.color_primary == "#6366f1"
    # Modern theme has a code font of Fira Code
    assert theme.font_code == "Fira Code"


# ---------------------------------------------------------------------------
# test_list_themes
# ---------------------------------------------------------------------------


def test_list_themes():
    """list_themes() returns at least default, academic, and modern."""
    themes = list_themes()
    assert isinstance(themes, list)
    assert "default" in themes
    assert "academic" in themes
    assert "modern" in themes
    # default must be the first entry (always prepended)
    assert themes[0] == "default"


# ---------------------------------------------------------------------------
# test_theme_not_found
# ---------------------------------------------------------------------------


def test_theme_not_found():
    """load_theme raises FileNotFoundError for an unknown theme name."""
    with pytest.raises(FileNotFoundError):
        load_theme("nonexistent_theme_xyz")


# ---------------------------------------------------------------------------
# test_custom_theme_from_file
# ---------------------------------------------------------------------------


def test_custom_theme_from_file(tmp_path):
    """A YAML file on disk can be loaded by its path string."""
    yaml_content = (
        "name: mytest\n"
        "description: Custom test theme\n"
        "fonts:\n"
        "  heading: Georgia\n"
        "  body: Verdana\n"
        "body:\n"
        "  size: 13\n"
    )
    custom_file = tmp_path / "mytest.yaml"
    custom_file.write_text(yaml_content, encoding="utf-8")

    theme = load_theme(str(custom_file))
    assert isinstance(theme, Theme)
    assert theme.name == "mytest"
    assert theme.font_heading == "Georgia"
    assert theme.font_body == "Verdana"
    assert theme.body_size == 13
    # Unspecified fields fall back to Theme() defaults
    assert theme.font_code == "Courier New"


# ---------------------------------------------------------------------------
# test_theme_partial_override
# ---------------------------------------------------------------------------


def test_theme_partial_override(tmp_path):
    """A YAML that only overrides 'fonts' still produces all other defaults."""
    yaml_content = "fonts:\n  heading: Palatino\n"
    partial_file = tmp_path / "partial.yaml"
    partial_file.write_text(yaml_content, encoding="utf-8")

    theme = load_theme(str(partial_file))
    assert theme.font_heading == "Palatino"
    # Body, code, and page fields should be the defaults
    assert theme.font_body == "Calibri"
    assert theme.font_code == "Courier New"
    assert theme.body_size == 11
    assert theme.margin_top == "2.54cm"
    assert theme.color_primary == "#2563eb"


# ---------------------------------------------------------------------------
# test_heading_styles
# ---------------------------------------------------------------------------


def test_heading_styles():
    """The default Theme has correct sizes for h1 through h6."""
    theme = Theme()
    assert theme.h1.size == 24
    assert theme.h1.bold is True
    assert theme.h2.size == 20
    assert theme.h2.bold is True
    assert theme.h3.size == 16
    assert theme.h3.bold is True
    assert theme.h4.size == 14
    assert theme.h4.bold is True
    assert theme.h5.size == 12
    assert theme.h5.bold is True
    assert theme.h6.size == 11
    assert theme.h6.bold is True
    assert theme.h6.italic is True
