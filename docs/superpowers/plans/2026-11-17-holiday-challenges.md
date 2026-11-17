# Holiday Challenges Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Steps use checkbox syntax.

**Goal:** 10 holiday challenges on the Challenges card with 8 new ribbons. **Spec:** `docs/superpowers/specs/2026-11-17-holiday-challenges-design.md`
**Architecture:** replace the hard-coded md/vd logic in `chSpecial`, `chSpecialHtml`, `chAct`, `chClean`, `rbChCount` with a `HOL` table. Tests extend `tests/challenges_test.py` as stage 4.

## Global Constraints
- Window ±3 days; holiday year owns the window; one holiday open at a time (no windows overlap).
- Existing ribbon ids `chmd`, `chvd`, stored `S.ch.sp['<y>-md']` and `stepup` logs keep working unchanged.
- Bump `sw.js`; README ribbon count 108.

## Review Focus
1. 30 Dec 2026 → New Year 2027 open, N = 27; 5 Jan 2027 → none.
2. Easter dates: 2027-03-28, 2028-04-16 (computus).
3. A backup with `sp['2027-xm']` holding 12 items restores; `sp['2027-zz']` dropped; a checklist key with the wrong item count is padded/trimmed to the holiday's count.
4. Holiday logs never change `chState().day/week/month` totals.
5. Army Birthday target in 2026 = 251 (Easy 126, Hard 377).

### Task 1: Holiday table, dates, counts, ribbons
**Produces:** `HOL` = `[{id, name, rb, kind:'list'|'total', key?, u?, date(y)->'YYYY-MM-DD', items?(y)->string[], t?(y)->[e,s,h], line}]`; `chEaster(y)->'YYYY-MM-DD'`; `chSpecial(d)->null|{id,year,date,from,to}` (checks years y−1..y+1); `chHolLevel(h,year)->0..3`; ribbon ids `chny, cheas, chab, chid4, chlab, chhw, chtg, chxm`; `rbChCount` handles every holiday ribbon via `chHolLevel>=1` per year.
- [ ] Stage 4 tests: Review Focus 1, 2, 3, 4, 5; `chSpecial('2026-11-26').id=='tg'`, `('2026-09-07').id=='lab'`, `('2026-10-31').id=='hw'`, `('2026-06-14').id=='ab'`; ribbon `chid4` awarded after 888 `hid4` reps in the 2027 window; `chxm` after marking 12 items + level; `RB_SHOW.length==108`. Run → FAIL. Implement. Run all stages → OK. Commit.
### Task 2: Card UI for any holiday
- [ ] Stage 4 UI tests: forcing `chSpecial` to Christmas renders 12 checklist chips and locked level buttons; forcing Thanksgiving renders a + Log row whose sheet logs to `htg` in km/mi; tribute/theme line present. Run → FAIL. Implement. Screenshot. Run all → OK. Ship.
