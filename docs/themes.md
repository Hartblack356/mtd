# Theme Specification

Themes in mtd are YAML files that define visual styles for document output.

## Structure

```yaml
name: theme-name
description: Short description of the theme

fonts:
  heading: "Font Name"
  body: "Font Name"
  code: "Monospace Font Name"

colors:
  primary: "#hex"
  secondary: "#hex"
  text: "#hex"
  background: "#hex"
  code_background: "#f5f5f5"

heading:
  h1:
    size: 24
    bold: true
    color: "#hex"
  h2:
    size: 20
    bold: true
    color: "#hex"
  h3:
    size: 16
    bold: true
  h4:
    size: 14
    bold: true
  h5:
    size: 12
    bold: true
  h6:
    size: 11
    bold: true
    italic: true

body:
  size: 11
  line_spacing: 1.15

code:
  size: 10
  background: "#f5f5f5"

page:
  margin_top: "2.54cm"
  margin_bottom: "2.54cm"
  margin_left: "2.54cm"
  margin_right: "2.54cm"
  size: "A4"

titlepage:
  title_size: 28
  subtitle_size: 20
  info_size: 14
  spacing_top: "7cm"
```

## Defaults

Any omitted field falls back to the default theme values. Custom themes only need to specify the fields they want to override.

## Usage

```bash
# Use a built-in theme
mtd convert doc.md -o doc.docx --theme academic

# Use a custom YAML file
mtd convert doc.md -o doc.docx --theme path/to/custom.yaml
```
