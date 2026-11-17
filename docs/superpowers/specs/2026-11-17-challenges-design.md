# Challenges: daily, weekly, monthly and special-day — design

## Intent

Give Soldiers something new to go after every time they open the app: a
daily exercise challenge, a weekly total and a monthly total, plus two
once-a-year special-day challenges. Finishing one earns a ribbon in the
existing ribbon system. The point is repeat visits and daily movement,
shared across a squad (everyone gets the same challenge on the same day).

## Goals

- One daily challenge built around a single exercise, the same for every
  Soldier on a given date.
- One weekly and one monthly challenge that add up over their period.
- Two special-day challenges: Memorial Day and Veterans Day.
- Ribbons for finishing them, using the existing ribbon machinery
  (awards, stars on repeats, popup, medal case, backup).
- Logged on trust, like the goal test.

## Non-goals

- No leaderboards, no sharing of challenge results (the squad screen is
  unchanged).
- No proof, video or leader sign-off.
- No push notifications or reminders.
- No user-made challenges (the goal test covers that).
- Challenge logs do not count as training anywhere else (decided by the
  owner): they feed only the challenges and the Challenge ribbons, never
  workout history, streaks, Training/log-day ribbons or the squad summary.

## Anti-goals (failure even if it works)

- Lift challenges that ask for heavy singles or a fixed weight. Lifts are
  always total reps at a weight the Soldier chooses.
- Trademarked event names. Use generic names (see Special days).
- A medal case where the long-haul ribbons get buried.
- A challenge card that nags or blocks the Today screen.

## Constraints

- Single-file PWA (`index.html`), no build step, no server, data stays on
  the phone in `S` (localStorage). Bump the `sw.js` version.
- Ribbons are defined by `RB_IDS` / `RB_RAW` / `RB_META`, counted in
  `rbCount(id)`, awarded by `rbCheck()` / `rbSoon()`. Stripes sum to 50
  (mirrored). Repeatable ribbons (`rep` flag) collect stars.
- Units follow the app's existing lb/kg setting (`S.assess.unit`): lb
  means miles, kg means kilometres. *(My call:)* all distance targets are
  defined and checked in miles; km users see exact conversions to one
  decimal (2 mi shows as 3.2 km) and enter km, which is converted on save.
  Switching units never changes a past result.
- The day boundary is the app's local `today()`.

## Approaches considered

1. **Plug into the existing ribbon system (picked).** A small challenge
   log in `S.ch`; ribbon counts are derived from it in `rbCount`. Awards,
   stars, popups and backup come for free.
2. **Separate challenge system with its own badges.** Duplicates the
   award, popup and backup machinery; rejected.
3. **Challenges as auto-made goal tests.** The goal test is one active
   test with baseline/goal numbers; it doesn't fit daily rotation;
   rejected.

## The challenges

### Daily (11 exercises, rotating by date)

Every challenge shows three marks on one bar: Easy / Standard / Hard.
There is no level to pick up front: reaching Easy completes it and earns
the ribbon; the highest level reached is recorded. *(My call: removes a
choice and still rewards going further.)*

| Challenge | Easy / Standard / Hard | Kind | Library id |
|---|---|---|---|
| Push-up | 50 / 100 / 150 reps | fixed | pu |
| Bodyweight squat | 75 / 150 / 250 reps | fixed | bws |
| Hand-release push-up | 30 / 60 / 100 reps | fixed | hrpu |
| Plank | 3 / 6 / 10 min total | fixed | plank |
| Burpee | 30 / 60 / 100 reps | fixed | burp |
| Pull-up | 20 / 40 / 60 reps | fixed | pull |
| Run | 2 / 3 / 5 mi | fixed | — |
| Ruck | 2 / 4 / 6 mi, pack weight you choose | fixed distance | ruck |
| Deadlift | 30 / 50 / 75 total reps | weight you choose | dl |
| Bench press | 30 / 50 / 75 total reps | weight you choose | bench |
| Back squat | 30 / 50 / 75 total reps | weight you choose | bsq |

- Rotation: the list order above, indexed by days since a fixed epoch,
  modulo 11, so every phone shows the same challenge on the same date.
- Logging adds to the day's total: "+ Log" opens a small entry (reps,
  minutes, or distance). Several logs a day add up. Logs can be undone
  (remove the last entry) the same day.
- Weight challenges (deadlift, bench, back squat, ruck) ask for the
  weight once per day, for the record only, with the line: "Pick a weight
  you can move with good form for every rep." The weight never affects
  completion.
- The exercise name links to its library entry (demo video/photos).
- Resets at local midnight. A missed day is simply missed.

### Weekly (Monday–Sunday, rotating by week)

One exercise per week, rotating through the same 11 (by week index), with
totals:

| Exercise | Easy / Standard / Hard per week |
|---|---|
| Push-up | 300 / 500 / 800 |
| Bodyweight squat | 400 / 700 / 1,000 |
| Hand-release push-up | 200 / 350 / 500 |
| Plank | 15 / 30 / 45 min |
| Burpee | 150 / 300 / 500 |
| Pull-up | 100 / 200 / 300 |
| Run | 8 / 12 / 20 mi |
| Ruck | 6 / 10 / 15 mi |
| Deadlift / Bench / Back squat | 150 / 250 / 400 total reps |

