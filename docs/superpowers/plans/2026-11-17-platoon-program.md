# Platoon Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A leader builds an 8-week platoon program on his phone and pushes it to Soldiers. Each Soldier sees the day's session, with their own weights, as a separate part of the app that never touches their own plan.

**Architecture:**
- The program lives in a new store, `S.prog`, with the Soldier's group in `S.grp`, inside the single-file PWA `index.html`.
- Leader and Soldier both use a new program sheet, opened from Train tools.
- A new per-day format `'p'` in the existing `S.fmt` arrays shows the program session on Train, Today, the week list and print.

**Tech Stack:** vanilla JS in `index.html`; Playwright (Python) tests in `tests/`; server via `. /tmp/srv.sh` (python http.server on :8765).

**Spec:** `docs/superpowers/specs/2026-11-17-platoon-program-design.md`

## Global Constraints

- Program = exactly 8 weeks × 5 weekdays (Mon–Fri). Block start is a Monday date key `YYYY-MM-DD` (as `mkey()` makes).
- Default focus per weekday (RTP microcycle): `['anaerobic','upper','lower','stretch','aerobic']`.
- RTP group table (lower is better for times):
  - shuttle A ≤60 s, B ≤66, C otherwise;
  - bench est. 1RM A ≥300 lb, B ≥225, C otherwise;
  - deadlift est. 1RM A ≥400, B ≥315, C otherwise;
  - ruck 1-mile split A ≤13:30 (810 s), B ≤14:15 (855 s), C otherwise.
- Group suggestion = majority of the entered results; a tie goes to the lower group (C below B below A).
- Est. 1RM from 5RM uses Epley: `w*(1+5/30)`, rounded with `wRound`.
- Weight line on a row: `"<pct>% → <w> <au()>"` when the row has a % and `maxOf(id)` returns a max. Otherwise `"<G> group: <rng[G]>"` when the Soldier has a group and the row has that range. Otherwise `''`. Never "NaN" or "undefined".
- Field limits:
  - name ≤ 60; rx ≤ 30; rest ≤ 12; each range ≤ 24; warm-up fields and cool down ≤ 200;
  - rows per day ≤ 15; rpe integer 1–10 or absent; pct 1–120 or absent.
- Code tag `H2FPROG1:`. Use short JSON keys (see Task 1).
- Loading a program must never change `S.plan`, `S.types` or `S.weeks[*].plan`.
- Startup normalization must not call anything defined later in the file. Use only inline checks there (the reopen crash lesson).
- Every new store: `BK_KEYS`, `cleanBackup`, `applyBackup`, startup normalization.
- Bump `sw.js` `c3a1e7m38` → `c3a1e7m39` once, in the last task.
- Commit messages end with the two attribution lines:
  - `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
  - `Claude-Session: https://claude.ai/code/session_014uyXh6zoA21sWb6tNM4t6o`

## Review Focus

1. **Custom exercises:** a program uses a leader's custom exercise the Soldier doesn't have. The code must carry it, as plan sharing does. Test in Task 4.
2. **Dates outside the block:** today is before the block start, after week 8, or a weekend. There is no program session, a `'p'` day falls back to the Soldier's own exercises, and the Program chip is hidden. Test in Task 5.
3. **kg unit:** a Soldier using kg sees % weights in kg. Range text shows as typed. Test in Task 1.
4. **Reopen:** reopening the app with a saved program boots cleanly (`BOOTED===true`). Test in Task 1.
5. **Bad codes:** a pasted code that is cut off or tampered with shows an error and changes nothing. Test in Task 4.

---

### Task 1: Program data core

**Files:**
- Modify: `index.html`. Add a program block next to the circuit helpers (after `ciPhases`). Also update the startup normalization (after the `S.dcir=` line), `BK_KEYS`, `cleanBackup` and `applyBackup`.
- Test: `tests/program_test.py` (new; same harness as `tests/circuit_test.py`).

**Interfaces:**
- Produces the shapes, using short keys:
  - Program: `{v:1, n:name, s:startKey, fr:from, w:[week×8]}`
  - Week: `{dl:bool, d:[day×5]}`
  - Day: `{f:focus, wu:{r,a,p}, cd, off:bool, r:[row]}`
  - Row: `{p:'P'|'M'|'A'|'C', id, rx, rs, rpe?, pct?, g?:{A,B,C}}`
  - The `p` codes are Power/Plyo, Main, Accessory and Conditioning.
