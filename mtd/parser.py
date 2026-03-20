"""Markdown parser module."""

import re
from pathlib import Path

import markdown
import yaml

from mtd.models import Document

# Markdown extensions to enable
EXTENSIONS = [
    "tables",
    "fenced_code",
    "codehilite",
    "toc",
    "footnotes",
    "attr_list",
    "md_in_html",
    "sane_lists",
    "smarty",
    "nl2br",
]

EXTENSION_CONFIGS = {
    "codehilite": {
        "css_class": "highlight",
        "guess_lang": False,
    },
}

FRONTMATTER_DELIMITER = "---"

# Regex to match :::titlepage ... ::: blocks
_TITLEPAGE_RE = re.compile(r":::titlepage\s*\n(.*?)\n:::", re.DOTALL)


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from Markdown content.

    Returns a tuple of (metadata_dict, markdown_body).
    If no frontmatter is found, returns an empty dict and the full text.
    """
    stripped = text.strip()
    if not stripped.startswith(FRONTMATTER_DELIMITER):
        return {}, text

    # Find the closing delimiter
    end = stripped.find(FRONTMATTER_DELIMITER, len(FRONTMATTER_DELIMITER))
    if end == -1:
        return {}, text

    frontmatter_raw = stripped[len(FRONTMATTER_DELIMITER) : end].strip()
    body = stripped[end + len(FRONTMATTER_DELIMITER) :].strip()

    try:
        metadata = yaml.safe_load(frontmatter_raw) or {}
    except yaml.YAMLError:
        metadata = {}

    if not isinstance(metadata, dict):
        metadata = {}

    return metadata, body


def _extract_titlepage(body: str, md_instance: markdown.Markdown) -> tuple[str | None, str]:
    """Extract :::titlepage ... ::: block from body text.

    Returns (titlepage_html, body_without_titlepage).
    If no titlepage block is found, returns (None, body).
    """
    match = _TITLEPAGE_RE.search(body)
    if match is None:
        return None, body

    titlepage_md = match.group(1)
    # Parse the titlepage content as HTML using a fresh Markdown instance
    tp_md = markdown.Markdown(
        extensions=EXTENSIONS,
        extension_configs=EXTENSION_CONFIGS,
    )
    titlepage_html = tp_md.convert(titlepage_md)

    # Remove the titlepage block from the body
    body_without = _TITLEPAGE_RE.sub("", body).strip()

    return titlepage_html, body_without


def parse_markdown(source: str | Path) -> Document:
    """Parse a Markdown file or string into a Document.

    Args:
        source: A file path (str or Path) or raw Markdown string.
            If the source looks like a file path and exists, it is read.
            Otherwise, it is treated as raw Markdown content.

    Returns:
        A Document with HTML content and extracted metadata.
    """
    path = Path(source) if not isinstance(source, Path) else source

    if path.suffix in (".md", ".markdown") and path.is_file():
        text = path.read_text(encoding="utf-8")
    else:
        text = str(source)

    metadata, body = _split_frontmatter(text)

    # Extract titlepage block before passing to the markdown library
    titlepage_html, body = _extract_titlepage(body, None)

    md = markdown.Markdown(
        extensions=EXTENSIONS,
        extension_configs=EXTENSION_CONFIGS,
    )
    html = md.convert(body)

    return Document(content=html, metadata=metadata, titlepage=titlepage_html)
