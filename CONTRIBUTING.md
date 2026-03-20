# Contributing to mtd

Thanks for your interest in contributing to mtd! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

### Getting Started

```bash
# Clone the repo
git clone https://github.com/Dxsk/mtd.git
cd mtd

# Install dependencies
uv sync

# Run tests
uv run pytest -v

# Run linters
uv run ruff check .
uv run ruff format --check .
```

### Pre-commit Hooks

We use pre-commit to ensure code quality. Install the hooks:

```bash
uv run pre-commit install
```

This will automatically run linters and formatters before each commit.

## Project Structure

```
mtd/
├── mtd/                  # Main package
│   ├── cli.py            # Click CLI entry point
│   ├── parser.py         # Markdown parser with frontmatter support
│   ├── models.py         # Data models (Document)
│   ├── writers/           # Output format writers
│   │   ├── docx_writer.py
│   │   └── odt_writer.py
│   └── themes/            # Theme system
│       ├── engine.py      # Theme loader and resolver
│       └── builtins/      # Built-in theme YAML files
├── tests/                 # Test suite
├── examples/              # Example Markdown files
└── docs/                  # Documentation
```

## How to Contribute

### Reporting Bugs

- Check existing issues first to avoid duplicates
- Use the Bug Report issue template
- Include: steps to reproduce, expected vs actual behavior, your environment

### Suggesting Features

- Use the Feature Request issue template
- Explain the use case and why it would be useful
- If possible, describe how it could work

### Submitting Code

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature
   ```
3. Make your changes
4. Write or update tests
5. Make sure all checks pass:
   ```bash
   uv run pytest -v
   uv run ruff check .
   uv run ruff format .
   uv run mypy mtd/ --ignore-missing-imports
   ```
6. Commit using conventional commits:
   - `feat: add new feature`
   - `fix: resolve bug`
   - `docs: update documentation`
   - `test: add tests`
   - `refactor: restructure code`
   - `chore: update dependencies`
7. Push and open a Pull Request

### Adding a New Theme

1. Create a YAML file in `mtd/themes/builtins/`
2. Follow the structure documented in `docs/themes.md`
3. Add tests for the new theme in `tests/test_themes.py`

### Adding a New Output Format

1. Create a new writer in `mtd/writers/` (e.g. `pdf_writer.py`)
2. Implement the `write_<format>(document, output, theme)` function
3. Register the extension in `mtd/cli.py` convert command
4. Add tests in `tests/test_writers.py`

## Code Style

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Line length: 100 characters
- Type hints are encouraged but not strictly required
- Write docstrings for public functions

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add PDF export support
fix: handle empty frontmatter gracefully
docs: update theme specification
test: add tests for nested lists in DOCX writer
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