- Produces `PR_FOCUS` (the default focus array), `PR_PART={P:'Power/Plyo',M:'Main',A:'Accessory',C:'Conditioning'}`.
- Produces `prClean(o, known?) -> program|null`. `known(id)` defaults to `id=>!!EX[id]`. Rows with unknown ids are dropped. It returns null unless there are exactly 8 weeks of 5 days and a valid start key.
- Produces `prBlank(name:string, start:string) -> program`.
- Produces `grpClean(o) -> {g:'A'|'B'|'C'|'', w0:{sh?,bp?,dl?,rk?}}`. All w0 values are positive numbers: sh = seconds, bp and dl = 5RM in `au()`, rk = mile split in seconds.
- Produces `grpSuggest(w0) -> 'A'|'B'|'C'|''`.
- Produces `prWeekOf(dateKey) -> 0..7` or `-1`. Produces `prDayAt(dateKey) -> day|null`, which is null on weekends, outside the block, or for an `off` day.
- Produces `prLoad(row) -> string`.

- [ ] **Step 1: Write the failing checks** in `tests/program_test.py` (Task 1 section):
  - `prBlank('RTP',mkey(0))` has 8 weeks, 5 days each, with focuses equal to `PR_FOCUS`.
  - `prClean` of that is deep-equal to it.
  - `prClean({})`, `prClean` with 7 weeks, and `prClean` with `s:'nope'` are all null.
  - A row `{p:'M',id:'zzz'}` is dropped.
  - `rx` is truncated to 30 characters; `rpe:11` is removed; `pct:'56'` becomes 56.
  - `grpSuggest({sh:58,bp:280,dl:420})` is `'A'`: A, B, A, so majority A.
  - `grpSuggest({sh:70,bp:310})` is `'C'`: a C and an A tie, and the tie goes to the lower group.
  - `grpSuggest({})` is `''`.
  - With `S.prog=prBlank('x',mkey(0))`:
    - `prWeekOf(mkey(0))` is 0;
    - `prWeekOf(mkey(8))` is -1;
    - `prDayAt` on a Saturday date is null.
  - `prLoad`:
    - `S.maxes.bench={v:300,u:'lb',d:today()}` with row `{p:'M',id:'bench',pct:50}` gives `'50% → 150 lb'`;
    - with no max, `S.grp.g='A'` and `g:{A:'185–150 lb'}` gives `'A group: 185–150 lb'`;
    - with no max and no group, it gives `''`.
  - With `S.assess.unit='kg'` and the max saved in kg, the line ends in `kg`.
  - `cleanBackup(makeBackup())` round-trips `prog` and `grp`.
  - Review Focus 4: after `S.prog=prBlank(...);save()` and a reload, `BOOTED===true` and `S.prog.n==='RTP'`.

- [ ] **Step 2: Run** `python3 tests/program_test.py`. Expected: FAIL (`prBlank is not defined`).

