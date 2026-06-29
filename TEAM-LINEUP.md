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
**~265 s faster**. With no no-show penalty this year it's a close fight, but committing a
single lineup (which is what really happens — we can't see Red first) leaves us a **slight
underdog** to Red's strongest plays — see §2.

---

## 2. Strategic analysis: one committed lineup, a close fight

Verified with an independent Python brute-force model (`solve_robust.py`): it enumerates all
of our 4-pairs-+-1-trio partitions — C(11,3) × 105 = **17,325** — and, for each, scores it
against the four Red plays, then picks the **minimax** lineup (the one with the best
worst-case margin).

### Why minimax, not per-Red best response
Lineups are committed **before** seeing the opponent — we can't tailor a fresh counter to
each Red play. So the right question isn't "what beats Red's balanced lineup?" but **"what
single lineup holds up best across everything Red might do?"** That's a minimax: maximise our
**worst-case** result over the plausible Red plays.

### The core finding — no lineup sweeps all four
Red is **~265 s faster on raw aggregate** (16,660 vs 16,925 s). With one committed lineup,
**no Blue partition beats all four Red plays.** The most robust one we can field is:

> **Our robust lineup:** `(LW*+DB+Apoon)trio · TT+WL · Cai+9J · CM+CP · SLK+Penny`
> (`*` = the runner on Leg 1 of the trio)

It **loses by 2** to Red's two strongest plays (optimal & balanced, **37 : 39**) and **wins**
the two weaker ones (stacks **39 : 37**, spread **40 : 36**). Worst case is a 2-point loss —
better than any other single lineup. So: a genuine coin-flip-ish contest, tilted slightly to
Red because of their aggregate-speed edge.

### Why it's still close (positional play)
Our two fast pairs (`WL+TT`, etc.) grab top points and the **trio half-credit is our tool
too** — we bury our three slowest into **one** trio so only that team sits at the bottom.
Against Red's spread/stacked plays that's enough to win; against Red's optimal/balanced
plays Red just out-places us by one slot. The **race-day win-chance** (±10 s/km jitter) for
the toughest case reads ≈ **46 % us / 54 % Red** — consistent with a slight underdog.

### Lessons / how to tilt it our way
- **Bury slows in ONE trio**, don't scatter them — one bottom team instead of several.
- **Spread your fast runners** so they take separate top positions rather than over-stacking.
- **Fastest on Leg 1 of the trio** (minimises its time → it doesn't sink further than it must).
- Our edge appears when **Red mis-plays** (spreads its aces, or stacks both in one pair). If
  Red plays optimally/balanced we need **execution + race-day luck** — keep every middle pair
  pushing to out-place a Red team.

---

## 3. The scenarios (app presets)

The dropdown **defaults to "Start blank"** (everyone benched — build your own). The four
loaded scenarios all field the **same robust Blue lineup** (§2) against a **different Red
play** — so you can see how our one committed lineup holds up. The toughest is listed first.
`*` marks the runner on **Leg 1** of a trio.

> **Our lineup (same in every scenario):**
> `(LW*+DB+Apoon)trio · TT+WL · Cai+9J · CM+CP · SLK+Penny`

| # | Scenario (Red's play) | Red lineup | Result |
|---|---|---|---|
| 1 | **Toughest — Red optimal** | `(KTY*+GoG+AK)` · LC+SIN · Sandro+FL · LP+LS · Oyster+5K | **37 : 39 — Red** |
| 2 | **Red plays balanced** | LC+LP · SIN+LS · Sandro+Oyster · FL+5K · `(KTY*+GoG+AK)` | **37 : 39 — Red** |
| 3 | **Red stacks both aces** | LC+SIN · Sandro+FL · KTY+LP · LS+Oyster · `(5K*+GoG+AK)` | **39 : 37 — Blue** |
| 4 | **Red spreads its aces** | LC+GoG · SIN+5K · Sandro+Oyster · FL+LS · `(KTY*+LP+AK)` | **40 : 36 — Blue** |

So with the robust lineup we **split 2–2**: narrow 2-point losses to Red's two best plays,
clear wins when Red mis-plays. That worst case (−2) is the best any single Blue lineup can
guarantee across these four.

> **Caveat (deeper game theory):** if Red could *see* our committed lineup, its unconstrained
> best response beats it ~41 : 35. But Red commits blind too, so the four named plays above
> are the realistic set. There's no pure "solution" lineup — the full game needs mixed
> strategies (the per-side best-responses oscillate), which is out of scope for the app.

---

## 4. How these map into the app

- The rosters above are `DEFAULTS` in `index.html`; the scenarios are the `PRESETS` /
  `LINEUPS` tables. `ourRobust` is the single Blue lineup used by every scenario; the four
  `red*` entries are Red's plays. A 3-name group is the trio; `lineupFromNames()` sets its
  **fastest** member on Leg 1 automatically.
- **Nil no-show this year**, so no preset marks an absent runner.
- Because Blue is identical across scenarios, you can just **cycle the dropdown** to watch our
  committed lineup play each Red setup. Or **🔒 Lock Blue**, then run **Best Red lineup** /
  cycle scenarios, to probe how Red might exploit us.
