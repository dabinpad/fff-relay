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
- **no-show / penalty modelling** (the live constraint for this cup — see §2/§4),
- **editable actual race times** (type the real splits on the day; paces back-solve),
- **per-team and whole-team locks** for comparing one fixed lineup against many opponent setups,
- a **race-day Monte-Carlo win probability**, and
- a **branded, screenshot-ready result block** to share the outcome with the team.

It exists to answer a strategic question (§4) interactively and to drive the lineup decision on race day.

---

## 2. The competition (domain rules — the source of truth)

Two main teams each split their runners into **small teams** that each run **2 × 5 km legs (10 km total)**.
For this cup both sides have **13 runners**, but **Blue (Our Team) has one no-show (FF)** → Blue effectively
fields **12** and must take the no-show penalty, while **Red fields 13**:

- **Our Team (Blue):** 13 listed, **FF is a no-show** → 12 active → **4 pairs + 1 trio + 1 capped no-show team**.
- **Opponent (Red):** 13 runners → **5 pairs + 1 trio**.

Total on the course: **12 small teams** (6 per side).

### Timing
- **Pair time** = sum of the two runners' 5K times. *Order-independent for scoring.*
- **Trio time** = `leg1_5K + (legA_5K + legB_5K) / 2`. The half-credit on two of the three runners is the
  key structural quirk. **Putting the fastest runner on leg 1 minimizes the trio time.**
- **Solo (no-show)** = one runner runs the full 10 km = `2 × 5K`.
- **10K-trio (no-show alt)** = the leg-1 runner runs the full 10 km and a teammate runs leg 2 only:
  `5K_runner + (latter-5K + partner_5K)/2`, where `latter-5K = 10K − 5K`. With 10K = 2×5K this reduces to
  `1.5·5K_runner + 0.5·5K_partner` — i.e. it "buries" the partner at half credit.

### Scoring
- All **12 small teams are ranked by time**; points by finishing position:
  **`[13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 0]`** (sums to 78).
- A main team needs **40+ points to win**.
- **Tie on points → faster combined (aggregate) time wins.** Exact time tie → "Dead tie".
- **Ties on time** between small teams split the tied positions' points evenly → legitimate **half-points**
  (two teams tied for 2nd share `(11+10)/2 = 10.5`). Half-points are correct and intentional.

### No-show / DNF penalties (modelled in the app)
- **No-show (1 runner absent):** that small team's points are **capped at a maximum of 6** *and* take **−5**.
  The team can be fielded two ways and the optimiser tries both, keeping the better:
  - **Solo** — a teammate runs the 10 km alone (`2×5K`), or
  - **10K-trio** — the leg-1 runner runs 10 km and a teammate is buried on leg 2.
- **DNF / two no-shows:** team placed last (0 pts) plus an extra **−5**.

---

## 3. Rosters & paces (the actual data, seeded into the app)

Pace is **min:sec per km**; 5K time = pace × 5. Stored in `DEFAULTS` (index.html).

**Our Team — `"TT & SLK team"` (Blue), 13 listed; FF is the no-show:**

| Runner | Pace | Runner | Pace | Runner | Pace |
|---|---|---|---|---|---|
| TT | 4:00 | LC | 4:10 | FL | 4:10 |
| LP | 4:45 | Ryan | 4:45 | LW | 5:15 |
| 5K | 5:15 | KK | 5:30 | DB | 5:30 |
| SLK | 5:45 | Penny | 5:45 | CHT | 6:00 |
| **FF** | **6:00 (no-show)** | | | | |

**Opponent — `"CM & SIN team"` (Red), 13 runners:**

| Runner | Pace | Runner | Pace | Runner | Pace |
|---|---|---|---|---|---|
| Sandro | 4:00 | WL | 4:00 | SIN | 4:15 |
| HT | 4:30 | CM | 4:30 | KTY | 4:45 |
| Cai | 5:00 | CP | 5:00 | Oyster | 5:15 |
| LS | 5:15 | 9J | 5:30 | GoG | 5:45 |
| AK | 6:30 | | | | |

> Renamed from earlier drafts: **LWL → WL**, **CL → Cai**. SLK is **5:45** (was 5:30). FF (6:00) is the
> 13th Blue runner and the modelled no-show.

The **announced final lineup** (default scenario) resolves to **Blue 30.5 : 42.5 Red** —
combined times **Blue 5:03:33 vs Red 4:50:38**.

---

## 4. The strategic analysis (the "why" behind everything)

The substance the app was built to explore. Verified with an independent Python model during the session.

