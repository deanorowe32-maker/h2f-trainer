"""Ruck & Run: plan a route on the map (tap, loop, name, save), track it with GPS (distance, distance left, off-route,
pause), finish and save (log entry), history, resume after reload, backup. Map tiles are stubbed. Server on :8765."""
import sys, math
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
LAT, LNG = 34.6617, -98.4029
def off(lat, lng, dn, de):  # metres north/east
    return lat + dn / 111320, lng + de / (111320 * math.cos(math.radians(lat)))
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, geolocation={'latitude': LAT, 'longitude': LNG, 'accuracy': 6}, permissions=['geolocation'])
    pg = ctx.new_page(); E = pg.evaluate
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.route('https://tile.openstreetmap.org/**', lambda r: r.fulfill(status=404, body=''))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
    E("localStorage.clear();sessionStorage.setItem('h2f.boot','1');localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    pg.add_style_tag(content='#rbSheet{display:none!important}')
    E("S.rk={seen:0};document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='ruck';render()"); pg.wait_for_timeout(1200)
    check('Ruck & Run is a Train section', E("GROUPS[1][2].includes('ruck')") and E("!!document.querySelector('.subnav [data-v=ruck]')"))
    check('map loads from the bundled Leaflet', E("!!window.L&&L.version") == '1.9.4' and E("!!document.querySelector('#gMap.leaflet-container')"))
    check('privacy and map credit shown', 'OpenStreetMap contributors' in E("document.getElementById('view').textContent"))
    # Plan
    pg.click('[data-a=gplan]'); pg.wait_for_timeout(1500)
    bx = pg.query_selector('#gMap').bounding_box()
    check('plan map is tall enough to use', bx['height'] >= 300)
    for dx, dy in [(90, 100), (250, 100), (250, 260)]:
        pg.mouse.click(bx['x'] + dx, bx['y'] + dy); pg.wait_for_timeout(150)
    check('tapping the map adds points', E("gp.pts.length") == 3)
    check('distance and time estimate update', E("document.getElementById('gpD').textContent") != '0.00 mi' and 'About' in E("document.getElementById('gpT').textContent"))
    pg.click('[data-a=gundo]'); check('undo removes the last point', E("gp.pts.length") == 2)
    E("document.getElementById('gMap').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300); bx = pg.query_selector('#gMap').bounding_box()
    pg.mouse.click(bx['x'] + 250, bx['y'] + 260); pg.wait_for_timeout(150)
    pg.click('[data-a=gloop]'); check('loop to start closes the route', E("gp.pts.length") == 4 and E("JSON.stringify(gp.pts[0])==JSON.stringify(gp.pts[3])"))
    pg.click('[data-a=gsave]'); check('a name is required', 'name' in E("document.getElementById('gpErr').textContent"))
    pg.fill('#gpName', 'Test loop'); pg.click('[data-a=gsave]'); pg.wait_for_timeout(600)
    check('route saved and picked', E("S.gps.routes.length") == 1 and E("S.gps.sel") == E("S.gps.routes[0].id") and 'Test loop' in E("document.querySelector('.gsel').textContent"))
    # Swap in a small known square loop (~60 m sides) so the walk is quick
    sq = [(0, 0), (60, 0), (60, 60), (0, 60), (0, 0)]
    pts = [list(off(LAT, LNG, n, e)) for n, e in sq]
    E(f"S.gps.routes[0].pts={pts};render()"); pg.wait_for_timeout(600)
    rlen = E("gLen(S.gps.routes[0].pts)")
    check(f'route length measured (got {rlen:.0f} m)', 235 < rlen < 245)
    # Track: walk the loop at about 6 m/s, one fix a second
    pg.click('[data-a=gstart]'); pg.wait_for_timeout(1200)
    check('tracking screen shows time, distance, pace and left', all(E(f"!!document.getElementById('{i}')") for i in ['gtT', 'gtD', 'gtP', 'gtL']))
    def walk(a, c, step=6):
        n = max(1, round(math.dist(a, c) / step))
        for k in range(1, n + 1):
            f = k / n; la, lo = off(LAT, LNG, a[0] + (c[0] - a[0]) * f, a[1] + (c[1] - a[1]) * f)
            ctx.set_geolocation({'latitude': la, 'longitude': lo, 'accuracy': 6}); pg.wait_for_timeout(1000)
    walk(sq[0], sq[1]); walk(sq[1], sq[2])
    left_mid = E("rt.left")
    check(f'distance left counts down on a loop (got {left_mid:.0f} m)', 90 < left_mid < 150)
    # off route: drift 70 m east of the third corner, then come back
    walk(sq[2], (60, 130), 7)
    check('off-route warning', 'Off route' in E("document.getElementById('gtS').textContent"))
    walk((60, 130), sq[2], 7)
    walk(sq[2], sq[3]); walk(sq[3], sq[4])
    m = E("rt.m")
    check(f'distance tracked (got {m:.0f} m incl. 140 m detour)', 330 < m < 430)
    check(f'nothing left at the finish (got {E("rt.left"):.0f} m)', E("rt.left") < 20)
    pg.click('[data-a=gpause]'); m1 = E("rt.m"); walk(sq[0], (0, 40));
    check('paused: no distance added', abs(E("rt.m") - m1) < 1)
    pg.click('[data-a=gpause]')
    # Reload mid-track offers resume
    E("rtSave()"); pg.reload(); pg.wait_for_timeout(900); pg.add_style_tag(content='#rbSheet{display:none!important}')
    E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='ruck';render()"); pg.wait_for_timeout(600)
    check('after a reload it offers to resume', E("!!document.querySelector('[data-a=gresume]')"))
    pg.click('[data-a=gresume]'); pg.wait_for_timeout(800)
    check('resumed with distance kept', E("rmode") == 'track' and E("rt.m") > 300)
    E("rt.start-=120000")  # make it longer than a minute so it logs
    pg.click('#gFinBtn'); check('finish needs a second tap', E("rmode") == 'track' and 'again' in E("document.getElementById('gFinBtn').textContent"))
    pg.click('#gFinBtn'); pg.wait_for_timeout(800)
    check('done screen with summary', E("rmode") == 'done' and 'done' in E("document.querySelector('#view h2').textContent"))
    pg.click('[data-a=gkeep]'); pg.wait_for_timeout(600)
    r = E("S.gps.runs[0]")
    check('run saved with track', E("S.gps.runs.length") == 1 and r['kind'] == 'ruck' and r['lb'] == 35 and len(r['pts']) >= 4 and r['m'] > 300)
    check('logged as a workout', E("S.hist[0].type").startswith('Ruck · ') and '35 lb' in E("S.hist[0].type"))
    check('history lists it', 'Ruck 35 lb' in E("document.getElementById('view').textContent"))
    check('unfinished copy cleared', E("localStorage.getItem('h2f.rt')") is None)
    # Run and units
    pg.click('[data-a=gkind][data-v=run]'); check('Run mode hides ruck weight', not E("!!document.getElementById('gLb')") and 'Start run' in E("document.getElementById('view').textContent"))
    pg.click('[data-a=gunit]'); check('kilometres', 'km' in E("document.querySelector('#view .list').textContent"))
    # Backup
    c = E("cleanBackup(makeBackup()).gps")
    check('backup keeps routes and runs', len(c['routes']) == 1 and len(c['runs']) == 1 and c['u'] == 'km' and c['kind'] == 'run')
    check('a loop track keeps its shape when saved', len(E("gSimp([[0,0],[0,.001],[.001,.001],[.001,0],[0,0]],4)")) == 5)
    check('backup drops junk', E("JSON.stringify(gpsClean({routes:[{id:'x',n:'a',pts:[[999,0]]}],runs:[{id:'y'}],lb:900}))") == '{"u":"mi","kind":"ruck","trail":true,"lb":35,"sel":"","routes":[],"runs":[]}')
    check('page fits the screen', E("document.documentElement.scrollWidth") <= 390)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
