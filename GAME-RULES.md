# FFF Don't Hide Legend Cup — Game Rules

> The competition ruleset: how the meet is structured, timed, and scored. This is the
> **source of truth** for the scoring engine in `index.html`. Roster data and lineup
> strategy live in **[TEAM-LINEUP.md](TEAM-LINEUP.md)**; how the app implements these rules
> lives in **[APP-DESIGN-SPEC.md](APP-DESIGN-SPEC.md)**.

---

## 1. Format

Two main teams — **Our team** (Blue) and the **Opponent** (Red) — each split their runners
into **small relay teams**. Every small team runs a **2-leg relay: Leg 1 = 5 km,
Leg 2 = 5 km** (10 km total).

How a side splits depends on its roster size — **pairs of 2, with one trio of 3 when the
count is odd:**

- **Current cup (2026-2027): 11 v 11.** Each side = **4 pairs + 1 trio = 5 small teams** →
  **10 small teams** on the course.
- The format scales with roster size. *(The previous cup was 13 a side → 5 pairs + 1 trio
  = 6 small teams per side, 12 total. More teammates may be added this year, which would
  change the split.)*

---

## 2. Timing (per small team)

- **Pair (2 runners):** `team time = runner A's 5K + runner B's 5K`.
  Order-independent for scoring. *(A cosmetic convention leads off with the slower runner
  on Leg 1 so the faster runner "does the chasing" on Leg 2 — it does not change the time.)*
- **Trio (3 runners):** Leg 1 is run solo; the other two run Leg 2 **together**, starting
  when Leg 1 finishes. Official time is

  > **`Leg-1 5K + (Leg-2 runner A's 5K + Leg-2 runner B's 5K) / 2`**

  i.e. **the two Leg-2 runners each count half.** This half-credit is the key structural
  quirk:
  - Putting the **fastest** runner on Leg 1 **minimises** the trio's time.
  - Burying the **two slowest** runners on Leg 2 minimises the cost of carrying them.

---

## 3. Scoring

All small teams are ranked by finishing time (fastest = 1st). **Points scale to the total
number of small teams `N`** (blue + red — always **even**, since both sides field the same
number of teams):

> **1st = `N + 1` · last = `0` · every position in between counts down by one.**

**2026-2027 — 10 small teams:**

| Place | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Points | 11 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 0 |

These **sum to 55** → a main team needs **more than 27.5 (i.e. 28+) to win**.

- The scheme **generalises with the small-team count** `N` (always even, since both sides
  field the same number): the previous 13-a-side cup made **12 small teams** →
  `13, 11, 10, … 2, 0` (sum 78, 40+ wins); if each side fielded **7 small teams** (14 total) it
  would be `15, 13, 12, … 2, 0` (sum 105, 53+ wins). The app derives the table from the live
  sub-team count, so it can't go stale.
- Each main team's score = the sum of its small teams' points. **The higher total wins.**
- **Tiebreak:** equal points → the main team with the **faster combined total time** (the
  sum of all its small-team times) wins. An exact time tie → **"dead tie"**.
- **Ties on time** between small teams split the tied positions' points evenly → legitimate
  **half-points** (two teams tied for 2nd share `(9 + 8) / 2 = 8.5` each).

---

## 4. No-show / DNF penalties

> These are the **standing rules**. **2026-2027 assumes nil no-show**, so they are dormant
> this cup — but the app still models them for general use.

- **1 runner no-show:** the remaining partner may run the full 10 km. That small team takes
  **−5 points** AND its result is **capped at a maximum of 6 points**. *(The cap stops a
  fast runner from pairing with the slowest runner and tactically "no-showing" the slow one
  for an advantage.)*
- **2 runners no-show, or any small team that starts but cannot finish (DNF):** placed
  **last (0 points)** plus an **additional −5** to the main team.

---

## 5. Modelling assumption (for win-probability)

Paces are estimates. Assume modest race-day variation — roughly **±10 sec/km per runner per
leg**, as independent draws — so finishing order is not perfectly deterministic. The app's
race-day **win-chance** is a Monte-Carlo simulation over many races under this jitter (see
[APP-DESIGN-SPEC.md](APP-DESIGN-SPEC.md)).
