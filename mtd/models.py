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
        return self.metadata.get("title")

    @property
    def author(self) -> str | None:
        return self.metadata.get("author")

    @property
    def date(self) -> str | None:
        return self.metadata.get("date")

    @property
    def theme(self) -> str:
        return self.metadata.get("theme", "default")

    @property
    def header(self) -> dict | None:
        return self.metadata.get("header")

    @property
    def footer(self) -> dict | None:
        return self.metadata.get("footer")
