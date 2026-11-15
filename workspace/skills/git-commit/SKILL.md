---
name: git-commit
description: Stage and commit changes with a Conventional Commits message.
---

# Git Commit

Stage and commit only the changes the user requested.

## Steps

1. Run `git status --short`. If the folder is not a git repository, ask the
   user before running `git init`.
2. Run `git --no-pager diff` and `git --no-pager diff --cached` with `bash`
   to inspect unstaged and staged changes. Read any untracked files you
   intend to include. Preserve unrelated changes, including staged ones.
3. Check for secrets (API keys, `.env` files, tokens). Never commit them.
   Warn the user if any are found.
4. Stage files by name, for example `git add todo.py tests/`. Avoid
   `git add .`. Do not commit generated data such as `todos.json`.
5. Inspect `git --no-pager diff --cached` again to confirm only intended
   changes are staged. If unrelated changes are staged, ask the user how to
   proceed; do not unstage or commit them without permission.
6. Commit with a Conventional Commits message, for example
   `git commit -m "fix(todo): use 1-based numbers in done command"`.
7. Check `git status --short` and `git --no-pager log -1 --oneline` to
   verify the commit and report any remaining changes.

## Message format

```
<type>(<scope>): <short summary in the imperative mood>
```

Keep the entire subject line at most 72 characters.

Types: `feat` (new feature), `fix` (bug fix), `test`, `docs`, `refactor`,
and `chore`.

Examples:

- `feat(todo): add remove command`
- `test(todo): cover marking a task as done`

## Output

Report the commit hash, subject, and any remaining changes. If no commit was
created, say why.

## Guardrails

- Never run `git push`, `git reset --hard`, or `git commit --amend` unless
  the user explicitly asks.
- Do not discard changes or bypass failed hooks to force a commit.
