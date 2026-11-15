---
name: code-review
description: Review code for bugs, security risks, and maintainability problems, and report findings by severity.
---

# Code Review

Review only. Do not edit files unless the user asks for fixes.

## Steps

1. Identify the files or changes the user wants reviewed.
2. Read them with `read`, along with the callers or tests needed to check
   their behavior. For a diff, use `git --no-pager diff` with `bash`.
3. Use the checklist below. Verify each finding against the actual code.
4. Report actionable findings using the output format below.

## Checklist (most important first)

1. **Correctness:** logic errors, off-by-one errors, unhandled edge cases
   (zero, empty input, `None`), and wrong operator or argument order.
2. **Security:** `eval`/`exec` on user input, shell commands built from user
   input, hard-coded secrets, and unchecked file paths.
3. **Error handling:** silent `except:` blocks and confusing error messages.
4. **Maintainability:** duplicated code, unclear names, and functions that do
   too many things.

Skip style nitpicks that a formatter would fix.

## Output

List the findings from most to least severe:

```
[HIGH] todo.py:37 - `done` uses the 1-based number from `list` as a 0-based index,
  so `done 1` marks the second task and `done <last>` raises IndexError.
  Fix: use `todos[number - 1]` and reject numbers outside 1..len(todos).
[MEDIUM] todo.py:36 - `done` with a missing or non-numeric argument crashes with a traceback.
  Fix: validate the argument and print the usage message.
[LOW] todo.py:27 - `add` with no text saves an empty task.
  Fix: print the usage message when the task is empty.
```

Finish with a one-line summary. If there are no real problems, say so; do
not invent findings.

## Guardrails

- The findings above are examples, not a review of the current code. Use
  the actual workspace-relative paths and line numbers in your report.
- Do not change files or fix findings without the user's request.
- Distinguish confirmed problems from assumptions or unverified risks.
