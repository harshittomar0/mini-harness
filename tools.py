"""The harness tools: workspace files, bash, and web, served by mcp_server.py."""

import subprocess
from pathlib import Path

import web

WORKSPACE_ROOT = Path(__file__).resolve().parent / "workspace"


def workspace_path(path):
    if Path(path).is_absolute():
        raise ValueError("Use a path relative to the workspace folder")
    resolved = (WORKSPACE_ROOT / path).resolve()
    if not resolved.is_relative_to(WORKSPACE_ROOT):
        raise ValueError("File access is limited to the workspace folder")
    return resolved


def read(path):
    return {"content": workspace_path(path).read_text(encoding="utf-8")}


def write(path, content):
    file = workspace_path(path)
    file.write_text(content, encoding="utf-8")
    return {"written": str(file.relative_to(WORKSPACE_ROOT))}


def edit(path, old, new):
    file = workspace_path(path)
    content = file.read_text(encoding="utf-8")
    if not old or content.count(old) != 1:
        raise ValueError("old must match exactly once; include more context")
    file.write_text(content.replace(old, new, 1), encoding="utf-8")
    return {"edited": str(file.relative_to(WORKSPACE_ROOT))}


def bash(command):
    result = subprocess.run(
        ["bash", "-c", command],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


# Every tool: what it does, example args (all strings), whether it needs approval, and its function.
TOOLS = {
    "read": {
        "description": "Read a UTF-8 file relative to the workspace.",
        "args": {"path": "notes.txt"},
        "approval": False,
        "run": read,
    },
    "write": {
        "description": "Write a UTF-8 file relative to the workspace; requires approval.",
        "args": {"path": "notes.txt", "content": "Hello"},
        "approval": True,
        "run": write,
    },
    "edit": {
        "description": "Replace old text exactly once in a workspace file; requires approval.",
        "args": {"path": "notes.txt", "old": "Hello", "new": "Hi"},
        "approval": True,
        "run": edit,
    },
    "bash": {
        "description": "Run bash in the workspace with a 30-second timeout; NOT sandboxed; requires approval.",
        "args": {"command": "ls"},
        "approval": True,
        "run": bash,
    },
    "web_search": {
        "description": "Search the web for the top results as title, url, and snippet.",
        "args": {"query": "python pathlib docs"},
        "approval": False,
        "run": web.web_search,
    },
    "fetch_url": {
        "description": "Fetch a page's text (up to 8000 characters); use it to read a search result.",
        "args": {"url": "https://docs.python.org/3/library/pathlib.html"},
        "approval": False,
        "run": web.fetch_url,
    },
}

GUIDANCE = """All file paths must be relative to the workspace folder.
read, write, and edit cannot access files outside the workspace.
Bash starts in the workspace but is not sandboxed.
write, edit, and bash need user confirmation."""


def check_call(name, args):
    """Returns an error message if the tool call is invalid, otherwise None."""
    if not isinstance(name, str) or name not in TOOLS:
        return f"Unknown tool; use {', '.join(TOOLS)}"
    fields = TOOLS[name]["args"]
    if not isinstance(args, dict) or set(args) != set(fields):
        return f"{name} requires: {', '.join(sorted(fields))}"
    if not all(isinstance(value, str) for value in args.values()):
        return "All tool arguments must be strings"
    if "path" in args:
        try:
            workspace_path(args["path"])
        except ValueError as error:
            return str(error)
    return None


def approval_message(name, args):
    message = f"Approve {name}: {args}"
    if name == "bash":
        message += f"\nWorking directory: {WORKSPACE_ROOT}. Bash is NOT sandboxed."
    return message


def execute(name, args):
    """Runs an already checked and approved tool call; errors become {"error": ...}."""
    try:
        return TOOLS[name]["run"](**args)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        return {"error": str(error)}

