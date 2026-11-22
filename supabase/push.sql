-- Reminder notifications (applied 2026-11-20 via migrations push_reminders, push_reminders_cron, pg_net_extensions_schema).
-- The edge function supabase/functions/push/index.ts (deployed with verify_jwt off) creates its VAPID keys on first use.
create extension if not exists pg_cron;
create extension if not exists pg_net schema extensions;
create table if not exists public.push_subs (
  endpoint text primary key, p256dh text not null, auth text not null, tz text not null default 'UTC',
  wk_on boolean not null default false, wk_time text not null default '06:00', wk_days int[] not null default '{1,2,3,4,5}',
  bed_on boolean not null default false, bed_time text not null default '21:45', bk_on boolean not null default false,
  last_wk date, last_bed date, last_bk date, created_at timestamptz not null default now(), updated_at timestamptz not null default now());
create table if not exists public.push_config (k text primary key, v text not null);
alter table public.push_subs enable row level security;
alter table public.push_config enable row level security;
revoke all on public.push_subs from anon, authenticated;
revoke all on public.push_config from anon, authenticated;
insert into public.push_config(k,v) values ('cron_secret', encode(extensions.gen_random_bytes(24),'hex')) on conflict (k) do nothing;
select cron.schedule('h2f-push-tick', '*/5 * * * *', $$
  select net.http_post('https://ensaxbeodtpdlcqplzhy.supabase.co/functions/v1/push', '{"action":"tick"}'::jsonb, '{}'::jsonb,
    jsonb_build_object('Content-Type','application/json','x-cron-secret',(select v from public.push_config where k='cron_secret')));
$$);
-- AFT test date reminders (push_aft migration): a week before and the day before, at 0800 local.
alter table public.push_subs add column if not exists aft_on boolean not null default false;
alter table public.push_subs add column if not exists aft_date date;
alter table public.push_subs add column if not exists last_aft date;
