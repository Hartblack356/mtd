# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-21

### Added

- Markdown to DOCX conversion via `python-docx`
- Markdown to ODT conversion via `odfpy`
- YAML frontmatter support (title, author, date, theme)
- Title page block (`:::titlepage`) for cover pages
- Header and footer support via frontmatter configuration
- Theme system with YAML configuration files
- 3 built-in themes: `default`, `academic`, `modern`
- Custom theme support from external YAML files
- CLI with `convert`, `themes`, `init`, and `serve` commands
- `mtd init` command to scaffold a template in any directory
- Python SDK with `convert()` and `convert_string()` functions
- FastAPI HTTP API microservice for system integration (`mtd serve`)
- Full Markdown support: headings, bold, italic, lists, tables, code blocks, blockquotes, links, footnotes
- 173 tests with 99.68% code coverage
- Self-hosted coverage badge (no external service)
- Security scanning with Bandit and pip-audit
- Pre-commit hooks (ruff, mypy, bandit)
- GitHub Actions CI with weekly schedule
- Auto-generated changelog on push to main
- Trusted publishing to PyPI via GitHub Actions
- CONTRIBUTING.md with development guide
- Issue and PR templates

### Fixed

- mypy type errors across all modules
- Hardcoded paths in CI tests
- coverage-badge incompatibility with Python 3.14
