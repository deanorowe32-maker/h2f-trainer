# Holiday challenges — short design (approved 2026-11-17)

**Intent:** more once-a-year reasons to train, extending the Memorial Day / Veterans Day special-day challenges to 10 US/Army holidays.

**Approach (only sensible one):** generalize the existing special-day code into one holiday table; reuse the Challenges card, log sheet, `S.ch` storage, backup cleaner and ribbon counting. Rejected: a separate holiday screen (duplicates the card) and per-holiday hand-written code (10× the same logic).

**Holidays** (window = 3 days before to 3 days after; ribbon per holiday, a star per year):

| id | Holiday | Date | Kind | Workout | Easy / Standard / Hard |
|---|---|---|---|---|---|
| ny | New Year | 1 Jan | checklist | N burpees, N squats (N = new year's last two digits) | half / full / full in vest or pack |
| eas | Easter "Dozen Eggs" | Western Easter Sunday | checklist | 12 rounds of 12 squats, 12 push-ups, 12 lunges, 100 m sprint | half / full / vest |
| md | Memorial Day Hero Workout | last Mon May | checklist | (existing) | (existing) |
| ab | Army Birthday | 14 Jun | total reps | Army's age (year − 1775) reps, any mix of push-ups, squats, sit-ups | ½ / 1 / 1.5 × age |
| id4 | Independence Day | 4 Jul | total reps | 1,776 reps, split as needed | 888 / 1,776 / 2,664 |
| lab | Labor Day | 1st Mon Sep | total miles | ruck or loaded carry | 1.5 / 3 / 4.5 mi |
| hw | Halloween | 31 Oct | checklist | 3 rounds of 31 burpees, 31 squats, 31 lunges | half / full / vest |
| vd | Veterans Day Step-Ups | 11 Nov | total reps | (existing) | 250 / 500 / 1,000 |
| tg | Thanksgiving "Turkey Burner" | 4th Thu Nov | total miles | run or ruck before the meal | 1.55 / 3.1 / 4.65 mi (2.5 / 5 / 7.5 km) |
| xm | Christmas "12 Days" | 25 Dec | checklist | 12 days, song-style: day N adds N of a new exercise and repeats all earlier ones | half / full / vest |

- The New Year window crosses the year line; the holiday's own year owns it (29 Dec 2026 counts toward New Year 2027).
- Checklist: tick every item, then "Done at Easy / Standard / Hard". Total: + Log like the daily challenge; level from the totals above.
- Holiday logs use their own keys (`hab`, `hid4`, `hlab`, `htg`, existing `stepup`) and never count toward daily/weekly/monthly totals or training.
- Ribbons (8 new, area Challenge, repeatable): New Year, Easter Dozen, Army Birthday, Independence Day, Labor Day, Halloween, Thanksgiving, Christmas. Medal case 100 → 108. Existing `chmd`/`chvd` unchanged.
- Generic names only; no trademarked event names.
