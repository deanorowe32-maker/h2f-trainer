# Duplication report

| # | Concern | Locations | Why diverged | Verdict |
|---|---|---|---|---|
| D1 | IndexedDB opener named `idbOpen` declared twice | index.html:1308 (state, db `h2f-state`, store `s`), index.html:4109 (photos, db `h2f-photos`, store `p`) | Photo storage was added later with the same name; function hoisting makes the second win everywhere | **Accidental, and a live bug:** the data second-copy is never written (measured), so a cleared localStorage cannot be recovered |
| D2 | Local date key `YYYY-MM-DD` | index.html:1427 `dayKeyTs`, :2257 `today`, :2307 `rbDK`, :3038 `slKey` (also `mkey` :1509 for Mondays) | Each feature wrote its own | Accidental; identical logic ×4 |
| D3 | Weekday strip | index.html:1434 `schedHtml` (Today, DSHORT "Aero/Anaer", done ticks), :1472 `strip` (Train/PT, full labels, selection) | Today strip added separately | Mostly accidental: same 5 cells, different labels; the "Aero/Anaer" copy was flagged in the design audit (#4) |
| D4 | Bar/line charts | index.html:2940 `vzBars` (generic), :3059 `sleepChartHtml`, :3103 `moodChartHtml`, :2732 `ruTrend` | Sleep and mood charts predate `vzBars` | Partly legitimate (sleep chart has day selection, mood overlays sleep); consolidate later, not now |
| D5 | 250 ms ticking timers | index.html:3352 `ensureTick` (workout), :3761 stations `setInterval(stTick)`, :3130 grounding exercise | Different state machines | Legitimate specialization; keep |
| D6 | Share codes | index.html:2696 `sqCode`, :2769 `ptCode` (prefixed JSON), :3783 `xsEnc` (base64 JSON) | Different payloads and channels (copy/paste vs link) | Legitimate; keep |
