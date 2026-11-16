# Scope

- **Audited:** H2F Trainer PWA, `index.html` (single file, ~575 KB) and `sw.js`, served locally and measured in a 390×844 phone viewport.
- **Screens:** the five bottom tabs at their default sub-view: Today, Train (Plan), Rehab (Injury PT Plan), Readiness (Sleep), Unit.
- **Primary user:** a US Army Soldier (or squad leader) using a phone, often between duties.
- **Primary task:** see today's workout and do it; secondary: log rehab, sleep, fuel, AFT score.
- **Constraints:** no build step, offline-capable PWA, plain HTML/CSS/JS, Army H2F vocabulary, independent and unofficial.
- **References:** none supplied.
- **Method:** source reading plus a Playwright script measuring every visible element per tab (`/home/claude/work/evid.py`). Evidence was gathered inline rather than with subagents to keep cost down; every number below cites that script or a source line.
