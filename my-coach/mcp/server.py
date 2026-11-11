"""MCP server (Module 5) — serve the interview guides to Claude Code as tools.

MCP (Model Context Protocol) is how an agent reaches data that lives outside the
code. This exposes the markdown guides in ../resources so Claude can pull the
right guidance on demand instead of you pasting it into a prompt.

Run it on its own (it waits silently for a client — that's correct):
    python mcp/server.py
"""
from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

# The guides live one level up, in resources/
RESOURCES = Path(__file__).resolve().parent.parent / "resources"

mcp = FastMCP("interview-guides")


@mcp.tool
def list_guides() -> list[str]:
    """List the available interview guide names, e.g. 'decomposition-guide'."""
    return sorted(path.stem for path in RESOURCES.glob("*.md"))


@mcp.tool
def get_guide(name: str) -> str:
    """Return the full markdown text of one guide, by name."""
    path = (RESOURCES / f"{name}.md").resolve()
    # Only plain guide names: reject anything that escapes resources/ (e.g. "../x").
    if path.parent != RESOURCES or not path.exists():
        raise ValueError(f"No guide named {name!r}. Call list_guides() to see the options.")
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
