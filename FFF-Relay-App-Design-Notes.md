# FFF Don't Hide Legend Cup — App Design Notes

> Working documentation for the relay lineup-tester web app.
> Purpose: let a future session (or another person) pick this up cold and understand
> **what the app does, why the numbers are what they are, and why each design choice was made.**

- **Live deliverable:** a single self-contained file committed as **`index.html`** (no external dependencies).
- **Hosting:** GitHub Pages, live at **`https://dabinfish.github.io/`**, deployed from the repo's **`main`** branch.
- **Repo / workflow:** git repo `dabinpad/fff-relay`. Development happens on branch
  **`claude/team-roster-optimization-qjmgrg`**; to publish, merge that branch into `main`
  and push (Pages rebuilds in ~1 min).
- **Primary use surface:** iPhone / Safari (mobile-first matters; desktop is the secondary view).

---

## 1. What this is

A standalone tool to **build relay lineups for two teams, rank all the small teams by finish time,
score the meet, and instantly see who wins** — with:
- a **brute-force optimizer** for each side's best response to the other's current setup,
- **no-show / penalty modelling** (dormant for the 2026-2027 cup — nil no-show — but kept for general use; see §2),
- **editable actual race times** (type the real splits on the day; paces back-solve),
- **per-team and whole-team locks** for comparing one fixed lineup against many opponent setups,
- a **race-day Monte-Carlo win probability**, and
- a **branded, screenshot-ready result block** to share the outcome with the team.

It exists to answer a strategic question (§4) interactively and to drive the lineup decision on race day.

---

## 2. The competition (domain rules — the source of truth)

Two main teams each split their runners into **small teams** that each run **2 × 5 km legs (10 km total)**.

**2026-2027 format: 11 v 11, no no-show.** Each side splits its **11 runners** into **4 pairs + 1 trio**
(= **5 small teams** per side):

- **Our Team (Blue):** 11 runners → **4 pairs + 1 trio**.
- **Opponent (Red):** 11 runners → **4 pairs + 1 trio**.

Total on the course: **10 small teams** (5 per side). **Assume nil no-show this year** — the no-show / cap
machinery still exists in the app (see §5) but **no scenario uses it**.

> Previous cup (archived in §8) was **13 v 13 with one Blue no-show (FF)** → 12 small teams. The engine is
> format-agnostic (it ranks whatever teams exist), so only the rosters and presets changed.

### Timing
- **Pair time** = sum of the two runners' 5K times. *Order-independent for scoring.*
- **Trio time** = `leg1_5K + (legA_5K + legB_5K) / 2`. The half-credit on two of the three runners is the
  key structural quirk. **Putting the fastest runner on leg 1 minimizes the trio time.**
- **Solo (no-show)** = one runner runs the full 10 km = `2 × 5K`.
- **10K-trio (no-show alt)** = the leg-1 runner runs the full 10 km and a teammate runs leg 2 only:
  `5K_runner + (latter-5K + partner_5K)/2`, where `latter-5K = 10K − 5K`. With 10K = 2×5K this reduces to
  `1.5·5K_runner + 0.5·5K_partner` — i.e. it "buries" the partner at half credit.

### Scoring
- All small teams are **ranked by time**; points by finishing position from the array
  **`[13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 0]`**. With **10 teams** this year only the first 10 slots are
  used (`13…3`), which **sum to 76** → a main team needs **39+ (more than 38) to win**.
  *(The 2,0 tail is harmless padding kept for robustness; the 13-v-13 cup used all 12 slots, summing to 78.)*
- **Tie on points → faster combined (aggregate) time wins.** Exact time tie → "Dead tie".
- **Ties on time** between small teams split the tied positions' points evenly → legitimate **half-points**
  (two teams tied for 2nd share `(11+10)/2 = 10.5`). Half-points are correct and intentional.

### No-show / DNF penalties (modelled in the app — **dormant in 2026-2027**, nil no-show assumed)
- **No-show (1 runner absent):** that small team's points are **capped at a maximum of 6** *and* take **−5**.
  The present teammate runs the full 10 km:
  - **Solo** — one present runner runs the 10 km alone (`2×5K`), or
  - **10K-trio** — the leg-1 runner runs 10 km and another *present* teammate is buried on leg 2.
- **The no-show runner stays visible** on that team as a non-running marker (see §5/§7) — the team is a
  no-show team the moment it carries an absent runner; the penalty applies automatically (no Optimise needed).
