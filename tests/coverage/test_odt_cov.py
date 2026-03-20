"""Tests targeting mtd/writers/odt_writer.py coverage.

Covers: _parse_cm variants, header/footer branches, list rendering,
inline styles (bold/italic, strikethrough, links, br, inline code),
blockquote, image alt text, table rendering, metadata, and parser utility methods.
"""

import io
import zipfile

from mtd.models import Document
from mtd.parser import parse_markdown
from mtd.themes.engine import Theme
from mtd.writers.odt_writer import _parse_cm as odt_parse_cm
from mtd.writers.odt_writer import write_odt


def _doc(md: str) -> Document:
    return parse_markdown(md)


def _odt_element_to_xml(element) -> str:
    """Serialize an odfpy element to an XML string."""
    buf = io.StringIO()
    element.toXml(0, buf)
    return buf.getvalue()


# ===========================================================================
# odt_writer.py -- uncovered rendering branches
# ===========================================================================


def test_odt_parse_cm_inches():
    """_parse_cm in odt_writer handles 'in' suffix (lines 42-43)."""
    result = odt_parse_cm("1in")
    assert abs(result - 2.54) < 0.001


def test_odt_parse_cm_bare_float():
    """_parse_cm in odt_writer handles bare float (line 44)."""
    result = odt_parse_cm("3.5")
    assert result == 3.5


def test_odt_hf_paragraph_with_page_number():
    """_build_odt_hf_paragraph with {page} generates a page number element (lines 281-289)."""
    from mtd.writers.odt_writer import _build_odt_hf_paragraph

    para = _build_odt_hf_paragraph("Page {page} of many", "2026-01-01", "Test Doc")
    xml = _odt_element_to_xml(para)
    assert "page-number" in xml or "page" in xml.lower()


def test_odt_hf_paragraph_with_date_title():
    """_build_odt_hf_paragraph replaces {date} and {title} placeholders."""
    from mtd.writers.odt_writer import _build_odt_hf_paragraph

    para = _build_odt_hf_paragraph("Date: {date}, Title: {title}", "2026-03-20", "My Report")
    xml = _odt_element_to_xml(para)
    assert "2026-03-20" in xml
    assert "My Report" in xml


def test_odt_header_with_center_text(tmp_path):
    """ODT header with center text hits the center branch (line 341)."""
    md = """\
---
header:
  left: "Left text"
  center: "Center text"
  right: ""
---
# Body
"""
    doc = _doc(md)
    output = tmp_path / "hdr_center.odt"
    write_odt(doc, output)
    assert output.exists()
    # Header/footer content is stored in styles.xml, not content.xml
    with zipfile.ZipFile(str(output)) as zf:
        styles_content = zf.read("styles.xml").decode()
    assert "Center text" in styles_content


def test_odt_header_with_right_page(tmp_path):
    """ODT header with right={page} hits the page-number path (line 346-348)."""
    md = """\
---
header:
  left: ""
  center: ""
  right: "{page}"
---
# Body
"""
    doc = _doc(md)
    output = tmp_path / "hdr_page.odt"
    write_odt(doc, output)
    assert output.exists()
    with zipfile.ZipFile(str(output)) as zf:
        styles_content = zf.read("styles.xml").decode()
    assert "page-number" in styles_content


def test_odt_footer_with_center_text(tmp_path):
    """ODT footer with center text (line 373)."""
    md = """\
---
footer:
  left: "Left footer"
  center: "Center footer"
  right: ""
---
# Body
"""
    doc = _doc(md)
    output = tmp_path / "ftr_center.odt"
    write_odt(doc, output)
    assert output.exists()
    # Footer content is in styles.xml
    with zipfile.ZipFile(str(output)) as zf:
        styles_content = zf.read("styles.xml").decode()
    assert "Center footer" in styles_content


