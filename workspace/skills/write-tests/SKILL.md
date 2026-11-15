---
name: write-tests
description: Write and run pytest tests for Python code in the workspace.
---

# Write Tests

Add focused tests for the requested behavior and verify their results.

## Conventions

- Follow the project's existing test runner and conventions. If it has
  none, use `pytest` and put tests in `tests/test_<module>.py`.
- Name each test after the behaviour it checks, for example
  `test_done_marks_the_numbered_task`.
- Cover the relevant normal case, edge cases (empty list, first/last item,
  empty input), and error paths for the requested behavior.
- One behaviour per test. Avoid tests that only repeat the implementation.

## Testing command-line scripts

For CLI scripts such as `todo.py`, run them as a subprocess. When using pytest,
use its
`tmp_path` as the working directory so tests never touch the real
`todos.json`:

```python
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "todo.py"


def run(tmp_path, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


def test_add_then_list_shows_task(tmp_path):
    run(tmp_path, "add", "buy milk")
    result = run(tmp_path, "list")
    assert result.returncode == 0, result.stderr
    assert "1. [ ] buy milk" in result.stdout


def test_done_marks_the_numbered_task(tmp_path):
    run(tmp_path, "add", "first")
    run(tmp_path, "add", "second")
    result = run(tmp_path, "done", "1")
    assert result.returncode == 0, result.stderr
    result = run(tmp_path, "list")
    assert result.returncode == 0, result.stderr
    assert "1. [x] first" in result.stdout
    assert "2. [ ] second" in result.stdout
```

## Steps

1. Read the module you are testing and any existing tests or test configuration
   with `read`.
2. Use `edit` to update existing tests or `write` to create a new test file.
   If `tests/` is missing, create it with an approved `bash` call first.
3. Run the relevant tests with `bash`, for example
   `python -m pytest -q tests/test_todo.py` or
   `python -m unittest discover -s tests`. If pytest is needed but missing,
   ask the user before running `python -m pip install pytest`.
4. If a test fails, decide whether the test or the code is wrong. Do not
   change a correct test just to make it pass. If the code is wrong, follow
   load `skills/debug-error/SKILL.md` with `read` before fixing it.

## Output

Summarize the behavior covered and the test command with its result.
Report failing tests or blocked verification explicitly.

## Guardrails

- Keep test data isolated from real workspace data.
- Do not change a correct test just to make it pass.
- Do not claim tests passed unless the test command succeeded.