- **DNF / two no-shows:** team placed last (0 pts) plus an extra **−5**.

---

## 3. Rosters & paces (the actual data, seeded into the app)

Pace is **min:sec per km**; 5K time = pace × 5. Stored in `DEFAULTS` (index.html). Team names are the
generic **"Our team"** (Blue) / **"Opponent"** (Red) this year. **More TMs may be added later** — these are
estimates for the next cup.

**Our team (Blue) — 11 runners:**

| Runner | Pace | Runner | Pace | Runner | Pace |
|---|---|---|---|---|---|
| TT | 4:05 | WL | 4:15 | Cai | 4:30 |
| CM | 4:45 | CP | 4:50 | 9J | 5:00 |
| LW | 5:45 | DB | 5:45 | SLK | 5:45 |
| Penny | 5:45 | Apoon | 6:00 | | |

**Opponent (Red) — 11 runners:**

| Runner | Pace | Runner | Pace | Runner | Pace |
|---|---|---|---|---|---|
| LC | 4:15 | SIN | 4:15 | Sandro | 4:15 |
| FL | 4:20 | KTY | 4:45 | LP | 5:12 |
| LS | 5:15 | Oyster | 5:20 | 5K | 5:25 |
| GoG | 5:45 | AK | 6:45 | | |

> Aggregate 5K (sum of all 11): **Our 16,925 s vs Red 16,660 s** — Red's raw aggregate is **~265 s faster**.
> Despite that, our best response **wins every modelled Red lineup** this year (no no-show penalty to
> overcome — see §4).

The **default scenario is blank** (everyone benched, dropdown reads "— Start blank"); the four loaded
scenarios are our solver-optimal response to each Red archetype (§6).

---

## 4. The strategic analysis (the "why" behind everything)

