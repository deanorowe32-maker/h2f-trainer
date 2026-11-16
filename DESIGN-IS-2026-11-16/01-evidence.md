# Evidence

Measured with Playwright, 390×844 viewport, logged-in, default data (E = evid.py output).

## Structural
| Tab | Interactive elements | Max DOM depth | Page length (screens) | Headings | Words |
|---|---|---|---|---|---|
| Today | 28 | 6 | 2.4 | 8 | 217 |
| Train | 94 | 7 | 4.2 | 8 | 291 |
| Rehab | 71 | 6 | 3.8 | 5 | 335 |
| Readiness | 49 | 8 | 3.6 | 7 | 325 |
| Unit | 93 | 9 | 2.2 | 5 | 170 |

- Two navigation levels on every tab: bottom tab bar (`index.html` nav.tabs, line 100) plus a segmented control (Plan/Library/Test, Sleep/Fuel/Mind/Spirit, Unit/FM 7-22/About).
- Rehab and Readiness add a third row of horizontally scrolling jump chips that are cut off at the right edge ("Fo…", "Tonight's…"): screenshots /tmp/all.png.
- Train's first screen is builder settings (title "Weekly Workout Builder", subtitle, week picker, day strip, focus chips, "How this works", format chips) before the first exercise (index.html 1529–1537). The Today shortcut now scrolls past it, but opening Train from the tab bar still lands there.
- Repeated affordance: the week strip appears on both Today (1433) and Train (`weekBar()`/`strip('train')`, 1531) with different labels (Today: "Lower/Aero/Anaer"; Train: "Lower body/Aerobic/Anaerobic").

## Visual
- Font sizes rendered per tab: 13 (Today), 13 (Train), 13 (Rehab), 13 (Readiness), 7 (Unit). Union: 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 15, 15.5, 16, 17, 18, 20, 24, 26, 34 px = **17 sizes**.
- Spacing values rendered: up to 19 distinct per tab, including odd values 1, 3, 5, 7, 9, 11, 13 px (E).
- Distinct colors referenced per tab: 8–17 (E).
- Lowest real contrast: **3.23:1 for "7–9 h target" at 10.5 px on Readiness** (fails WCAG AA 4.5:1). Other low readings (1.01 on the selected day tile, 1.11 on the medal panel) are measurement artefacts of gradient backgrounds; visually they pass.
- Tap targets under 44×44 px: 8 on Readiness, 0 elsewhere (E).
- States: empty states present (exercise list "Nothing here yet", medal case, history); focus-visible rules: 10; disabled styling: 1 rule; dark mode: 7 `prefers-color-scheme` rules; reduced motion: 12 rules; `aria-live` regions: 12. Loading state: none needed (all local). Error states for photo upload not verified.

## Copy & honesty
- Disclaimers present and accurate: AFT "Unofficial estimate…" (2663), FM 7-22 "plain-language overview… use the current manual" (2613), README "not an official U.S. Army product".
- Inflation words in UI strings: "powerful" ×1, "perfect" ×1 (grep).
- Jargon / unclear labels: day abbreviations "Aero", "Anaer" (DSHORT, 1508); section codes "W1/M1/C1" with no legend (listFor, 1484); a bare "%" box next to Weight (itemRow, 1473) whose meaning (% of 1-rep max) only appears in its aria-label; "FM 7-22" as a tab label.
- No dark patterns found.

## Weight & friction
- Initial transfer: `index.html` 575 KB with all CSS/JS inline; 2 requests on first load; load event ≈ 690 ms locally (E).
- 29 `@keyframes` defined; **0 infinite animations** on any idle tab (E); motion gated by prefers-reduced-motion.
- Modals on load: 0 after unlock (access-code gate on first visit).

## Accessibility
- Landmarks: 1 header, 1 main, 2 nav. Skip link: none found.
- All primary actions are buttons or links (keyboard reachable). Focus-visible styles present.
- Contrast failure: see Visual.
