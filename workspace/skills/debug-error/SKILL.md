---
name: debug-error
description: Find and fix the cause of an error, traceback, or wrong output.
---

# Debug Error

Fix the cause, not the symptom.

## Steps

1. **Reproduce.** Run the failing command with `bash` and capture the output.
   If you cannot reproduce it, ask the user for the exact command and input.
2. **Inspect the failure.** For a traceback, read from the bottom up. The last
   line is the error; the last frame inside a workspace file usually shows
   where to look. For wrong output, compare the actual and expected results.
3. **Read the code** around that line with `read`. Read the callers too if
   the bad value came from somewhere else.
4. **State the cause** in one sentence before editing, for example: "`list` shows
   1-based numbers but `done` uses the number as a 0-based index, so it marks
   the wrong task."
5. **Make the smallest fix** with `edit`. Do not refactor unrelated code.
6. **Re-run the same command** to confirm the fix. Add or update a focused
   regression test when appropriate, loading `skills/write-tests/SKILL.md`
   with `read` first. Run the relevant tests using the project's test runner.

## Output

Summarize the cause, the fix, and the commands run with their results.
State explicitly if reproduction or verification was blocked.

## Guardrails

- Do not wrap the failing code in `try/except` just to hide the error.
- Do not change unrelated code or make several speculative fixes at once.
- Do not say the bug is fixed before you have re-run the command.
