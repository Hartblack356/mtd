# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-20

### Added

- Markdown to DOCX conversion via `python-docx`
- Markdown to ODT conversion via `odfpy`
- YAML frontmatter support (title, author, date, theme)
- Title page block (`:::titlepage`) for cover pages
- Header and footer support via frontmatter configuration
- Theme system with YAML configuration files
- 3 built-in themes: `default`, `academic`, `modern`
- Custom theme support from external YAML files
- CLI with `convert` and `themes` commands
- Full Markdown support: headings, bold, italic, lists, tables, code blocks, blockquotes, links, footnotes
