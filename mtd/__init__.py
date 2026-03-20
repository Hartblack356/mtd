"""mtd: Markdown to Documents converter. Lightweight and themeable.

Quick usage:
    from mtd import convert
    convert("input.md", "output.docx", theme="modern")

Granular usage:
    from mtd import parse_markdown, write_docx, load_theme
    doc = parse_markdown("input.md")
    theme = load_theme("academic")
    write_docx(doc, "output.docx", theme)
"""

__version__ = "0.1.0"

from mtd.api import convert, convert_string
from mtd.models import Document
from mtd.parser import parse_markdown
from mtd.themes.engine import Theme, list_themes, load_theme
from mtd.writers.docx_writer import write_docx
from mtd.writers.odt_writer import write_odt

__all__ = [
    "Document",
    "Theme",
    "__version__",
    "convert",
    "convert_string",
    "list_themes",
    "load_theme",
    "parse_markdown",
    "write_docx",
    "write_odt",
]
