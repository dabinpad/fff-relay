---
description: Wrap up a session on the FFF relay app — what changed, verification, publish state
allowed-tools: Bash(git branch:*), Bash(git status:*), Bash(git log:*)
---
Wrap up this session on the **FFF relay app**. Produce a tight end-of-session report — a clean
handoff, not a transcript.

## Snapshot
!`git branch --show-current && git status --short && git log --oneline -8`

## Report
1. **What changed** — the files you edited this session, grouped (app · docs · commands),
   one line each on what and why. If nothing was written, say so plainly.
2. **Verification** — cite evidence, not "looks done": the Playwright run (any page errors?
   screenshots taken?), the Python solver cross-check, scores confirmed against expected. If
   you skipped verification, say that.
3. **Publish state** — be explicit about where the work is:
   - committed + pushed to the `claude/…` feature branch?
   - merged into `main` and pushed (→ live on GitHub Pages in ~1 min)?
   - or still uncommitted / pending?
4. **Docs in sync** — did the change warrant an **APP-DESIGN-SPEC** iteration-log entry, or a
   **TEAM-LINEUP** / **GAME-RULES** update? Confirm they're current, or flag what's stale.
5. **Pending / next** — anything proposed but not applied, or worth doing next session.

Then stop.
