"""Writer module for .odt (OpenDocument Text) output."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from odf.opendocument import OpenDocumentText
from odf.style import (
    MasterPage,
    PageLayout,
    PageLayoutProperties,
    ParagraphProperties,
    Style,
    TableCellProperties,
    TableColumnProperties,
    TextProperties,
)
from odf.table import Table, TableCell, TableColumn, TableRow
from odf.text import (
    H,
    List,
    ListItem,
    P,
    Span,
)

from mtd.models import Document  # noqa: TC001
from mtd.themes.engine import Theme

# ---------------------------------------------------------------------------
# Measurement helpers
# ---------------------------------------------------------------------------


def _parse_cm(value: str) -> float:
    """Parse a measurement string like '2.54cm' to float cm value."""
    value = value.strip().lower()
    if value.endswith("cm"):
        return float(value[:-2])
    if value.endswith("in"):
        return float(value[:-2]) * 2.54
    return float(value)


def _cm_to_in_str(value: str) -> str:
    """Convert a cm measurement string to an inch string for ODF."""
    cm = _parse_cm(value)
    inches = cm / 2.54
    return f"{inches:.4f}in"


# ---------------------------------------------------------------------------
# Style name constants
# ---------------------------------------------------------------------------

STYLE_NORMAL = "Normal"
STYLE_BOLD = "Bold"
STYLE_ITALIC = "Italic"
STYLE_BOLD_ITALIC = "BoldItalic"
STYLE_MONOSPACE = "Monospace"
STYLE_CODE_BLOCK = "CodeBlock"
STYLE_BLOCKQUOTE = "Blockquote"
STYLE_STRIKETHROUGH = "Strikethrough"
STYLE_TABLE_CELL = "TableCell"
STYLE_TABLE_HEADER = "TableHeader"
STYLE_TABLE_COL = "TableColumn"
STYLE_TP_H1 = "TitlepageH1"
STYLE_TP_H2 = "TitlepageH2"
STYLE_TP_TEXT = "TitlepageText"
STYLE_TP_PAGEBREAK = "TitlepagePageBreak"


def _heading_style_name(level: int) -> str:
    return f"Heading{level}"


# ---------------------------------------------------------------------------
# Style registration
# ---------------------------------------------------------------------------


def _build_styles(doc: OpenDocumentText, theme: Theme) -> None:
    """Register all automatic paragraph/text styles into the ODT document."""

    body_size_pt = f"{theme.body_size}pt"
    code_size_pt = f"{theme.code_size}pt"

    # Normal paragraph
    normal = Style(name=STYLE_NORMAL, family="paragraph")
    normal.addElement(ParagraphProperties(margintop="0.08in", marginbottom="0.08in"))
    normal.addElement(
        TextProperties(
            fontsize=body_size_pt,
            fontname=theme.font_body,
            color=theme.color_text,
        )
    )
    doc.automaticstyles.addElement(normal)

    # Headings H1-H6
    heading_styles = {
        1: theme.h1,
        2: theme.h2,
        3: theme.h3,
        4: theme.h4,
        5: theme.h5,
        6: theme.h6,
    }
    for level, h_style in heading_styles.items():
        size_pt = f"{h_style.size}pt"
        color = h_style.color if h_style.color else theme.color_primary
        s = Style(name=_heading_style_name(level), family="paragraph")
        s.addElement(ParagraphProperties(margintop="0.15in", marginbottom="0.05in"))
        text_props_kwargs = {
            "fontsize": size_pt,
            "fontname": theme.font_heading,
            "color": color,
        }
        if h_style.bold:
            text_props_kwargs["fontweight"] = "bold"
        if h_style.italic:
            text_props_kwargs["fontstyle"] = "italic"
        s.addElement(TextProperties(**text_props_kwargs))
        doc.automaticstyles.addElement(s)

    # Bold text
    bold_style = Style(name=STYLE_BOLD, family="text")
    bold_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(bold_style)

    # Italic text
    italic_style = Style(name=STYLE_ITALIC, family="text")
    italic_style.addElement(TextProperties(fontstyle="italic"))
    doc.automaticstyles.addElement(italic_style)

    # Bold + italic text
    bi_style = Style(name=STYLE_BOLD_ITALIC, family="text")
    bi_style.addElement(TextProperties(fontweight="bold", fontstyle="italic"))
    doc.automaticstyles.addElement(bi_style)

    # Monospace (inline code)
    mono_style = Style(name=STYLE_MONOSPACE, family="text")
    mono_style.addElement(TextProperties(fontname=theme.font_code, fontsize=code_size_pt))
    doc.automaticstyles.addElement(mono_style)

    # Code block paragraph
    code_block = Style(name=STYLE_CODE_BLOCK, family="paragraph")
    code_block.addElement(
        ParagraphProperties(
            marginleft="0.3in",
            margintop="0.05in",
            marginbottom="0.05in",
            backgroundcolor=theme.color_code_background,
        )
    )
    code_block.addElement(TextProperties(fontname=theme.font_code, fontsize=code_size_pt))
    doc.automaticstyles.addElement(code_block)

    # Blockquote paragraph
    bq_style = Style(name=STYLE_BLOCKQUOTE, family="paragraph")
    bq_style.addElement(
        ParagraphProperties(
            marginleft="0.4in",
            margintop="0.05in",
            marginbottom="0.05in",
        )
    )
    bq_style.addElement(TextProperties(fontstyle="italic"))
    doc.automaticstyles.addElement(bq_style)

    # Strikethrough text
    strike_style = Style(name=STYLE_STRIKETHROUGH, family="text")
    strike_style.addElement(
        TextProperties(
            textlinethroughstyle="solid",
            textlinethroughtype="single",
        )
    )
    doc.automaticstyles.addElement(strike_style)

    # Table cell
    tc_style = Style(name=STYLE_TABLE_CELL, family="table-cell")
    tc_style.addElement(TableCellProperties(border="0.05pt solid #000000", padding="0.05in"))
    doc.automaticstyles.addElement(tc_style)

    # Table header cell (slightly darker background)
    th_style = Style(name=STYLE_TABLE_HEADER, family="table-cell")
    th_style.addElement(
        TableCellProperties(
            border="0.05pt solid #000000",
            padding="0.05in",
            backgroundcolor="#d0d0d0",
        )
    )
    doc.automaticstyles.addElement(th_style)

    # Table column
    col_style = Style(name=STYLE_TABLE_COL, family="table-column")
    col_style.addElement(TableColumnProperties(columnwidth="1.8in"))
    doc.automaticstyles.addElement(col_style)

    tp_title_size = f"{theme.titlepage_title_size}pt"
    tp_subtitle_size = f"{theme.titlepage_subtitle_size}pt"
    tp_info_size = f"{theme.titlepage_info_size}pt"

    # Titlepage H1 style
    tp_h1 = Style(name=STYLE_TP_H1, family="paragraph")
    tp_h1.addElement(
        ParagraphProperties(
            textalign="center",
            margintop="1.5in",
            marginbottom="0.2in",
        )
    )
    tp_h1.addElement(
        TextProperties(
            fontsize=tp_title_size,
            fontweight="bold",
            fontname=theme.font_heading,
            color=theme.color_primary,
        )
    )
    doc.automaticstyles.addElement(tp_h1)

    # Titlepage H2 style
    tp_h2 = Style(name=STYLE_TP_H2, family="paragraph")
    tp_h2.addElement(
        ParagraphProperties(
            textalign="center",
            margintop="0.1in",
            marginbottom="0.1in",
        )
    )
    tp_h2.addElement(
        TextProperties(
            fontsize=tp_subtitle_size,
            fontname=theme.font_heading,
        )
    )
    doc.automaticstyles.addElement(tp_h2)

    # Titlepage regular text style
    tp_text = Style(name=STYLE_TP_TEXT, family="paragraph")
    tp_text.addElement(
        ParagraphProperties(
            textalign="center",
            margintop="0.1in",
            marginbottom="0.1in",
        )
    )
    tp_text.addElement(
        TextProperties(
            fontsize=tp_info_size,
            fontname=theme.font_body,
        )
    )
    doc.automaticstyles.addElement(tp_text)

    # Titlepage page-break style (empty paragraph with page break after)
    tp_pb = Style(name=STYLE_TP_PAGEBREAK, family="paragraph")
    tp_pb.addElement(ParagraphProperties(breakafter="page"))
    doc.automaticstyles.addElement(tp_pb)


# ---------------------------------------------------------------------------
# Header/Footer helpers for ODT
# ---------------------------------------------------------------------------


def _make_page_number_element():
    """Return an ODF text:page-number element."""
    from odf.text import PageNumber

    return PageNumber(selectpage="current", text="1")


def _build_odt_hf_paragraph(text: str, date_str: str, title_str: str):
    """Build a P element with text, replacing {page}, {date}, {title}."""
    para = P(stylename=STYLE_NORMAL)
    parts = text.split("{page}")
    for i, part in enumerate(parts):
        part = part.replace("{date}", date_str).replace("{title}", title_str)
        if part:
            para.addText(part)
        if i < len(parts) - 1:
            para.addElement(_make_page_number_element())
    return para


def _build_odt_master_page(
    doc: OpenDocumentText,
    header_dict: dict | None,
    footer_dict: dict | None,
    date_str: str,
    title_str: str,
    theme: Theme | None = None,
) -> None:
    """Create a page layout and master page with header/footer."""
    from odf.style import Footer, Header

    if theme is None:
        theme = Theme()

    # Page layout using theme margins
    pl = PageLayout(name="MtdPageLayout")
    pl.addElement(
        PageLayoutProperties(
            margintop=_cm_to_in_str(theme.margin_top),
            marginbottom=_cm_to_in_str(theme.margin_bottom),
            marginleft=_cm_to_in_str(theme.margin_left),
            marginright=_cm_to_in_str(theme.margin_right),
        )
    )
    doc.automaticstyles.addElement(pl)

    # Master page
    mp = MasterPage(name="Standard", pagelayoutname="MtdPageLayout")

    if header_dict is not None:
        hdr = Header()
        left = header_dict.get("left", "").replace("{date}", date_str).replace("{title}", title_str)
        center = (
            header_dict.get("center", "").replace("{date}", date_str).replace("{title}", title_str)
        )
        right_raw = header_dict.get("right", "")

        right_parts = right_raw.split("{page}")
        right_resolved = []
        for j, rp in enumerate(right_parts):
            rp = rp.replace("{date}", date_str).replace("{title}", title_str)
            right_resolved.append(("text", rp))
            if j < len(right_parts) - 1:
                right_resolved.append(("page", None))

        hdr_para = P(stylename=STYLE_NORMAL)
        if left:
            hdr_para.addText(left)
        if center:
            hdr_para.addText("\t" + center)
        if right_resolved:
            hdr_para.addText("\t")
            for rtype, rval in right_resolved:
                if rtype == "text" and rval:
                    hdr_para.addText(rval)
                elif rtype == "page":
                    hdr_para.addElement(_make_page_number_element())

        hdr.addElement(hdr_para)
        mp.addElement(hdr)

    if footer_dict is not None:
        ftr = Footer()
        left = footer_dict.get("left", "").replace("{date}", date_str).replace("{title}", title_str)
        center = (
            footer_dict.get("center", "").replace("{date}", date_str).replace("{title}", title_str)
        )
        right_raw = footer_dict.get("right", "")

        right_parts = right_raw.split("{page}")
        right_resolved = []
        for j, rp in enumerate(right_parts):
            rp = rp.replace("{date}", date_str).replace("{title}", title_str)
            right_resolved.append(("text", rp))
            if j < len(right_parts) - 1:
                right_resolved.append(("page", None))

        ftr_para = P(stylename=STYLE_NORMAL)
        if left:
            ftr_para.addText(left)
        if center:
            ftr_para.addText("\t" + center)
        if right_resolved:
            ftr_para.addText("\t")
            for rtype, rval in right_resolved:
                if rtype == "text" and rval:
                    ftr_para.addText(rval)
                elif rtype == "page":
                    ftr_para.addElement(_make_page_number_element())

        ftr.addElement(ftr_para)
        mp.addElement(ftr)

    doc.masterstyles.addElement(mp)


# ---------------------------------------------------------------------------
# Titlepage renderer for ODT
# ---------------------------------------------------------------------------


def _render_titlepage_odt(titlepage_html: str, body) -> None:
    """Parse titlepage HTML and emit styled ODT elements into body."""
    from html.parser import HTMLParser as _HTMLParser

    class _TpParser(_HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self._body = body
            self._current_tag = None
            self._buf = ""
            self._first = True

        def handle_starttag(self, tag, attrs):
            self._current_tag = tag
            self._buf = ""

        def handle_endtag(self, tag):
            text = self._buf.strip()
            if not text:
                self._current_tag = None
                return
            if tag == "h1":
                style = STYLE_TP_H1
            elif tag == "h2":
                style = STYLE_TP_H2
            else:
                style = STYLE_TP_TEXT
            para = P(stylename=style)
            para.addText(text)
            self._body.addElement(para)
            self._current_tag = None
            self._buf = ""

        def handle_data(self, data):
            if self._current_tag is not None:
                self._buf += data
            elif data.strip():
                # Bare text outside tags
                para = P(stylename=STYLE_TP_TEXT)
                para.addText(data.strip())
                body.addElement(para)

    parser = _TpParser()
    parser.feed(titlepage_html)

    # Add a page break after the titlepage
    pb = P(stylename=STYLE_TP_PAGEBREAK)
    body.addElement(pb)


# ---------------------------------------------------------------------------
# HTML parser
# ---------------------------------------------------------------------------


class _OdtHTMLParser(HTMLParser):
    """Walk HTML produced by the Markdown parser and build ODT elements."""

    def __init__(self, odt_doc: OpenDocumentText) -> None:
        super().__init__(convert_charrefs=True)
        self._doc = odt_doc
        self._body: Any = odt_doc.text

        # Stack of open HTML tags
        self._tag_stack: list[str] = []

        # Current ODT block element (P or H) where inline content is appended
        self._current_block: Any = None
        # Current inline container (Span or block itself)
        self._current_inline: Any = None

        # Inline formatting counters (allow nesting)
        self._bold: int = 0
        self._italic: int = 0
        self._code: int = 0
        self._strike: int = 0

        # Pre-block state
        self._in_pre: int = 0
        self._pre_buf: list[str] = []

        # Blockquote depth
        self._in_blockquote: int = 0

        # List stack: each entry is [list_type, odf_list_el, current_odf_li]
        self._list_stack: list[list] = []

        # Table accumulation
        self._in_table: bool = False
        self._in_thead: bool = False
        self._table_rows: list[tuple[bool, list[tuple[bool, str]]]] = []
        self._current_row_is_header: bool = False
        self._current_row_cells: list[tuple[bool, str]] = []
        self._current_cell_buf: list[str] | None = None

    # ---- Formatting helpers -----------------------------------------------

    def _effective_text_style(self) -> str:
        """Return the ODT text style name for the current inline formatting state."""
        if self._bold and self._italic:
            return STYLE_BOLD_ITALIC
        if self._bold:
            return STYLE_BOLD
        if self._italic:
            return STYLE_ITALIC
        if self._code:
            return STYLE_MONOSPACE
        if self._strike:
            return STYLE_STRIKETHROUGH
        return ""

    # ---- Block creation helpers -------------------------------------------

    def _para_style(self) -> str:
        if self._in_blockquote:
            return STYLE_BLOCKQUOTE
        return STYLE_NORMAL

    def _new_block(self, style: str) -> object:
        para = P(stylename=style)
        self._body.addElement(para)
        self._current_block = para
        self._current_inline = para
        return para

    def _new_heading(self, level: int) -> object:
        h = H(outlinelevel=level, stylename=_heading_style_name(level))
        self._body.addElement(h)
        self._current_block = h
        self._current_inline = h
        return h

    def _close_block(self) -> None:
        self._current_block = None
        self._current_inline = None

    # ---- Text emission helpers --------------------------------------------

    def _emit_text(self, text: str) -> None:
        """Add text to the current inline container with the active style."""
        if self._current_inline is None:
            return
        style = self._effective_text_style()
        if style:
            sp = Span(stylename=style)
            sp.addText(text)
            self._current_inline.addElement(sp)
        else:
            self._current_inline.addText(text)

    def _flush_pre(self) -> None:
        """Emit accumulated pre-block lines as code-block paragraphs."""
        raw = "".join(self._pre_buf)
        for line in raw.splitlines():
            para = P(stylename=STYLE_CODE_BLOCK)
            para.addText(line)
            self._body.addElement(para)
        self._pre_buf = []

    # ---- HTMLParser callbacks ---------------------------------------------

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        self._tag_stack.append(tag)

        # pre block
        if tag == "pre":
            self._in_pre += 1
            self._pre_buf = []
            return

        if tag == "code" and self._in_pre:
            return

        # headings
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._new_heading(int(tag[1]))
            return

        # paragraph
        if tag == "p":
            self._new_block(self._para_style())
            return

        # div: treat as paragraph if we have no block
        if tag == "div":
            if self._current_block is None:
                self._new_block(self._para_style())
            return

        # blockquote
        if tag == "blockquote":
            self._in_blockquote += 1
            return

        # unordered list
        if tag == "ul":
            lst = List()
            if self._list_stack:
                parent_li = self._list_stack[-1][2]
                if parent_li is not None:
                    parent_li.addElement(lst)
                else:
                    self._body.addElement(lst)
            else:
                self._body.addElement(lst)
            self._list_stack.append(["ul", lst, None])
            return

        # ordered list
        if tag == "ol":
            lst = List()
            if self._list_stack:
                parent_li = self._list_stack[-1][2]
                if parent_li is not None:
                    parent_li.addElement(lst)
                else:
                    self._body.addElement(lst)
            else:
                self._body.addElement(lst)
            self._list_stack.append(["ol", lst, None])
            return

        # list item
        if tag == "li":
            if self._list_stack:
                entry = self._list_stack[-1]
                lst = entry[1]
                li = ListItem()
                lst.addElement(li)
                para = P(stylename=STYLE_NORMAL)
                li.addElement(para)
                self._current_block = para
                self._current_inline = para
                entry[2] = li
            return

        # table
        if tag == "table":
            self._in_table = True
            self._table_rows = []
            return

        if tag == "thead":
            self._in_thead = True
            return

        if tag == "tbody":
            self._in_thead = False
            return

        if tag == "tr":
            self._current_row_is_header = self._in_thead
            self._current_row_cells = []
            return

        if tag in ("th", "td"):
            self._current_cell_buf = []
            if tag == "th":
                self._current_row_is_header = True
            return

        # inline: bold
        if tag in ("strong", "b"):
            self._bold += 1
            return

        # inline: italic
        if tag in ("em", "i"):
            self._italic += 1
            return

        # inline: code
        if tag == "code":
            self._code += 1
            return

        # inline: strikethrough
        if tag in ("del", "s"):
            self._strike += 1
            return

        # links: just show the text (handled by handle_data)
        if tag == "a":
            return

        # line break
        if tag == "br":
            if self._current_block is not None:
                from odf.text import LineBreak

                self._current_block.addElement(LineBreak())
            return

        # horizontal rule: empty paragraph
        if tag == "hr":
            self._new_block(STYLE_NORMAL)
            self._close_block()
            return

        # image: emit alt text
        if tag == "img":
            alt = attrs_dict.get("alt", "")
            if alt:
                if self._current_block is None:
                    self._new_block(STYLE_NORMAL)
                self._emit_text(f"[Image: {alt}]")
            return

    def handle_endtag(self, tag: str) -> None:
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        # pre block
        if tag == "pre":
            self._in_pre = max(0, self._in_pre - 1)
            if self._in_pre == 0:
                self._flush_pre()
            return

        if tag == "code" and self._in_pre:
            return

        # headings / paragraphs
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6", "p"):
            self._close_block()
            return

        if tag == "div":
            return

        # blockquote
        if tag == "blockquote":
            self._in_blockquote = max(0, self._in_blockquote - 1)
            self._close_block()
            return

        # lists
        if tag in ("ul", "ol"):
            if self._list_stack:
                self._list_stack.pop()
            self._close_block()
            return

        if tag == "li":
            self._close_block()
            return

        # table sections
        if tag == "thead":
            self._in_thead = False
            return

        if tag == "table":
            self._in_table = False
            self._build_table()
            return

        if tag == "tr":
            self._table_rows.append((self._current_row_is_header, list(self._current_row_cells)))
            self._current_row_cells = []
            return

        if tag in ("th", "td"):
            if self._current_cell_buf is not None:
                cell_text = "".join(self._current_cell_buf)
                is_header = self._current_row_is_header or tag == "th"
                self._current_row_cells.append((is_header, cell_text))
                self._current_cell_buf = None
            return

        # inline formatting
        if tag in ("strong", "b"):
            self._bold = max(0, self._bold - 1)
            return

        if tag in ("em", "i"):
            self._italic = max(0, self._italic - 1)
            return

        if tag == "code":
            self._code = max(0, self._code - 1)
            return

        if tag in ("del", "s"):
            self._strike = max(0, self._strike - 1)
            return

    def handle_data(self, data: str) -> None:
        if not data:
            return

        # Pre-block: accumulate raw text
        if self._in_pre:
            self._pre_buf.append(data)
            return

        # Table cell: accumulate cell text
        if self._in_table and self._current_cell_buf is not None:
            self._current_cell_buf.append(data)
            return

        # Skip whitespace-only outside any block
        if self._current_block is None:
            if not data.strip():
                return
            # Create an implicit paragraph
            if self._in_blockquote:
                self._new_block(STYLE_BLOCKQUOTE)
            else:
                self._new_block(STYLE_NORMAL)

        self._emit_text(data)

    # ---- Table building ---------------------------------------------------

    def _build_table(self) -> None:
        """Emit the accumulated table rows as an ODF table."""
        if not self._table_rows:
            return

        col_count = max((len(cells) for _, cells in self._table_rows), default=0)
        if col_count == 0:
            return

        tbl = Table()
        for _ in range(col_count):
            tbl.addElement(TableColumn(stylename=STYLE_TABLE_COL))

        for is_header_row, cells in self._table_rows:
            tr = TableRow()
            tbl.addElement(tr)

            for i in range(col_count):
                if i < len(cells):
                    is_header_cell, cell_text = cells[i]
                else:
                    is_header_cell, cell_text = False, ""

                use_header = is_header_row or is_header_cell
                cell_style = STYLE_TABLE_HEADER if use_header else STYLE_TABLE_CELL
                tc = TableCell(stylename=cell_style)
                para = P(stylename=STYLE_NORMAL)
                if use_header:
                    sp = Span(stylename=STYLE_BOLD)
                    sp.addText(cell_text)
                    para.addElement(sp)
                else:
                    para.addText(cell_text)
                tc.addElement(para)
                tr.addElement(tc)

        self._body.addElement(tbl)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def write_odt(document: Document, output: str | Path, theme: Theme | None = None) -> Path:
    """Convert a Document to ODT format.

    Args:
        document: Parsed Document object.
        output: Output file path.
        theme: Optional Theme to apply. Defaults to Theme() if not provided.

    Returns:
        The path to the created ODT file.
    """
    if theme is None:
        theme = Theme()

    output = Path(output)

    odt = OpenDocumentText()
    _build_styles(odt, theme)

    # Set document metadata if available
    if document.title or document.author or document.date:
        import odf.dc as dc

        if document.title:
            odt.meta.addElement(dc.Title(text=document.title))
        if document.author:
            odt.meta.addElement(dc.Creator(text=document.author))
        if document.date:
            odt.meta.addElement(dc.Date(text=str(document.date)))

    # Resolve placeholder values
    date_str = str(document.date) if document.date else ""
    title_str = document.title or ""

    # Set up master page with header/footer if needed
    if document.header is not None or document.footer is not None:
        _build_odt_master_page(odt, document.header, document.footer, date_str, title_str, theme)
    else:
        # Still apply page layout from theme even without header/footer
        pl = PageLayout(name="MtdPageLayout")
        pl.addElement(
            PageLayoutProperties(
                margintop=_cm_to_in_str(theme.margin_top),
                marginbottom=_cm_to_in_str(theme.margin_bottom),
                marginleft=_cm_to_in_str(theme.margin_left),
                marginright=_cm_to_in_str(theme.margin_right),
            )
        )
        odt.automaticstyles.addElement(pl)
        mp = MasterPage(name="Standard", pagelayoutname="MtdPageLayout")
        odt.masterstyles.addElement(mp)

    # Render titlepage before main content
    if document.titlepage is not None:
        _render_titlepage_odt(document.titlepage, odt.text)

    parser = _OdtHTMLParser(odt)
    parser.feed(document.content)
    parser.close()

    odt.save(str(output))
    return output
