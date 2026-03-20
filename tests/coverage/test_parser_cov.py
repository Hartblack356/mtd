"""Tests targeting mtd/parser.py coverage.

Covers: non-dict YAML frontmatter handling (line 62).
"""

from mtd.parser import parse_markdown

# ===========================================================================
# parser.py (line 62) -- non-dict YAML frontmatter
# ===========================================================================


def test_frontmatter_non_dict_list():
    """YAML frontmatter that is a list (not dict) results in empty metadata (line 62)."""
    from mtd.parser import _split_frontmatter

    text = "---\n- item one\n- item two\n---\n# Hello\n"
    meta, _body = _split_frontmatter(text)
    assert meta == {}
    assert "Hello" in _body


def test_frontmatter_non_dict_string():
    """YAML frontmatter that is a plain string results in empty metadata (line 62)."""
    from mtd.parser import _split_frontmatter

    text = "---\njust a string value\n---\n# Content\n"
    meta, _body = _split_frontmatter(text)
    assert meta == {}


def test_parse_markdown_non_dict_frontmatter():
    """parse_markdown with non-dict frontmatter returns empty metadata."""
    doc = parse_markdown("---\n- list item\n---\n# Hi\n")
    assert doc.metadata == {}
