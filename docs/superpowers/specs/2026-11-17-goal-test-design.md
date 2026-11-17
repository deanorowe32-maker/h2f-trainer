# My goal test: design

## Intent
A Soldier designs their own fitness test as a personal training goal, presents it to their leader for buy-in, then trains and retests until they meet it. It gives Soldiers ownership of a goal (e.g. preparing for Air Assault) and a clean way to show a leader what they're working toward.

## Goals
- Build a test in a few minutes on a phone: name, why, target date, 1–6 events with a baseline and a goal each.
- Present it as a one-page summary: shown in person, sent as a link, or copied as plain text.
- Log retests and see progress per event and overall.
- Mark leader approval on trust ("Approved by SSG Smith, 17 Nov").

## Non-goals
- Leader verification or approval on the leader's own phone.
- Results syncing to a leader or a server (there is no server).
- Several active goal tests at once.
- Points or scoring tables like the AFT.

## Anti-goals
- Anything that looks like an official Army form or implies official approval. The summary says "Personal training goal" and the approval line is the Soldier's own entry.

## Approaches considered
1. **One active goal test under Train → Test (chosen).** A "My goal test" section next to the AFT scorer and CFT timer; finished or replaced tests move to "Past goal tests". Simple and focused.
2. A library of many tests. More flexible, but more screens and dilutes "this is my goal".
3. Custom events inside the AFT scorer. Fewest screens, but mixes an official test with a personal one.

## Decided with the user
- Approach 1.
- Approval is on trust: the Soldier types the leader's name and date.

## Builder's calls (Claude), open to correction
- **Events:** 1–6. Each is picked from the exercise library or typed in, with a measure: reps, time (m:ss, lower is better), weight (in the app's lb/kg unit) or distance (mi or km). Optional note per event (e.g. "35 lb ruck").
- **Retests:** date plus one value per event; skipped events allowed. Progress per event = latest vs baseline vs goal, shown as "225 → 255 of 275" and a bar. "Goal met" when every event reaches its goal.
- **Sharing:** a link that opens a read-only summary in the app, with the test packed into the link the same way exercise sharing works today (no server); a "Copy as text" version for a text message.
- **Ribbon:** "Own Standard" (Test area), earned when a goal test is fully met; repeatable.
- **Storage:** on the phone with everything else, included in backups.
- **Training link-up:** later, not now (could feed the Train focus card).
