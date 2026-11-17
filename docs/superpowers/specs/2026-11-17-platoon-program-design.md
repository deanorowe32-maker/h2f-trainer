# Platoon program (8-week mesocycle) — design

## Intent

The user is a platoon leader running the Rowe Training Program (RTP): an 8-week mesocycle with a fixed weekly microcycle, built in Excel (`Rowe_Training_Program_RTP_3.xlsx`). He wants:
- to build that program in the H2F app on his phone, as **its own separate part of the app**;
- to push it to his 23 Soldiers, so that each Soldier's phone shows the right session for the day, with weights fitted to that Soldier.

**Success:** a Soldier opens Today on Tuesday of Week 3 and sees the warm-up, the bench press at 56% with *their* weight, and rest and RPE for each exercise. The leader didn't message anyone individually, and the Soldier's own plan is still intact.

## What the RTP holds (source of truth for the shape)

- **Microcycle:** Mon ANC, Tue UBME, Wed LBME, Thu active recovery, Fri AC.
- **Each day:**
  - A RAMP warm-up: Raise / Activate-Mobilize / Potentiate.
  - Then rows in order: Power/Plyo, the main lift or activity, Accessories 1–4, and a cool down.
  - Each row has sets, reps or duration, rest and RPE.
- **Main lift:** a %1RM, plus a load range for each A/B/C group.
- **Conditioning:**
  - Shuttle: rounds × W:R, with a target time per group.
  - Ruck: load × distance, with a pace per group.
- **Mesocycle:**
  - Weeks 1–3 progress, week 4 deloads; weeks 5–7 progress from a higher base, week 8 deloads.
  - Fridays alternate between a ruck and an AGR run.
- **Week 0 assessments:** shuttle, bench 5RM, deadlift 5RM, 3 mi ruck. These map to groups through the table below. Estimated 1RM uses Epley: weight × (1 + reps/30).

### RTP classification table (Needs Analysis tab)

| Assessment | A | B | C |
|---|---|---|---|
| 300 yd shuttle | 50–60 s | 61–66 s | 67–72 s |
| Bench est. 1RM | 300–365 lb | 225–299 lb | 165–224 lb |
| Deadlift est. 1RM | 400–465 lb | 315–399 lb | 250–314 lb |
| Ruck 1-mile split | 12:45–13:30 | 13:31–14:15 | 14:16–15:00 |

Better than A counts as A; worse than C counts as C.

## Decisions the user made

1. **Audience:** the leader builds and pushes; the platoon receives. It is one-way, and nothing is logged back.
2. **Loads, both ways:** the % of the Soldier's own max when one is entered (existing `pctW`/`maxOf`); otherwise the range for the Soldier's group.
3. **Authoring:** on the phone, week by week, starting each week from a copy of the week before.
4. **Length:** 8-week blocks. One push = one block.
5. **Separate part:** the program lives alongside the Soldier's own week plan and never overwrites it. (This reverses an earlier pick of "grow the existing plan".)
6. **Two ways in, both wanted:**
   - a **Platoon program** entry in the Train tools list, between Circuit and Print week plan, which opens the program screen;
   - a **Program** choice under Workout format, after Normal / Stations / Circuit.
7. **One group overall** per Soldier (A, B or C), not one per event.

## Approaches considered

- **A. Grow the existing week plan to 8 weeks.**
  - The smallest build, but a push overwrites the Soldier's plan.
  - The user chose it first, then rejected it in favor of a separate part.
- **B. A separate program store, with its own screen, plus a per-day "Program" format (chosen).**
  - The Soldier's plan is untouched.
  - Costs its own editor, Today card, print and share code.
- **C. Import the .xlsx.** Rejected: the user wants phone authoring, and it is brittle to sheet layout.

## The design

### Data

`S.prog`: the one loaded program, or null.
- `name`: for example "RTP Block 1 of 3, AHA prep".
- `start`: the dated Monday key of Week 1.
- `from`: the leader's name.
- `weeks`: an array of 8 weeks. Each week holds:
  - `deload` (true/false);
  - `days`: Mon–Fri, five entries.
