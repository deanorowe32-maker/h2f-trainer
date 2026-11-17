# Circuit workout format — short design (approved 2026-11-17)
Intent: a third workout format beside Normal and Stations for circuit days.
Approach: reuse the day's main (M) exercises in order; per-day config S.dcir[i] = {mode:'t'|'r', work:40, rest:20, rounds:3, rrest:90, reps:{<exId>:10}}; fmt 'c'. Rejected: separate exercise lists like stations (more UI, duplicates the plan).
Timed: work/rest per exercise, rest between rounds, auto-advance, vibrate on change, pause/skip/stop. Reps: target per exercise, Next button, round counter, timed rest between rounds. End: "Circuit done" + mark today's workout done.
Everywhere: Today card, week list "Ci", print, PT plan share, weeks storage, backups.
Calls left to the builder: limits (work 10–300 s, rest 0–180 s, rounds 1–10, round rest 0–600 s, reps 1–200), sheet layout.
