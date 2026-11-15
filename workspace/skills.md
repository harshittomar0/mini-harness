# Skills Catalog

When the user's task matches a skill below, first load its instructions with
the read tool and follow them. **Only read the skill you need** so the context
stays small. Do not read skills that do not match the task.

## Skill pointers

| When the user asks to... | Read this skill (workspace-relative path) |
| --- | --- |
| write, add, or fix tests | `skills/write-tests/SKILL.md` |
| fix an error, traceback, crash, or wrong output | `skills/debug-error/SKILL.md` |
| review, audit, or check code quality | `skills/code-review/SKILL.md` |
| commit, save changes to git, or write a commit message | `skills/git-commit/SKILL.md` |

Load a skill with the read tool, for example:

```json
{"tool":"read","args":{"path":"skills/write-tests/SKILL.md"}}
```

## Rules that apply to every skill

1. Read the relevant source files before changing anything.
2. File-tool paths must be relative to the workspace folder. `bash` starts
   there but is not sandboxed; do not assume it is limited to the workspace.
3. `write`, `edit`, and `bash` need user approval, so keep each call focused
   and explain why you need it.
4. Prefer `edit` for small changes to existing files. Only use `write` for
   new files or full rewrites. The parent folder must already exist; create
   it with an approved `bash` call if needed.
5. If a task matches more than one skill (for example "fix this bug and add a
   test"), read the skills one at a time in the order you need them.
6. If no skill matches, do the task directly using the rules above.
7. Report failed or declined tool calls accurately. Do not claim a change,
   test run, or commit succeeded without checking the tool result.
