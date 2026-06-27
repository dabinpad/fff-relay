# FFF Don't Hide Legend Cup — App Design Notes

> Working documentation for the relay lineup-tester web app.
> Purpose: let a future session (or another person) pick this up cold and understand
> **what the app does, why the numbers are what they are, and why each design choice was made.**

- **Live deliverable:** `FFF Don't Hide Legend Cup.html` (single self-contained file, no external dependencies)
- **Hosting:** GitHub repo `github.com/dabinfish/fff-relay`, served via GitHub Pages. The file must be committed as **`index.html`** for the site to load at `https://dabinfish.github.io/fff-relay/`.
- **Primary use surface:** iPhone / Safari (mobile-first matters; desktop is the secondary view).

---

## 1. What this is

A standalone tool to **build relay lineups for two teams, rank all the small teams by finish time, score the meet, and instantly see who wins** — plus an optimizer that brute-forces each team's best possible lineup against the other side's current setup. It exists to answer a strategic question (below) interactively, and to let the user explore "what if" scenarios on the day.

---

## 2. The competition (domain rules — the source of truth)

Two main teams each split their runners into **small teams** that each run **2 × 5 km legs (10 km total)**:

- **Our Team (Blue):** 12 runners → **6 pairs** (no trio).
- **Opponent (Red):** 13 runners → **5 pairs + 1 trio**.

### Timing
- **Pair time** = sum of the two runners' 5K times. *Order-independent for scoring.*
- **Trio time** = `leg1_5K + (legA_5K + legB_5K) / 2`. The half-credit on two of the three runners is the key structural quirk. **Putting the fastest runner on leg 1 minimizes the trio time** (this is the optimal trio arrangement).

### Scoring
- All **12 small teams are ranked by time**; points awarded by finishing position:
  **`[13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 0]`** (sums to 78).
- A main team needs **40+ points to win** (out of 78).
- **Tie on points → the team with the faster combined (aggregate) time wins.**
- **Ties on time** between small teams split the tied positions' points evenly → this legitimately produces **half-points** (e.g., two teams tied for 2nd share `(11+10)/2 = 10.5` each). Half-points in the score column are correct and intentional.

### Penalty cases (modeled in the app)
- **No-show (1 runner left):** partner runs the 10 km solo; that team's points are **capped at 6** *and* the team takes **−5**.
- **DNF / two no-shows:** team placed last (0 pts) and takes **−5**.

---

## 3. Rosters & paces (the actual data, seeded into the app)

Pace is **min:sec per km**; 5K time = pace × 5.

**Our Team (Blue), 12 runners:**

| Runner | Pace | Runner | Pace | Runner | Pace |
|---|---|---|---|---|---|
| TT | 4:00 | LC | 4:10 | FL | 4:10 |
| LP | 4:45 | Ryan | 4:45 | LW | 5:15 |
| 5K | 5:15 | KK | 5:30 | SLK | 5:30 |
| DB | 5:30 | Penny | 5:45 | CHT | 6:00 |

Fixed aggregate (all pairs) = **18,175 s = 5:02:55**.

**Opponent (Red), 13 runners:**

| Runner | Pace | Runner | Pace | Runner | Pace |
|---|---|---|---|---|---|
| Sandro | 4:00 | LWL | 4:00 | SIN | 4:15 |
| HT | 4:30 | CM | 4:30 | KTY | 4:45 |
| CL | 5:00 | CP | 5:00 | Oyster | 5:15 |
| LS | 5:15 | 9J | 5:30 | GoG | 5:45 |
| AK | 6:30 | | | | |

Best-case aggregate (trio half-credit burying the two slowest, AK + GoG) = **17,437.5 s ≈ 4:50:38**.

---

## 4. The strategic analysis (the "why" behind everything)

This is the substance the app was built to explore. Verified with Python during the session.

### The core finding
**Red has a structural advantage.** The trio's half-credit lets Red effectively "bury" its two slowest runners (AK 1950s + GoG 1725s), making Red's effective aggregate ≈ **4:50:38** versus Blue's fixed **5:02:55** — roughly **12 minutes faster**. Because the scoring is near-linear in aggregate time, the faster-aggregate team is structurally favored.

### What this means for Blue
- **Against optimal Red play, Blue cannot win**, even with full information and a perfect best-response. Blue's best-response ceiling is ~35 points unrestricted (≈37.5 within the specific opening the user feared).
- **Blue only wins if Red misplays.**

### The decisive predictor
The outcome hinges on **how many Red small teams finish under ~47:00**:
- Red fields **only 2 fast teams** → **Blue can win (≈40–38)**.
- Red fields **3+ fast teams** → **Blue loses**.

