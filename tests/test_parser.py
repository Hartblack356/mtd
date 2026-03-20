"""Unit tests for the mtd Markdown parser."""

import datetime
from pathlib import Path

from mtd.models import Document
from mtd.parser import _split_frontmatter, parse_markdown

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
TEMPLATE_PATH = EXAMPLES_DIR / "template.md"


def _h(tag: str, content: str) -> bool:
    """Return True when an HTML element open-tag (possibly with attributes)
    followed by *content* appears somewhere in the string.

    The toc extension adds id="..." to every heading, so we cannot do a
    simple '<h1>' substring match.  Instead we check for '<h1' (tag start)
    and the expected text content separately.
    """
    return True  # used only as a docstring anchor; see usages below


# ---------------------------------------------------------------------------
# Test 1: Parse a simple heading
# ---------------------------------------------------------------------------


def test_parse_simple_heading():
    """A single H1 heading produces an <h1 ...> tag in the HTML output.

    The toc extension emits '<h1 id="hello-world">Hello World</h1>',
    so we match on '<h1' (the tag start) rather than the exact '<h1>'.
    """
    doc = parse_markdown("# Hello World")
    assert isinstance(doc, Document)
    assert "<h1" in doc.content
    assert "Hello World" in doc.content


# ---------------------------------------------------------------------------
# Test 2: Parse bold and italic text
# ---------------------------------------------------------------------------


def test_parse_bold_text():
    """Double-asterisk syntax produces a <strong> tag."""
    doc = parse_markdown("**bold text**")
    assert "<strong>" in doc.content
    assert "bold text" in doc.content


def test_parse_italic_text():
    """Single-asterisk syntax produces an <em> tag."""
    doc = parse_markdown("*italic text*")
    assert "<em>" in doc.content
    assert "italic text" in doc.content


# ---------------------------------------------------------------------------
# Test 3: Parse unordered list
# ---------------------------------------------------------------------------


def test_parse_unordered_list():
    """Dash-prefixed items produce a <ul> with <li> entries."""
    md = "- First item\n- Second item\n- Third item"
    doc = parse_markdown(md)
    assert "<ul>" in doc.content
    assert "<li>" in doc.content
    assert "First item" in doc.content
    assert "Third item" in doc.content


# ---------------------------------------------------------------------------
# Test 4: Parse ordered list
# ---------------------------------------------------------------------------


def test_parse_ordered_list():
    """Numbered items produce an <ol> with <li> entries."""
    md = "1. Step one\n2. Step two\n3. Step three"
    doc = parse_markdown(md)
    assert "<ol>" in doc.content
    assert "<li>" in doc.content
    assert "Step one" in doc.content
    assert "Step three" in doc.content


# ---------------------------------------------------------------------------
# Test 5: Parse code block (fenced)
# ---------------------------------------------------------------------------


def test_parse_fenced_code_block():
    """Triple-backtick fenced blocks produce a <code> element inside <pre>."""
    md = "```python\nprint('hello')\n```"
    doc = parse_markdown(md)
    assert "<code" in doc.content
    assert "print" in doc.content


def test_parse_fenced_code_block_preserves_content():
    """Code content is preserved verbatim inside the code block."""
    md = "```\nsome_function(arg1, arg2)\n```"
    doc = parse_markdown(md)
    assert "some_function" in doc.content


# ---------------------------------------------------------------------------
# Test 6: Parse table
# ---------------------------------------------------------------------------


def test_parse_table():
    """Pipe-delimited tables produce a <table> element with headers and rows."""
    md = "| Name  | Age |\n|-------|-----|\n| Alice | 30  |\n| Bob   | 25  |\n"
    doc = parse_markdown(md)
    assert "<table>" in doc.content
    assert "<th>" in doc.content or "<thead>" in doc.content
    assert "Alice" in doc.content
    assert "Bob" in doc.content


# ---------------------------------------------------------------------------
# Test 7: Parse blockquote
# ---------------------------------------------------------------------------


def test_parse_blockquote():
    """Greater-than-sign prefix produces a <blockquote> element."""
    md = "> This is a blockquote."
    doc = parse_markdown(md)
    assert "<blockquote>" in doc.content
    assert "This is a blockquote." in doc.content


# ---------------------------------------------------------------------------
# Test 8: Frontmatter extraction (title, author, date, theme)
# ---------------------------------------------------------------------------


def test_frontmatter_all_fields():
    """All standard frontmatter fields are extracted and accessible as properties.

    YAML parses ISO-date values (e.g. 2026-01-01) as datetime.date objects,
    not plain strings.  The Document.date property exposes whatever type YAML
    produced, so we compare against datetime.date rather than a string.
    """
    md = "---\ntitle: My Document\nauthor: Jane Doe\ndate: 2026-01-01\ntheme: dark\n---\n# Body\n"
    doc = parse_markdown(md)
    assert doc.title == "My Document"
    assert doc.author == "Jane Doe"
    # pyyaml coerces ISO dates to datetime.date
    assert doc.date == datetime.date(2026, 1, 1)
    assert doc.theme == "dark"