- [ ] **Step 3: Implement the functions above.**
  - `prLoad` uses `maxOf`, `wRound`, `au()` and `S.grp`.
  - Startup normalization:
    - `S.prog = S.prog ? prClean(S.prog, id=>typeof id==='string') : null`. Use the permissive `known` here because custom exercises load after this point.
    - `S.grp` defaults to `{g:'',w0:{}}`.
  - Add `'prog','grp'` to `BK_KEYS`. In `cleanBackup` set `out.prog` (via `prClean` with the backup's known set) and `out.grp`. In `applyBackup` copy both.

- [ ] **Step 4: Run** `python3 tests/program_test.py`. Expected: `RESULT OK`.

- [ ] **Step 5: Commit** `feat: platoon program data core`.

### Task 2: Program sheet (view) + Train tools entry + My group

**Files:**
- Modify: `index.html`:
  - a new `#pgSheet` beside `#ciSheet`;
  - a tools-list button after `#ciOpenBtn`;
  - a new click and input handler block after the circuit handlers.
- Test: `tests/program_test.py` (Task 2 section).

**Interfaces:**
- Consumes everything from Task 1.
- Produces:
  - `prOpen()`, which shows the sheet;
  - `prBody()`, which renders the sheet;
  - state `prWk` (the week index being viewed; defaults to `max(0,prWeekOf(today()))`, else 0);
  - `prDayHtml(day) -> string`, which shows the warm-up, rows grouped by part with `rx · rest · RPE n` and the `prLoad` line, and the cool down. Today reuses it in Task 5.
- Actions:
  - `data-a="propen"`: the tools button, label "Platoon program".
  - `prwk` (data-v week index), `prgrp` (data-v A/B/C/''), `pgclose`.
  - `prtoday`: "Start today's session". Closes the sheet and goes to Today. Shown only when `prDayAt(today())`.
- Input `data-f="prw0"` with `data-k` in `sh|bp|dl|rk`:
  - updates `S.grp.w0`;
  - shows `grpSuggest` as "Suggested: A group" with a `prgrp` button;
  - for bp and dl, also saves `S.maxes.bench` and `S.maxes.dl` as `{v:e1rm,u:au(),d:today()}`.
- Ruck split input: text `mm:ss`, parsed to seconds; an invalid entry is ignored.

- [ ] **Step 1: Write the failing checks:**
  - The tools order contains `,cibuild,propen,print`.
  - With no program, the sheet shows "Paste a program from your leader" and "Build a program".
  - With `S.prog=prBlank` and one row added in JS, the sheet shows "Week 1 of 8", the row's exercise name and `RPE 8`.
  - A week marked `dl:true` shows "Deload" on its week chip.
  - `prgrp` B sets `S.grp.g==='B'`.
  - Entering bp `250` saves `S.maxes.bench.v===wRound(250*(1+5/30))`.
  - Entering sh `58`, bp `280` and dl `420` makes the suggestion "A".

- [ ] **Step 2: Run.** Expected: FAIL.
- [ ] **Step 3: Implement.** Model the sheet markup and classes on `ciBuild`/`#ciSheet`.
- [ ] **Step 4: Run.** Expected: `RESULT OK`.
- [ ] **Step 5: Commit** `feat: platoon program sheet and My group`.

### Task 3: Leader editing

**Files:** Modify: `index.html` (program handler block). Test: `tests/program_test.py` (Task 3 section).

**Interfaces:**
- Consumes `prBody`, `prWk`, `PR_PART` and the exercise picker. Add `pickKind==='prog'`, which appends a row `{p:prPart, id, rx:RXC[EX[id].cat], rs:''}` to the day being edited.
- Actions:
  - `prnew`: `S.prog=prBlank('',mkey(0))`, after one confirm tap if a program exists.
  - `prday` (data-v day index): open the editor for that day.
  - `pradd` (data-sec P/M/A/C): opens the picker.
  - `prrm` / `prup` (data-i): remove a row / move it up.
  - `prcopy`: week `prWk-1` deep-copied into `prWk`. Hidden on week 1.
  - `prbump` (data-v ±1/±2/±5): every row in the week with a `pct` gets `pct+=v`, clamped 1–120.
  - `prdl`: toggle `dl`.
  - `proff`: toggle the day's `off`.
- Inputs:
  - `data-f="prf"` with `data-k` in `n|s|f|wur|wua|wup|cd`, for name, start, focus, the three warm-up fields and the cool down. `s` is a `<select>` of the Monday keys `mkey(-4..8)`.
  - `data-f="prr"` with `data-i` and `data-k` in `rx|rs|rpe|pct|gA|gB|gC`.
  - Each input is cleaned to the Global Constraints limits, then `save()`.

- [ ] **Step 1: Write the failing checks:**
  - `prnew` creates 8 weeks.
  - Add `bench` to Tue Main via the picker.
  - Set rx `3 x 12-15`, rest `60s`, rpe `8`, pct `50` and gA `185–150 lb`. `S.prog.w[0].d[1].r[0]` matches.
  - Moving to week 2 and pressing `prcopy`: week 2 equals week 1.
  - `prbump` +3 makes pct 53.
  - `prdl` sets `w[1].dl===true`.
  - `prup` reorders rows; `prrm` removes one.
  - rpe `0` is ignored and the field reverts.
  - The name is saved and appears in the header.

- [ ] **Step 2: Run.** Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run.** Expected: `RESULT OK`.
- [ ] **Step 5: Commit** `feat: platoon program editing`.

### Task 4: Push and load

**Files:** Modify: `index.html` (program handler block). Test: `tests/program_test.py` (Task 4 section).

**Interfaces:**
- Consumes `prClean` and `prBody`.
- Produces:
  - `prCode() -> string`: `'H2FPROG1:'+JSON.stringify(prog + {fr:S.squad.name, cu:[custom exercises used]})`. The custom exercise shape is the same as `ptMake().custom`.
  - `prParse(txt) -> program`. It throws an Error with a plain message ("This is not a program code." / "The program code looks cut off."). Custom exercises are cleaned the same way as in `ptClean` and are known for the row check.
  - `prApply(prog)`:
    - adds the missing custom exercises to `S.custom` and `EX`;
    - sets `S.progPrev=S.prog` and `S.prog=prog`;
    - sets `fmt[i]='p'` for every weekday inside the block: the current week's `S.fmt`, plus each existing `S.weeks[k].fmt` whose key falls inside the block;
    - leaves `plan` and `types` untouched;
    - saves and renders.
- Actions:
  - `prpush`: shows a textarea with `prCode()`, a Copy button, and a Share button through `navigator.share` when available. The message reads "Paste this in H2F Trainer: Train, Platoon program, Paste a program."
  - `prpaste`: a textarea and a Load button.
  - `prload`: calls `prParse` then `prApply`, or shows the error under the textarea.
  - `prundo`: restores `S.progPrev`. It shows only when `progPrev` exists.
  - `prdel`: removes the program after a confirm tap, and sets `'p'` days back to `'n'`.
- `progPrev` is not in `BK_KEYS`; Undo lives until the next load.

- [ ] **Step 1: Write the failing checks (two pages, A and B, as in `share_ex_test.py`):**
  - A builds a program with a custom exercise and the bench row; B pastes `prCode()` from A and loads it.
  - B's `S.prog.w[0].d[1].r[0].id==='bench'`, and B's custom exercise exists in `EX`.
  - B's `S.plan` is unchanged (JSON before equals after).
  - B's `S.fmt` in the block is `'p'`.
  - `prundo` restores B's previous program, or null.
  - Review Focus 5: loading the code with its last 20 characters cut shows "cut off", and `S.prog` is unchanged. Loading `H2FPT1:{}` shows "not a program code".
  - The code length for a full RTP-shaped block (8 weeks × 5 days × 6 rows) is under 30,000 characters.

- [ ] **Step 2: Run.** Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run.** Expected: `RESULT OK`.
- [ ] **Step 5: Commit** `feat: push and load platoon programs`.

### Task 5: "Program" workout format everywhere

**Files:**
- Modify: `index.html`:
  - the fmt chips in `viewTrain`;
  - the `fmt` handler and fmt normalizations: startup, `cleanBackup` weeks, `ptClean`, `ptWeekOut`. Accept `'p'`. In `ptWeekOut`/`ptClean`, send `'p'` as `'n'`, because programs travel only by program code.
  - `listFor`, the Today card, `monthHtml`, `tddone`, and `prHtml` `'train'` and `'mo'`.
- Test: `tests/program_test.py` (Task 5 section).

**Interfaces:**
- Consumes `prDayAt`, `prDayHtml` and `prOpen`.
- Produces:
  - `prDate(off,i) -> dateKey`, the date of weekday i in week offset off: `dk` of `monday(off)` plus i days;
  - `isPrW(w,i,off) -> bool`: `w.fmt[i]==='p'` and `prDayAt(prDate(off,i))`.
- Rules:
  - The chip "Program" shows on every focus, only when `prDayAt(prDate(S.week,S.day))`.
  - Selecting a chip sets `S.fmt[S.day]='p'`.
  - Stations and Circuit chips keep their upper/lower-only rule.
- Train `listFor` on a `'p'` day:
  - replaces all three sections with a "Program · Week N of 8" card;
  - shows `prDayHtml` and a button `propen` "Open program";
  - leaves the Soldier's own exercises untouched in `S.plan`.
- Today:
  - title `"<focus> · Program"`;
  - text "Week N of 8" plus " · Deload" on deload weeks;
  - `prDayHtml(day)` in place of the exercise rows;
  - the existing Mark workout done.
- `tddone` type text: `'Program · '+DTYPES[focus]`.
- Week list cell tag: `<i>Pr</i>`. The legend gains `"Pr" a program day`.
- Print:
  - `'train'`: a `'p'` day prints the program day's rows with rx, rest, RPE and the `prLoad` line.
  - `'mo'`: one line, "Program: <part names and exercise names>".
- Program sheet `prprint` ("Print block"): adds a `prHtml('pr')` kind that prints all 8 weeks, one page per week, with each day's rows, rx, rest, RPE and the A/B/C ranges.
- Days outside the block or on weekends behave as `'n'` everywhere (Review Focus 2).

- [ ] **Step 1: Write the failing checks:**
  - After `prApply` of a block starting `mkey(0)`, Train on a weekday shows "Program · Week 1 of 8" and the program row, while `S.plan[S.day]` is unchanged.
  - The chip list has `data-v=p` pressed.
  - Selecting Normal brings back the own exercises; selecting Program again shows the program.
  - If today is a weekday, Today shows "Week 1 of 8", and Mark done logs `S.hist[0].type` starting with `'Program · '`.
  - The week list HTML contains `<i>Pr</i>`.
  - `prHtml('train',false)` contains the program row's exercise name.
  - `prHtml('pr',false)` contains "Week 8" and the row's A range.
  - Review Focus 2: with a block starting `mkey(1)` (next week), the current week:
    - shows no Program chip;
    - shows the own exercises even though `S.fmt` is `'p'`;
    - Today shows the normal card.
  - `ptClean(ptMake()).fmt` contains no `'p'`.
  - Backup round trip keeps `'p'` in `fmt`.

- [ ] **Step 2: Run.** Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `python3 tests/program_test.py`, then every `tests/*.py`. Expected: all `RESULT OK`.
- [ ] **Step 5:**
  - Bump `sw.js` to `c3a1e7m39`.
  - Add a README line: Platoon program.
  - Commit `feat: Program workout format across Train, Today, week list and print`.
  - Push.
  - Check the Vercel status via `gh api repos/deanorowe32-maker/h2f-trainer/commits/<sha>/statuses`.
