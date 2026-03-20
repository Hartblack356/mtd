# mtd

[![CI](https://github.com/Dxsk/mtd/actions/workflows/ci.yml/badge.svg)](https://github.com/Dxsk/mtd/actions/workflows/ci.yml)
![coverage](coverage.svg)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Yet another Markdown to Documents converter. Lightweight, themeable, and API-ready.

Convert your Markdown files to **DOCX** and **ODT** with custom themes. Available as a CLI tool, a Python SDK, or a local HTTP microservice for integration with other systems.

## Features

- 📄 Convert Markdown to `.docx` and `.odt`
- 🎨 Built-in themes: `default`, `academic`, `modern`
- 🧩 Custom themes via simple YAML files
- 📝 YAML frontmatter support (title, author, date, theme)
- 📑 Title page and headers/footers support
- 🐍 Python SDK for programmatic use
- 🌐 HTTP API microservice (FastAPI) for system integration
- ⚡ Fast and lightweight with minimal dependencies
- 🛠️ CLI, SDK, and API: three ways to use it

## Install

```bash
# With uv (recommended)
uv pip install mtd

# With pip
pip install mtd
```

## Quick Start

```bash
# Convert to DOCX
mtd convert README.md -o output.docx

# Convert to ODT with a theme
mtd convert README.md -o output.odt --theme modern

# List available themes
mtd themes list

# Show theme details
mtd themes show academic
```

## SDK / Python API

Use mtd as a library in your own Python projects.

### Install

```bash
pip install mtd
```

### Quick Convert

```python
from mtd import convert

# Markdown file to DOCX
convert("report.md", "report.docx")

# With a theme
convert("report.md", "report.docx", theme="academic")

# To ODT
convert("report.md", "report.odt", theme="modern")
```

### Convert from String

```python
from mtd import convert_string

markdown = """
---
title: Generated Report
author: Automation Bot
---

# Results

Processing completed successfully.
"""

convert_string(markdown, "report.docx", theme="modern")
```

### Granular API

For more control, use the lower-level functions:

```python
from mtd import parse_markdown, write_docx, write_odt, load_theme, Document

# Parse
doc = parse_markdown("report.md")
print(doc.title)       # from frontmatter
print(doc.author)
print(doc.theme)       # "default" if not set
print(doc.titlepage)   # HTML of titlepage block, or None
print(doc.header)      # header config dict, or None
print(doc.footer)      # footer config dict, or None

# Load a theme
theme = load_theme("academic")
# Or from a custom YAML file
theme = load_theme("path/to/custom.yaml")

# Write to DOCX
write_docx(doc, "output.docx", theme)

# Write to ODT
write_odt(doc, "output.odt", theme)
```

### Available Exports

| Import | Description |
|--------|-------------|
| `convert(input, output, theme=)` | High-level one-liner conversion |
| `convert_string(markdown, output, theme=)` | Convert from a Markdown string |
| `parse_markdown(source)` | Parse a file or string into a Document |
| `Document` | Parsed document dataclass |
| `write_docx(doc, output, theme=)` | Write Document to DOCX |
| `write_odt(doc, output, theme=)` | Write Document to ODT |
| `load_theme(name_or_path)` | Load a theme by name or YAML path |
| `list_themes()` | List available built-in theme names |
| `Theme` | Theme configuration dataclass |

## HTTP API

mtd includes an optional HTTP API server for integration with other systems.

> **WARNING**: This API is for local/internal use only. It has no authentication or security hardening. Do not expose it to the public internet. Use it behind a reverse proxy or within a private network.

### Install

```bash
pip install mtd[api]
```

### Start the Server

```bash
# Via CLI
mtd serve --port 8484

# Or directly with uvicorn
uvicorn mtd.server:app --host 127.0.0.1 --port 8484
```

API documentation is available at `http://127.0.0.1:8484/docs` (Swagger UI).

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/themes` | List available themes |
| `GET` | `/themes/{name}` | Get theme details |
| `POST` | `/convert` | Convert Markdown text (form data) |
| `POST` | `/convert/file` | Convert uploaded Markdown file |

### Examples

```bash
# Health check
curl http://127.0.0.1:8484/health

# List themes
curl http://127.0.0.1:8484/themes

# Convert Markdown text to DOCX
curl -X POST http://127.0.0.1:8484/convert \
  -F "markdown=# Hello World" \
  -F "format=docx" \
  -F "theme=modern" \
  -o output.docx

# Upload and convert a file
curl -X POST http://127.0.0.1:8484/convert/file \
  -F "file=@document.md" \
  -F "format=odt" \
  -F "theme=academic" \
  -o output.odt
```

## Themes

mtd ships with 3 built-in themes:

| Theme | Description |
|-------|-------------|
| `default` | Clean and neutral. Serif body, sans-serif headings |
| `academic` | Formal. Times New Roman, wide margins, double spacing |
| `modern` | Contemporary. Sans-serif, tight spacing, accent colors |

### Custom Themes

Create a YAML file with your style preferences:

```yaml
name: my-theme
fonts:
  heading: Helvetica
  body: Georgia
  code: Fira Code
colors:
  primary: "#2563eb"
  text: "#1f2937"
page:
  margin_top: 2.5cm
  margin_bottom: 2.5cm
```

Then use it:

```bash
mtd convert doc.md -o doc.docx --theme path/to/my-theme.yaml
```

## Markdown Template

mtd extends standard Markdown with special blocks for professional document generation. A complete example is available in [examples/template.md](examples/template.md).

### Full Example

```markdown
---
title: Quarterly Report
subtitle: Q1 2026 Results
author: Jane Doe
date: 2026-03-20
theme: modern
header:
  left: "Quarterly Report"
  center: ""
  right: "{page}"
footer:
  left: "Jane Doe"
  center: "Confidential"
  right: "{date}"
---

:::titlepage
# Quarterly Report
## Q1 2026 Results
Jane Doe
ACME Corp.
March 2026
:::

# Introduction

Document content starts here...
```

### Frontmatter Reference

The YAML frontmatter block (`---`) at the top of the file controls all document metadata and layout.

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Document title (used in metadata and `{title}` placeholder) |
| `subtitle` | string | Subtitle (displayed on title page) |
| `author` | string | Author name (used in metadata and `{author}` placeholder) |
| `date` | string | Date in `YYYY-MM-DD` format (used in metadata and `{date}` placeholder) |
| `theme` | string | Theme name or path to a `.yaml` file. Defaults to `default` |
| `header` | object | Header configuration (see below) |
| `footer` | object | Footer configuration (see below) |

#### Headers and Footers

Headers and footers support three zones: `left`, `center`, and `right`. Each zone is optional and defaults to empty.

```yaml
header:
  left: "Company Name"
  center: ""
  right: "{page}"
footer:
  left: "{author}"
  center: "Draft"
  right: "{date}"
```

**Available placeholders:**

| Placeholder | Replaced with |
|-------------|---------------|
| `{page}` | Current page number (auto-incremented) |
| `{date}` | Document date from frontmatter |
| `{title}` | Document title from frontmatter |

Headers and footers are repeated on every page. When a title page is present, it is excluded from headers/footers automatically.

### Title Page Block

The `:::titlepage` block generates a dedicated cover page before the document content. Content inside the block is centered with larger fonts.

```markdown
:::titlepage
# Main Title
## Subtitle
Author Name
Organization
Date or other info
:::
```

**Rendering rules:**

| Element | Style |
|---------|-------|
| `# Heading 1` | Large bold title (28pt by default, configurable via theme) |
| `## Heading 2` | Subtitle (20pt by default) |
| Plain text | Info lines (14pt by default, centered) |

The title page sizes are controlled by the theme:

```yaml
titlepage:
  title_size: 28      # H1 font size in pt
  subtitle_size: 20   # H2 font size in pt
  info_size: 14       # Plain text font size in pt
  spacing_top: "7cm"  # Top margin before content
```

A page break is automatically inserted after the title page.

### Supported Markdown Elements

| Element | Syntax | DOCX | ODT |
|---------|--------|:----:|:---:|
| Headings | `# H1` to `###### H6` | Yes | Yes |
| Bold | `**text**` | Yes | Yes |
| Italic | `*text*` | Yes | Yes |
| Bold + Italic | `***text***` | Yes | Yes |
| Strikethrough | `~~text~~` | Yes | Yes |
| Inline code | `` `code` `` | Yes | Yes |
| Fenced code blocks | ` ```python ` | Yes | Yes |
| Unordered lists | `- item` (supports nesting) | Yes | Yes |
| Ordered lists | `1. item` (supports nesting) | Yes | Yes |
| Task lists | `- [x] done` / `- [ ] todo` | Yes | Yes |
| Tables | Pipe syntax with alignment | Yes | Yes |
| Blockquotes | `> quote` (supports nesting) | Yes | Yes |
| Links | `[text](url)` | Yes | Yes |
| Images | `![alt](url)` | Yes | Yes |
| Horizontal rules | `---` | Yes | Yes |
| Footnotes | `text[^1]` / `[^1]: note` | Yes | Yes |

### Minimal Template

The simplest valid mtd document:

```markdown
---
title: My Document
author: Your Name
---

# Hello World

This is a paragraph.
```

### Full-Featured Template

For a production-ready template with all features, copy the example:

```bash
cp examples/template.md my-document.md
mtd convert my-document.md -o my-document.docx --theme academic
```

## License

MIT