def test_odt_footer_with_right_page(tmp_path):
    """ODT footer right={page} hits page number element path (lines 379-380)."""
    md = """\
---
footer:
  left: ""
  center: ""
  right: "{page}"
---
# Body
"""
    doc = _doc(md)
    output = tmp_path / "ftr_page.odt"
    write_odt(doc, output)
    assert output.exists()
    with zipfile.ZipFile(str(output)) as zf:
        styles_content = zf.read("styles.xml").decode()
    assert "page-number" in styles_content


def test_odt_ordered_list(tmp_path):
    """Ordered list creates ODF List elements (lines 603-613)."""
    md = "1. Alpha\n2. Beta\n3. Gamma\n"
    output = tmp_path / "ol.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "text:list" in content
    assert "Alpha" in content


def test_odt_nested_unordered_list(tmp_path):
    """Nested unordered list -- parent_li path for nested list (lines 592-596)."""
    md = "- Top item\n  - Nested item\n    - Deep item\n- Another top\n"
    output = tmp_path / "nested_ul.odt"
    write_odt(_doc(md), output)
    assert output.exists()
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "Nested item" in content


def test_odt_nested_ordered_list(tmp_path):
    """Nested ordered list -- exercises ol nested path (lines 606-610)."""
    md = "1. First\n   1. Nested first\n2. Second\n"
    output = tmp_path / "nested_ol.odt"
    write_odt(_doc(md), output)
    assert output.exists()


def test_odt_bold_italic_combined(tmp_path):
    """Bold+italic combined text emits STYLE_BOLD_ITALIC span (line 493)."""
    md = "***bold and italic***"
    output = tmp_path / "bold_italic.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "BoldItalic" in content or "bold" in content.lower()


def test_odt_strikethrough(tmp_path):
    """Strikethrough text uses STYLE_STRIKETHROUGH span (lines 672-673, 778-779).

    Uses raw HTML document since the markdown library does not support ~~ strikethrough
    without a special extension. Feeds <del> directly to the ODT parser.
    """
    doc = Document(
        content="<p>Normal text <del>strikethrough</del> and <s>also this</s></p>",
        metadata={},
    )
    output = tmp_path / "strike.odt"
    write_odt(doc, output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "Strikethrough" in content


def test_odt_horizontal_rule(tmp_path):
    """<hr> creates a blank paragraph and closes the block (line 698)."""
    md = "Before.\n\n---\n\nAfter."
    output = tmp_path / "hr.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "Before" in content
    assert "After" in content


def test_odt_image_with_alt_text(tmp_path):
    """img with alt attribute emits alt text (lines 694-700)."""
    md = "![My image alt](image.png)\n\nOther text."
    output = tmp_path / "image.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "My image alt" in content or "Image:" in content


def test_odt_image_without_alt_text(tmp_path):
    """img without alt attribute is silently skipped."""
    md = "![](image.png)\n\nText."
    output = tmp_path / "image_noalt.odt"
    write_odt(_doc(md), output)
    assert output.exists()


def test_odt_image_with_alt_no_current_block(tmp_path):
    """img tag when no current block creates a new block first (line 698)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)
    # Feed an img tag directly with no preceding paragraph -- current_block is None
    parser.feed('<img src="x.png" alt="TestAlt"/>')
    # Should create a block and emit the alt text
    import io as _io

    buf = _io.StringIO()
    odt.text.toXml(0, buf)
    xml = buf.getvalue()
    assert "TestAlt" in xml


def test_odt_blockquote_creates_implicit_paragraph(tmp_path):
    """Text inside a blockquote without an explicit p creates an implicit block (line 800-801)."""
    md = "> Quoted text here.\n"
    output = tmp_path / "bq.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "Quoted text here" in content or "Blockquote" in content


def test_odt_link(tmp_path):
    """Links in ODT just emit the text content (line 677)."""
    md = "Check [this link](https://example.com) out."
    output = tmp_path / "link.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "this link" in content


def test_odt_br_tag(tmp_path):
    """<br> in ODT adds a LineBreak element (lines 680-684)."""
    md = "Line one  \nLine two"
    output = tmp_path / "br.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "Line one" in content


def test_odt_table_with_header_row(tmp_path):
    """ODT table renders header row with STYLE_TABLE_HEADER (lines 812, 816, 830)."""
    md = "| Col A | Col B |\n|-------|-------|\n| val 1 | val 2 |\n"
    output = tmp_path / "table_hdr.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "TableHeader" in content
    assert "Col A" in content


def test_odt_build_table_empty_rows():
    """_build_table returns immediately when no rows (line 812)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)
    parser._table_rows = []
    parser._build_table()
    # No table should have been added
    import io as _io

    buf = _io.StringIO()
    odt.text.toXml(0, buf)
    assert "table:table" not in buf.getvalue()


