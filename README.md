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

mtd extends standard Markdown with special blocks for document generation.

### Frontmatter

YAML frontmatter controls document metadata, theme, and page layout:

```yaml
---
title: My Report
subtitle: Q1 2026 Results
author: Jane Doe
date: 2026-03-20
theme: modern
header:
  left: "My Report"
  right: "{page}"
footer:
  left: "Jane Doe"
  right: "{date}"
---
```

Available placeholders for headers/footers: `{page}` (page number), `{date}` (document date), `{title}` (document title).

### Title Page

Use the `:::titlepage` block to generate a cover page with centered, large text. This page is rendered separately before the document content, with no header/footer.

```markdown
:::titlepage
# My Report
## Q1 2026 Results
Jane Doe
March 2026
:::
```

### Supported Markdown Features

mtd supports all common Markdown elements:

- Headings (H1 to H6)
- **Bold**, *italic*, ~~strikethrough~~, `inline code`
- Ordered and unordered lists (with nesting)
- Fenced code blocks with syntax highlighting
- Tables
- Blockquotes
- Links and images
- Horizontal rules
- Footnotes

See [examples/template.md](examples/template.md) for a complete sample.

## License

MIT
