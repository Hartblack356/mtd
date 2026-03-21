"""Tests for the mtd public API."""

from pathlib import Path

import pytest

from mtd import (
    Document,
    Theme,
    __version__,
    convert,
    convert_string,
    list_themes,
    load_theme,
    parse_markdown,
    write_docx,
    write_odt,
)

# Absolute path to the project root so tests work regardless of cwd
_PROJECT_ROOT = Path(__file__).parent.parent


class TestPublicExports:
    """Verify all public exports are accessible."""

    def test_version(self):
        assert __version__  # version string is not empty

    def test_all_exports_importable(self):
        from mtd import (
            Document,
            Theme,
            convert,
            convert_string,
            list_themes,
            load_theme,
            parse_markdown,
            write_docx,
            write_odt,
        )

        assert all(
            [
                convert,
                convert_string,
                parse_markdown,
                write_docx,
                write_odt,
                load_theme,
                list_themes,
                Document,
                Theme,
            ]
        )


class TestConvert:
    """Tests for the high-level convert function."""

    def test_convert_to_docx(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Hello\n\nWorld\n")
        out = tmp_path / "test.docx"
        result = convert(md, out)
        assert result == out
        assert out.exists()
        assert out.stat().st_size > 0

    def test_convert_to_odt(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Hello\n\nWorld\n")
        out = tmp_path / "test.odt"
        result = convert(md, out)
        assert result == out
        assert out.exists()
        assert out.stat().st_size > 0

    def test_convert_with_theme_name(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Hello\n\nWorld\n")
        out = tmp_path / "test.docx"
        result = convert(md, out, theme="academic")
        assert result == out
        assert out.exists()

    def test_convert_with_theme_object(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Hello\n\nWorld\n")
        out = tmp_path / "test.docx"
        theme = load_theme("modern")
        result = convert(md, out, theme=theme)
        assert result == out
        assert out.exists()

    def test_convert_unsupported_format(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Hello\n")
        out = tmp_path / "test.pdf"
        with pytest.raises(ValueError, match="Unsupported"):
            convert(md, out)

    def test_convert_explicit_format(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Hello\n\nWorld\n")
        out = tmp_path / "output"  # no extension
        result = convert(md, out, format="docx")
        assert result == out
        assert out.exists()

    def test_convert_with_template(self, tmp_path):
        template = _PROJECT_ROOT / "examples" / "template.md"
        out = tmp_path / "template.docx"
        result = convert(template, out, theme="modern")
        assert result == out
        assert out.stat().st_size > 0


class TestConvertString:
    """Tests for convert_string function."""

    def test_basic_string(self, tmp_path):
        out = tmp_path / "test.docx"
        result = convert_string("# Hello\n\nWorld\n", out)
        assert result == out
        assert out.exists()

    def test_string_with_frontmatter(self, tmp_path):
        md = "---\ntitle: Test\nauthor: Bot\n---\n\n# Hello\n"
        out = tmp_path / "test.docx"
        convert_string(md, out)
        assert out.exists()

    def test_string_to_odt(self, tmp_path):
        out = tmp_path / "test.odt"
        result = convert_string("# Hello\n", out)
        assert result == out
        assert out.exists()

    def test_string_with_theme(self, tmp_path):
        out = tmp_path / "test.docx"
        convert_string("# Hello\n", out, theme="modern")
        assert out.exists()


class TestGranularAPI:
    """Tests for the granular lower-level API."""

    def test_parse_then_write_docx(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\ntitle: API Test\n---\n\n# Content\n")
        doc = parse_markdown(md)
        assert doc.title == "API Test"

        theme = load_theme("default")
        out = tmp_path / "test.docx"
        result = write_docx(doc, out, theme)
        assert result == out
        assert out.exists()

    def test_parse_then_write_odt(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Content\n\nParagraph.\n")
        doc = parse_markdown(md)

        theme = load_theme("academic")
        out = tmp_path / "test.odt"
        result = write_odt(doc, out, theme)
        assert result == out
        assert out.exists()

    def test_list_themes_returns_builtins(self):
        themes = list_themes()
        assert "default" in themes
        assert "academic" in themes
        assert "modern" in themes

    def test_load_theme_returns_theme(self):
        theme = load_theme("modern")
        assert isinstance(theme, Theme)
        assert theme.name == "modern"

    def test_document_model(self):
        doc = parse_markdown("---\ntitle: Test\nauthor: Me\n---\n\n# Hi\n")
        assert isinstance(doc, Document)
        assert doc.title == "Test"
        assert doc.author == "Me"
