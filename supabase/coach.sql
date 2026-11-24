-- H2F Coach daily caps. Only the coach edge function (service role) touches this; no client access.
create table if not exists public.coach_use (
  day date not null,
  who text not null,
  n int not null default 0,
  primary key (day, who)
);
alter table public.coach_use enable row level security;
revoke all on public.coach_use from anon, authenticated;

-- Counts one question for each key and returns the new counts. Keys: 'd:<device>', 'i:<ip>', 'all'.
create or replace function public.coach_hit(p_keys text[])
returns table (who text, n int)
language sql
security definer
set search_path = public
as $$
  insert into public.coach_use as c (day, who, n)
  select (now() at time zone 'utc')::date, k, 1 from unnest(p_keys) as k
  on conflict (day, who) do update set n = c.n + 1
  returning c.who, c.n;
$$;
revoke all on function public.coach_hit(text[]) from public, anon, authenticated;
grant execute on function public.coach_hit(text[]) to service_role;

-- keep two weeks only
create or replace function public.coach_prune() returns void language sql security definer set search_path = public as $$
  delete from public.coach_use where day < (now() at time zone 'utc')::date - 14;
$$;
revoke all on function public.coach_prune() from public, anon, authenticated;
grant execute on function public.coach_prune() to service_role;
