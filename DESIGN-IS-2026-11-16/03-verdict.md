# Verdict: REDESIGN (16/30)

The app's purpose and content are sound, but at 16/30 (below the 20 refine threshold) its presentation needs a structural redesign of the interface layer: the type/spacing system, the Train screen order and the labels, not a feature rewrite.

No principle scored 0. The redesign is scoped to the UI layer; the data model, features, honesty notes and brand stay.

## Highest-leverage moves
1. **#4 Understandable:** replace jargon labels: "Aero/Anaer" → full focus names; drop "W1/M1/C1" codes (the section headings already say Warm-up/Main/Cool-down); label the "%" box "% max"; wrap jump-chip rows instead of cutting them off. Evidence: index.html 1508, 1484, 1473; /tmp/all.png.
2. **#2 Useful / #10 Little design:** Train opens on the selected day's exercises; week picker stays, but the builder controls (focus chips, "How this works", format) fold into one "Edit this day" disclosure, and the 34 px "Weekly Workout Builder" title + subtitle go. Evidence: index.html 1529–1537; Train = 94 interactive elements, 4.2 screens.
3. **#3 Aesthetic:** collapse 17 font sizes to a 6-step type scale (12, 14, 16, 18, 24, 32) and snap spacing to a 4 px grid. Evidence: 01-evidence.md Visual.
4. **#8 Thorough:** fix Readiness "7–9 h target" contrast (3.23:1 at 10.5 px → ≥4.5:1 at ≥12 px) and enlarge its 8 sub-44 px tap targets. Evidence: evid.py Readiness.
5. **#5 Unobtrusive:** slim the sticky header (drop the "Holistic Health & Fitness" subtitle) so content starts higher. Evidence: header.top, index.html 86.
