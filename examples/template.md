---
title: Document Title
subtitle: A comprehensive template for mtd
author: Your Name
date: 2026-03-20
theme: default
header:
  left: "Document Title"
  right: "{page}"
footer:
  left: "Your Name"
  right: "{date}"
---

:::titlepage
# Document Title
## A comprehensive template for mtd
Your Name
2026-03-20
:::

# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6

## Paragraphs

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Text Formatting

This is **bold text** and this is *italic text*.

You can also use ***bold and italic*** together.

This is ~~strikethrough~~ text.

This is `inline code` within a paragraph.

## Lists

### Unordered List

- First item
- Second item
  - Nested item A
  - Nested item B
- Third item

### Ordered List

1. First step
2. Second step
   1. Sub-step A
   2. Sub-step B
3. Third step

### Task List

- [x] Completed task
- [ ] Pending task
- [ ] Another pending task

## Links and Images

[Visit the mtd repository](https://github.com/Dxsk/mtd)

![Placeholder image](https://via.placeholder.com/600x200)

## Blockquotes

> This is a blockquote. It can span multiple lines
> and supports **formatting** inside.
>
> It can also have multiple paragraphs.

## Code Blocks

### Python

```python
def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
```

### JSON

```json
{
  "name": "mtd",
  "version": "0.1.0",
  "description": "Markdown to Documents converter"
}
```

## Tables

| Feature       | DOCX | ODT |
|---------------|:----:|:---:|
| Headings      |  Yes |  Yes |
| Bold / Italic |  Yes |  Yes |
| Code blocks   |  Yes |  Yes |
| Tables        |  Yes |  Yes |
| Images        |  Yes |  Yes |

## Horizontal Rule

---

## Footnotes

Here is a sentence with a footnote[^1].

[^1]: This is the footnote content.

## Summary

This template covers all the Markdown features supported by mtd. Use it as a starting point for your own documents, or as a test file to preview themes.