### The core finding
**Red has a structural advantage.** The trio half-credit lets Red "bury" its two slowest runners
(AK + GoG), so Red's effective aggregate ≈ **4:50:38** vs Blue's ≈ **5:03:33** — and because scoring is
near-linear in aggregate time, the faster-aggregate team is structurally favored.

### The on-the-day reality: the FF no-show makes it worse
Blue is down a runner. One Blue small team **must** be a capped no-show team (solo or 10K-trio): it earns
**at most 6 points and then loses 5** — a swing of roughly a full team's worth of points handed to Red.
With FF out:
- **Blue cannot win the announced matchup.** The default scenario lands **30.5–42.5**.
- The least-bad sacrifice is to burn a **slow** runner (SLK as the capped solo), **not** a fast one (TT),
  so the fast runners stay in scoring pairs. The cap is decisive either way; sacrificing SLK loses ~4
  fewer points than wasting TT.
- Across Red's archetypes Blue's ceiling is roughly **31–35.5** — still a loss. Blue only closes the gap
  if Red badly over-concentrates its speed.

### The decisive predictor (unchanged from the no-no-show analysis)
Outcome hinges on **how many Red teams finish under ~47:00**. Red fielding only 2 fast teams is the one
archetype Blue can stay close to; 3+ fast teams and Blue is comfortably beaten. The user expects Red to
play a **spread** (the "Red's optimal spread" preset is the toughest case and the app's #2 scenario).

### Recurring lessons surfaced to the user
- **Don't stack slow-on-slow** — it creates multiple bottom "sacrifice" teams.
- **Spread the fast runners** across teams.
- A sacrifice team **must still finish ahead of the opponent's slowest team**, so it doesn't gift a position.
- **Sacrifice the slow walker, not an ace**, for the forced no-show team.

### Monte-Carlo sanity (now built into the app)
With per-leg race-day jitter (±10 s/km), the announced Blue lineup wins essentially **0%** of races vs the
current Red lineup — the cap + the aggregate gap are too large to overcome on luck.

> These scenarios are baked into the app's **scenario presets** (§6), so the analysis is explorable.

---

## 5. App architecture (how it works under the hood)

- **One file, zero dependencies.** No external scripts/fonts/CDN. Native Apple system fonts. The cup logo
  (an interlocking "4-F" emblem) is embedded once as a **base64 PNG** in the header `<img class="logo">`;
  the **sticky bar** and the **result header** reuse the same bitmap by copying `src` at init (no second copy
  in the source).
- **Single source of truth for speed = the effective 5K.** Each runner has a `pace` (mm:ss/km) and an
  optional exact override `actSec` (a 5K time in seconds). `resolve()` exposes an *effective pace*
  `p = actSec/5` when an override is set, else `paceToSec(pace)`, so every `fiveK(p)` stays exact. Editing a
  pace clears the override; editing a time sets it.
- **Scoring engine (vanilla JS):** `teamTime()` computes pair/trio/solo/10k-trio times; `computeResults()`
  ranks all 12 teams, applies the points table, splits ties (half-points), applies the no-show cap+penalty,
  and resolves the winner (points, then aggregate time, then "Dead tie").
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

- **Editable rosters** (Runner / Pace / 5K / **NS** checkbox). Tick **NS** to mark a runner absent.
- **Card-based lineup builder:** pairs / trio (leg-1 selector) / solo / 10K-trio; **DNF** toggle; **per-team
  lock**; an editable **team total time** and editable **per-runner leg times**.
- **Editable actual times** (single source of truth = pace):
  - Edit a **team total** → splits **proportionally** across its runners.
  - Edit a **runner's leg** → holds the team total and **rebalances the partner(s)**; the runner's pace
    updates to match. Roster, board, and win% all recompute live.
- **No-show handling:** mark NS in the roster; **Optimise** fields one capped no-show team per NS, trying
  solo vs 10K-trio and keeping the better.
- **Locks (two levels):**
  - **Per-team lock** (on a card) — the optimiser keeps that exact team fixed; its runners can't be
    added/removed (times stay editable). Use it to pin a chosen 10 km runner before optimising.
  - **🔒 Lock Blue / 🔒 Lock Red** (by the scenario picker) — pins the whole side: switching scenarios only
    rewrites the *other* team, its Optimise button is disabled, every small-team lock is auto-checked, and
    its composition is frozen (add/remove/clear hidden; NS/delete of a locked-in runner blocked). Restores
    individual locks when released. **This is the "compare my lineup vs each opponent combo" tool.**
- **Live finish board:** all 12 teams ranked, with position, colored medal, time, trio/solo/DNF flag, and
  net points (no-show rows show their net −x, not the capped raw).
- **Top scoreboard:** big points per team + "combined H:MM:SS" subline + a verdict pill.
- **Race-day win-chance row** under the scoreboard (colour-coded pills; hidden when there's no valid matchup).
- **Branded result header** (logo + "FFF Don't Hide Legend Cup 2026") above the scoreboard so one screenshot
  captures name + logo + scores + win chance + finish board for sharing.
- **Sticky score bar** on scroll: logo + game name (centre), each team's name beside its score (blue left /
  red right).
- **Scenario presets (dropdown):**
  1. **★ Announced final lineup (TT & SLK vs CM & SIN)** ← **default**, FF no-show → 30.5–42.5
  2. *Toughest — Red's optimal spread (Blue best ≈ 31)*
  3. *Red plays two big pairs — Blue's best shot (35.5)*
  4. *Red spreads its 3 aces (33)*
  5. *Red stacks both aces in one pair (31.5)*

  Every preset bakes in **FF as the no-show**; presets 2–5 load Red's archetype + Blue's best response.
- **Auto-optimize** bar (the two best-lineup buttons), laid out **blue-left / red-right** to mirror the
  scoreboard. **Reset to defaults** (clears locks too).

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

### Win probability placement
- Win% was first inline next to the big score (looked cramped), then moved to its **own labelled row**
  ("RACE-DAY WIN CHANCE · x% vs y%") below the scoreboard. Keep it out of the big-number cards.

### Shareable result
- A **branded result header** sits directly above the scoreboard so a single screencap of the result is
  self-contained (name + logo + scores + win + board), independent of scroll position / the sticky bar.
  This intentionally duplicates the page header's logo+name — that's the point (the result block stands
  alone for sharing).

### Controls & sticky bar layout
- Lock + Optimise controls are laid out **blue-left / red-right** to match the scoreboard's two cards.
- The sticky bar shows the **logo + bigger game title** (centre) and each **team name beside its score**
  (verdict text dropped — the scores make it obvious). Names use `stickyName()` to strip a trailing "team".
- Team-lock chips read **"🔒 Lock Blue" / "🔒 Lock Red"** (short, not the full team name).

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
- Score cards **stack vertically** on phone (a wide 4-char score like 52.5 overflowed side-by-side).
- The scenario **label is on its own line**; the **dropdown + "Reset" share the next line** (select uses
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

---

## 9. Technical / working notes

- **No browser storage** (no localStorage/sessionStorage) — all state is in-memory JS.
- **Verification approach (current):** a headless browser **is** available this session — Chromium at
  `/opt/pw-browsers/chromium-*/chrome-linux/chrome`, driven via `playwright-core` (`--no-sandbox`). Used for
  behavioural tests (lock guards, master-lock state, editable-time math, optimiser) **and** for rendered
  screenshots (desktop + mobile). A Python engine replica (`solve.py`, using `fractions`) and jsdom tests
  cross-check the scoring numbers. An **adversarial multi-agent diff review** (4 lenses + verification) was
  run before finalising the lock/UI overhaul and caught 5 real defects (all fixed).
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
   block. The branded header already makes manual screenshots clean.

---

## 11. Quick reference for a fresh session

- **Open `index.html`** to see the current state; the default scenario is the **announced final lineup with
  FF no-show → Blue 30.5 : 42.5 Red**.
- **Strategic bottom line:** Red is structurally favored (trio half-credit ⇒ ~12-min faster aggregate), and
  **Blue's FF no-show forces a capped −5 team**, so Blue loses the announced matchup. Sacrifice the slow
  walker (SLK), keep the aces in pairs.
- **Don't undo:** whole-second time rounding; intentional half-points; faster-runner-on-leg-2; the real 4-F
  emblem logo; **pace as the single source of truth** for editable times; the **lock invariants** (locked =
  composition frozen, times editable; master lock cascades + restores via `_ulock`); win% in its own row; the
  branded result header; controls/sticky blue-left/red-right.
- **Not a bug:** the optimizer is a **best-response vs the other side's current lineup**; clicking both
  buttons oscillates by design (§5/§10).
- **To publish:** merge `claude/team-roster-optimization-qjmgrg` into `main` and push; Pages serves
  `index.html` at `https://dabinfish.github.io/`.
- **Verify changes** with `playwright-core` against the local file (chromium at `/opt/pw-browsers/…`) for both
  behaviour and screenshots; cross-check scoring with `solve.py` / jsdom.
