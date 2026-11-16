````
/make-plan Redesign the H2F Trainer interface layer (repo /home/claude/h2f-trainer, single-file index.html). Current design failed a Dieter Rams audit at 16/30 with weak scores (1/3) on #3 aesthetic, #4 understandable, #9 environmentally friendly and #10 as little design as possible.

Verdict paragraph:
> The app's purpose and content are sound, but at 16/30 (below the 20 refine threshold) its presentation needs a structural redesign of the interface layer: the type/spacing system, the Train screen order and the labels, not a feature rewrite.

Why redesign and not refine: the total is below the 20-point threshold, driven by the type/spacing system and the Train screen structure rather than by isolated details.

Preserve from current design:
- Brand tokens: dark green ink, gold accent, H2F shield logo (CSS custom properties at the top of index.html, header.top line 86).
- Five-tab bottom navigation (Today, Train, Rehab, Readiness, Unit), nav.tabs line 100.
- All data in localStorage (S.*): no migration; every existing plan, weight, photo and ribbon must survive.
- Honesty notes: AFT "Unofficial estimate" (2663), FM 7-22 overview note (2613).
- Dark mode and prefers-reduced-motion support.

Discard:
- Builder-first Train layout (title, subtitle, focus chips, "How this works", format chips above the exercises). Evidence: index.html 1529–1537. Caused failure on #2 and #10.
- Abbreviated labels "Aero/Anaer" (1508), section codes "W1/M1/C1" (1484), bare "%" box (1473). Caused failure on #4.
- Ad-hoc type sizes (17 distinct, 10.5–34 px) and off-grid spacing (1, 3, 5, 7, 9, 11, 13 px). Caused failure on #3.
- Cut-off horizontal jump-chip rows on Rehab and Readiness. Caused failure on #4.

Top moves from the audit:
1. #4 Understandable: full focus names, drop W/M/C codes, "% max" label, wrap chip rows. Evidence: index.html 1508, 1484, 1473.
2. #2 Useful / #10 Little design: Train opens on the day's exercises; builder controls fold into "Edit this day"; remove the big title + subtitle. Evidence: 1529–1537.
3. #3 Aesthetic: 6-step type scale (12, 14, 16, 18, 24, 32) and a 4 px spacing grid.
4. #8 Thorough: Readiness "7–9 h target" to ≥4.5:1 contrast at ≥12 px; 8 tap targets to ≥44 px.
5. #5 Unobtrusive: drop the header subtitle.

Redesign principles in priority order:
1. #2 Useful: a Soldier opening Train sees today's first exercise without scrolling.
2. #4 Understandable: every label readable by a new Soldier without a legend.
3. #10 As little design as possible: one navigation level per screen beyond the tab bar.

Deliverables for the plan:
- New Train screen order (low-fi, compared to current)
- Type and spacing tokens in one CSS block
- States checklist (empty, error, success, focus, disabled) re-verified per tab
- No data migration (UI only); verify with an existing localStorage snapshot
- Cutover: ship in one deploy; old layout is not kept behind a flag

Anti-patterns to guard against:
- Porting old structure under new styling
- Keeping both layouts behind a flag
- Following a trend instead of the principles above
- Touching features or data while restyling
````
