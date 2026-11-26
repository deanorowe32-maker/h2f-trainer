// H2F Trainer trail routing. Snaps one planned leg (2 to 10 points) to walkable paths using openrouteservice
// "foot-hiking" (api.heigit.org; api.openrouteservice.org was retired with HTTP 410). The ORS key stays here as the ORS_KEY secret; the app never sees it.
// POST {pts:[[lat,lng],...]}  or  GET ?pts=lat,lng~lat,lng (";" also works)   ->  {pts:[[lat,lng],...], m:metres}
const ORIGINS = ["https://h2ftrainer.com", "https://www.h2ftrainer.com", "https://h2f-trainer.vercel.app", "http://localhost:8765"];
const PREVIEW = /^https:\/\/h2f-trainer-git-[a-z0-9-]+-h2-f-trainer\.vercel\.app$/;
const allowed = (o: string) => ORIGINS.includes(o) || PREVIEW.test(o);
function cors(req: Request) {
  const o = req.headers.get("origin") || "";
  return { "Access-Control-Allow-Origin": allowed(o) ? o : ORIGINS[0], "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "content-type", "Vary": "Origin" };
}
const json = (req: Request, body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { ...cors(req), "Content-Type": "application/json", "Cache-Control": "no-store" } });
const hav = (a: number[], b: number[]) => { const R = 6371000, t = Math.PI / 180, dLa = (b[0] - a[0]) * t, dLo = (b[1] - a[1]) * t, x = Math.sin(dLa / 2) ** 2 + Math.cos(a[0] * t) * Math.cos(b[0] * t) * Math.sin(dLo / 2) ** 2; return 2 * R * Math.asin(Math.min(1, Math.sqrt(x))); };
// best-effort burst limit per caller, per running instance (ORS also enforces 40/min and 2000/day on the key)
const hits = new Map<string, number[]>();
function limited(ip: string) { const now = Date.now(), h = (hits.get(ip) || []).filter((t) => now - t < 60000); h.push(now); hits.set(ip, h); if (hits.size > 5000) hits.clear(); return h.length > 30; }
function parse(raw: unknown): number[][] | null {
  if (!Array.isArray(raw) || raw.length < 2 || raw.length > 10) return null;
  const pts = raw.map((p) => Array.isArray(p) ? [Number(p[0]), Number(p[1])] : [NaN, NaN]);
  if (pts.some(([a, b]) => !Number.isFinite(a) || !Number.isFinite(b) || Math.abs(a) > 90 || Math.abs(b) > 180)) return null;
  let m = 0; for (let i = 1; i < pts.length; i++) m += hav(pts[i - 1], pts[i]);
  return m <= 30000 ? pts : null; // one leg, at most 30 km in a straight line
}
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: cors(req) });
  const o = req.headers.get("origin");
  if (o && !allowed(o)) return json(req, { error: "origin" }, 403);
  try {
    let raw: unknown = null;
    if (req.method === "GET") { const q = new URL(req.url).searchParams.get("pts") || ""; raw = q.split(/[;~|]/).filter(Boolean).map((s) => s.split(",")); }
    else if (req.method === "POST") raw = ((await req.json().catch(() => ({}))) as { pts?: unknown }).pts;
    else return json(req, { error: "method" }, 405);
    const pts = parse(raw); if (!pts) return json(req, { error: "points" }, 400);
    const ip = (req.headers.get("x-forwarded-for") || "").split(",")[0].trim() || "anon";
    if (limited(ip)) return json(req, { error: "busy" }, 429);
    const key = Deno.env.get("ORS_KEY"); if (!key) return json(req, { error: "no key" }, 503);
    const r = await fetch("https://api.heigit.org/openrouteservice/v2/directions/foot-hiking/geojson", {
      method: "POST", headers: { "Authorization": key, "Content-Type": "application/json", "Accept": "application/geo+json" },
      body: JSON.stringify({ coordinates: pts.map(([la, lo]) => [lo, la]), radiuses: pts.map(() => 350), instructions: false, elevation: false }),
      signal: AbortSignal.timeout(9000),
    });
    if (r.status === 429) return json(req, { error: "limit" }, 429);
    if (!r.ok) { const t = await r.text(); console.log("ors", r.status, t.slice(0, 400)); return json(req, { error: "router", status: r.status, detail: t.slice(0, 160) }, 502); }
    const g = await r.json(), f = g?.features?.[0];
    const line: number[][] = (f?.geometry?.coordinates || []).map((c: number[]) => [+c[1].toFixed(5), +c[0].toFixed(5)]);
    if (line.length < 2) return json(req, { error: "no route" }, 404);
    return json(req, { pts: line.slice(0, 2000), m: Math.round(f?.properties?.summary?.distance ?? 0) });
  } catch (e) {
    return json(req, { error: String(e).slice(0, 120) }, 500);
  }
});
