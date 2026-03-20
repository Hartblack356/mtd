"""Smoke tests for mtd CLI."""

from pathlib import Path

from click.testing import CliRunner

from mtd.cli import cli

# ---------------------------------------------------------------------------
# Original smoke tests
# ---------------------------------------------------------------------------


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "convert" in result.output
    assert "themes" in result.output


def test_convert_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["convert", "--help"])
    assert result.exit_code == 0
    assert "--output" in result.output
    assert "--theme" in result.output


def test_themes_list():
    runner = CliRunner()
    result = runner.invoke(cli, ["themes", "list"])
    assert result.exit_code == 0


def test_themes_show():
    runner = CliRunner()
    result = runner.invoke(cli, ["themes", "show", "default"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Integration tests: convert command
# ---------------------------------------------------------------------------


def test_convert_to_docx(tmp_path: Path):
    """CLI convert command produces a .docx file from a Markdown source."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Hello\n\nWorld\n", encoding="utf-8")
    output_file = tmp_path / "test.docx"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(md_file),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0, f"Unexpected exit code. Output: {result.output}"
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_convert_to_odt(tmp_path: Path):
    """CLI convert command produces a .odt file from a Markdown source."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Hello\n\nWorld\n", encoding="utf-8")
    output_file = tmp_path / "test.odt"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(md_file),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0, f"Unexpected exit code. Output: {result.output}"
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_convert_with_theme(tmp_path: Path):
    """CLI convert command accepts --theme academic and still produces a valid file."""
    md_file = tmp_path / "academic.md"
    md_file.write_text("# Academic Document\n\nSome text.\n", encoding="utf-8")
    output_file = tmp_path / "academic.docx"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(md_file),
            "--output",
            str(output_file),
            "--theme",
            "academic",
        ],
    )

    assert result.exit_code == 0, f"Unexpected exit code. Output: {result.output}"
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_convert_unsupported_format(tmp_path: Path):
    """CLI convert exits with an error when the output extension is unsupported."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Hello\n", encoding="utf-8")
    output_file = tmp_path / "test.pdf"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(md_file),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code != 0
    assert "unsupported" in result.output.lower() or "error" in result.output.lower()


def test_convert_missing_file(tmp_path: Path):
    """CLI convert exits with an error when the input file does not exist."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(tmp_path / "does_not_exist.md"),
        ],
    )
    # Click raises UsageError for a non-existent required argument path
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Integration tests: themes subcommands
# ---------------------------------------------------------------------------


def test_themes_list_output():
    """themes list output includes default, academic, and modern."""
    runner = CliRunner()
    result = runner.invoke(cli, ["themes", "list"])
    assert result.exit_code == 0
    assert "default" in result.output
    assert "academic" in result.output
    assert "modern" in result.output


def test_themes_show_output():
    """themes show default outputs font info."""
    runner = CliRunner()
    result = runner.invoke(cli, ["themes", "show", "default"])
    assert result.exit_code == 0
    # The show command always prints a Fonts section
    assert "Fonts" in result.output or "font" in result.output.lower()
    # Should include the heading font name from the default theme
    assert "Arial" in result.output


def test_themes_show_nonexistent():
    """themes show for an unknown name exits with an error."""
    runner = CliRunner()
    result = runner.invoke(cli, ["themes", "show", "definitely_nonexistent_theme"])
    assert result.exit_code != 0
    assert "error" in result.output.lower() or "Error" in result.output
