"""FastAPI HTTP API for mtd.

This server is designed for LOCAL/INTERNAL use only.
Do NOT expose it directly to the internet. It has no authentication,
rate limiting, or security hardening. Use it behind a reverse proxy
or within a private network to let other systems convert documents.

Usage:
    uvicorn mtd.server:app --host 127.0.0.1 --port 8484

    # Or via the CLI
    mtd serve --port 8484
"""

import io
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from mtd import __version__
from mtd.api import convert_string
from mtd.themes.engine import list_themes, load_theme

app = FastAPI(
    title="mtd API",
    description=(
        "Markdown to Documents converter API. "
        "WARNING: This API is for local/internal use only. "
        "Do not expose to the public internet."
    ),
    version=__version__,
)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": __version__}


@app.get("/themes")
def get_themes():
    """List all available themes."""
    themes = []
    for name in list_themes():
        t = load_theme(name)
        themes.append({"name": t.name, "description": t.description})
    return {"themes": themes}


@app.get("/themes/{name}")
def get_theme(name: str):
    """Get details about a specific theme."""
    try:
        t = load_theme(name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Theme '{name}' not found") from exc
    return {
        "name": t.name,
        "description": t.description,
        "fonts": {
            "heading": t.font_heading,
            "body": t.font_body,
            "code": t.font_code,
        },
        "colors": {
            "primary": t.color_primary,
            "text": t.color_text,
            "code_background": t.color_code_background,
        },
        "body": {
            "size": t.body_size,
            "line_spacing": t.line_spacing,
        },
        "page": {
            "size": t.page_size,
            "margins": {
                "top": t.margin_top,
                "bottom": t.margin_bottom,
                "left": t.margin_left,
                "right": t.margin_right,
            },
        },
    }


@app.post("/convert")
def convert_markdown(
    markdown: str = Form(..., description="Raw Markdown content"),
    format: str = Form("docx", description="Output format: docx or odt"),
    theme: str = Form("default", description="Theme name"),
):
    """Convert Markdown text to a document.

    Accepts raw Markdown content as form data and returns the generated
    document file.
    """
    if format not in ("docx", "odt"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: '{format}'. Use 'docx' or 'odt'.",
        )

    try:
        load_theme(theme)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Theme '{theme}' not found") from exc

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / f"output.{format}"
        convert_string(markdown, output_path, theme=theme)
        return FileResponse(
            output_path,
            media_type="application/octet-stream",
            filename=f"document.{format}",
        )


@app.post("/convert/file")
async def convert_file(
    file: UploadFile = File(..., description="Markdown file to convert"),  # noqa: B008
    format: str = Form("docx", description="Output format: docx or odt"),
    theme: str = Form("default", description="Theme name"),
):
    """Convert an uploaded Markdown file to a document.

    Upload a .md file and receive the converted document.
    """
    if format not in ("docx", "odt"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: '{format}'. Use 'docx' or 'odt'.",
        )

    try:
        load_theme(theme)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Theme '{theme}' not found") from exc

    content = await file.read()
    markdown_text = content.decode("utf-8")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / f"output.{format}"
        convert_string(markdown_text, output_path, theme=theme)

        # Read the file into memory before tmpdir cleanup
        output_bytes = output_path.read_bytes()

    # Return from memory
    return StreamingResponse(
        io.BytesIO(output_bytes),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=document.{format}"},
    )
