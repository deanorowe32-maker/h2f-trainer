```
/make-plan Fix the state backup in /home/claude/h2f-trainer/index.html. Two functions are both named idbOpen (line 1308 opens 'h2f-state' store 's'; line 4109 opens 'h2f-photos' store 'p'); hoisting makes the photo one win, so idbPut/idbRestore (1311–1312) never write the state copy. Rename to idbOpenState and idbOpenPhotos and update every call site (idbPut, idbRestore; phInit, phTx, phPut, phDelete, phSave, phRemove, phDeleteAll, refreshInfo at 4110–4137). Verify in a browser that indexedDB.databases() lists both h2f-state and h2f-photos after save(), and that photos still save and load. Flowchart: PATHFINDER-2026-11-16/01-flowcharts/storage-backup.md. Guard: no new storage layer, no migration, keep the existing db names.
```

```
/make-plan Unify the date-key helper in /home/claude/h2f-trainer/index.html: add dk(d) next to monday() (line 1327) and make dayKeyTs (1427), today (2257), rbDK (2307) and slKey (3038) one-line wrappers. Keep the old names as aliases. Verify ribbons, sleep log and history keys are unchanged for today's date. Guard: do not rename call sites; no date library.
```

```
/make-plan Make the Today week strip (schedHtml, index.html:1434) use full focus names from DTYPES (1235) instead of DSHORT abbreviations (1508), matching the Train strip (1472). Check the cells still fit at 390 px width. Flowchart: PATHFINDER-2026-11-16/01-flowcharts/weekly-plan-and-today.md. Guard: no merge of the two strip functions.
```
