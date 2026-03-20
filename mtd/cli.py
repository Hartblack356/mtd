"""Command-line interface for mtd."""

import sys
from pathlib import Path

import click

from mtd import __version__


@click.group()
@click.version_option(version=__version__, prog_name="mtd")
def cli():
    """mtd: Markdown to Documents converter, lightweight and themeable."""


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-o",
    "--output",
    default=None,
    help="Output file path (.docx or .odt). Defaults to input name with .docx extension.",
)
@click.option(
    "-t",
    "--theme",
    default=None,
    help="Theme name or path to a YAML theme file. Defaults to document frontmatter or 'default'.",
)
def convert(input_file, output, theme):
    """Convert a Markdown file to DOCX or ODT."""
    from mtd.parser import parse_markdown
    from mtd.themes.engine import load_theme
    from mtd.writers.docx_writer import write_docx
    from mtd.writers.odt_writer import write_odt

    # Parse input
    input_path = Path(input_file)
    doc = parse_markdown(input_path)

    # Resolve output path
    if output is None:
        output = input_path.with_suffix(".docx")
    output_path = Path(output)

    # Resolve theme (CLI flag > frontmatter > default)
    theme_name = theme or doc.theme or "default"
    try:
        resolved_theme = load_theme(theme_name)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Choose writer based on output extension
    ext = output_path.suffix.lower()
    if ext == ".docx":
        result = write_docx(doc, output_path, resolved_theme)
    elif ext == ".odt":
        result = write_odt(doc, output_path, resolved_theme)
    else:
        click.echo(f"Error: unsupported output format '{ext}'. Use .docx or .odt.", err=True)
        sys.exit(1)

    click.echo(f"Created {result}")


@cli.group()
def themes():
    """Manage and inspect available themes."""


@themes.command(name="list")
def themes_list():
    """List all available themes."""
    from mtd.themes.engine import list_themes, load_theme

    for name in list_themes():
        t = load_theme(name)
        click.echo(f"  {name:<12} {t.description}")


@themes.command(name="show")
@click.argument("name")
def themes_show(name):
    """Show details about a specific theme."""
    from mtd.themes.engine import load_theme

    try:
        t = load_theme(name)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Theme: {t.name}")
    click.echo(f"Description: {t.description}")
    click.echo("")
    click.echo("Fonts:")
    click.echo(f"  Heading: {t.font_heading}")
    click.echo(f"  Body:    {t.font_body}")
    click.echo(f"  Code:    {t.font_code}")
    click.echo("")
    click.echo("Colors:")
    click.echo(f"  Primary:    {t.color_primary}")
    click.echo(f"  Text:       {t.color_text}")
    click.echo(f"  Code bg:    {t.color_code_background}")
    click.echo("")
    click.echo(f"Body: {t.body_size}pt, {t.line_spacing}x spacing")
    margins = f"{t.margin_top}/{t.margin_bottom}/{t.margin_left}/{t.margin_right}"
    click.echo(f"Page: {t.page_size}, margins {margins}")