Any log of that exercise during the week counts, including logs made for
the daily challenge. The weekly row has its own "+ Log" for days when the
daily is something else.

### Monthly (calendar month)

Two parts, both needed:

1. **Miles:** run and ruck distance combined. Easy / Standard / Hard =
   20 / 40 / 60 mi.
2. **Lift of the month:** rotates Deadlift → Bench press → Back squat by
   calendar month. Easy / Standard / Hard = 300 / 500 / 800 total reps.

The month's level is the lower of the two parts' levels. Daily and weekly
logs of run, ruck and the month's lift count toward it.

### Special days (once a year)

Open from 3 days before to 3 days after the date *(my call: lets units
do it on a weekend or training day)*:

- **Memorial Day Hero Workout** (last Monday of May): 1-mile run, 100
  pull-ups, 200 push-ups, 300 squats, 1-mile run, split as needed. Easy =
  half volume; Standard = full; Hard = full in a weighted vest or plate
  carrier. Logged as a five-item checklist plus the level done. Short
  tribute line naming that it honors fallen service members. Never called
  "Murph" or "The Murph Challenge".
- **Veterans Day Step-Ups** (11 November): step-ups with a pack. Easy /
  Standard / Hard = 250 / 500 / 1,000. Short line on veteran mental
  health. Never called "Chad 1000x".

When a special day is open, it shows as an extra row at the top of the
card.

## Ribbons (15 new, all repeatable with stars; 85 → 100 shown)

New area **"Challenge"** in the medal case.

- 11 per-exercise daily ribbons: Push-up Challenge, Squat Challenge,
  Hand-Release Challenge, Plank Challenge, Burpee Challenge, Pull-up
  Challenge, Run Challenge, Ruck Challenge, Deadlift Challenge, Bench
  Challenge, Back Squat Challenge. Earned again each time that exercise's
  daily is completed.
- Weekly Challenge, Monthly Challenge.
- Memorial Day Hero, Veterans Day Step-Up (once per year each).

Counts in `rbCount`: number of completed periods derived from the log
(e.g. Push-up Challenge = number of dates whose daily was push-ups and
whose push-up total reached Easy). Ribbon detail text shows the highest
level reached most recently. Total Soldier (`tsol`) keeps counting
only the original eight H2F areas; Challenge is left out of it *(my call:
Total Soldier is about the H2F domains)*. Undo can remove a mistaken entry
the same day, but a ribbon already awarded stays, matching the rule that
awards are never removed *(my call: on trust, like everything else)*.
The "closest ribbon" card ignores the
Challenge area (it's handled by the challenge card itself). The hidden
Open Door ribbon logic is unchanged; the medal-case total becomes 100
(+1 once Open Door is found).

## Where it lives

A **Challenges** card on Today, above the closest-ribbon card:

```
CHALLENGES
Today · Push-ups          60 / 100  ▓▓▓▓▓▓░░░░  [+ Log]
This week · Squats       180 / 700  ▓▓▓░░░░░░░  [+ Log]
November · Miles        12.5 / 40   ▓▓▓░░░░░░░  [+ Log]
           Deadlift      140 / 500  ▓▓░░░░░░░░  [+ Log]
```

- The bar's fill target is the next unreached level; the three level
  marks show on the bar. Completed rows show a check and the level.
- Finishing triggers the normal ribbon popup.
- The card can be collapsed (remembered); it is never hidden for good.

## Data

`S.ch = { log: { 'YYYY-MM-DD': { <key>: number } }, w: { 'YYYY-MM-DD': { <key>: string } }, sp: { '<year>-md' | '<year>-vd': { items: [bool...], lvl: 0-3 } }, last: [ {d, key, n} ] }`

- Keys are challenge keys (`pu`, `bws`, `hrpu`, `plank`, `burp`, `pull`,
  `run`, `ruck`, `dl`, `bench`, `bsq`, `stepup`). Distances are stored in
  miles, minutes for plank; display converts for km.
- `w` keeps the optional weight text per day per lift/ruck.
- Logs are never pruned *(my call: one small entry per day, a few KB a
  year; pruning would make derived ribbon counts fall below stored awards
  and stop stars being added)*.
- `'ch'` is added to `BK_KEYS` with a cleaner that drops anything
  malformed per entry (not the whole store), clamps numbers (≥ 0, sane
  caps such as 2,000 reps or 100 miles per day entry).

## Left to the builder

- Exact copy for the card, entry sheet and ribbon rules.
- Ribbon stripe designs (one colour family for the Challenge area).
- Epoch choice for rotation, and the entry UI details (number pad,
  quick "+10"/"+25" buttons are welcome).
- Tests: a Playwright script like `tests/goal_test.py` covering rotation
  determinism, logging/undo, weekly/monthly roll-up, unit display, special
  day windows, ribbon awards and backup round-trip.