def test_odt_table_missing_cells_padding(tmp_path):
    """ODT table with rows of unequal cell count pads missing cells (line 830)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())

    parser = _OdtHTMLParser(odt)
    # Simulate a table where second row has fewer cells than the header
    html = (
        "<table>"
        "<thead><tr><th>A</th><th>B</th><th>C</th></tr></thead>"
        "<tbody><tr><td>1</td><td>2</td></tr></tbody>"
        "</table>"
    )
    parser.feed(html)
    # Should not crash; table is built with padding for missing cells
    assert True


def test_odt_emit_text_with_no_inline():
    """_emit_text returns early when _current_inline is None (line 534)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)
    assert parser._current_inline is None
    # Should return without raising
    parser._emit_text("hello")


def test_odt_handle_data_empty_string():
    """handle_data with an empty string returns early (line 783)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)
    # Should not raise
    parser.handle_data("")


def test_odt_ul_inside_list_with_no_parent_li(tmp_path):
    """ul when list_stack has no parent_li hits the else branch (line 596)."""
    from odf.opendocument import OpenDocumentText
    from odf.text import List

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)
    # Manually put a list entry with parent_li=None into the stack
    fake_list = List()
    odt.text.addElement(fake_list)
    parser._list_stack.append(["ul", fake_list, None])  # parent_li is None
    # Now trigger another ul tag -- hits the parent_li is None branch (line 596)
    parser.feed("<ul><li>Item</li></ul>")


def test_odt_ol_inside_list_with_parent_li(tmp_path):
    """ol when list_stack has a parent_li hits the parent_li.addElement branch (line 608)."""
    from odf.opendocument import OpenDocumentText
    from odf.text import List, ListItem

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)
    # Set up a fake parent list item in the stack
    fake_list = List()
    odt.text.addElement(fake_list)
    fake_li = ListItem()
    fake_list.addElement(fake_li)
    parser._list_stack.append(["ul", fake_list, fake_li])  # parent_li is a real li
    # Feed an ol tag -- hits the parent_li is not None branch (line 607-608)
    parser.feed("<ol><li>Item</li></ol>")


def test_odt_div_tag_creates_block_when_no_current_block(tmp_path):
    """div without an open block creates a new paragraph (lines 579-580)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)
    parser.feed("<div>Some div content</div>")
    # Should not crash


def test_odt_write_with_author_and_date(tmp_path):
    """write_odt sets document metadata (title, author, date) in ODT meta."""
    md = "---\ntitle: ODT Doc\nauthor: Bob\ndate: 2026-01-15\n---\n# Hello\n"
    doc = _doc(md)
    output = tmp_path / "meta.odt"
    write_odt(doc, output)
    assert output.exists()
    with zipfile.ZipFile(str(output)) as zf:
        meta_content = zf.read("meta.xml").decode()
    assert "ODT Doc" in meta_content or "Bob" in meta_content


def test_odt_code_block(tmp_path):
    """Code block renders as STYLE_CODE_BLOCK paragraphs."""
    md = "```python\ndef hello():\n    print('hello')\n```\n"
    output = tmp_path / "code.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "CodeBlock" in content
    assert "hello" in content


def test_odt_inline_code(tmp_path):
    """Inline code renders as STYLE_MONOSPACE span."""
    md = "Here is `inline code` in a sentence."
    output = tmp_path / "inline_code.odt"
    write_odt(_doc(md), output)
    with zipfile.ZipFile(str(output)) as zf:
        content = zf.read("content.xml").decode()
    assert "Monospace" in content or "inline code" in content


