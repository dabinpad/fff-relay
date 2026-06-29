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
**~265 s faster**. Despite that, our best response **wins every modelled Red lineup** this
year (no no-show penalty to overcome — see below).

---

## 2. Strategic analysis — a winnable fight this year

Re-verified with an independent Python brute-force model (enumerates all of our
4-pairs-+-1-trio partitions — C(11,3) × 105 = **17,325** — against each Red lineup, plus a
minimax loop for Red's toughest play).

### The core finding
Red is still **slightly faster on raw aggregate** (Red 16,660 s vs our 16,925 s, ≈265 s).
But **there is no no-show penalty this year**, so we no longer spot Red a capped −5 team.
With both sides at full strength, our best response **beats every realistic Red lineup**
(see the scenario table in §3).

### Why we win despite the slower aggregate
The win is **positional, not raw-speed**. Our two fast teams (e.g. `WL + TT` ≈ 41:40) take
the top points, and the **trio half-credit is our tool too**: we bury our three slowest
into **one** trio so only that single team sits at the bottom, keeping the middle pairs
competitive. Red's faster total is spread such that they don't out-place us where it counts.

### The Monte-Carlo caveat (race-day variance is real)
On the **deterministic** board our best response wins every archetype. But the **race-day
win-chance** (±10 s/km jitter) for the toughest case reads roughly **46% us / 54% Red** —
because the point margin is thin and Red's faster aggregate means small jitters can flip the
close positional battles. **Read both numbers:** we're favoured on the expected-points
board, but it's close enough that execution on the day matters. This is the honest picture —
not a structural loss.

### Lessons
- **Bury slows in ONE trio**, don't scatter them — one bottom team instead of several.
- **Spread your fast runners** so they take separate top positions rather than over-stacking
  one pair.
- **Put the fastest on Leg 1 of the trio** (minimises its time → it doesn't sink further
  than it must).
- Keep every middle pair **ahead of a Red team** — positions, not raw speed, decide it.

---

## 3. The scenarios (app presets)

The app's scenario dropdown **defaults to blank** (everyone benched — you build from
scratch). Four loaded scenarios each pair a **Red archetype** with **our solver-optimal
response**. `*` marks the runner placed on **Leg 1** of a trio.

| Red plays | Our best response | Result |
|---|---|---|
| **Balanced** (aces split, slows buried in trio) | `(LW*+DB+Apoon)` · TT+CM · WL+9J · Cai+CP · SLK+Penny | **41 : 35 — win** |
| **Spread aces** | `(LW*+DB+Apoon)` · TT+CM · WL+CP · Cai+9J · SLK+Penny | **41 : 35 — win** |
| **Stacks both aces** in one pair | `(Cai*+LW+Apoon)` · TT+WL · CM+DB · CP+9J · SLK+Penny | **39 : 37 — win** |
| **Optimal** (minimax-toughest) | `(Cai*+LW+Apoon)` · TT+WL · CM+DB · CP+SLK · 9J+Penny | **39.5 : 36.5 — win** |

The corresponding **Red** lineups loaded by each scenario:

| Scenario | Red lineup |
|---|---|
| Balanced | LC+LP · SIN+LS · Sandro+Oyster · FL+5K · `(KTY*+GoG+AK)` |
| Spread aces | LC+GoG · SIN+5K · Sandro+Oyster · FL+LS · `(KTY*+LP+AK)` |
| Stacked | LC+SIN · Sandro+FL · KTY+LP · LS+Oyster · `(5K*+GoG+AK)` |
| Optimal | `(KTY*+GoG+AK)` · LC+SIN · Sandro+FL · LP+LS · Oyster+5K |

Even Red's **minimax-optimal** lineup — the toughest play found by iterating Red's best
response against ours — only narrows it to **39.5 : 36.5**: still our win.

---

## 4. How these map into the app

- The rosters above are `DEFAULTS` in `index.html`; the scenarios are the `PRESETS` /
  `LINEUPS` tables. A 3-name group is the trio; `lineupFromNames()` automatically sets its
  **fastest** member on Leg 1.
- **Nil no-show this year**, so no preset marks an absent runner.
- Use **🔒 Lock Blue / Lock Red** beside the scenario picker to pin one side, then cycle the
  opponent scenarios to compare our score against each Red play.
