# Features

Single-file PWA: `index.html` (≈4,160 lines; CSS 1–897, data 932–1262, app JS 1263–4160) plus `sw.js` (cache-first offline shell). Discovery was done inline from section markers and the 318 top-level functions.

| Feature | Entry points | Core functions (index.html line) | Purpose |
|---|---|---|---|
| Shell & navigation | `render` 1716 | renderTabs 1371, subnavHtml 1382, jumpLinks 1393, groupView 1417, afterRender 1421 | Tabs, sub-tabs, jump chips, view switching |
| Storage & backup | `save` 1303, `init` 1293 | idbOpen 1308, idbPut 1311, idbRestore 1312, makeBackup 3423, cleanBackup 3441, applyBackup 3491 | localStorage state, IndexedDB second copy, file backup/restore |
| Weekly plan | `viewTrain` 1535 | genDay 1243, wkGo 1515, wkPack 1511, listFor 1488, itemRow 1482, lastW 1477 | Build each weekday's workout, weeks ahead/behind |
| Workout & stations timers | `openTimer` 3391, stations `stBtn` 3742 | tick 3353, renderTimer 3368, stTick 3734 | Run a workout, rest timer, station rotations |
| Today | `viewToday` 1437 | schedHtml 1434, startHtml 1464, streakHtml 1431 | Daily summary and shortcuts |
| Rehab / PT | `viewPT` 1557 | genPT 1269, body map bodyHtml 1606, bodyPick 1638 | Injury plans, tap-where-it-hurts finder |
| Exercise library & demos | `viewLib` 1587, `openInfo` 2158 | RAW 935, EX 1231, illHtml 2088, demoLink 1729, phSave 4128 | Exercise data, photos, YouTube/SmartWorkout demos, user photos |
| Readiness | viewSleep 3082, viewNut 3000, viewMind 3131, viewSpirit 3183 | sleepChartHtml 3059, nuChart 2970, moodChartHtml 3103 | Sleep, fuel, mind, spirit logging and charts |
| Assessment | `viewAssess` 3601 | aftScore 2636, pctW 3573, rmCalc 3625, runCalc 3636 | AFT scoring, 1RM and percentages |
| Ribbons | `rbCheck` 2443 | rbCount 2358, rbCaseHtml 2468, rbSvg 2453 | Awards and medal case |
| Squad & sharing | `sqHtml` 2813 | sqCode 2696, ptCode 2769, xsEnc 3783, shareHtml 3971, qrDraw 3979 | Squad readiness, sharing plans and exercises |
