# Challenges Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Daily, weekly, monthly and special-day exercise challenges on Today, logged on trust, earning 15 new repeatable ribbons.

**Architecture:** All code in `index.html`, in a new block just before `function viewToday(){`. State in `S.ch`, saved with `save()` and in backups (`BK_KEYS` + a cleaner). Ribbon counts are derived from `S.ch` inside `rbCount`, so awards, stars, popups and backup come from the existing ribbon system.

**Tech Stack:** Plain HTML/CSS/JS, no build step; Playwright (Python) check script.

**Spec:** `docs/superpowers/specs/2026-11-17-challenges-design.md`

## Global Constraints
- 11 challenge keys, in this rotation order: `pu, bws, hrpu, plank, burp, pull, run, ruck, dl, bench, bsq`; plus `stepup` (Veterans Day only).
- Units stored: reps, minutes (plank), miles (run, ruck). Targets are checked in miles; with `S.assess.unit==='kg'` distances display as km to one decimal (×1.609344) and typed km are converted to miles on save.
- Reaching Easy completes a challenge; the highest level reached is recorded. No level picked up front.
- Lift and ruck weight is optional text, stored for the record only. Copy: "Pick a weight you can move with good form for every rep."
- Challenge logs never feed workout history, streaks, Training/log-day ribbons or the squad summary.
- Logs are never pruned. Awards are never removed (undo keeps an earned ribbon).
- Special days: Memorial Day = last Monday of May; Veterans Day = 11 Nov; each open from 3 days before to 3 days after. Names: "Memorial Day Hero Workout", "Veterans Day Step-Ups". Never "Murph" or "Chad".
- Bump the `sw.js` version string; commit to `main`.

## Review Focus
1. A log made at 23:59 and another at 00:01 → each lands on its own local date (`today()`); yesterday's total is unchanged and today's challenge is the next in rotation.
2. A km user types "5" for a run → stored as 3.107 mi; shows "5.0 km"; after switching to lb it shows "3.1 mi"; completion is unchanged by the switch.
3. Entry "", "abc", "-5" or "0" → rejected with the field marked invalid; "99999" reps → rejected (caps per entry: 2000 reps, 600 min, 100 mi).
4. A backup whose `ch` has a bad date key, an unknown challenge key or a string amount → only those entries dropped; the rest restore.
5. A week spanning two months (e.g. Mon 30 Nov – Sun 6 Dec 2026) → weekly total covers all seven days; monthly totals split at the month line.

---

### Task 1: Challenge data, rotation and totals

**Files:** Modify `index.html` (new block before `function viewToday(){`; `S.ch` init next to `S.goal` init; `'ch'` in `BK_KEYS` with `chClean` used by the backup cleaner like `gtCleanStore`). Create `tests/challenges_test.py` (same harness as `tests/goal_test.py`: stages, `check()`, `RESULT OK`).

**Interfaces — Produces:**
- `CH`: array of `{k, name, ex:libraryId|null, u:'reps'|'min'|'mi', d:[e,s,h], w:[e,s,h], wt:boolean}` with the spec's daily and weekly targets (lifts weekly 150/250/400; run weekly 8/12/20; ruck weekly 6/10/15). `CH_BY[k]`.
- `S.ch = {log:{'YYYY-MM-DD':{k:number}}, w:{'YYYY-MM-DD':{k:string}}, sp:{'<year>-md':{items:bool[5], lvl:0..3}}, last:[{d,k,n}] (max 50)}`
- `chDayKey(d) -> k`: `CH[(days since '2026-01-05') mod 11].k` (negative-safe mod).
- `chWeekStart(d) -> 'YYYY-MM-DD'` (Monday); `chWeekKey(d) -> k`: `CH[(weeks since 2026-01-05) mod 11].k`.
- `chMonthLift(d) -> 'dl'|'bench'|'bsq'`: `['dl','bench','bsq'][(months since Jan 2026) mod 3]`.
- `chSum(k, from, to) -> number` (inclusive date range).
- `chLevel(total, [e,s,h]) -> 0..3`.
- `chState(d) -> {day:{k,total,lvl}, week:{k,start,total,lvl}, month:{miles,mlvl,lift,lift_total,llvl,lvl:min(mlvl,llvl)}, special:null|{id:'md'|'vd',year,date}}`; month miles targets 20/40/60, lift 300/500/800.
- `chSpecial(d) -> null|{id,year,date}`.
- `chParse(u, text) -> number|null` (applies km→mi when the unit is kg and `u==='mi'`; rejects ≤0, NaN and over the caps).
- `chShow(u, v) -> string` (e.g. "60", "6.5 min", "3.1 mi" / "5.0 km").
- `chLog(k, n, d)`, `chUndo(d) -> boolean` (removes the last `last` entry for date `d`).
- `chClean(o) -> S.ch-shaped object`.

