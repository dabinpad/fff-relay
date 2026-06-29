# FFF Don't Hide Legend Cup — Team Lineup & Strategy

> Who's running, their estimated paces, and how we should line up. The ruleset is in
> **[GAME-RULES.md](GAME-RULES.md)**; the app that computes all of this is `index.html`
> (see **[APP-DESIGN-SPEC.md](APP-DESIGN-SPEC.md)**).

---

## 1. Rosters & paces (2026-2027)

Pace is **min:sec per km**; **5K time = pace × 5**. Seeded into `DEFAULTS` in `index.html`.
Team names are the generic **"Our team"** (Blue) / **"Opponent"** (Red). **More teammates
may be added later** — these are estimates for the next cup.

### Our team (Blue) — 11 runners

| Runner | Pace | Runner | Pace | Runner | Pace |
|---|---|---|---|---|---|
| TT | 4:05 | WL | 4:15 | Cai | 4:30 |
| CM | 4:45 | CP | 4:50 | 9J | 5:00 |
| LW | 5:45 | DB | 5:45 | SLK | 5:45 |
| Penny | 5:45 | Apoon | 6:00 | | |

### Opponent / Red team — 11 runners

| Runner | Pace | Runner | Pace | Runner | Pace |
|---|---|---|---|---|---|
| LC | 4:15 | SIN | 4:15 | Sandro | 4:15 |
| FL | 4:20 | KTY | 4:45 | LP | 5:12 |
| LS | 5:15 | Oyster | 5:20 | 5K | 5:25 |
| GoG | 5:45 | AK | 6:45 | | |

**Aggregate 5K** (sum of all 11): **Our 16,925 s vs Red 16,660 s** — Red's raw aggregate is
**~265 s faster**. With no no-show penalty it's close: if we can read Red's play our best
response wins on the board, but the naive "both teams just line up" baseline (the **Random**
scenario) is a one-point Red win, and race-day variance keeps it tight (§2).

---

## 2. Strategic analysis

Verified with an independent Python brute-force model (`solve_scenarios.py`): for each Red
play it searches all of our 4-pairs-+-1-trio partitions — C(11,3) × 105 = **17,325** — for
Blue's best response, and it builds the naive "Random" lineup for both sides.

### The strategic scenarios show our *ceiling* vs each Red play
Each strategic scenario loads **Red's play + our optimal counter to it**. On the deterministic
board our best response **wins all four** (points are out of 55 for 10 teams; **28+ wins** —
see [GAME-RULES §3](GAME-RULES.md#3-scoring)):

| Red plays | our best response | race-day win-chance (Blue) |
|---|---|---|
| Optimal (toughest) | **29.5 : 25.5** | ~57 % |
| Balanced | **30 : 25** | ~70 % |
| Stacks both aces | **29 : 26** | ~33 % |
| Spreads its aces | **30 : 25** | ~80 % |

**This is a ceiling, not a promise** — it assumes we can tailor our lineup to Red's, but in
reality both sides commit blind. The honest "nobody optimises" baseline is the **Random**
scenario.

### The Random (naive) baseline — a real toss-up
"Random" = both teams group by **similar pace**, burying the two slowest in a trio behind a
mid runner (Red `Oyster*+GoG+AK`, Blue `DB*+Penny+Apoon`). That lands **Blue 27 : 28 Red** — a
one-point Red win, race-day **~21 % Blue**. So with no strategy on either side, **Red is the
slight favourite**, driven by their ~265 s aggregate-speed edge.

### Reading it
- The **strategic scenarios** tell you *how to respond* if you read Red's intent — e.g. vs Red
  stacking both aces, our `(Cai*+LW+Apoon)` trio + `TT+WL` pair takes the top points.
- The **Random** scenario is the no-information baseline: close, slightly Red-favoured.
- **Race-day win-chance** (±10 s/km jitter) is the reality check — even a deterministic win can
  be a race-day underdog (Red *stacks*: 29 : 26 on the board, but only ~33 % to win on the day)
  because so many teams finish within seconds of each other.

### Lessons
- **Bury the slowest two in ONE trio** behind a faster Leg-1 runner — one weak team, not several.
- **Spread the fast runners** so they take separate top positions rather than over-stacking a pair.
- Our wins come from **out-placing Red in the middle** — keep every pair pushing to beat a Red team.

---

## 3. The scenarios (app presets)

The dropdown **defaults to "Start blank"** (everyone benched — build your own). Scenario 1 is
**Random** (both teams naive); scenarios 2–5 load a Red strategic play with **our optimised
counter**. `*` = the **Leg-1** runner of a trio.

| # | Scenario | Our lineup | Red lineup | Result (/55) |
|---|---|---|---|---|
| 1 | **Random** (both naive) | TT+WL · Cai+CM · CP+9J · LW+SLK · `(DB*+Penny+Apoon)` | LC+SIN · Sandro+FL · KTY+LP · LS+5K · `(Oyster*+GoG+AK)` | **27 : 28 — Red** |
| 2 | **Toughest — Red optimal** | `(Cai*+LW+Apoon)` · TT+WL · CM+DB · CP+SLK · 9J+Penny | `(KTY*+GoG+AK)` · LC+SIN · Sandro+FL · LP+LS · Oyster+5K | **29.5 : 25.5 — Blue** |
| 3 | **Red plays balanced** | `(LW*+DB+Apoon)` · TT+CM · WL+9J · Cai+CP · SLK+Penny | LC+LP · SIN+LS · Sandro+Oyster · FL+5K · `(KTY*+GoG+AK)` | **30 : 25 — Blue** |
| 4 | **Red stacks both aces** | `(Cai*+LW+Apoon)` · TT+WL · CM+DB · CP+9J · SLK+Penny | LC+SIN · Sandro+FL · KTY+LP · LS+Oyster · `(5K*+GoG+AK)` | **29 : 26 — Blue** |
| 5 | **Red spreads its aces** | `(LW*+DB+Apoon)` · TT+CM · WL+CP · Cai+9J · SLK+Penny | LC+GoG · SIN+5K · Sandro+Oyster · FL+LS · `(KTY*+LP+AK)` | **30 : 25 — Blue** |

Scenarios 2–5 are our **best case** against each Red play (we tailor to Red). The **Random**
baseline is closer to a real blind-commit matchup — a one-point Red win.

---

## 4. How these map into the app

- The rosters above are `DEFAULTS` in `index.html`; the scenarios are the `PRESETS` /
  `LINEUPS` tables. `ourRandom` / `redRandom` are the naive lineups; the `red*` entries are
  Red's strategic plays and the `ourVs*` entries are our best responses. A 3-name group is the
  trio; `lineupFromNames()` sets its **fastest** member on Leg 1 automatically.
- **Nil no-show this year**, so no preset marks an absent runner.
- Use **🔒 Lock Blue / Lock Red** beside the optimise buttons to pin one side, then cycle the
  scenarios to compare — or hit **Best Blue / Best Red lineup** to re-optimise against whatever
  is on the board.