The substance the app was built to explore. For 2026-2027 re-verified with an independent Python brute-force
model (`solve2026.py` — enumerates all of our 4-pairs+1-trio partitions, C(11,3)×105 = **17,325**, for each
Red lineup; plus a minimax loop for Red's toughest play).

### The core finding — it's a winnable fight this year
Red is still **slightly faster on raw aggregate** (Red 16,660 s vs our 16,925 s, ≈265 s). But **there is no
no-show penalty this year**, so we no longer spot Red a capped −5 team. With both sides at full strength our
**best response beats every realistic Red lineup**:

| Red plays | Our best response | Result |
|---|---|---|
| **balanced** (aces split, slows buried in trio) | trio `LW*+DB+Apoon` · TT+CM · WL+9J · Cai+CP · SLK+Penny | **41 : 35 (WIN)** |
| **spread aces** | trio `LW*+DB+Apoon` · TT+CM · WL+CP · Cai+9J · SLK+Penny | **41 : 35 (WIN)** |
| **stacks both aces** in one pair | trio `Cai*+LW+Apoon` · TT+WL · CM+DB · CP+9J · SLK+Penny | **39 : 37 (WIN)** |
| **optimal** (minimax-toughest) | trio `Cai*+LW+Apoon` · TT+WL · CM+DB · CP+SLK · 9J+Penny | **39.5 : 36.5 (WIN)** |

(`*` = the runner placed on leg 1 of the trio.) Even Red's **minimax-optimal** lineup — the toughest play we
could find by iterating Red's best response against ours — only narrows it to **39.5 : 36.5**: still our win.

### Why we win despite the slower aggregate
The win is **positional, not raw-speed**. Our two fast teams (e.g. `WL+TT` ≈ 41:40) take the top points,
and the **trio half-credit is our tool too**: we bury our three slowest (LW/DB/SLK/Penny/Apoon class) into
**one** trio so only that single team sits at the bottom, keeping the middle pairs competitive. Red's faster
total is spread such that they don't out-place us where it counts.

### The Monte-Carlo caveat (race-day variance is real)
On the **deterministic** board our best response wins every archetype. But the **race-day win-chance**
(±10 s/km jitter, §5) for the toughest case reads roughly **46% us / 54% Red** — because the point margin is
thin and Red's faster aggregate means small jitters can flip the close positional battles. **Read both
numbers:** we're favored on the expected-points board, but it's close enough that execution on the day
matters. This is the honest picture — not the lopsided structural loss of last year.

### Recurring lessons (carried over, still true)
- **Bury slows in ONE trio**, don't scatter them — one bottom team instead of several.
- **Spread your fast runners** so they take separate top positions rather than over-stacking one pair.
- **Put the fastest on leg 1 of the trio** (minimizes its time → it doesn't sink further than it must).
- Keep every middle pair **ahead of a Red team** — positions, not raw speed, decide it.

> These scenarios are baked into the app's **scenario presets** (§6), so the analysis is explorable. The
> default is **blank** so you build from scratch; pick a scenario to load a Red archetype + our best answer.

---

## 5. App architecture (how it works under the hood)

- **One file, zero dependencies.** No external scripts/fonts/CDN. Native Apple system fonts. The cup logo
  (an interlocking "4-F" emblem) is embedded once as a **base64 PNG** in the header `<img class="logo">`.
  The page header (logo + **"FFF Don't Hide Legend Cup 2026-2027"**, **left-aligned** — the year wraps under
  "FFF" on narrow phones) doubles as the branding above the result, so a top-down screencap is
  self-contained. *(The earlier separate "result header" and the scroll **sticky score bar** were both
  removed — see §7/§8.)*
- **Single source of truth for speed = the effective 5K.** Each runner has a `pace` (mm:ss/km) and an
  optional exact override `actSec` (a 5K time in seconds). `resolve()` exposes an *effective pace*
  `p = actSec/5` when an override is set, else `paceToSec(pace)`, so every `fiveK(p)` stays exact. Editing a
  pace clears the override; entering a 5K sets it (and writes the derived pace back). `parseTimeInput()`
  normalises shorthand (`415`→4:15, `2115`→21:15, `4`→4:00) on every time field.
- **No-show model (members-driven).** A team is a no-show team if it carries the `noshow` flag **or any
  member has `ns:true`**. `teamTime()`/`teamLegs()` score it from the **present** runners only — the absent
  (ns) members are non-running *markers* that keep the no-show runner visible on the team. 1 present → solo
  (`2×5K`); ≥2 present → leg-1 runs 10 km + the rest buried (`1.5·r + 0.5·others`). Marking NS keeps the
  runner on a no-show team (`ensureNoShowTeam`), so the cap+penalty apply immediately; the optimiser
  re-attaches the ns runner to its capped team as a marker. *(2026-2027 presets carry no no-show, so
  `applyPreset` no longer calls `markNoShowTeams` — that path is exercised only by manual NS toggling.)*
- **Scoring engine (vanilla JS):** `teamTime()` computes pair/trio/solo/10k-trio times; `computeResults()`
  ranks **all small teams** (10 this year), applies the points table, splits ties (half-points), applies the no-show cap+penalty,
  and resolves the winner (points, then aggregate time, then "Dead tie"). When **every** runner's effective
  5K is 0 (`isBlankRecord`, after *Clear record*), the board renders a **blank scorecard** instead of ranking.
- **Optimizer (`optimize(side)`):** brute-forces the side's partitions (pairs + trio + the forced no-show
  team, trying **both** solo and 10K-trio for each no-show) to maximise points **against the other side's
  current lineup**. It honours per-team locks (keeps locked teams fixed) and is a **no-op when that side is
  whole-team-locked**. Uses the effective 5K, so manually-entered actual times feed the optimiser.
- **Win probability (`winProbBoard` / `simWin`):** seeded Monte-Carlo (mulberry32-style RNG so the % is
  stable, not flickering), 2000 races, each leg jittered with σ≈50 s (≈±10 s/km). Deferred via `setTimeout`
  with a token so fast edits stay snappy.
- **State model:** `state[side] = { name, runners[], teams[] }`. A runner is
  `{id, name, pace, actSec, ns}`. A small team is `{id, memberIds[], leg1Id, dnf, noshow, lock}`
  (plus a transient `_ulock` used by the master-lock snapshot/restore).

### Key engine facts to remember
- The optimizer is a **best response to the other side's currently-displayed lineup**, not a joint
  equilibrium. Clicking both buttons in sequence oscillates **by design**.
- `tenKsec` was removed; 10 km is always `2 × 5K` (a per-runner 10K override field was added then deleted —
  the editable team times capture real fatigue more directly now).

---

## 6. Feature set (current)

- **Editable rosters** (Runner / **Pace** / **5K** / **NS** checkbox). Pace **and** 5K are editable and
  **bidirectional** (enter a pace → 5K fills in; enter a 5K → pace fills in). Tick **NS** to mark a runner absent.
- **Smart time entry** on every time field — type digits + Enter: `415`→4:15, `2115`→21:15, `4`→4:00.
- **Card-based lineup builder:** pairs / trio (leg-1 selector) / solo / 10K-trio; **DNF** toggle; **per-team
  lock**; an editable **team total time** and editable **per-runner leg times**.
- **Editable actual times** (single source of truth = pace):
  - Edit a **team total** → splits **proportionally** across its runners.
  - Edit a **runner's leg** → holds the team total and **rebalances the partner(s)**; the runner's pace
    updates to match. Roster, board, and win% all recompute live.
- **No-show handling:** tick **NS** in the roster — the runner **stays visible** on a no-show team (a dashed
  `NO-SHOW` marker chip), the team auto-becomes capped (`−5`, max 6) with a present teammate on the 10 km, and
  the penalty applies **immediately**. **Optimise** still finds the lowest-cost sacrifice (solo vs 10K-trio).
- **Locks (two levels):**
  - **Per-team lock** (on a card) — the optimiser keeps that exact team fixed; its runners can't be
    added/removed (times stay editable). Use it to pin a chosen 10 km runner before optimising.
  - **🔒 Lock Blue / 🔒 Lock Red** (by the scenario picker) — pins the whole side: switching scenarios only
    rewrites the *other* team, its Optimise button is disabled, every small-team lock is auto-checked, and
    its composition is frozen (add/remove/clear hidden; NS/delete of a locked-in runner blocked). Restores
    individual locks when released. **This is the "compare my lineup vs each opponent combo" tool.**
- **Live finish board:** all small teams ranked (10 this year), with position, colored medal, time, trio/no-show/DNF flag, and
  net points (no-show rows show their net −x, not the capped raw). When the record is blank (after *Clear
  record*) it becomes a **scorecard** — teams in lineup order with dashes for rank/time/points and no winner.
- **Top scoreboard:** big points per team + "combined H:MM:SS" subline + a verdict pill.
- **Race-day win-chance row** *below the finish board* (colour-coded pills; hidden when blank/no matchup) — so
  it's outside a clean result screencap.
- **Result screencap** = the **left-aligned** page header (logo + "FFF Don't Hide Legend Cup **2026-2027**") →
  scoreboard → finish board, all stacked at the top. The controls sit **below** the board so they're out of frame.
  *(There is no longer a scroll sticky score bar — removed this cup.)*
- **Clear record** (in the controls card) — after a confirm, zeroes every pace/5K (keeps the lineups) to
  enter the real race times; the board falls back to the blank scorecard. Pick a scenario to restore defaults.
- **Scenario presets (dropdown):**
  1. **— Start blank (everyone benched)** ← **default**: rosters loaded but **no teams**, board empty,
     you build from scratch.
  2. *Red plays balanced — our best shot (41 : 35)*
  3. *Red spreads its aces (41 : 35)*
  4. *Red stacks both aces in one pair (39 : 37)*
  5. *Toughest — Red's optimal lineup (39.5 : 36.5)*

  Presets 2–5 each load **Red's archetype + our solver-optimal response** (§4). **Nil no-show this year**, so
  no preset marks an absent runner.
- **One compact controls card** (below the finish board, above the rules) wraps **both** the scenario row
  (picker + **Clear record**) **and** the **Auto-optimize** panel (two best-lineup buttons + the two
  whole-team locks), separated by a hairline — laid out **blue-left / red-right** to mirror the scoreboard.
  Concise **"?" help popovers** replace the old inline hints (scenario, optimise/lock, §1, §2).

---

## 7. Key design decisions & rationale

Choices that should *not* be silently undone.

### Lock semantics
- A locked team's **composition is immutable** (no add/remove of runners, no team delete); **times stay
  editable**. The guard is enforced both in render (controls hidden) and in every handler (member-remove,
  del-team, clear, add, bench-add, **NS toggle**, **roster delete**).
- The **whole-team lock is the master switch**: ON locks all small teams (checked + disabled) and pins the
  side across scenario switches *and* disables its optimise; OFF restores each team's prior individual lock
  via a `_ulock` snapshot (don't replace this with a blind "set all = checkbox" — that clobbers individual
  locks and, if keyed off the wrong field, breaks the delete-protection).

### Editable times = pace as single source of truth
- Times are paces in different units; an exact `actSec` override keeps team totals exact while the roster
  pace shows a clean rounded value. Team-total edits scale **proportionally**; runner edits **hold the
  team total** and rebalance partners (confirmed with the user: "proportional" + "total stays fixed").
- **Pace ↔ 5K are bidirectional in the roster**, and **smart shorthand** (`parseTimeInput`) applies on every
  time field — a power-user nicety for entering race-day splits fast.

### No-show keeps the runner visible (confirmed with the user)
- Marking NS must **not** silently bench the runner or rely on Optimise to apply the penalty (that was the
  reported bug). Instead the no-show runner **stays on a no-show team as a marker** and the cap+penalty apply
  automatically. The score is unchanged because **ns members never contribute time** (`teamTime` scores from
  present runners only) — `SLK + FF` computes exactly as SLK solo. Don't revert to "benching the no-show".

### Clear record + blank scorecard (confirmed with the user)
- **Clear record** (a confirm-gated reset) zeroes paces/5Ks but **keeps the lineups**, for typing in real
  results. With everything at 0 the board is a **blank scorecard** (teams in lineup order, dashes for
  rank/time/points, no winner) rather than a broken all-tied ranking. Re-pick a scenario to restore defaults.

### Win probability placement
- Win% was first inline next to the big score (looked cramped), then moved to its **own labelled row**
  ("RACE-DAY WIN CHANCE · x% vs y%") below the scoreboard. Keep it out of the big-number cards.

### Shareable result (layout)
- The **result comes first**: page header (logo + title, **left-aligned** — the "2026-2027" year wraps under
  "FFF" on narrow phones) → scoreboard → finish board. The **controls block sits below the board**, and the
  once-separate "result header" was **removed** as a duplicate — the page header now does that job, so a
  top-down screencap is the shareable result.
- The **win-chance row sits below the board** so it's outside that screencap.

### Controls layout (one card) & the removed sticky bar
- The scenario row **and** the Lock/Optimise grid live in **one compact `.controls` card** (light purple
  gradient, hairline divider between the two halves) — the user asked for "a single session". Lock + Optimise
  are laid out **blue-left / red-right** to match the scoreboard's two cards.
- Team-lock chips read **"🔒 Lock Blue" / "🔒 Lock Red"** (short, not the full team name).
- **The scroll sticky score bar was removed** at the user's request ("I don't need the hanging effect now").
  All `.stickybar`/`.sb*` markup + CSS, the `renderResults` sb-update block, the `sb-logo` init copy, the
  IntersectionObserver, and `stickyName()` were deleted. **Don't reintroduce it** without being asked.

### Leg ordering within a pair (realism)
- Slower runner leads off leg 1, faster runner runs leg 2 ("does the chasing") — cosmetic only (pair time is
  the sum), normalized via `legSorted()` across optimizer/presets/manual and both render paths. **Trios keep
  the fastest on leg 1** (minimizes trio time).

### Times vs points formatting
- **Displayed times round to whole seconds** (`fmtTime`/`fmtTotal`); underlying values stay exact so
  rankings/tiebreaks are unaffected. **Half-points in the score column are intentional** (legitimate
  tie-splits).

### Colour & identity
- Blue `--our:#2563EB` / `--our-d:#1B45C4`; Red `--opp:#D11A35` / `--opp-d:#A8142A`; brand purple
  `#7030A0/#5A2483`; gold `#DE9B17`. Logo is the interlocking 4-F emblem (gray + brand purple), restored
  after a failed "stacked literal F's" attempt — keep the real emblem.
- **1st-place badge** stays gold but the number is team-coloured and ringed so tied 1st-place slots are
  identifiable.

### Mobile-specific (iOS is primary)
- **Header is left-aligned** on phone (`.brand{justify-content:flex-start;text-align:left}`); the "2026-2027"
  year wraps onto its own line under "FFF" rather than centering. *(Reverted an earlier mobile-centering pass
  at the user's request.)*
- Score cards **stack vertically** on phone (a wide 4-char score like 52.5 overflowed side-by-side).
- The scenario **label is on its own line**; the **dropdown + "Clear record" share the next line** (select uses
  `flex:1 1 0` so it shrinks instead of hogging the row).
- Team controls keep blue-left/red-right via grid-areas; the optimize label + note drop below.
- Finish board uses the colored medal + fixed-width columns; DNF checkbox sits inline; the desktop "VS"
  column is hidden. Inputs ≥16px to stop iOS auto-zoom.

---

## 8. Iteration log

### Phase A — original deterministic build (earlier sessions)
1. Round times to whole seconds (".5" only in the points column, as tie-splits).
2. Rename to "FFF Don't Hide Legend Cup" (title + file).
3. De-duplicate the score display; combined times into the scoreboard.
4. Pair leg order = faster runner on leg 2 (via `legSorted`); trios keep fastest on leg 1.
5. Mobile finish-board pass (colored medal, aligned columns, removed "PAIR", inline DNF, hid VS block).
6. Consistency pass (uppercase roster name; finish-board points in display font + team colour).
7. Stacked mobile score cards; gold 1st badge with team-coloured number + ring.

### Phase B — no-show, optimisation & this session's overhaul
8. **No-show modelling:** runner-level **NS** checkbox; the optimiser fields one capped no-show team per NS,
   trying **solo vs 10K-trio** and keeping the better; finish board shows **net** points for capped/DNF rows.
9. **Per-runner 10K override** added, then **removed** (superseded by editable actual times).
10. **Win probability** added (seeded Monte-Carlo); first shown inline, later moved to its own row.
11. **Presets revamped:** announced final lineup as the default; toughest Red spread next; FF no-show baked in.
12. **Team names** → "TT & SLK team" / "CM & SIN team"; Red runners **LWL→WL, CL→Cai**; SLK→5:45; FF added.
13. **Logo:** restored the real interlocking 4-F emblem; reused in the header, sticky bar, and result header.
14. **Whole-team lock** (Lock Blue / Lock Red): pin a side, switch scenarios to compare vs each opponent combo.
15. **Lock blocks Optimise**; **10K column removed**; **editable actual times** (team total proportional;
    runner edit holds total and rebalances; pace back-solves).
16. **Lock hardening (adversarial review):** locked teams can't lose runners via NS/roster-delete; master
    lock cascades to small locks and **restores** individual locks on release; no new teams while locked.
17. **Display polish:** controls blue-left/red-right; sticky bar (logo + bigger title + name-beside-score);
    **branded result header** for a clean shareable screencap; win% relocated to its own labelled row;
    mobile toolbar (dropdown + Reset on one line); short "Lock Blue / Lock Red" chips.
18. **Win% below the board**; **purple** checkered band over the finish board; sticky title forced to one
    line; concise **"?" help popovers** replace inline hints.

### Phase C — capture & race-day data entry
19. **Smart time entry** (`415`→4:15, `2115`→21:15, `4`→4:00) on all time fields; **roster 5K editable and
    bidirectional** with pace.
20. **No-show keeps the runner visible** on a no-show team with the penalty auto-applied (fixes the
    "no penalty after manual edit" bug); ns members are non-running markers; presets keep FF visible and the
    optimiser re-attaches it.
21. **Layout for clean screencaps:** moved the whole control block **below** the finish board; **removed the
    duplicate result header**; **centered the page header on mobile**.
22. **Clear record** (confirm-gated) zeroes all paces/5Ks (keeps lineups) → **blank scorecard** board.

### Phase D — 2026-2027 cup (new rosters, 11 v 11, no no-show)
23. **Header:** year **2026 → 2026-2027**; mobile header **re-aligned left** (year wraps under "FFF") —
    reverted the Phase C mobile-centering.
24. **One compact controls card:** merged the scenario row and the Lock/Optimise grid into a single
    `.controls` card with a hairline divider ("a single session").
25. **Team names back to generic:** "TT & SLK team" / "CM & SIN team" → **"Our team" / "Opponent"**.
26. **Sticky score bar removed** entirely (markup + CSS + JS observer + `stickyName()`) — "don't need the
    hanging effect now".
27. **Roster refresh → 2026-2027:** 11 v 11, **nil no-show**. New `DEFAULTS` (§3); `applyPreset` no longer
    marks no-shows; the blank "— Start blank" default loads rosters with **no teams** (everyone benched).
28. **New scenario presets** from a fresh brute-force solver (`solve2026.py`): blank default + four Red
    archetypes (balanced / spread / stacked / minimax-optimal), each paired with our solver-optimal response.
    All four are **our wins** (41:35, 41:35, 39:37, 39.5:36.5) — verified live in-browser against the solver.

---

## 9. Technical / working notes

- **No browser storage** (no localStorage/sessionStorage) — all state is in-memory JS.
- **Verification approach (current):** a headless browser **is** available this session — Chromium at
  `/opt/pw-browsers/chromium-*/chrome-linux/chrome`, driven via `playwright-core` (`--no-sandbox`). Used for
  behavioural tests (lock guards, master-lock state, editable-time math, optimiser) **and** for rendered
  screenshots (desktop + mobile). Python engine replicas (`solve.py` for the 13-v-13 cup, **`solve2026.py`**
  for the current 11-v-11 cup, both using `fractions`) and jsdom tests cross-check the scoring numbers — the
  2026-2027 presets were verified live in-browser to match `solve2026.py` exactly (41:35, 41:35, 39:37,
  39.5:36.5). An **adversarial multi-agent diff review** (4 lenses + verification) was run before finalising
  the lock/UI overhaul and caught 5 real defects (all fixed).
- **iOS gotcha:** Safari/Chrome on iPhone can't open local files directly; use the hosted Pages link.

---

## 10. Backlog & status

### Now implemented (previously deferred)
- **Win-probability mode** — built (seeded Monte-Carlo, ±10 s/km, own row under the scoreboard).
- **Multi-scenario comparison** — built via **Lock Blue/Red + scenario dropdown**: pin your lineup, cycle the
  opponent presets, read the score each time.

### Worth doing when next touched (small, low-risk)
1. **Completeness guard before optimizing.** The optimiser only checks the other side has *some* times, not a
   full 6-team field, so optimising against a half-built opponent silently returns a "best vs incomplete"
   lineup. Low effort; rarely bites because presets load full fields and a short field is visible on the board.
2. **Optimizer result wording** — the post-click note already frames it as "best vs the current setup"; keep
   that framing in the note, not as permanent subtext under the buttons.

### Features, not fixes (skip unless wanted)
3. **One-click equilibrium / minimax.** Alternating best-responses oscillate by design; the strategic answer
   is the robust framing in §4, not a solver.
4. **Save/share a result image** (beyond the manual screencap) — e.g. render-to-canvas export of the result
   block. The result-first layout (centered header → scores → board) already makes manual screenshots clean.

---

## 11. Quick reference for a fresh session

- **Open `index.html`** to see the current state; the default scenario is **blank** (rosters loaded,
  everyone benched, board empty — you build from scratch). Pick a scenario to load a Red archetype + our
  best response.
- **Current cup = 2026-2027, 11 v 11, nil no-show.** Each side = 4 pairs + 1 trio (10 small teams; first 10
  point slots `13…3` sum to 76 → 39+ wins). Team names "Our team" / "Opponent".
- **Strategic bottom line:** Red is ~265 s faster on raw aggregate, but with **no no-show penalty** our best
  response **wins every modelled Red lineup** (41:35 down to 39.5:36.5 in the toughest case). The win is
  **positional**: take the top points with two fast pairs, bury our slows in **one** trio. Race-day win-%
  is close (~46/54 in the toughest case) because the point margin is thin — execution matters.
- **Don't undo:** whole-second time rounding; intentional half-points; faster-runner-on-leg-2; the real 4-F
  emblem logo; **pace as the single source of truth** for editable times (5K↔pace bidirectional; smart
  shorthand); **no-show keeps the runner visible** when used (ns members are non-running markers; penalty
  auto-applies — don't go back to benching), even though no 2026-2027 preset uses it; the **lock invariants**
  (locked = composition frozen, times editable; master lock cascades + restores via `_ulock`); the
  result-first layout (left-aligned header → scores → board, controls below, win% below the board);
  **Clear record** + blank scorecard; the **one-card controls** (blue-left/red-right); **no sticky bar**
  (removed — don't reintroduce); the **blank "— Start blank" default**.
- **Not a bug:** the optimizer is a **best-response vs the other side's current lineup**; clicking both
  buttons oscillates by design (§5/§10).
- **To publish:** merge `claude/team-roster-optimization-qjmgrg` into `main` and push; Pages serves
  `index.html` at `https://dabinfish.github.io/`.
- **Verify changes** with `playwright-core` against the local file (chromium at `/opt/pw-browsers/…`) for both
  behaviour and screenshots; cross-check scoring with `solve.py` / jsdom.
