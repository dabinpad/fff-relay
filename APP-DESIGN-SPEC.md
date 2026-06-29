# FFF Don't Hide Legend Cup — App Design Spec

> How the app is built and **why each design choice was made** — so a future session (or
> another person) can pick it up cold. The competition **rules** live in
> **[GAME-RULES.md](GAME-RULES.md)**; the **rosters, paces, and lineup strategy** live in
> **[TEAM-LINEUP.md](TEAM-LINEUP.md)**. This doc is the one to **read first before any code
> change**.

---

## At a glance

- **Deliverable:** a single self-contained file, **`index.html`** — no external scripts,
  fonts, or CDN.
- **Hosting:** GitHub Pages, live at **https://dabinfish.github.io/**, served from the
  repo's **`main`** branch.
- **Workflow:** develop on a `claude/…` feature branch; to publish, **merge into `main` and
  push** (Pages rebuilds in ~1 min). See [README](README.md#publishing).
- **Primary use surface:** iPhone / Safari — **mobile-first** matters; desktop is secondary.

---

## 1. What this is

A standalone tool to **build relay lineups for two teams, rank all the small teams by finish
time, score the meet, and instantly see who wins** — with:

- a **brute-force optimizer** for each side's best response to the other's current setup,
- **no-show / penalty modelling** (dormant for 2026-2027 — nil no-show — but kept for
  general use; see [GAME-RULES §4](GAME-RULES.md#4-no-show--dnf-penalties)),
- **editable actual race times** (type the real splits on the day; paces back-solve),
- **per-team and whole-team locks** for comparing one fixed lineup against many opponents,
- a **race-day Monte-Carlo win probability**, and
- a **screenshot-ready result block** to share the outcome with the team.

It exists to drive the lineup decision on race day and to explore the strategic question
analysed in [TEAM-LINEUP §2](TEAM-LINEUP.md#2-strategic-analysis).

---

## 2. App architecture (how it works under the hood)

- **One file, zero dependencies.** No external scripts/fonts/CDN. Native Apple system fonts.
  The header is **plain title text** ("FFF Don't Hide Legend Cup 2026-2027", left-aligned;
  the year wraps under "FFF" on narrow phones) — **no logo image**. *(An embedded base64
  emblem existed earlier and was removed — see §4/§5.)* The page header doubles as the
  branding above the result, so a top-down screencap is self-contained. A **slim sticky score
  bar** (score · verdict · score) slides in on scroll — see §4.
- **Single source of truth for speed = the effective 5K.** Each runner has a `pace`
  (mm:ss/km) and an optional exact override `actSec` (a 5K time in seconds). `resolve()`
  exposes an *effective pace* `p = actSec/5` when an override is set, else
  `paceToSec(pace)`, so every `fiveK(p)` stays exact. Editing a pace clears the override;
  entering a 5K sets it (and writes the derived pace back). `parseTimeInput()` normalises
  shorthand (`415`→4:15, `2115`→21:15, `4`→4:00) on every time field.
- **No-show model (members-driven).** A team is a no-show team if it carries the `noshow`
  flag **or any member has `ns:true`**. `teamTime()`/`teamLegs()` score it from the
  **present** runners only — the absent (ns) members are non-running *markers* that keep the
  no-show runner visible on the team. 1 present → solo (`2×5K`); ≥2 present → leg-1 runs
  10 km + the rest buried (`1.5·r + 0.5·others`). Marking NS keeps the runner on a no-show
  team (`ensureNoShowTeam`), so the cap+penalty apply immediately. *(2026-2027 presets carry
  no no-show, so `applyPreset` no longer calls `markNoShowTeams`; that helper is currently
  uncalled and retained only in case presets carry no-shows again.)*
- **Scoring engine (vanilla JS):** `teamTime()` computes pair/trio/solo/10k-trio times;
  `computeResults()` ranks **all small teams** (10 this year), applies the points scheme,
  splits ties (half-points), applies the no-show cap+penalty, and resolves the winner
  (points, then aggregate time, then "dead tie"). When **every** runner's effective 5K is 0
  (`isBlankRecord`, after *Clear record*), the board renders a **blank scorecard** instead
  of ranking.
- **Points are derived, not stored.** `pointsFor(K)` returns the table for `K` sub-teams
  (`1st = K+1`, `last = 0`, middle = `K − position`); 10 teams → `11,9,8,…,2,0` (sum 55,
  28+ wins), 12 → `13,11,10,…,2,0`. `computeResults` / `simWin` / `scoreCapped` each call it
  with their own team count, so the scheme **auto-scales** if the rosters change. The points
  table in the rules drawer (`renderPoints`) shows the derived values **read-only** (the old
  per-cell editing was removed). *(`state.points` no longer exists.)*
- **Optimizer (`optimize(side)`):** brute-forces the side's partitions (pairs + trio, plus
  the forced no-show team when one exists — trying **both** solo and 10K-trio for each
  no-show) to maximise points **against the other side's current lineup**. It honours
  per-team locks (keeps locked teams fixed) and is a **no-op when that side is
  whole-team-locked**. Uses the effective 5K, so manually-entered actual times feed it.
- **Win probability (`winProbBoard` / `simWin`):** seeded Monte-Carlo (mulberry32-style RNG
  so the % is stable, not flickering), 2000 races, each leg jittered with σ≈50 s
  (≈±10 s/km). Deferred via `setTimeout` with a token so fast edits stay snappy.
- **State model:** `state[side] = { name, runners[], teams[] }`. A runner is
  `{id, name, pace, actSec, ns}`. A small team is `{id, memberIds[], leg1Id, dnf, noshow,
  lock}` (plus a transient `_ulock` used by the master-lock snapshot/restore).

### Key engine facts to remember
- The optimizer is a **best response to the other side's currently-displayed lineup**, not a
  joint equilibrium. Clicking both buttons in sequence oscillates **by design**.
- `tenKsec` was removed; 10 km is always `2 × 5K` (a per-runner 10K override field was added
  then deleted — the editable team times capture real fatigue more directly now).

---

## 3. Feature set (current)

- **Editable rosters** (Runner / **Pace** / **5K** / **NS** checkbox). Pace **and** 5K are
  editable and **bidirectional** (enter a pace → 5K fills in; enter a 5K → pace fills in).
  Tick **NS** to mark a runner absent.
- **Smart time entry** on every time field — type digits + Enter: `415`→4:15, `2115`→21:15,
  `4`→4:00.
- **Card-based lineup builder:** pairs / trio (leg-1 selector) / solo / 10K-trio; **DNF**
  toggle; **per-team lock**; an editable **team total time** and editable **per-runner leg
  times**.
- **Editable actual times** (single source of truth = pace):
  - Edit a **team total** → splits **proportionally** across its runners.
  - Edit a **runner's leg** → holds the team total and **rebalances the partner(s)**; the
    runner's pace updates to match. Roster, board, and win% all recompute live.
- **No-show handling:** tick **NS** in the roster — the runner **stays visible** on a
  no-show team (a dashed `NO-SHOW` marker chip), the team auto-becomes capped (`−5`, max 6)
  with a present teammate on the 10 km, and the penalty applies **immediately**. **Optimise**
  still finds the lowest-cost sacrifice (solo vs 10K-trio).
- **Locks (two levels):**
  - **Per-team lock** (on a card) — the optimiser keeps that exact team fixed; its runners
    can't be added/removed (times stay editable). Use it to pin a chosen 10 km runner before
    optimising.
  - **🔒 Blue / 🔒 Red** (the compact lock chips in the Auto-optimize row) — pins the whole
    side: switching scenarios only rewrites the *other* team, its Optimise button is disabled,
    every small-team lock is auto-checked, and its composition is frozen (add/remove/clear
    hidden; NS/delete of a locked-in runner blocked). Restores individual locks when released.
    **This is the "compare my lineup vs each opponent combo" tool.**
- **Live finish board:** all small teams ranked (10 this year), with position, coloured
  medal, time, trio/no-show/DNF flag, and net points (no-show rows show their net −x, not
  the capped raw). When the record is blank (after *Clear record*) it becomes a
  **scorecard** — teams in lineup order with dashes for rank/time/points and no winner.
- **Top scoreboard:** big points per team + "combined H:MM:SS" subline + a verdict pill.
- **Race-day win-chance row** *below the finish board* (colour-coded pills; hidden when
  blank/no matchup) — so it's outside a clean result screencap.
- **Result screencap** = the **left-aligned** page header (title only, no logo) →
  scoreboard → finish board, all stacked at the top. The controls sit **below** the board so
  they're out of frame.
- **Clear record** (in the controls card) — after a confirm, zeroes every pace/5K (keeps the
  lineups) to enter the real race times; the board falls back to the blank scorecard. Pick a
  scenario to restore defaults.
- **Scenario presets (dropdown):** default **"Start blank"**, then **Random** (both teams
  grouped by similar pace — the naive baseline) and four Red strategic plays each paired with
  **our optimised best response**. The actual lineups and scores live in
  **[TEAM-LINEUP §3](TEAM-LINEUP.md#3-the-scenarios-app-presets)**.
- **One compact controls card** (below the finish board, above the rules), stacked as four
  thin lines: (1) the centred **⚡ Auto-optimize** title, (2) a single row of **four**
  elements — `🔒 Blue · Best Blue lineup · Best Red lineup · 🔒 Red` (`.optrow` grid
  `auto 1fr 1fr auto`; the buttons take the slack and wrap to 2–3 lines on narrow phones),
  (3) the **Try a scenario** label, (4) the scenario picker + **Clear record**. Still
  **blue-left / red-right** to mirror the scoreboard; a hairline divides the optimise half
  from the scenario half. Concise **"?" help popovers** replace the old inline hints.
- **Slim sticky score bar** — a thin fixed header that slides down once the scoreboard
  scrolls out of view: **Blue score · verdict · Red score** ("Our team win" in blue /
  "Opponent win" in red / "Dead tie"). Mirrors the scoreboard live; hidden when the record is
  blank or no lineups are set.

---

## 4. Key design decisions & rationale

Choices that should *not* be silently undone.

### Lock semantics
- A locked team's **composition is immutable** (no add/remove of runners, no team delete);
  **times stay editable**. The guard is enforced both in render (controls hidden) and in
  every handler (member-remove, del-team, clear, add, bench-add, **NS toggle**, **roster
  delete**).
- The **whole-team lock is the master switch**: ON locks all small teams (checked +
  disabled) and pins the side across scenario switches *and* disables its optimise; OFF
  restores each team's prior individual lock via a `_ulock` snapshot (don't replace this with
  a blind "set all = checkbox" — that clobbers individual locks and, if keyed off the wrong
  field, breaks the delete-protection).

### Editable times = pace as single source of truth
- Times are paces in different units; an exact `actSec` override keeps team totals exact
  while the roster pace shows a clean rounded value. Team-total edits scale
  **proportionally**; runner edits **hold the team total** and rebalance partners (confirmed
  with the user: "proportional" + "total stays fixed").
- **Pace ↔ 5K are bidirectional in the roster**, and **smart shorthand** (`parseTimeInput`)
  applies on every time field — a power-user nicety for entering race-day splits fast.

### No-show keeps the runner visible (confirmed with the user)
- Marking NS must **not** silently bench the runner or rely on Optimise to apply the penalty
  (that was the reported bug). Instead the no-show runner **stays on a no-show team as a
  marker** and the cap+penalty apply automatically. The score is unchanged because **ns
  members never contribute time** (`teamTime` scores from present runners only) — `SLK + FF`
  computes exactly as SLK solo. Don't revert to "benching the no-show".

### Clear record + blank scorecard (confirmed with the user)
- **Clear record** (a confirm-gated reset) zeroes paces/5Ks but **keeps the lineups**, for
  typing in real results. With everything at 0 the board is a **blank scorecard** (teams in
  lineup order, dashes for rank/time/points, no winner) rather than a broken all-tied
  ranking. Re-pick a scenario to restore defaults.

### Win probability placement
- Win% was first inline next to the big score (looked cramped), then moved to its **own
  labelled row** ("RACE-DAY WIN CHANCE · x% vs y%") below the scoreboard. Keep it out of the
  big-number cards.

### Shareable result (layout)
- The **result comes first**: page header (title, left-aligned — the "2026-2027" year wraps
  under "FFF" on narrow phones) → scoreboard → finish board. The **controls block sits below
  the board**, and the once-separate "result header" was **removed** as a duplicate — the
  page header now does that job, so a top-down screencap is the shareable result.
- The **win-chance row sits below the board** so it's outside that screencap.

### Controls layout (one card) & the removed logo
- The Auto-optimise block **and** the scenario row live in **one compact `.controls` card**
  (light purple gradient, hairline divider between the two halves) — the user asked for "a
  single session". Four thin lines: title → the 4-up `.optrow` (lock · best-blue · best-red ·
  lock) → "Try a scenario" → picker + Clear record. Still **blue-left / red-right** to match
  the scoreboard's two cards.
- Team-lock chips are a narrow **2-row stack** — `[checkbox 🔒]` on top, the team name
  ("Blue"/"Red") below (`.lk-top` over `.lk-name`; the word "Lock" was dropped). Keeping the
  chips narrow lets the two buttons take the slack and wrap to a tidy **2 lines** ("Best Blue"
  / "lineup") rather than 3.
- **The persistent "Loaded the best … lineup → N pts" note was removed** — after optimising,
  `#optnote` is cleared (the board shows the result). `#optnote` still carries the transient
  guard messages ("Set the other team's lineup first", lock warnings) and collapses when empty.
- **The header logo was removed** at the user's request — the banner is just the title text
  now. The `.logo` CSS, the base64 data URI, and the `<img>` were all deleted. **Don't
  reintroduce the logo** without being asked.

### Slim sticky score bar (re-added)
- A thin `position:fixed` bar (`#stickybar`) that slides down once the `.scorestrip`
  scoreboard is **~half scrolled above the top** (the big scores have gone, but before the
  finish board reaches the top) — an **IntersectionObserver** on `.scorestrip` toggles `.show`
  when `boundingClientRect.top < 0 && intersectionRatio < 0.5`. Content: **Blue score ·
  verdict · Red score**, where the verdict reads "Our team win" (blue) / "Opponent win" (red)
  / "Dead tie".
- `renderResults` keeps it in sync and sets `#stickybar`'s `data-has` to `1` only when there's
  a real result (non-blank, lineups set); the observer won't reveal it otherwise. This is a
  fresh, simpler build than the earlier removed bar (no logo, no team names — just scores +
  verdict), re-added at the user's request ("add back the thin hanging header").

### Leg ordering within a pair (realism)
- Slower runner leads off Leg 1, faster runner runs Leg 2 ("does the chasing") — cosmetic
  only (pair time is the sum), normalized via `legSorted()` across optimizer/presets/manual
  and both render paths. **Trios keep the fastest on Leg 1** (minimizes trio time).

### Times vs points formatting
- **Displayed times round to whole seconds** (`fmtTime`/`fmtTotal`); underlying values stay
  exact so rankings/tiebreaks are unaffected. **Half-points in the score column are
  intentional** (legitimate tie-splits).

### Colour & identity
- Blue `--our:#2563EB` / `--our-d:#1B45C4`; Red `--opp:#D11A35` / `--opp-d:#A8142A`; brand
  purple `#7030A0/#5A2483`; gold `#DE9B17`.
- **1st-place badge** stays gold but the number is team-coloured and ringed so tied 1st-place
  slots are identifiable.

### Mobile-specific (iOS is primary)
- **Header is left-aligned** on phone (`.brand{justify-content:flex-start;text-align:left}`);
  the "2026-2027" year wraps onto its own line under "FFF" rather than centering, and stays
  intact (`.yr{white-space:nowrap}` — it never splits at the hyphen).
- Score cards **stack vertically** on phone (a wide 4-char score like 52.5 overflowed
  side-by-side).
- The controls keep the **4-up optimise row** on phone (lock chips + buttons just tighten:
  smaller padding/font, buttons wrap to 2–3 lines). The scenario **label is on its own line**;
  the **dropdown + "Clear record" share the next line** (select uses `flex:1 1 auto` so it
  shrinks instead of hogging the row).
- The Auto-optimize row keeps all four elements on one line (lock chips + buttons just
  tighten); blue-left/red-right is preserved.
- Finish board uses the coloured medal + fixed-width columns; DNF checkbox sits inline; the
  desktop "VS" column is hidden. Inputs ≥16px to stop iOS auto-zoom.

---

## 5. Iteration log

### Phase A — original deterministic build (earlier sessions)
1. Round times to whole seconds (".5" only in the points column, as tie-splits).
2. Rename to "FFF Don't Hide Legend Cup" (title + file).
3. De-duplicate the score display; combined times into the scoreboard.
4. Pair leg order = faster runner on Leg 2 (via `legSorted`); trios keep fastest on Leg 1.
5. Mobile finish-board pass (coloured medal, aligned columns, removed "PAIR", inline DNF,
   hid VS block).
6. Consistency pass (uppercase roster name; finish-board points in display font + team
   colour).
7. Stacked mobile score cards; gold 1st badge with team-coloured number + ring.

### Phase B — no-show, optimisation & UI overhaul
8. **No-show modelling:** runner-level **NS** checkbox; the optimiser fields one capped
   no-show team per NS, trying **solo vs 10K-trio** and keeping the better; finish board
   shows **net** points for capped/DNF rows.
9. **Per-runner 10K override** added, then **removed** (superseded by editable actual times).
10. **Win probability** added (seeded Monte-Carlo); first inline, later its own row.
11. **Whole-team lock** (Lock Blue / Lock Red): pin a side, switch scenarios to compare vs
    each opponent combo. **Lock blocks Optimise**; **10K column removed**; **editable actual
    times** (team total proportional; runner edit holds total and rebalances; pace
    back-solves).
12. **Lock hardening (adversarial review):** locked teams can't lose runners via
    NS/roster-delete; master lock cascades to small locks and **restores** individual locks
    on release; no new teams while locked.
13. **Display polish:** controls blue-left/red-right; **branded result header** for a clean
    shareable screencap; win% relocated to its own labelled row; short "Lock Blue / Lock Red"
    chips. **Win% below the board**; concise **"?" help popovers** replace inline hints.

### Phase C — capture & race-day data entry
14. **Smart time entry** (`415`→4:15, `2115`→21:15, `4`→4:00) on all time fields; **roster
    5K editable and bidirectional** with pace.
15. **No-show keeps the runner visible** on a no-show team with the penalty auto-applied
    (fixes the "no penalty after manual edit" bug); ns members are non-running markers.
16. **Layout for clean screencaps:** moved the whole control block **below** the finish
    board; **removed the duplicate result header**.
17. **Clear record** (confirm-gated) zeroes all paces/5Ks (keeps lineups) → **blank
    scorecard** board.

### Phase D — 2026-2027 cup (new rosters, 11 v 11, no no-show)
18. **Header:** year **2026 → 2026-2027**; mobile header **re-aligned left** (year wraps
    under "FFF").
19. **One compact controls card:** merged the scenario row and the Lock/Optimise grid into a
    single `.controls` card with a hairline divider.
20. **Team names back to generic:** "Our team" / "Opponent".
21. **Sticky score bar removed** entirely (markup + CSS + JS observer + `stickyName()`).
22. **Roster refresh → 2026-2027:** 11 v 11, **nil no-show**. New `DEFAULTS`; `applyPreset`
    no longer marks no-shows; the blank "— Start blank" default loads rosters with **no
    teams** (everyone benched).
23. **New scenario presets** from a fresh brute-force solver: blank default + four Red
    archetypes (balanced / spread / stacked / minimax-optimal), each paired with our
    solver-optimal response. All four are **our wins** (41:35, 41:35, 39:37, 39.5:36.5) —
    verified live in-browser against the solver.
24. **Header logo removed** — the banner is plain title text; `.logo` CSS + base64 + `<img>`
    deleted.
25. **Docs consolidated** into `README.md` + three docs (`GAME-RULES.md`, `TEAM-LINEUP.md`,
    this spec); the old `Game-rules-2026.md`, `Relay_Problem_Spec_v1/v2`, and
    `FFF-Relay-App-Design-Notes.md` were folded in and removed (recoverable from git history).
26. **`/start` + `/end` slash commands** added under `.claude/commands/`; **`.gitignore`**
    added for the now-public repo; two Google-Drive links scrubbed from git history with
    `git-filter-repo` (force-pushed).
27. **Mobile header fix:** `2026-2027` kept on one line (`.yr{white-space:nowrap}`) — was
    splitting at the hyphen on narrow iOS.
28. **Controls re-flowed to four thin lines** (title → 4-up lock/buttons row → scenario label
    → picker + Clear record); the persistent "Loaded the best…" optimise note was removed.
29. **Sticky score bar re-added** (slim: Blue score · verdict · Red score; IntersectionObserver
    on `.scorestrip`) — supersedes its earlier removal in step 21, at the user's request.
    Trigger later refined to fire at **half-scroll** (`intersectionRatio < 0.5`) rather than
    when the scoreboard fully exits.
30. **Scenarios reworked to a single robust (minimax) Blue lineup** (`solve_robust.py`):
    instead of a tailored per-Red best response, every scenario now fields the **same** Blue
    lineup — the one with the best worst-case margin across the four Red plays. First preset
    simplified to **"Start blank"**; the **toughest Red is scenario #2**. Honest result: the
    robust lineup **splits 2–2** (loses 37:39 to Red optimal/balanced, wins 39:37 / 40:36 vs
    stacked / spread) — no single lineup sweeps all four. See
    [TEAM-LINEUP §2–3](TEAM-LINEUP.md#2-strategic-analysis).
31. **Points-table bug fix → derived scoring.** The points were a fixed 12-slot array
    (`[13,11,…,0]`), wrong for a 10-team meet. Replaced with **`pointsFor(K)`** derived from
    the live sub-team count (1st = K+1, last = 0, middle = K−i); the rules-drawer table is now
    read-only. Win threshold for 10 teams is **28+ (sum 55)**. Re-ran `solve_robust.py` under
    the corrected points: same robust lineup, scores now **26:29 / 26:29 / 29:26 / 29:26**, and
    the race-day win-chance shows **Red favoured in 3 of 4** scenarios.
32. **Scenarios: back to per-Red optimised + a Random baseline** (`solve_scenarios.py`).
    Reverted from the single robust lineup to **our best response per Red play** (wins all four:
    29.5:25.5 / 30:25 / 29:26 / 30:25). Added a **Random** scenario as #2 (toughest → #3) where
    **both** teams group by similar pace — trio = a mid runner + the two slowest (Red
    `Oyster*+GoG+AK`, Blue `DB*+Penny+Apoon`); that naive matchup is **27 : 28 Red**. The
    construction was verified to reproduce the user's exact example trios.

---

## 6. Technical / working notes

- **No browser storage** (no localStorage/sessionStorage) — all state is in-memory JS.
- **Verification approach:** a headless browser is available — Chromium at
  `/opt/pw-browsers/chromium-*/chrome-linux/chrome`, driven via `playwright-core`
  (`--no-sandbox`). Used for behavioural tests (lock guards, master-lock state, editable-time
  math, optimiser) **and** rendered screenshots (desktop + mobile). A **Python brute-force
  model** (using `fractions`) cross-checks the scoring numbers — the 2026-2027 presets were
  verified live in-browser to match the solver exactly (our optimised responses win 29.5:25.5 /
  30:25 / 29:26 / 30:25 vs Red optimal / balanced / stacked / spread; the naive Random matchup
  is 27:28, out of 55). An
  **adversarial multi-agent diff review** (4 lenses + verification) was run before finalising
  the lock/UI overhaul and caught 5 real defects (all fixed).
- **iOS gotcha:** Safari/Chrome on iPhone can't open local files directly; use the hosted
  Pages link.

---

## 7. Backlog & status

### Now implemented (previously deferred)
- **Win-probability mode** — built (seeded Monte-Carlo, ±10 s/km, own row under the
  scoreboard).
- **Multi-scenario comparison** — built via **Lock Blue/Red + scenario dropdown**: pin your
  lineup, cycle the opponent presets, read the score each time.

### Worth doing when next touched (small, low-risk)
1. **Completeness guard before optimizing.** The optimiser only checks the other side has
   *some* times, not a full field, so optimising against a half-built opponent silently
   returns a "best vs incomplete" lineup. Low effort; rarely bites because presets load full
   fields and a short field is visible on the board.
2. **Remove the now-dead `markNoShowTeams`** (no caller since the 2026-2027 presets dropped
   no-shows) — or re-wire it if a future cup brings no-shows back.

### Features, not fixes (skip unless wanted)
3. **One-click equilibrium / minimax.** Alternating best-responses oscillate by design; the
   strategic framing — per-Red best response vs the naive Random baseline — lives in
   [TEAM-LINEUP §2](TEAM-LINEUP.md#2-strategic-analysis),
   not a solver in the app.
4. **Save/share a result image** (beyond the manual screencap) — e.g. render-to-canvas
   export of the result block.

---

## 8. Quick reference for a fresh session

- **Open `index.html`** to see the current state; the default scenario is **blank** (rosters
  loaded, everyone benched, board empty — you build from scratch). Pick a scenario: **Random**
  (both teams naive) or a Red play + our optimised counter.
- **Current cup = 2026-2027, 11 v 11, nil no-show.** Each side = 4 pairs + 1 trio (10 small
  teams; points derived from the team count → `11,9,8,…,2,0`, sum 55 → 28+ wins). Team names "Our team" /
  "Opponent". Rules in [GAME-RULES](GAME-RULES.md); rosters + strategy in
  [TEAM-LINEUP](TEAM-LINEUP.md).
- **Don't undo:** whole-second time rounding; intentional half-points; faster-runner-on-leg-2;
  **pace as the single source of truth** for editable times (5K↔pace bidirectional; smart
  shorthand); **no-show keeps the runner visible** when used (ns members are non-running
  markers; penalty auto-applies — don't go back to benching); the **lock invariants** (locked
  = composition frozen, times editable; master lock cascades + restores via `_ulock`); the
  result-first layout (left-aligned header → scores → board, controls below, win% below the
  board); **Clear record** + blank scorecard; the **one-card controls** (4 thin lines, 4-up
  optimise row, blue-left/red-right); the **slim sticky score bar** (score · verdict · score —
  re-added by request); **no header logo** (removed — don't reintroduce); the **"Start blank"**
  default; the scenarios = a **Random** (both-naive) baseline + four Red plays each with **our
  optimised best response**; **points derived from the team count** (`pointsFor(K)`).
- **Not a bug:** the optimizer is a **best-response vs the other side's current lineup**;
  clicking both buttons oscillates by design (§2/§7).
- **To publish:** merge the `claude/…` branch into `main` and push; Pages serves `index.html`
  at https://dabinfish.github.io/.
- **Verify changes** with `playwright-core` against the local file (Chromium at
  `/opt/pw-browsers/…`) for both behaviour and screenshots; cross-check scoring with the
  Python brute-force model.
