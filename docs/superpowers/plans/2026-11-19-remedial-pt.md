# Remedial PT Implementation Plan

**Goal:** Add a leader-run Remedial PT (ABCP) section: a session library, a 12-week plan and per-day cards, all running on the circuit runner.
**Spec:** docs/superpowers/specs/2026-11-19-remedial-pt-design.md
**Tech:** single-file `index.html`, Playwright tests in `tests/`.

## Global constraints
- Workouts only. Never store personal data.
- Remedial never changes `S.plan`, `S.types` or `S.fmt`.
- Bump the `sw.js` version.

## Review focus
- An invalid or empty `S.rem` from old saves or a backup must not crash start-up. Run the cleaner before render.
- Swapped exercise ids that were deleted (custom) fall back to the built-in exercise.
- The week number is limited to 1–12, and a start date in the future previews week 1.
- Stopping a remedial run returns to the Remedial sheet, not the quick-circuit builder.
- Days chips can be toggled down to an empty list. In that case no day cards show.

### Task 1: data, library, scaling, runner, UI
Test: `tests/remedial_test.py`
- `remClean` returns the default on null or garbage input.
- `REM_LIB` has 12 sessions, and every id is in `EX`.
- `remSess` week 4 is shorter than week 3. Week 11 is longer than week 1.
- `remWeek(st)` gives 1 for today, 2 a week later, and is limited to 12.
- The chip opens the sheet, which shows "Week 1 of 12".
- Start runs `CI` with ctx `'rem'`. Stopping it shows the Remedial sheet again.
- A day card shows on a remedial day and not on other days.
- Swapping an exercise is used by `remSess`.
- Backup round-trips `rem`.
- There are no page errors.
- Then run the full suite, commit, and push.