- [ ] Step 1: write stage 1 of `tests/challenges_test.py`: `chDayKey('2026-01-05')=='pu'`, `chDayKey('2026-01-16')=='pu'`, `chDayKey('2026-01-04')=='bsq'`; `chWeekKey('2026-01-11')=='pu'` and `chWeekKey('2026-01-12')=='bws'`; `chMonthLift('2026-11-17')=='bench'`; `chSpecial('2027-05-31').id=='md'` (last Monday of May 2027), `chSpecial('2027-05-28')` not null, `chSpecial('2027-05-27')` null, `chSpecial('2026-11-14').id=='vd'`, `chSpecial('2026-11-15')` null; `chLevel(60,[50,100,150])==1`, `chLevel(150,[50,100,150])==3`, `chLevel(49,[50,100,150])==0`; Review Focus 1 (`chLog` on two dates, totals kept apart), 2 (`S.assess.unit='kg'`, `chParse('mi','5')` ≈ 3.107, `chShow('mi',3.107)=='5.0 km'`, then lb → `'3.1 mi'`), 3 (all four rejected inputs return null), 4 (`chClean` on a mixed bad/good object keeps exactly the good entries), 5 (logs on 2026-11-30 and 2026-12-06 both count in the week starting 2026-11-30; November miles exclude the 6 Dec log); `chUndo` removes only the last entry.
- [ ] Step 2: run `python3 tests/challenges_test.py 1` (server on :8765) → FAIL, functions undefined.
- [ ] Step 3: implement the Produces list.
- [ ] Step 4: run → `RESULT OK`; `python3 tests/goal_test.py all` still OK. Commit.

### Task 2: Today card, entry sheet and special-day rows

**Files:** Modify `index.html`: `chHtml()` inserted in `viewToday` before `${rbNextHtml()}`; actions in a `chAct(a,v)` dispatcher called from the main click handler (pattern of `gtAct`); entry sheet `#chSheet` (pattern of `#gtShared`); CSS next to the goal-test CSS.

**Interfaces — Consumes:** Task 1. **Produces:** `chHtml() -> string`; actions `chopen` (v=row id `day|week|miles|lift|vd`), `chadd`, `chundo`, `chfold`, `chmditem` (v=0..4), `chmdlvl` (v=1..3).
- Card "Challenges", collapsible (`S.ch.fold`, remembered). Rows as in the spec sketch: label, `total / next unreached target`, bar with three level ticks, "+ Log"; completed rows show a check and the level name. Exercise names link to the library entry (`ex`).
- Entry sheet: number input (`inputmode="decimal"`), quick buttons +10/+25 for reps, weight text field for `wt` challenges with the Global Constraints copy, "Add", "Undo last" (today only), invalid input sets `aria-invalid`.
- Special rows at the top while open: Memorial Day = 5-item checklist (1-mile run, 100 pull-ups, 200 push-ups, 300 squats, 1-mile run; Easy shows half numbers) then level buttons Easy/Standard/Hard, enabled once all 5 are checked; Veterans Day = a step-up row logged like the others (250/500/1,000 over the open window). One tribute line each (honoring fallen service members / veteran mental health).
- [ ] Step 1: stage 2 tests: with today forced via `S.ch` logs on `today()`, render Today → card present with 3 rows (day, week, miles+lift); log 60 push-ups through the sheet on a push-up day (set date by overriding `chDayKey` to return `'pu'`) → row shows "60 / 100"; invalid "abc" marks the input invalid and logs nothing; undo removes it; fold persists across `render()`; with `chSpecial` overridden to Memorial Day the checklist row appears and level buttons stay disabled until 5 items are checked. No page errors.
- [ ] Step 2: run → FAIL. Step 3: implement. Step 4: run → OK; screenshot `/tmp/ch.png` at 390×844 and look at it. Commit.

### Task 3: Ribbons, ship

**Files:** Modify `index.html`: `RB_IDS` += `chpu, chbws, chhrpu, chplank, chburp, chpull, chrun, chruck, chdl, chbench, chbsq, chwk, chmo, chmd, chvd`; matching `RB_RAW` rows (area `"Challenge"`, `rep` = 1, stripes sum 50, one colour family) and `RB_META` (`[1,'challenge done']` etc.); `RB_AREAS` gets `['Challenge',…]`; `rbCount` cases; `tsol` excludes area `Challenge`; `rbNext` skips area `Challenge`; call `rbSoon()` after `chadd`/`chmdlvl`. `README.md`: 85 → 100 ribbons, mention Challenges on Today. `sw.js` version bump.

**Interfaces — Consumes:** Task 1 (`S.ch`, `chDayKey`, `chWeekKey`, `chSum`, `chLevel`, `chSpecial`).
- Counts: `ch<k>` = number of log dates `d` with `chDayKey(d)===k` and `log[d][k] >= CH_BY[k].d[0]`; `chwk` = number of week starts whose `chWeekKey` total reaches Easy; `chmo` = months whose `lvl >= 1`; `chmd` = years with `sp['<y>-md'].lvl >= 1`; `chvd` = years whose step-up total across that year's window ≥ 250.
- [ ] Step 1: stage 3 tests: logging 50 push-ups on a push-up date awards `chpu` once; a second push-up date makes `n==2`; undoing after the award leaves `S.rb.aw.chpu`; weekly total reaching Easy awards `chwk`; Memorial Day level 1 awards `chmd`; `rbCount('tsol')` unchanged by a Challenge award; `rbNext()` never returns a Challenge ribbon; medal case shows "100 ribbons to earn" on a fresh state; backup round-trip (`makeBackup` → `applyBackup`) keeps `S.ch`.
- [ ] Step 2: run → FAIL. Step 3: implement. Step 4: `python3 tests/challenges_test.py all` and `python3 tests/goal_test.py all` → OK. Bump `sw.js`, commit, push, check Vercel status.
