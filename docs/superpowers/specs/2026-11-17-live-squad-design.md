# Live squad (Supabase) — design (approved 2026-11-17)

## Intent
Soldiers' weekly summaries reach their leader without copying and pasting
codes. The leader's roster and squad challenge board update on their own.

## Goals
- Leader creates a squad and gets a join code; Soldiers join once with it.
- A joined Soldier's summary (same opt-in fields as today's code) is sent
  automatically when the app opens, at most once an hour, plus "Send now".
- Leader sees the live roster and the challenge board, can remove a Soldier
  and reset the join code.
- Soldier can leave; leaving deletes their row on the server.
- Existing paste codes keep working as a fallback.

## Non-goals
- No email or password accounts. No messaging, no leader-to-Soldier PT plan
  sync (codes still do that). No roll-up of several squads (codes still do).

## Anti-goals
- Anyone other than the squad's leader able to read a Soldier's summary.
- Journals, notes, rehab details or anything outside the opt-in summary sent.
- A server outage breaking the app: everything else keeps working offline.

## Constraints
- Supabase free plan: one project, region US East (us-east-1) *(my call: US
  Army data stored in the US is easier to defend to S6)*. Free
  projects pause after 7 days idle; the client must tolerate a slow first
  call and failures, and retry on next open.
- The app stays a single static file; the publishable (anon) key is public.
- Privacy wording changes to "Only what you choose to share, only with your
  leader."

## Approaches
1. **Locked tables + server functions with device keys (picked).** Tables
   have row-level security on and no policies, so nothing is readable
   directly. All access goes through a handful of database functions that
   check a secret device key (stored hashed). No Supabase Auth settings
   needed, so nothing has to be switched on by hand in the dashboard.
2. Supabase anonymous sign-in + row-level security policies. Needs the
   anonymous sign-in setting enabled in the dashboard (not available through
   the connector) and more complex policies.
3. Our own server (Edge Functions). More code to write, host and secure.

## Design
**Identity.** Each phone makes two random 32-byte keys on first use: a member
key and a leader key. The server stores only SHA-256 hashes. *(My calls,
from the builder check:)* keys and squad links live in their own storage
key (`h2f.cloud`), **not** in `S` and **not** in backup codes, so a leaked
backup can't expose a squad and restoring a backup never changes squad
membership. A Soldier on a new phone rejoins with the code. A leader can
copy a separate **leader key** (with a warning) to take the squad to a new
phone. One phone leads at most one squad and is a member of at most one.

**Consent.** Joining shows the exact fields that will be sent, using the
existing Include choices, and needs a tap on "Share these with <squad>".
Changing a choice later sends the new summary straight away, so turned-off
fields disappear from the server copy.

**Roster control.** No join approval: new members appear marked "New" and
the leader can remove them. A removed phone is blocked from rejoining that
squad. Limits: 60 members a squad, names up to 40 characters, summaries up
to 8 KB.

**Retention.** Leader can delete the squad (removes every row). Each server
call also deletes members not updated for 60 days and squads whose leader
has not opened them for 180 days. Leaving deletes the member's row.

**Leader's phone.** Live members are cached in their own storage key, not in
backups, for offline viewing. If a pasted member has the same name as a live
one, the newer summary wins. Live members count on the challenge board and
the roll-up dashboard.

**Tables** (`public`, RLS on, no policies, no grants to anon):
- `squads(id uuid pk, name text ≤40, join_code text unique, leader_hash text,
  created_at)`
- `members(id uuid pk, squad_id fk on delete cascade, member_hash text,
  name text ≤40, summary jsonb ≤8 KB, updated_at, joined_at,
  unique(squad_id, member_hash))`

**Functions** (security definer, fixed search_path, execute granted to anon):
`create_squad(name, leader_key) → {squad_id, join_code}`,
`reset_code(squad_id, leader_key) → join_code`,
`join_squad(code, member_key, name) → {squad_id, squad_name}`,
`push_summary(squad_id, member_key, name, summary) → updated_at`,
`leave_squad(squad_id, member_key)`,
`leader_roster(squad_id, leader_key) → rows (id, name, summary, updated_at)`,
`remove_member(squad_id, leader_key, member_id)`,
`member_status(squad_id, member_key) → squad_name or null (removed)`,
`delete_squad(squad_id, leader_key)`.
Join codes: 8 characters from an unambiguous alphabet, shown as `XXXX-XXXX`.
Wrong keys or codes return nothing and raise no detail.

**Client.** RPC over `fetch` to `/rest/v1/rpc/<fn>` with the publishable key.
Summaries from the server go through the existing `sqClean` before display,
like pasted codes. Leader's live members show beside pasted ones, marked
"Live", and feed the challenge board. A leader can be a member of another
squad at the same time.

## Left to the builder
Exact copy, layout inside the Squad sheet, retry timing, tests (mock the
server in the browser tests; test the SQL functions directly).
