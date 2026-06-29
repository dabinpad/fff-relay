---
description: Orient a fresh session on the FFF relay app — read the docs, check git state, report status
allowed-tools: Bash(git branch:*), Bash(git status:*), Bash(git log:*)
---
Orient this session on the **FFF Don't Hide Legend Cup relay app** (`index.html`).

## Live state
!`git branch --show-current && git status --short && git log --oneline -8`

## Orient
1. Read **APP-DESIGN-SPEC.md** first — architecture, the design decisions in §4, the
   iteration log in §5, and the quick-reference in §8 (the "don't undo" invariants). Then
   skim **README.md**, **GAME-RULES.md**, and **TEAM-LINEUP.md** as the task needs.
2. The app is a single self-contained `index.html` (no dependencies). It publishes via
   **GitHub Pages from `main`**. Current cup: **2026-2027, 11 v 11, nil no-show** (4 pairs +
   1 trio per side).
3. Note the invariants you must not silently undo (APP-DESIGN-SPEC §4/§8): pace as the single
   source of truth for times; no-show keeps the runner visible; the lock semantics;
   result-first layout; **no header logo**; the **slim sticky score bar**; the **"Start blank"**
   default.

## Then
- If a task was given with this command, scope it to the relevant files and start on it.
- If not, report: current branch + working-tree state, what looks pending, and ask what I'd
  like to do.
- **Wait for my go-ahead before making changes.** Develop on the `claude/…` feature branch;
  don't push to `main` without it being the agreed publish step.

Task / focus (optional): $ARGUMENTS
