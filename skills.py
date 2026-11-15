"""Loads the workspace's skills.md catalog for on-demand instructions."""

from pathlib import Path


def discover_skills(root):
    """Reads skills.md as plain Markdown; workspaces without it have no skills."""
    try:
        return (Path(root) / "skills.md").read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
