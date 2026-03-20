"""Public API for mtd.

Use this module to convert Markdown files programmatically.

Quick usage:
    from mtd import convert
    convert("input.md", "output.docx", theme="modern")

Granular usage:
    from mtd import parse_markdown, write_docx, load_theme
    doc = parse_markdown("input.md")
    theme = load_theme("academic")
    write_docx(doc, "output.docx", theme)
"""

from pathlib import Path

from mtd.parser import parse_markdown
from mtd.themes.engine import Theme, load_theme
from mtd.writers.docx_writer import write_docx
from mtd.writers.odt_writer import write_odt


def convert(
    input: str | Path,
    output: str | Path,
    *,
    theme: str | Theme | None = None,
    format: str | None = None,
) -> Path:
    """Convert a Markdown file to a document.

    This is the main high-level function for using mtd as a library.

    Args:
        input: Path to the Markdown file, or a raw Markdown string.
        output: Path for the output file (.docx or .odt).
        theme: Theme name (e.g. "modern"), path to a YAML file,
            or a Theme object. If None, uses the theme from the
            document frontmatter, or "default".
        format: Output format ("docx" or "odt"). If None, inferred
            from the output file extension.

    Returns:
        Path to the created output file.

    Raises:
        ValueError: If the output format is unsupported.
        FileNotFoundError: If the input file or theme is not found.

    Examples:
        Basic conversion:

        >>> from mtd import convert
        >>> convert("report.md", "report.docx")
        PosixPath('report.docx')

        With a theme:

        >>> convert("report.md", "report.docx", theme="academic")
        PosixPath('report.docx')

        To ODT:

        >>> convert("report.md", "report.odt", theme="modern")
        PosixPath('report.odt')
    """
    # Parse input
    doc = parse_markdown(input)

    # Resolve output path
    output_path = Path(output)

    # Resolve theme
    if theme is None:
        resolved_theme = load_theme(doc.theme or "default")
    elif isinstance(theme, Theme):
        resolved_theme = theme
    else:
        resolved_theme = load_theme(theme)

    # Resolve format
    fmt = output_path.suffix.lower().lstrip(".") if format is None else format.lower().lstrip(".")

    # Write
    if fmt == "docx":
        return write_docx(doc, output_path, resolved_theme)
    elif fmt == "odt":
        return write_odt(doc, output_path, resolved_theme)
    else:
        raise ValueError(f"Unsupported output format: '{fmt}'. Use 'docx' or 'odt'.")


def convert_string(
    markdown: str,
    output: str | Path,
    *,
    theme: str | Theme | None = None,
    format: str | None = None,
) -> Path:
    """Convert a Markdown string (not a file) to a document.

    Same as convert(), but takes raw Markdown content instead of a file path.
    Useful when generating Markdown dynamically.

    Args:
        markdown: Raw Markdown string.
        output: Path for the output file.
        theme: Theme name, path, or Theme object.
        format: Output format ("docx" or "odt").

    Returns:
        Path to the created output file.

    Examples:
        >>> from mtd import convert_string
        >>> md = "# Hello\\n\\nWorld"
        >>> convert_string(md, "hello.docx")
        PosixPath('hello.docx')
    """
    doc = parse_markdown(markdown)

    output_path = Path(output)

    if theme is None:
        resolved_theme = load_theme(doc.theme or "default")
    elif isinstance(theme, Theme):
        resolved_theme = theme
    else:
        resolved_theme = load_theme(theme)

    fmt = output_path.suffix.lower().lstrip(".") if format is None else format.lower().lstrip(".")

    if fmt == "docx":
        return write_docx(doc, output_path, resolved_theme)
    elif fmt == "odt":
        return write_odt(doc, output_path, resolved_theme)
    else:
        raise ValueError(f"Unsupported output format: '{fmt}'. Use 'docx' or 'odt'.")


__all__ = [
    "convert",
    "convert_string",
]
