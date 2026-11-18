# Exercise progressions and regressions (short design)

**Intent:** a Soldier looking at an exercise can see easier and harder versions and step to them. A leader can tailor those ladders for the platoon.

**Where:** the exercise info card only. It gets two new lines under the steps and cue: **Easier** and **Harder**. Each holds up to 3 exercise names, and tapping a name opens that exercise's card.

**Approach (A, chosen):**
- Built-in ladders are ordered chains (easiest → hardest), for example `chsq → bws → gsq → bsq`. A card's Easier option is the step before it in a chain, and Harder is the step after. An exercise can be in more than one chain (Goblet Squat in squat and lunge chains), and options merge without duplicates.
- Edits are stored per exercise as `{e:[ids], h:[ids]}`, and replace that exercise's built-in options.
- Rejected:
  - B, easier/harder fields on all 295 exercise lines: a big diff, and the two directions drift apart.
  - C, editing whole chains: clumsy on a phone.

**Who decides, in order of priority:**
1. The Soldier's own edits, on their phone (`S.lad`).
2. The leader's edits, pushed with the Integrator program (`prog.ld`), applied while that program is loaded.
3. The built-in chains.

**Editing:**
- "Edit easier/harder" on the card opens a picker per line (add from the library, remove with ×) and "Reset to default".
- Custom exercises can have links too. Links on a custom exercise travel when it's shared, in the existing share format, as optional `ld`.

**Carried:**
- `S.lad` goes in backups.
- The leader's `S.lad` is copied into `prog.ld` when pushing. Only links between exercises the code can resolve are kept.

**Goals:** cards show ladders for most strength, bodyweight, core, carry, plyo and rehab moves; edits work as above.
**Non-goals:** swapping an exercise inside a planned workout (could come later); automatic progression over time.
**Anti-goals:** a link that opens a missing exercise; a Soldier's own edits overwritten by a push.

**Calls left to the builder:**
- Chains use only exercises that exist today. Where a common step is missing (Knee Push-Up, Incline Push-Up, Band-Assisted Pull-Up, Negative Pull-Up), add those few as new library exercises with text steps and no photo.
- Limits: 3 options per line, 40 links in a pushed program.
