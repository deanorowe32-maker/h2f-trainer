"""Ruck & Run map opens where you are: asks for location on open, remembers the last fix, falls back to the phone's
time zone (Germany for Europe/Berlin, never a fixed US view), has a locate button, and explains when location is blocked."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
GRAF = {'latitude': 49.7167, 'longitude': 11.9064, 'accuracy': 10}
def page(b, **kw):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/Berlin', **kw)
    pg = ctx.new_page(); pg.route('https://tile.openstreetmap.org/**', lambda r: r.fulfill(status=404, body=''))
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    return ctx, pg, errs
def open_ruck(pg, clear=True):
    E = pg.evaluate
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(400)
    if clear: E("localStorage.clear()")
    E("sessionStorage.setItem('h2f.boot','1');localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(800)
    pg.add_style_tag(content='#rbSheet{display:none!important}')
    E("S.rk={seen:0};document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='ruck';render()"); pg.wait_for_timeout(2000)
with sync_playwright() as p:
    b = p.chromium.launch()
    # 1. Location allowed, in Grafenwoehr
    ctx, pg, errs = page(b, geolocation=GRAF, permissions=['geolocation']); E = pg.evaluate
    open_ruck(pg)
    c = E("[gm.getCenter().lat,gm.getCenter().lng,gm.getZoom()]")
    check(f'opens on your location in Grafenwoehr (got {c[0]:.3f},{c[1]:.3f} z{c[2]})', abs(c[0] - 49.7167) < .01 and abs(c[1] - 11.9064) < .01 and c[2] >= 15)
    check('last fix remembered on the phone', E("JSON.parse(localStorage.getItem('h2f.lastfix'))") == [49.7167, 11.9064])
    check('locate button on the map', E("!!document.querySelector('#gMap .gloc a')"))
    E("gm.setView([0,0],3)"); E("document.querySelector('#gMap .gloc a').click()"); pg.wait_for_timeout(1000)
    check('locate button brings you back', abs(E("gm.getCenter().lat") - 49.7167) < .01)
    pg.click('[data-a=gplan]'); pg.wait_for_timeout(1800)
    check('route planner also opens on you', abs(E("gm.getCenter().lat") - 49.7167) < .01 and abs(E("gm.getCenter().lng") - 11.9064) < .01)
    check('no page errors (allowed)', not errs)
    ctx.close()
    # 2. Location blocked, phone set to Berlin time
    ctx, pg, errs = page(b); E = pg.evaluate
    open_ruck(pg)
    c = E("[gm.getCenter().lat,gm.getCenter().lng,gm.getZoom()]")
    check(f'blocked: falls back to Germany, not the US (got {c[0]:.1f},{c[1]:.1f} z{c[2]})', 47 < c[0] < 55 and 6 < c[1] < 15)
    check('blocked: explains how to allow location', 'Location is blocked' in E("document.getElementById('gNote').textContent") and not E("document.getElementById('gNote').hidden"))
    check('no page errors (blocked)', not errs)
    ctx.close()
    # 3. Blocked now, but a fix was saved earlier: opens there
    ctx, pg, errs = page(b); E = pg.evaluate
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(300); E("localStorage.clear();localStorage.setItem('h2f.lastfix','[49.7167,11.9064]')")
    open_ruck(pg, clear=False)
    check('opens on the last known spot', abs(E("gm.getCenter().lat") - 49.7167) < .01 and E("gm.getZoom()") >= 15)
    check('time zone table never points Berlin at the US', E("gTzView()")[0] > 45)
    ctx.close(); b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