def test_frontmatter_not_in_html_body():
    """YAML frontmatter keys do not appear verbatim in the rendered HTML body."""
    md = "---\ntitle: Hidden Title\n---\nBody paragraph.\n"
    doc = parse_markdown(md)
    # The raw YAML delimiter should not leak into HTML
    assert "---" not in doc.content
    assert "Body paragraph" in doc.content


# ---------------------------------------------------------------------------
# Test 9: Frontmatter missing (returns empty metadata, default theme)
# ---------------------------------------------------------------------------


def test_no_frontmatter_empty_metadata():
    """Documents without frontmatter have an empty metadata dict."""
    doc = parse_markdown("# No frontmatter here")
    assert doc.metadata == {}
    assert doc.title is None
    assert doc.author is None
    assert doc.date is None


def test_no_frontmatter_default_theme():
    """The theme property falls back to 'default' when frontmatter is absent."""
    doc = parse_markdown("Just some plain text.")
    assert doc.theme == "default"


# ---------------------------------------------------------------------------
# Test 10: Frontmatter with invalid YAML (gracefully returns empty metadata)
# ---------------------------------------------------------------------------


def test_invalid_yaml_frontmatter_returns_empty_metadata():
    """Malformed YAML in frontmatter is silently ignored; metadata is empty."""
    md = "---\ntitle: [unclosed bracket\nauthor: : bad colon:\n---\nContent here.\n"
    doc = parse_markdown(md)
    assert doc.metadata == {}
    assert doc.theme == "default"
    # Body content must still be rendered
    assert "Content here" in doc.content


# ---------------------------------------------------------------------------
# Test 11: Parse from file path (examples/template.md)
# ---------------------------------------------------------------------------


def test_parse_from_file_path_string():
    """parse_markdown accepts a string path to a .md file and reads it."""
    doc = parse_markdown(str(TEMPLATE_PATH))
    assert isinstance(doc, Document)
    # Template has known frontmatter
    assert doc.title == "Document Title"
    assert doc.author == "Your Name"
    assert doc.theme == "default"
    # Template body contains headings (toc extension adds id attrs)
    assert "<h1" in doc.content or "<h2" in doc.content


def test_parse_from_file_path_object():
    """parse_markdown accepts a Path object pointing to a .md file."""
    doc = parse_markdown(TEMPLATE_PATH)
    assert isinstance(doc, Document)
    assert doc.title == "Document Title"
    # Template contains a table
    assert "<table>" in doc.content
    # Template contains a blockquote
    assert "<blockquote>" in doc.content


# ---------------------------------------------------------------------------
# Test 12: Parse from raw string (not a file path)
# ---------------------------------------------------------------------------


def test_parse_from_raw_string_returns_document():
    """A raw Markdown string (not a file path) is parsed directly.

    The toc extension adds id attributes, so match on '<h2' not '<h2>'.
    """
    raw = "## Section\n\nSome **bold** content."
    doc = parse_markdown(raw)
    assert isinstance(doc, Document)
    assert "<h2" in doc.content
    assert "<strong>" in doc.content
    assert "bold" in doc.content


def test_parse_raw_string_with_frontmatter():
    """Raw string with frontmatter is parsed correctly without file I/O."""
    raw = "---\ntitle: Raw String Doc\ntheme: light\n---\nParagraph text.\n"
    doc = parse_markdown(raw)
    assert doc.title == "Raw String Doc"
    assert doc.theme == "light"
    assert "Paragraph text" in doc.content


# ---------------------------------------------------------------------------
# Internal helper: _split_frontmatter
# ---------------------------------------------------------------------------


def test_split_frontmatter_no_delimiter():
    """Text without a leading delimiter returns empty metadata and full text."""
    text = "# Heading\nBody"
    meta, body = _split_frontmatter(text)
    assert meta == {}
    assert "Heading" in body


def test_split_frontmatter_valid():
    """Valid frontmatter is parsed into a dict and body is returned separately."""
    text = "---\ntitle: T\nauthor: A\n---\nBody content"
    meta, body = _split_frontmatter(text)
    assert meta == {"title": "T", "author": "A"}
    assert "Body content" in body
    assert "title" not in body


def test_split_frontmatter_unclosed_delimiter():
    """Frontmatter with no closing delimiter returns empty metadata and full text."""
    text = "---\ntitle: Missing close\n"
    meta, body = _split_frontmatter(text)
    assert meta == {}
    assert "Missing close" in body


def test_document_is_dataclass():
    """Document can be instantiated directly and fields are accessible."""
    doc = Document(content="<p>Hi</p>", metadata={"title": "Test"})
    assert doc.content == "<p>Hi</p>"
    assert doc.title == "Test"
    assert doc.theme == "default"
