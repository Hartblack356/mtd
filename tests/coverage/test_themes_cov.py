"""Tests targeting mtd/themes/engine.py coverage.

Covers: color/code/page/titlepage/heading YAML overrides, yml extension,
and default fallback when builtin file is missing.
"""

from mtd.themes.engine import Theme, load_theme

# ===========================================================================
# themes/engine.py (lines 96, 126, 139, 182)
# ===========================================================================


def test_theme_color_background_override(tmp_path):
    """Setting colors.background in a YAML theme hits line 96."""
    yaml_content = "colors:\n  background: '#fafafa'\n"
    f = tmp_path / "bg.yaml"
    f.write_text(yaml_content, encoding="utf-8")
    theme = load_theme(str(f))
    assert theme.color_background == "#fafafa"


def test_theme_code_background_in_code_section(tmp_path):
    """Setting code.background in YAML hits line 126."""
    yaml_content = "code:\n  background: '#eeeeee'\n  size: 9\n"
    f = tmp_path / "code_bg.yaml"
    f.write_text(yaml_content, encoding="utf-8")
    theme = load_theme(str(f))
    assert theme.color_code_background == "#eeeeee"
    assert theme.code_size == 9


def test_theme_page_size_override(tmp_path):
    """Setting page.size in YAML hits line 139."""
    yaml_content = "page:\n  size: Letter\n  margin_top: 3cm\n"
    f = tmp_path / "page.yaml"
    f.write_text(yaml_content, encoding="utf-8")
    theme = load_theme(str(f))
    assert theme.page_size == "Letter"
    assert theme.margin_top == "3cm"


def test_theme_titlepage_overrides(tmp_path):
    """Setting titlepage settings in YAML hits the titlepage section (near line 182)."""
    yaml_content = (
        "titlepage:\n  title_size: 32\n  subtitle_size: 22\n  info_size: 16\n  spacing_top: 8cm\n"
    )
    f = tmp_path / "tp.yaml"
    f.write_text(yaml_content, encoding="utf-8")
    theme = load_theme(str(f))
    assert theme.titlepage_title_size == 32
    assert theme.titlepage_subtitle_size == 22
    assert theme.titlepage_info_size == 16
    assert theme.titlepage_spacing_top == "8cm"


def test_theme_yml_extension(tmp_path):
    """load_theme picks up .yml extension (not just .yaml) -- exercises the path check."""
    yaml_content = "name: ymltest\ndescription: yml extension test\n"
    f = tmp_path / "ymltest.yml"
    f.write_text(yaml_content, encoding="utf-8")
    theme = load_theme(str(f))
    assert theme.name == "ymltest"


def test_theme_heading_overrides(tmp_path):
    """Custom heading definitions in YAML override per-level styles."""
    yaml_content = (
        "heading:\n"
        "  h1:\n"
        "    size: 30\n"
        "    bold: true\n"
        "    italic: false\n"
        "    color: '#ff0000'\n"
        "  h2:\n"
        "    size: 22\n"
        "    bold: false\n"
        "    italic: true\n"
    )
    f = tmp_path / "headings.yaml"
    f.write_text(yaml_content, encoding="utf-8")
    theme = load_theme(str(f))
    assert theme.h1.size == 30
    assert theme.h1.color == "#ff0000"
    assert theme.h2.size == 22
    assert theme.h2.italic is True


def test_theme_default_fallback_when_no_builtin_file(monkeypatch, tmp_path):
    """load_theme('default') returns Theme() via fallback if the builtin file is missing."""
    # Temporarily redirect _THEMES_DIR to an empty tmp directory
    import mtd.themes.engine as engine_mod

    original_dir = engine_mod._THEMES_DIR
    monkeypatch.setattr(engine_mod, "_THEMES_DIR", tmp_path)

    # Now load_theme("default") won't find a builtin file -> hits line 182
    theme = load_theme("default")
    assert isinstance(theme, Theme)
    assert theme.name == "default"

    monkeypatch.setattr(engine_mod, "_THEMES_DIR", original_dir)