- **Each day** holds:
  - `focus`: one of the existing day types. RTP mapping:
    - ANC → anaerobic
    - UBME → upper
    - LBME → lower
    - AR → stretch
    - AC → aerobic
  - `wu`: warm-up, `{raise, act, pot}` text.
  - `rows`: the exercises, in order.
  - `cd`: cool-down text.
  - `off`: true for a day with nothing planned.
- **Each row** holds:
  - `part`: Power/Plyo, Main, Accessory or Conditioning.
  - `id`: an exercise from the library, including custom exercises.
  - `rx`: sets × reps or duration, text.
  - `rest`: text.
  - `rpe`: 1–10.
  - `pct`: optional %1RM.
  - `rng`: optional `{A, B, C}` text.

`S.grp`: the Soldier's own group ('A', 'B', 'C' or ''), plus their Week 0 results.

### Program screen (from Train tools → Platoon program)

- **Header:** block name, "Week N of 8" (computed from today's date and `start`), and a strip of the 8 weeks with deload weeks marked.
- **Body:** the chosen week's 5 days. Each day shows its warm-up, rows and cool down, the same way Today does.
- **Leader tools:**
  - Edit day: add, remove and reorder rows; edit the fields above.
  - Copy last week.
  - Bump % by N points across the week.
  - Mark deload.
  - Set block name and start week.
  - Push to platoon: a share code, shared and pasted like plan sharing today.
  - Print block.
- **Soldier tools:**
  - My group: pick A/B/C, or enter Week 0 results to get a suggestion. A, B or C is suggested from the four results by majority, and a tie goes to the lower group. Entering bench and deadlift 5RMs also saves the estimated 1RMs as maxes.
  - Start today's session.
- **Receive and replace:**
  - Paste a program code to load it.
  - Loading a new program replaces the old one, with Undo kept until the next load.
  - Remove program.
- **Empty state:**
  - Explains what a platoon program is.
  - "Paste a program from your leader".
  - "Build a program": starts 8 empty weeks, or a 1-week microcycle copied across 8.

### "Program" workout format (Train → Edit day)

- **When it shows:** on every weekday, for every focus, while a program is loaded and that date falls inside the block.
- **Picking it:** that day shows the program's session for that date in place of the Soldier's own exercises. The Soldier's own exercises are kept and come back when they pick Normal.
- **On load:** loading a program sets each weekday inside the block to Program. This is stored per dated week, so it survives week changes. The Soldier can switch any day back to Normal.
- **Where it shows elsewhere:** Today, the week list (marked "Pr") and print all follow the day's format.
- **Mark done:** "Mark workout done" logs the history entry as "Program · <focus>".

### Weight shown on a row

- With `pct` and a Soldier max: "56% → 205 lb".
- Otherwise, with a range for the Soldier's group: "A group: 205–170 lb".
- Otherwise: the plain prescription only. Never blank or NaN.

### Carried everywhere

- Backups: `BK_KEYS` gains `prog` and `grp`; `cleanBackup` validates both; the load normalization runs at startup.
- The program code gets its own tag (for example `H2FPROG1:`) and a strict clean, like `ptClean`.
- `sw.js` version bump; Playwright tests.

## Goals / non-goals / anti-goals

**Goals:** everything under "The design".

**Non-goals:**
- Soldiers reporting results back.
- Excel import or export.
- More than one loaded program at a time.
- Blocks longer than 8 weeks.
- Auto-progression rules.
- The leader assigning groups remotely.

**Anti-goals:**
- A Soldier's own plan is changed by loading a program.
- A blank or NaN weight shows anywhere.
- The program fields make the normal Train editor heavier for a Soldier who never loads a program. Program UI only appears when a program exists, except the one tools-list entry.

## Constraints

- Single-file PWA (`index.html`); state in `S`, saved to localStorage `h2f.v1` plus IndexedDB.
- Load normalization must not call anything defined later in the file. This caused an earlier crash on reopen.
- The share code travels by text, so 8 weeks of rows must stay compact. Use short keys.

## Left to the builder

- Field limits: rest ≤ 12 characters, range ≤ 24, warm-up fields ≤ 200, rows per day ≤ 15.
- Layout of the day editor.
- Whether Week 0 lives on the program screen or the Test tab. Suggested: the program screen, under My group.
- Whether a Program day can run through the Circuit or Stations timer. Suggested: not in v1.
