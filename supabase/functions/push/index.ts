// H2F Trainer reminder notifications.
// GET            -> { key }  the public application server key for pushManager.subscribe
// POST save      -> store this phone's subscription and reminder times (no names, no app data)
// POST delete    -> forget this phone
// POST tick      -> (cron only, x-cron-secret) send any reminders that are due
import { createClient } from "npm:@supabase/supabase-js@2";
import * as webpush from "jsr:@negrel/webpush@0.5.0";

const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const ORIGINS = ["https://h2ftrainer.com", "https://www.h2ftrainer.com", "https://h2f-trainer.vercel.app", "http://localhost:8765"];
const PUSH_HOSTS = [/(^|\.)fcm\.googleapis\.com$/, /(^|\.)push\.services\.mozilla\.com$/, /(^|\.)push\.apple\.com$/, /(^|\.)notify\.windows\.com$/];
const MSG = {
  wk: { title: "Today's workout is ready", body: "Open H2F Trainer and get after it.", url: "/#today" },
  bed: { title: "Time to wind down", body: "Lights out soon. Sleep is part of your training.", url: "/#sleep" },
  bk: { title: "Back up your data", body: "Copy a fresh backup code in Unit, Backup.", url: "/#unit" },
  on: { title: "Reminders are on", body: "H2F Trainer will remind you at the times you picked.", url: "/#unit" },
};

function cors(req: Request) {
  const o = req.headers.get("origin") || "";
  return {
    "Access-Control-Allow-Origin": ORIGINS.includes(o) ? o : ORIGINS[0],
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "content-type",
    "Vary": "Origin",
  };
}
const json = (req: Request, body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors(req), "Content-Type": "application/json" } });

async function conf(k: string) {
  const { data } = await db.from("push_config").select("v").eq("k", k).maybeSingle();
  return data?.v as string | undefined;
}
let server: webpush.ApplicationServer | null = null, appKey = "";
async function app() {
  if (server) return server;
  let raw = await conf("vapid");
  if (!raw) {
    const keys = await webpush.generateVapidKeys({ extractable: true });
    await db.from("push_config").upsert({ k: "vapid", v: JSON.stringify(await webpush.exportVapidKeys(keys)) }, { onConflict: "k", ignoreDuplicates: true });
    raw = await conf("vapid");
  }
  const keys = await webpush.importVapidKeys(JSON.parse(raw!), { extractable: true });
  appKey = await webpush.exportApplicationServerKey(keys);
  server = await webpush.ApplicationServer.new({ contactInformation: "mailto:h2ftrainer@h2ftrainer.com", vapidKeys: keys });
  return server;
}
const hm = (s: unknown) => typeof s === "string" && /^([01]\d|2[0-3]):[0-5]\d$/.test(s);
const tzOk = (tz: unknown) => { try { return typeof tz === "string" && tz.length < 64 && !!new Intl.DateTimeFormat("en-US", { timeZone: tz }); } catch { return false; } };
const pushOk = (u: unknown) => { try { const x = new URL(String(u)); return x.protocol === "https:" && PUSH_HOSTS.some((r) => r.test(x.hostname)) && String(u).length < 1000; } catch { return false; } };

async function send(row: { endpoint: string; p256dh: string; auth: string }, m: { title: string; body: string; url: string }) {
  const s = await app();
  try {
    await s.subscribe({ endpoint: row.endpoint, keys: { p256dh: row.p256dh, auth: row.auth } }).pushTextMessage(JSON.stringify(m), { ttl: 3600 });
    return "ok";
  } catch (e) {
    const st = (e as { response?: Response }).response?.status;
    if (st === 404 || st === 410) { await db.from("push_subs").delete().eq("endpoint", row.endpoint); return "gone"; }
    return "error " + (st || String(e).slice(0, 80));
  }
}

function local(tz: string, now: Date) {
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: tz, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", weekday: "short" }).formatToParts(now).map((x) => [x.type, x.value]));
  const dow = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].indexOf(p.weekday) + 1;
  return { date: `${p.year}-${p.month}-${p.day}`, min: +p.hour * 60 + +p.minute, dow };
}
const due = (min: number, t: string, last: string | null, date: string) => { const [h, m] = t.split(":").map(Number), at = h * 60 + m; return min >= at && min < at + 20 && last !== date; };

async function tick() {
  const now = new Date(); let sent = 0;
  const { data } = await db.from("push_subs").select("*").or("wk_on.eq.true,bed_on.eq.true,bk_on.eq.true").limit(5000);
  for (const r of data || []) {
    const L = local(r.tz, now), upd: Record<string, string> = {};
    if (r.wk_on && (r.wk_days || []).includes(L.dow) && due(L.min, r.wk_time, r.last_wk, L.date)) { if ((await send(r, MSG.wk)) === "gone") continue; upd.last_wk = L.date; sent++; }
    if (r.bed_on && due(L.min, r.bed_time, r.last_bed, L.date)) { if ((await send(r, MSG.bed)) === "gone") continue; upd.last_bed = L.date; sent++; }
    if (r.bk_on && L.dow === 7 && due(L.min, "18:00", r.last_bk, L.date)) { if ((await send(r, MSG.bk)) === "gone") continue; upd.last_bk = L.date; sent++; }
    if (Object.keys(upd).length) await db.from("push_subs").update(upd).eq("endpoint", r.endpoint);
  }
  return sent;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: cors(req) });
  try {
    if (req.method === "GET") { await app(); return json(req, { key: appKey }); }
    if (req.method !== "POST") return json(req, { error: "method" }, 405);
    const b = await req.json().catch(() => ({}));
    if (b.action === "tick") {
      if (!req.headers.get("x-cron-secret") || req.headers.get("x-cron-secret") !== (await conf("cron_secret"))) return json(req, { error: "forbidden" }, 403);
      return json(req, { sent: await tick() });
    }
    if (b.action === "delete") {
      if (!pushOk(b.endpoint)) return json(req, { error: "endpoint" }, 400);
      await db.from("push_subs").delete().eq("endpoint", b.endpoint);
      return json(req, { ok: true });
    }
    if (b.action === "save") {
      const s = b.sub || {}, p = b.prefs || {};
      if (!pushOk(s.endpoint) || typeof s.keys?.p256dh !== "string" || typeof s.keys?.auth !== "string" || s.keys.p256dh.length > 200 || s.keys.auth.length > 100) return json(req, { error: "subscription" }, 400);
      if (!tzOk(b.tz) || !hm(p.wk_time) || !hm(p.bed_time)) return json(req, { error: "times" }, 400);
      const days = Array.isArray(p.wk_days) ? [...new Set(p.wk_days.filter((d: unknown) => Number.isInteger(d) && (d as number) >= 1 && (d as number) <= 7))] : [1, 2, 3, 4, 5];
      const row = { endpoint: s.endpoint, p256dh: s.keys.p256dh, auth: s.keys.auth, tz: b.tz, wk_on: !!p.wk_on, wk_time: p.wk_time, wk_days: days, bed_on: !!p.bed_on, bed_time: p.bed_time, bk_on: !!p.bk_on, updated_at: new Date().toISOString() };
      const { error } = await db.from("push_subs").upsert(row, { onConflict: "endpoint" });
      if (error) return json(req, { error: "save" }, 500);
      const r = b.test ? await send(row, MSG.on) : "skipped";
      return json(req, { ok: true, test: r });
    }
    return json(req, { error: "action" }, 400);
  } catch (e) {
    return json(req, { error: String(e).slice(0, 120) }, 500);
  }
});
