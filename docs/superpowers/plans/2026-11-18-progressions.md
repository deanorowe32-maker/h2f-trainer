# Exercise Progressions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (chosen: native, as for the previous plan).

**Goal:** Easier and Harder lines on every exercise card. They come from built-in chains, with leader and Soldier edits layered on top.
**Architecture:** In `index.html`:
- `LAD_CHAINS` (ordered id arrays) gives built-in neighbors.
- `S.lad` holds the Soldier's own edits; `S.prog.ld` holds the leader's pushed edits.
- `ladFor(id)` resolves the options in priority order: own edits, then the program's, then built-in.
**Spec:** `docs/superpowers/specs/2026-11-18-progressions-design.md`
**Tests:** `tests/ladder_test.py` (same harness as `program_test.py`); server via `. /tmp/srv.sh`.

## Global Constraints
- Up to 3 options per line. Up to 40 exercise links in a pushed program. Edits stored as `{e:[ids], h:[ids]}`, and an id may not link to itself.
- New library exercises: `ipu` Incline Push-Up, `kpu` Knee Push-Up, `bapu` Band-Assisted Pull-Up, `npu` Negative Pull-Up. Text steps, no photo.
- Startup normalization calls only functions (hoisted) and consts defined earlier in the file.
- Bump `sw.js` once at the end. Commit lines end with the two attribution lines.

## Review Focus
1. A chain or edit that names a missing exercise never renders a dead link.
2. A Soldier's own edit survives loading a new program.
3. Custom-exercise links survive share and receive (ids are kept by receive).
4. kg/lb has no effect here (no loads).
5. Reopen with `S.lad` saved boots cleanly.

### Task 1: Ladder data and resolution
- Tests:
  - every chain id exists in `EX`;
  - `ladFor('pu')` is `{e:['kpu'],h:['hrpu']}`;
  - with `S.prog.ld={pu:{e:['ipu'],h:[]}}`, `ladFor('pu').e` is `['ipu']`;
  - with `S.lad.pu={e:['chsq'],h:['pplu']}`, the own edit wins;
  - `ladClean` drops unknown ids, self links, and anything past 3 per line;
  - the backup round trip keeps `lad`;
  - reload boots.
- Implement: `LAD_CHAINS`, the 4 exercises, `ladClean(o, known) -> {id:{e,h}}`, `ladFor(id) -> {e,h}`, `S.lad` normalization, and `BK_KEYS`/`cleanBackup`/`applyBackup`.

### Task 2: Card UI
- Tests:
  - the Push-Up card shows "Easier" with Knee Push-Up and "Harder" with Hand-Release Push-Up;
  - tapping a name opens that card;
  - Edit easier/harder → add via the picker (`pickKind='lad'`) → `S.lad` is updated;
  - × removes an option;
  - Reset deletes `S.lad[id]`;
  - an exercise with no ladder shows no lines but still offers Edit.
- Implement in `openInfo`: `ladHtml(id)`, edit mode `ladEd` (the card's id), and the actions `ladedit`, `ladadd` (data-k e/h), `ladrm`, `ladreset`, `laddone`.

### Task 3: Ladders travel
- Tests:
  - `prParse(prCode()).prog.ld` carries the leader's `S.lad`;
  - on a Soldier's phone, `ladFor` uses it, and the Soldier's own `S.lad` still wins;
  - `prClean` drops links to unknown ids and caps at 40;
  - a shared custom exercise with links → after receive, `S.lad[customId]` is set (unless the Soldier already has their own).
- Implement:
  - `prCode` adds `ld` (the leader's `S.lad` limited to links between resolvable ids);
  - `prClean` keeps `ld` via `ladClean`;
  - `xsEnc`/`xsDec` add optional `ld` for the exercises being shared;
  - `xsadd` applies `ld` to `S.lad` where missing.
