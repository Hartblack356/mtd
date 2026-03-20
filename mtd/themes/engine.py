"""Theme engine: load and resolve theme configurations."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class HeadingStyle:
    size: int = 11
    bold: bool = True
    italic: bool = False
    color: str | None = None


@dataclass
class Theme:
    """Complete theme configuration."""

    name: str = "default"
    description: str = ""

    # Fonts
    font_heading: str = "Arial"
    font_body: str = "Calibri"
    font_code: str = "Courier New"

    # Colors
    color_primary: str = "#2563eb"
    color_secondary: str = "#64748b"
    color_text: str = "#1f2937"
    color_background: str = "#ffffff"
    color_code_background: str = "#f5f5f5"

    # Headings
    h1: HeadingStyle = field(default_factory=lambda: HeadingStyle(size=24, bold=True))
    h2: HeadingStyle = field(default_factory=lambda: HeadingStyle(size=20, bold=True))
    h3: HeadingStyle = field(default_factory=lambda: HeadingStyle(size=16, bold=True))
    h4: HeadingStyle = field(default_factory=lambda: HeadingStyle(size=14, bold=True))
    h5: HeadingStyle = field(default_factory=lambda: HeadingStyle(size=12, bold=True))
    h6: HeadingStyle = field(default_factory=lambda: HeadingStyle(size=11, bold=True, italic=True))

    # Body
    body_size: int = 11
    line_spacing: float = 1.15

    # Code
    code_size: int = 10

    # Page
    margin_top: str = "2.54cm"
    margin_bottom: str = "2.54cm"
    margin_left: str = "2.54cm"
    margin_right: str = "2.54cm"
    page_size: str = "A4"

    # Title page
    titlepage_title_size: int = 28
    titlepage_subtitle_size: int = 20
    titlepage_info_size: int = 14
    titlepage_spacing_top: str = "7cm"


# Directory containing built-in themes
_THEMES_DIR = Path(__file__).parent / "builtins"


def _parse_theme_yaml(data: dict) -> Theme:
    """Parse a raw YAML dict into a Theme, applying defaults for missing fields."""
    theme = Theme()

    if "name" in data:
        theme.name = data["name"]
    if "description" in data:
        theme.description = data["description"]

    # Fonts
    fonts = data.get("fonts", {})
    if "heading" in fonts:
        theme.font_heading = fonts["heading"]
    if "body" in fonts:
        theme.font_body = fonts["body"]
    if "code" in fonts:
        theme.font_code = fonts["code"]

    # Colors
    colors = data.get("colors", {})
    if "primary" in colors:
        theme.color_primary = colors["primary"]
    if "secondary" in colors:
        theme.color_secondary = colors["secondary"]
    if "text" in colors:
        theme.color_text = colors["text"]
    if "background" in colors:
        theme.color_background = colors["background"]
    if "code_background" in colors:
        theme.color_code_background = colors["code_background"]

    # Headings
    heading = data.get("heading", {})
    for level in range(1, 7):
        key = f"h{level}"
        if key in heading:
            h_data = heading[key]
            style = HeadingStyle(
                size=h_data.get("size", getattr(theme, key).size),
                bold=h_data.get("bold", getattr(theme, key).bold),
                italic=h_data.get("italic", getattr(theme, key).italic),
                color=h_data.get("color", getattr(theme, key).color),
            )
            setattr(theme, key, style)

    # Body
    body = data.get("body", {})
    if "size" in body:
        theme.body_size = body["size"]
    if "line_spacing" in body:
        theme.line_spacing = body["line_spacing"]

    # Code
    code = data.get("code", {})
    if "size" in code:
        theme.code_size = code["size"]
    if "background" in code:
        theme.color_code_background = code["background"]

    # Page
    page = data.get("page", {})
    if "margin_top" in page:
        theme.margin_top = page["margin_top"]
    if "margin_bottom" in page:
        theme.margin_bottom = page["margin_bottom"]
    if "margin_left" in page:
        theme.margin_left = page["margin_left"]
    if "margin_right" in page:
        theme.margin_right = page["margin_right"]
    if "size" in page:
        theme.page_size = page["size"]

    # Title page
    tp = data.get("titlepage", {})
    if "title_size" in tp:
        theme.titlepage_title_size = tp["title_size"]
    if "subtitle_size" in tp:
        theme.titlepage_subtitle_size = tp["subtitle_size"]
    if "info_size" in tp:
        theme.titlepage_info_size = tp["info_size"]
    if "spacing_top" in tp:
        theme.titlepage_spacing_top = tp["spacing_top"]

    return theme


def load_theme(name_or_path: str) -> Theme:
    """Load a theme by name or file path.

    Args:
        name_or_path: Either a built-in theme name (e.g. "default", "academic", "modern")
            or a path to a custom YAML theme file.

    Returns:
        A resolved Theme object with all defaults applied.

    Raises:
        FileNotFoundError: If the theme name or path cannot be found.
    """
    # Check if it's a file path
    path = Path(name_or_path)
    if path.suffix in (".yaml", ".yml") and path.is_file():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return _parse_theme_yaml(data)

    # Check built-in themes
    builtin = _THEMES_DIR / f"{name_or_path}.yaml"
    if builtin.is_file():
        data = yaml.safe_load(builtin.read_text(encoding="utf-8")) or {}
        return _parse_theme_yaml(data)

    # Default theme (no file needed)
    if name_or_path == "default":
        return Theme()

    raise FileNotFoundError(f"Theme '{name_or_path}' not found. Checked: {path}, {builtin}")


def list_themes() -> list[str]:
    """List all available built-in theme names."""
    themes = ["default"]
    if _THEMES_DIR.is_dir():
        for f in sorted(_THEMES_DIR.glob("*.yaml")):
            name = f.stem
            if name not in themes:
                themes.append(name)
    return themes