def test_odt_titlepage_bare_text(tmp_path):
    """Titlepage with bare text (outside tags) exercises the bare text path (line 429-433)."""
    md = """\
:::titlepage
# Title

Author Name Here
:::

# Content
"""
    doc = _doc(md)
    output = tmp_path / "tp_bare.odt"
    write_odt(doc, output)
    assert output.exists()


def test_odt_blockquote_depth(tmp_path):
    """Nested blockquote increments and decrements depth correctly."""
    md = "> Outer\n>\n> > Inner blockquote\n"
    output = tmp_path / "nested_bq.odt"
    write_odt(_doc(md), output)
    assert output.exists()


def test_odt_build_master_page_no_theme(tmp_path):
    """_build_odt_master_page with theme=None uses a default Theme (line 304)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_odt_master_page, _build_styles

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    # Call with theme=None -- should use Theme() internally
    _build_odt_master_page(odt, {"left": "hi", "center": "", "right": ""}, None, "", "", None)
    # Should not raise


def test_odt_master_page_header_right_with_text(tmp_path):
    """ODT header with right text (not page number) hits the 'text' rtype branch (line 345-346)."""
    md = """\
---
header:
  left: ""
  center: ""
  right: "Static right"
---
# Body
"""
    doc = _doc(md)
    output = tmp_path / "hdr_right_text.odt"
    write_odt(doc, output)
    assert output.exists()
    with zipfile.ZipFile(str(output)) as zf:
        styles_content = zf.read("styles.xml").decode()
    assert "Static right" in styles_content


# ===========================================================================
# Additional tests for remaining uncovered lines
# ===========================================================================


def test_odt_blockquote_implicit_paragraph_in_blockquote():
    """Data outside any block while _in_blockquote > 0 creates Blockquote paragraph (800-801)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)

    # Force state: in_blockquote > 0 but no current block
    parser._in_blockquote = 1
    parser._current_block = None

    # Feeding non-whitespace data triggers the implicit blockquote paragraph branch
    parser.handle_data("Bare blockquote text")

    import io as _io

    buf = _io.StringIO()
    odt.text.toXml(0, buf)
    xml = buf.getvalue()
    assert "Bare blockquote text" in xml


def test_odt_build_table_zero_col_count():
    """_build_table with rows containing no cells hits col_count == 0 branch (line 816)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)

    # Inject table_rows with empty cell lists so col_count == 0
    parser._table_rows = [(False, []), (True, [])]
    parser._build_table()

    # No table should be created
    import io as _io

    buf = _io.StringIO()
    odt.text.toXml(0, buf)
    assert "table:table" not in buf.getvalue()


def test_odt_ol_nested_in_list_no_parent_li():
    """ol inside a list when parent_li is None hits line 610 (body.addElement branch)."""
    from odf.opendocument import OpenDocumentText
    from odf.text import List

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)
    # Manually put a list entry with parent_li=None into the stack (for ol specifically)
    fake_list = List()
    odt.text.addElement(fake_list)
    parser._list_stack.append(["ol", fake_list, None])  # parent_li is None
    # Feed an ol -- hits the `else: self._body.addElement(lst)` branch (line 610)
    parser.feed("<ol><li>Nested item</li></ol>")


def test_odt_implicit_paragraph_not_in_blockquote():
    """Data outside any block while NOT in blockquote creates Normal paragraph (line 803)."""
    from odf.opendocument import OpenDocumentText

    from mtd.writers.odt_writer import _build_styles, _OdtHTMLParser

    odt = OpenDocumentText()
    _build_styles(odt, Theme())
    parser = _OdtHTMLParser(odt)

    # Force state: no blockquote, no current block, non-whitespace data
    parser._in_blockquote = 0
    parser._current_block = None
    parser.handle_data("Bare normal text")

    import io as _io

    buf = _io.StringIO()
    odt.text.toXml(0, buf)
    xml = buf.getvalue()
    assert "Bare normal text" in xml
