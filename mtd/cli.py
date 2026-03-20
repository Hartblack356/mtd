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
    from mtd.api import convert as mtd_convert

    input_path = Path(input_file)
    if output is None:
        output = input_path.with_suffix(".docx")
    output_path = Path(output)

    try:
        result = mtd_convert(input_path, output_path, theme=theme)
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
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


@cli.command()
@click.option(
    "-o",
    "--output",
    default="template.md",
    show_default=True,
    help="Output file name.",
)
def init(output):
    """Copy the example Markdown template to the current directory."""
    import shutil

    template = Path(__file__).parent.parent / "examples" / "template.md"
    if not template.exists():
        # Fallback for installed packages
        import importlib.resources

        ref = importlib.resources.files("mtd").joinpath("../examples/template.md")
        template = Path(str(ref))

    dest = Path(output)
    if dest.exists():
        click.echo(f"Error: '{dest}' already exists. Use -o to specify another name.", err=True)
        sys.exit(1)

    shutil.copy2(template, dest)
    click.echo(f"Created {dest}")


@cli.command()
@click.option(
    "-h",
    "--host",
    default="127.0.0.1",
    show_default=True,
    help="Host to bind to. Use 127.0.0.1 for local only.",
)
@click.option(
    "-p",
    "--port",
    default=8484,
    show_default=True,
    help="Port to listen on.",
)
def serve(host, port):
    """Start the HTTP API server (local/internal use only)."""
    try:
        import uvicorn
    except ImportError:
        click.echo(
            "Error: API dependencies not installed. Install with: pip install mtd[api]",
            err=True,
        )
        sys.exit(1)

    click.echo(f"Starting mtd API server on http://{host}:{port}")
    click.echo("WARNING: For local/internal use only. Do not expose to the internet.")
    click.echo(f"API docs available at http://{host}:{port}/docs")
    uvicorn.run("mtd.server:app", host=host, port=port)
