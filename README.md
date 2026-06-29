# FFF Don't Hide Legend Cup — Relay Lineup App

A single self-contained web app to **build relay lineups for two teams, rank the small
teams by finish time, score the meet, and instantly see who wins** — with a brute-force
optimiser, editable race-day times, team locks for comparing one lineup against many, and
a race-day Monte-Carlo win chance.

- **Live:** https://dabinfish.github.io/
- **The app:** [`index.html`](index.html) — one file, zero dependencies.

## Docs

| Doc | What it covers |
|---|---|
| **[GAME-RULES.md](GAME-RULES.md)** | The competition ruleset — format, timing formulas, scoring, penalties. The source of truth for how the meet works. |
| **[TEAM-LINEUP.md](TEAM-LINEUP.md)** | Current rosters & paces, the strategic analysis, and the scenario lineups (our one robust lineup vs each Red play). |
| **[APP-DESIGN-SPEC.md](APP-DESIGN-SPEC.md)** | How the app is built — architecture, features, design decisions, iteration log. **Read first for any code change.** |

## Current cup

**2026-2027 — 11 v 11, nil no-show.** Each side fields **4 pairs + 1 trio** (10 small
teams total). See [GAME-RULES](GAME-RULES.md) for the ruleset and [TEAM-LINEUP](TEAM-LINEUP.md)
for who's running and how we should line up.

## Session commands

Two project slash commands (in `.claude/commands/`) bookend a working session:

- **`/start`** — orient on the app: prints git state, points at the docs, and recaps the
  invariants not to undo. Optionally takes a task focus.
- **`/end`** — wrap up: what changed, verification evidence, publish state, and whether the
  docs are in sync.

## Publishing

The app is served by **GitHub Pages from `main`**. To publish a change:

1. Commit on the feature branch (`claude/…`).
2. Merge the feature branch into `main` and push.
3. Pages rebuilds in ~1 minute; the change is live at the link above.

## Verifying changes

Open `index.html` in any browser, or drive it headless with **Playwright** (Chromium under
`/opt/pw-browsers/…`, launched with `--no-sandbox`) for behaviour checks and screenshots.
Scoring is cross-checked against a small **Python brute-force model**. See
[APP-DESIGN-SPEC § Technical / working notes](APP-DESIGN-SPEC.md#6-technical--working-notes).
