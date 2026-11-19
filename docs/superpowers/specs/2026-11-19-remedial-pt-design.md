# Remedial PT (ABCP) — design

## Intent
The platoon leader runs remedial PT for Soldiers on the Army Body Composition Program (AR 600-9). ABCP progress is judged monthly (3–8 lb or 1% body fat). The app helps the leader plan and run the extra sessions. It holds workouts only.

## Goals
- Ready to use on day one: a 12-week plan, 3 sessions a week, 30–45 minutes, on top of regular PT.
- Fat-loss focus: steady cardio, full-body strength circuits (to keep lean mass), intervals, and mixed sessions.
- The plan builds week to week. Weeks 4, 8 and 12 are lighter.
- The leader can run any library session on any day ("Pick a session").
- The leader chooses which weekdays are remedial days. On those days, a Remedial card appears in the Train day view after the main workout, never in place of it.
- Exercises can be swapped, and every exercise keeps its easier/harder links (info card).

## Non-goals and anti-goals
- No roster, names, weights or body fat. This was the user's choice: "Workouts only".
- Nothing goes through live squad or Supabase.
- Remedial must never replace or change the regular day plan.

## Approaches considered
1. Built-in 12-week plan.
2. Remedial as a day format.
3. A pick-a-session library.

**Chosen: a mix of all three (the user's choice).** The library is the core. The plan schedules library sessions with week-based scaling. Days add a card in the planner.

## Design
- **Library:** `REM_LIB`, 12 sessions in 4 kinds (3 each):
  - Steady cardio: z2, ruck, pool swim.
  - Strength circuit: bodyweight, dumbbell, kettlebell.
  - Intervals: run, bike/row, hill/stair.
  - Mixed: cardio + core, carries + crawls, ruck + lunges.
- **Scaling:** by week level `REM_LV=[0,1,2,0,2,3,4,2,4,5,6,3]`.
  - Cardio minutes: base + 3×level.
  - Circuit rounds: 2 + ⌊level/2⌋, at 40 s work / 20 s rest.
  - Interval rounds: 6 + level.
- **Week plan:** session 1 is cardio, session 2 is strength, session 3 is intervals in odd weeks and mixed in even weeks. Within each kind, the session rotates by week.
- **Format:** each session has a 5-minute warm-up and a 5-minute cool-down, and runs on the existing circuit runner (`CI`, ctx `'rem'`) in `#ciSheet`.
- **State:** `S.rem={st:'YYYY-MM-DD'|'', days:[0,2,4], sw:{'sid.b.e':id}}`. It is cleaned on start-up, and included in backup.
- **Week number:** ⌊(date − start)/7⌋ + 1, limited to 1–12. Before a start date is set, the screens preview week 1.
- **Entry points:** a "Remedial PT" chip in the Main workout quick row, plus a tools menu entry.

## Left to the builder
Exact copy, session names, and exercise picks within each kind.
