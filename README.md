# mtd

Yet another Markdown to Documents converter. Lightweight and themeable.

Convert your Markdown files to **DOCX** and **ODT** with custom themes, in a single command.

## Features

- 📄 Convert Markdown to `.docx` and `.odt`
- 🎨 Built-in themes: `default`, `academic`, `modern`
- 🧩 Custom themes via simple YAML files
- 📝 YAML frontmatter support (title, author, date, theme)
- ⚡ Fast and lightweight with minimal dependencies
- 🛠️ Simple CLI interface

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
