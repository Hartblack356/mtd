"""Data models for mtd."""

from dataclasses import dataclass, field


@dataclass
class Document:
    """Represents a parsed Markdown document."""

    content: str
    """The Markdown content rendered as HTML."""

    metadata: dict = field(default_factory=dict)
    """Metadata extracted from YAML frontmatter (title, author, date, theme, etc.)."""

    titlepage: str | None = None
    """HTML content of the titlepage block, or None if absent."""

    @property
    def title(self) -> str | None:
        val = self.metadata.get("title")
        return str(val) if val is not None else None

    @property
    def author(self) -> str | None:
        val = self.metadata.get("author")
        return str(val) if val is not None else None

    @property
    def date(self) -> str | None:
        return self.metadata.get("date")  # type: ignore[no-any-return]

    @property
    def theme(self) -> str:
        val = self.metadata.get("theme", "default")
        return str(val) if val is not None else "default"

    @property
    def header(self) -> dict | None:
        val = self.metadata.get("header")
        return val if isinstance(val, dict) else None

    @property
    def footer(self) -> dict | None:
        val = self.metadata.get("footer")
        return val if isinstance(val, dict) else None