The **"balanced" Red opening** (two strong pairs, e.g. Sandro+SIN and LWL+CM) is the *only* archetype Blue can beat, precisely because it over-concentrates Red's speed into just 2 fast teams. The "spread" archetypes (v2/v3, optimal spread, stars-stacked) give Red 3+ fast teams, and Blue's best result collapses to a 39–39 tie — **lost on the time tiebreak** (Red's aggregate is faster). The user believes Red will play a spread variant.

### Blue's winning answer vs a balanced Red ("the sweep")
Pack 5 teams just above Red's cluster and sacrifice one:
`TT+KK, LC+SLK, FL+DB, LP+LW, Ryan+5K, Penny+CHT` → 40–38.

### Recurring lessons surfaced to the user
- **Don't stack slow-on-slow** — it creates multiple bottom "sacrifice" teams.
- **Spread the fast runners** across teams.
- A sacrifice team **must lose its own matchup but still finish ahead of the opponent's slowest team**, so it doesn't gift the opponent a position.

### Monte-Carlo sanity (with per-runner variance)
vs spread-v2 ≈ 0–5% win for Blue even with luck; vs spread-v3 best-response ≈ 15–20% (knife-edge).

> These scenarios are baked into the app's **scenario presets** (see §6), so the analysis is explorable, not just written down.

---

## 5. App architecture (how it works under the hood)

- **One file, zero dependencies.** No external scripts, no web fonts, no CDN. Uses native Apple system fonts (SF Pro Display / Text / Mono) so it works fully offline and renders natively on iOS. The logo is embedded as a base64 data URI (transparent background).
- **Scoring engine (vanilla JS):** computes pair/trio/solo times, ranks all 12 teams, applies the points table, handles ties (half-points), tiebreak, and penalty cases. Unit-tested in Node to reproduce the analysis numbers exactly (e.g. sweep vs balanced = 40–38; v3counter vs spreadV3 = 39–39 with Red winning on time).
- **Optimizer:** brute-forces all valid pairings for a side (Blue ≈ 10,395 partitions; Red trio+pairs ≈ 270k) to find that team's **best response to the other side's current lineup**. Surfaced as two buttons: "Best Blue lineup" / "Best Red lineup".
- **State model:** each team has runners (editable) and a list of small teams; each small team has `memberIds`, a `leg1Id` (for trios), and a `dnf` flag.

### Key engine facts to remember
- Winner logic: higher points wins; tie on points → faster combined time; exact time-tie → "Dead tie". (`computeResults`)
- The optimizer optimizes **one side's points against the other side's fixed current lineup** — it is a best-response, not a joint equilibrium solve.

---

## 6. Feature set (current)

- **Editable rosters** (prefilled with the data in §3), with pace → 5K shown.
- **Card-based lineup builder:** pairs / trio (with a leg-1 selector), solo (1 runner), DNF toggle.
- **Live finish board:** all 12 teams ranked by time, with position, team color, time, and points.
- **Top scoreboard:** big points for each team + small "combined H:MM:SS" subline + a verdict pill.
- **Scenario presets (dropdown):**
  1. *Red spreads its two aces — close loss (39–39)* ← **default**
  2. *Red plays two strong pairs — Blue wins 40–38*
  3. *Red puts both aces in one pair*
  4. *Red's strongest setup — toughest case*
  5. *Pitfall: Blue stacks its slow runners (32–46)*
- **Auto-optimize** bar (the two best-lineup buttons).
- **Sticky score bar** that appears once you scroll past the scoreboard (so the score/verdict stays visible while editing lineups).
- **Reset to defaults.**

---

## 7. Key design decisions & rationale

Grouped by theme. These are the choices that should *not* be silently undone in a future session.

### Leg ordering within a pair (realism)
- Within every pair, the **slower runner leads off on leg 1; the faster runner runs leg 2** so the faster athlete "does the chasing." This is purely cosmetic (pair time is the sum, order-independent), normalized at display time via a `legSorted()` helper so it holds everywhere: optimizer output, presets, and manual builds, on both the finish board and the lineup cards.
- **Trios are exempt:** the fastest runner stays on **leg 1** (that's what minimizes the trio time). The order of the two leg-2 runners doesn't matter.
- Equal-pace pairs keep whatever order (doesn't matter).

### Times vs points formatting
- **All displayed times are rounded to whole seconds** (no ".5" on any clock) — the trio averaging and combined totals otherwise produce half-seconds, which looked odd. Rounding is **display-only** (`fmtTime` / `fmtTotal`); the underlying values stay exact so rankings/tiebreaks are unaffected.
- **Half-points in the score column are intentional** and were deliberately *not* removed — they represent legitimate tie-splits (two teams on the same time share the position points).

### Scoreboard & finish board
- The combined aggregate time lives **in the top scoreboard** (small subline under each team's points). An earlier duplicate score+verdict block inside the finish board was removed to avoid showing the same thing twice.
- **Finish-board points use the display font (bold) and are colored by team** — blue for Our Team rows, red for Opponent rows — matching the big score at the top. Race **times stay in monospace**, so points and times are visually distinct.
- The **"PAIR" label was removed** from both the finish board and the lineup cards (it's the common case = noise). The meaningful flags **trio / solo / DNF are kept**.

### Color & identity
- Team colors: **Blue `--our:#2563EB` / `--our-d:#1B45C4`**, **Red `--opp:#D11A35` / `--opp-d:#A8142A`**. Brand purple `#7030A0/#5A2483`, gold `#DE9B17`.
- **1st-place badge:** stays **gold** (winner cue), but the number is colored by team (blue/red) **and** wrapped in a thin team-colored ring, so you can tell which team holds each 1st-place slot — important when several teams tie for 1st (e.g. four Red teams all at 46:15).
- Team names are shown **UPPERCASE everywhere** (scoreboard, roster panel, lineup panel) for consistency. The roster name is an editable input uppercased via CSS only — the stored value is unchanged, so editing still works.

### Naming
- Document/file name and the in-page `<title>` are **"FFF Don't Hide Legend Cup"** (dropped the old working name "Relay Lineup Lab"). The header H1 reads "FFF Don't Hide Legend Cup 2026"; the subtitle is a plain descriptor.

### Mobile-specific layout (iOS is the primary surface)
- **Score cards stack vertically on phone** (big score on top, then team name, then combined time). This was a bug fix: side-by-side cards overflowed off-screen once the optimizer pushed a score to a wide 4-character value like **52.5**. Desktop keeps side-by-side.
- **Finish board on phone:** shows the **colored rank medal** for team identification, with **fixed-width columns** so rank / time / score line up vertically across rows (2-digit ranks like "10th"/"12th" no longer jam into the names).
- **DNF checkbox sits on the same line** as the player chips (not a separate row).
- The **"VS / verdict" block is hidden on phone** (it looked awkward under the cards); the winner still appears in the sticky bar on scroll.
- Inputs use ≥16px font on mobile to prevent iOS auto-zoom.

---

## 8. Iteration log (this session's back-and-forth, in order)

A compressed history of the refinements, so the reasoning is traceable:

1. **Round times to whole seconds.** Clarified that the remaining ".5" values live in the *points* column (tie-splits) and are correct.
2. **Rename to "FFF Don't Hide Legend Cup"** — first the `<title>`, then the actual downloadable file name.
3. **De-duplicate the score display:** removed the summary block inside the finish board; moved combined times up into the scoreboard cards.
4. **Leg order = faster runner on leg 2** for pairs (slower leads off); trios keep fastest on leg 1; applied via `legSorted` across optimizer/presets/manual and both render paths.
5. **Mobile finish-board pass:** re-added the colored rank medal, fixed-width aligned columns, removed "PAIR", moved DNF inline, hid the "VS/verdict" block on phone.
6. **Consistency pass:** uppercased the roster team name; switched finish-board points to the display font + team color (matching the top score, distinct from the mono time).
7. **Two bug/polish fixes:** stacked the mobile score cards (wide score like 52.5 was overflowing the Opponent card off-screen); gave the gold 1st-place badge a team-colored number + ring so the winner's team is identifiable.

---

## 9. Technical / working notes

- **File locations during a build session:** scratch work in `/home/claude`; final deliverables copied to `/mnt/user-data/outputs`. The named deliverable and an internal working copy (`relay-lineup-lab.html`) were kept in sync — when editing, edit one and copy to the other before presenting.
- **No browser storage** is used (no localStorage/sessionStorage) — all state is in-memory JS.
- **Verification approach:** since there's no headless browser available in-session (and its download host isn't reachable), changes were verified with **jsdom** in Node — checking DOM output (badges, medal, scores), computed styles via `getComputedStyle` for non-media-query CSS, and presence of the intended CSS rule text for media-query layout. Visual/mobile-layout correctness was confirmed by the user via screenshots. **A fresh screenshot from the user is the fastest way to fine-tune mobile spacing.**
- **iOS gotcha:** Safari/Chrome on iPhone can't open local files directly; use the hosted GitHub Pages link (or Files-app Quick Look).

---

## 10. Backlog & reviewed enhancements (deferred — not applied yet)

> **Status:** captured for a future build. As of this writing the app is **not** being changed.
> An independent AI review (June 2026) **rebuilt the exhaustive optimizer in Python and confirmed the app's engine and optimizer are correct** — the app-selected lineups matched the independent optimum on every built-in preset (e.g. balanced → Blue 40–38; spread-aces → 39–39 Red on tiebreak; Red's best responses → 48–30 / 52.5–25.5). It then raised four points. None are critical; assessment below.

### Verified-correct (no action)
The scoring engine and both optimizer buttons work as designed: deterministic **best response to the other side's currently displayed lineup**, using the exact pair/trio timing and points rules in §2.

### Worth doing when the app is next touched (small, low-risk)

1. **Completeness guard before optimizing** *(the one genuinely actionable item).*
   The optimizer currently only checks that the other side has *some* times (`oppTimes.length === 0`). It does **not** require a full 6-team opponent, so optimizing against a half-built opponent silently returns a "best" lineup vs an incomplete field — misleading.
   *Fix:* before optimizing, require the other side to have exactly 6 non-empty teams; warn if solo/DNF/incomplete teams are present. Low effort. In practice this rarely bites because presets always load full 6-v-6 and a short field is visible on the board (fewer than 12 teams), which is why it's deferred rather than urgent.

2. **Clarify the optimizer result wording.**
   "Best Blue lineup" / "Best Red lineup" can read as "objectively optimal" when each is really *optimal vs whatever the other side is currently showing*. This matters mainly **if the app is shared with coaches/teammates who don't know the §4 analysis.**
   *Preferred implementation:* state the framing in the **post-click result note** (e.g. "Loaded Blue's best lineup **against the current Red setup** → 40 pts"), **not** as permanent subtext under the buttons — that subtext was deliberately removed earlier to keep the optimize bar clean. Don't reintroduce it.

### Features, not fixes (skip unless specifically wanted)

3. **One-click equilibrium / minimax / simultaneous optimum.**
   The buttons do **not** compute a stable joint solution, and clicking both in sequence oscillates (observed: 39–39 → Red 48–30 → Blue 40–38 → Red 49–29). **This is expected, not a bug:** alternating best-responses cycle because there's no clean pure-strategy equilibrium here. The correct strategic answer to "what should Blue do not knowing Red's choice" is a **mixed/robust strategy**, which §4 already provides qualitatively (balanced is the only archetype Blue beats; against any spread Blue caps at 39–39 and loses on time). A solver would only mechanize an answer we already have. Real, larger feature — defer.

4. **Monte-Carlo / win-probability mode.**
   The older `Relay_Problem_Spec.md` asked for race-day variation (±10 s/km per runner per leg) and maximizing/estimating **win probability**. The app is intentionally **deterministic** — and the current spec is `v2_nilvary` (**nil variance**), so deterministic is correct *by design*. The Monte-Carlo analysis was run **separately** during the session (≈0–20% Blue win bands vs spread archetypes). This is a possible future toggle, not a gap against the current spec.

5. **Multi-scenario comparison view.**
   "Test one Blue lineup against several Red setups at once" (offered earlier, not built). Pairs naturally with the robust-strategy framing.

### Review's verification caveat (context, not an app issue)
The external reviewer could not run a live browser click-test — **Chromium wouldn't launch in the container** (missing shared libraries), the same limitation noted in §9. Verification was by source-level event-path inspection + an independent exhaustive Python model; live behavior continues to be confirmed by the user via screenshots.

---

## 11. Quick reference for a fresh session

- **Open the app file** (`FFF Don't Hide Legend Cup.html`) to see the current state; the default scenario is the 39–39 close loss.
- **The strategic bottom line:** Red is structurally favored (~12 min faster effective aggregate via the trio half-credit). Blue wins only if Red fields ≤2 fast teams; against a 3-fast-team spread, Blue tops out at 39–39 and loses on time.
- **Don't undo:** whole-second time rounding, intentional half-points, faster-runner-on-leg-2, uppercase team names, team-colored finish-board points, the gold+team-ring 1st badge, mobile vertical score cards, and the mobile finish-board medal/alignment.
- **Not a bug:** the optimizer is a **best-response vs the other side's current lineup** (externally confirmed correct, June 2026). Clicking both buttons oscillates by design. See §10 before "fixing" it into an equilibrium solver.
- **To update the live site:** commit the file as `index.html` to `github.com/dabinfish/fff-relay` (Pages: Settings → Pages → Deploy from a branch → main → /root).
