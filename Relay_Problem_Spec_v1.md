# Relay Championship — Problem Specification (for independent analysis)

> Self-contained spec. Goal: find the optimal small-team lineup for **Our Team** and estimate the probability of winning the championship. No solution is included here — solve from scratch.

---

## 1. Format

- Two main teams compete: **Our Team** and the **Opponent**.
- Each main team is split into small relay teams (pairs of 2; a trio of 3 only if the main team has 13 runners).
- **Our Team has 12 runners → 6 pairs (no trio).**
- **Opponent has 13 runners → 5 pairs + 1 trio.**
- Total on the course: **12 small relay teams** (6 from each side).

## 2. Relay rules (per small team)

Each small team runs a 2-leg relay: **Leg 1 = 5 km, Leg 2 = 5 km** (10 km total).

- **Pair (2 runners):** Runner A runs Leg 1, Runner B runs Leg 2.
  `Team time = A's 5K time + B's 5K time`
- **Trio (3 runners):**
  - Leg 1: one runner runs the 5 km alone.
  - Leg 2: the other two runners run the 5 km **together** (they start together when Leg 1 finishes).
  - Official time = `Leg-1 time + average(the two Leg-2 runners' finish times)`
  - Equivalently: `t_leg1 + (t_legA + t_legB) / 2` — i.e. **the two Leg-2 runners each count half.**

## 3. Scoring

- All 12 small teams are ranked by finishing time (fastest = 1st).
- Points by finishing position:

| Place | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Points | 13 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 0 |

- Each main team's score = sum of its 6 small teams' points (total points across both teams = **78**).
- **The main team with the higher total wins** (so you need **40+** to win).
- **Tiebreak:** if the point totals are equal, the main team with the **faster combined total time** (sum of all 6 small-team times) wins.

## 4. No-show / DNF penalties

- **1 runner no-show:** the partner may run the full 10 km solo; that small team's result gets **−5 points** AND is **capped at a maximum of 6 points**.
- **2 runners no-show, or any small team that starts but cannot finish (DNF):** placed **last (0 points)** plus an **additional −5** to the main team.

## 5. Rosters & paces

Paces are per-km estimates; **5K time = pace × 5**.

### 🟦 Our Team — 12 runners (→ 6 pairs, no trio)

| Runner | Pace /km | 5K time |
| :----- | :------: | :-----: |
| TT     |   4:00   |  20:00  |
| LC     |   4:10   |  20:50  |
| FL     |   4:10   |  20:50  |
| LP     |   4:45   |  23:45  |
| Ryan   |   4:45   |  23:45  |
| LW     |   5:15   |  26:15  |
| 5K     |   5:15   |  26:15  |
| KK     |   5:30   |  27:30  |
| SLK    |   5:30   |  27:30  |
| DB     |   5:30   |  27:30  |
| Penny  |   5:45   |  28:45  |
| CHT    |   6:00   |  30:00  |

### 🟥 Opponent — 13 runners (→ 5 pairs + 1 trio)

| Runner | Pace /km | 5K time |
| :----- | :------: | :-----: |
| Sandro |   4:00   |  20:00  |
| LWL    |   4:00   |  20:00  |
| SIN    |   4:15   |  21:15  |
| HT     |   4:30   |  22:30  |
| CM     |   4:30   |  22:30  |
| KTY    |   4:45   |  23:45  |
| CL     |   5:00   |  25:00  |
| CP     |   5:00   |  25:00  |
| Oyster |   5:15   |  26:15  |
| LS     |   5:15   |  26:15  |
| 9J     |   5:30   |  27:30  |
| GoG    |   5:45   |  28:45  |
| AK     |   6:30   |  32:30  |

## 6. Modeling assumption

- Paces are estimates. Assume modest race-day variation — roughly **±10 sec/km per runner per leg** (independent draws) — so finishing order is not perfectly deterministic.

## 7. Questions to solve

1. **Optimal lineup:** how should Our Team's 12 runners be split into 6 pairs to maximize the probability of winning the championship?
2. **Win probability** of that lineup:
   - (a) against the Opponent's *best* counter-lineup, and
   - (b) against a "balanced / fair teams" Opponent lineup (each pair = one faster + one slower runner).
3. **Dependence on the Opponent:** does the best Our-Team lineup change depending on how the Opponent arranges its teams (e.g. spreading runners evenly vs. concentrating fast runners into a few lean teams)? Explain the trade-off.

*(Both teams set their lineups; state your assumption about whether lineups are revealed simultaneously or one side can react to the other.)*
