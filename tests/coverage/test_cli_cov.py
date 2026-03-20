"""Tests targeting mtd/cli.py coverage.

Covers: default output path derivation, serve command with and without uvicorn.
"""

from click.testing import CliRunner

from mtd.cli import cli

# ===========================================================================
# cli.py (line 37) -- default output path when -o not provided
# ===========================================================================


def test_cli_convert_default_output_path(tmp_path):
    """Without --output, the CLI derives the output path from the input (line 37)."""
    md_file = tmp_path / "myfile.md"
    md_file.write_text("# Title\n\nContent.\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["convert", str(md_file)])
    # Default output should be myfile.docx
    expected_output = tmp_path / "myfile.docx"
    assert result.exit_code == 0, f"CLI output: {result.output}"
    assert expected_output.exists()


# ===========================================================================
# cli.py (lines 109-122) -- serve command
# ===========================================================================


def test_cli_serve_no_uvicorn(monkeypatch):
    """When uvicorn is not installed, serve prints an error and exits 1 (lines 112-117)."""
    import builtins
    import sys

    # Remove uvicorn from sys.modules so the import inside serve fails
    uvicorn_backup = sys.modules.pop("uvicorn", None)

    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "uvicorn":
            raise ImportError("No module named 'uvicorn'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    runner = CliRunner()
    result = runner.invoke(cli, ["serve"])
    assert result.exit_code == 1
    assert "api" in result.output.lower() or "install" in result.output.lower()

    # Restore
    if uvicorn_backup is not None:
        sys.modules["uvicorn"] = uvicorn_backup


def test_cli_serve_messages_with_uvicorn(monkeypatch):
    """When uvicorn is available, serve prints startup messages (lines 119-122)."""
    import sys
    import types

    # Create a fake uvicorn module that has a run() function which does nothing
    fake_uvicorn = types.ModuleType("uvicorn")

    def fake_run(app, host, port):
        # Just return immediately without actually starting a server
        pass

    fake_uvicorn.run = fake_run

    sys.modules["uvicorn"] = fake_uvicorn

    runner = CliRunner()
    result = runner.invoke(cli, ["serve", "--host", "127.0.0.1", "--port", "9999"])

    del sys.modules["uvicorn"]

    # Should have printed startup messages
    assert "Starting" in result.output or "mtd API server" in result.output
    assert "127.0.0.1" in result.output
    assert "9999" in result.output
