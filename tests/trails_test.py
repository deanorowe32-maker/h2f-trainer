"""Follow trails: planned legs bend along paths from the route function (stubbed), distance follows the path,
waiting leg blocks save, failures fall back to straight, switch off = straight, out-and-back reuses legs, save keeps waypoints."""
import sys, json, math
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
calls = []; mode = {'v': 'ok', 'delay': 0}
def handle(route):
    req = route.request
    if req.method == 'OPTIONS': return route.fulfill(status=204, headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'})
    body = json.loads(req.post_data or '{}'); calls.append(body)
    if mode['v'] == 'fail': return route.fulfill(status=429, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}, body='{"error":"limit"}')
    a, b = body['pts']
    mid = [(a[0] + b[0]) / 2 + 0.002, (a[1] + b[1]) / 2 + 0.002]   # bent detour
    route.fulfill(status=200, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}, body=json.dumps({'pts': [a, mid, b], 'm': 1}))
with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={'width': 390, 'height': 844}, geolocation={'latitude': 49.70, 'longitude': 11.93, 'accuracy': 6}, permissions=['geolocation'])
    pg = ctx.new_page(); E = pg.evaluate
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.route('https://tile.openstreetmap.org/**', lambda r: r.fulfill(status=404, body=''))
    pg.route('**/functions/v1/route', handle)
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
    E("localStorage.clear();sessionStorage.setItem('h2f.boot','1');localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    pg.add_style_tag(content='#rbSheet{display:none!important}')
    E("S.rk={seen:0};document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='ruck';render()"); pg.wait_for_timeout(1200)
    check('privacy note mentions openrouteservice', 'openrouteservice' in E("document.getElementById('view').textContent"))
    pg.click('[data-a=gplan]'); pg.wait_for_timeout(1500)
    check('Follow trails switch on by default', E("document.querySelector('[data-a=gtrail]').checked"))
    bx = pg.query_selector('#gMap').bounding_box()
    pg.mouse.click(bx['x'] + 90, bx['y'] + 100); pg.wait_for_timeout(150)
    pg.mouse.click(bx['x'] + 250, bx['y'] + 260); pg.wait_for_timeout(800)
    check('one request for one leg', len(calls) == 1 and len(calls[0]['pts']) == 2)
    check('leg follows returned path', E("Array.isArray(gp.legs[1])&&gp.legs[1].length==3") and E("gPath().length") == 3 and E("JSON.stringify(gPath()[0])!==JSON.stringify(gPath()[1])"))
    straight = E("gLen(gp.pts)"); bent = E("gLen(gPath())")
    check(f'distance uses the path ({straight:.0f} → {bent:.0f} m)', bent > straight + 50)
    # waiting leg blocks save
    held = []
    def slow(route):
        if route.request.method == 'OPTIONS': return handle(route)
        held.append(route)
    pg.unroute('**/functions/v1/route'); pg.route('**/functions/v1/route', slow)
    pg.mouse.click(bx['x'] + 250, bx['y'] + 120); pg.wait_for_timeout(200)
    check('waiting leg shows finding paths', 'Finding' in E("document.getElementById('gpT').textContent"))
    pg.fill('#gpName', 'Trail')
    dis=E("document.querySelector('[data-a=gsave]').disabled"); E("gAct('gsave')"); cnt=E("S.gps.routes.length"); msg=E("document.getElementById('gpErr').textContent")
    check(f'cannot save while waiting ({dis},{cnt},{msg})', dis and cnt == 0 and 'finding' in msg)
    for r in held: handle(r)
    pg.wait_for_timeout(800)
    check('leg arrives', E("Array.isArray(gp.legs[2])"))
    pg.unroute('**/functions/v1/route'); pg.route('**/functions/v1/route', handle)
    # failure → straight + note
    mode['v'] = 'fail'
    pg.mouse.click(bx['x'] + 120, bx['y'] + 200); pg.wait_for_timeout(800)
    check('failed leg falls back to straight', E("gp.legs[3]") is None and 'straight' in E("document.getElementById('view').textContent"))
    mode['v'] = 'ok'
    pg.click('[data-a=gundo]'); check('undo trims legs', E("gp.legs.length") == 3)
    n0 = len(calls)
    pg.click('[data-a=gback]'); pg.wait_for_timeout(300)
    check('out and back reuses legs, no new requests', len(calls) == n0 and E("gp.pts.length") == 5 and E("Array.isArray(gp.legs[4])&&Array.isArray(gp.legs[3])"))
    check('return leg is reversed', E("JSON.stringify(gp.legs[4][0])==JSON.stringify(gp.pts[3])"))
    pg.click('[data-a=gsave]'); pg.wait_for_timeout(600)
    r = E("S.gps.routes[0]")
    check('saved route keeps waypoints and path', r and len(r['wp']) == 5 and len(r['pts']) > 5 and r['tr'] is True)
    check('backup keeps waypoints', E("gpsClean(JSON.parse(JSON.stringify(S.gps))).routes[0].wp.length") == 5)
    # edit re-fetches legs
    n1 = len(calls)
    E("gAct('gedit',S.gps.routes[0].id)"); pg.wait_for_timeout(1000)
    check('editing reopens waypoints and refetches', E("gp.pts.length") == 5 and len(calls) - n1 == 4)
    # switch off → straight
    pg.click('[data-a=gtrail]'); pg.wait_for_timeout(200)
    check('switch off makes straight lines', E("S.gps.trail") is False and E("gPath().length") == 5)
    E("document.getElementById('gMap').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300); bx = pg.query_selector('#gMap').bounding_box()
    pg.mouse.click(bx['x'] + 200, bx['y'] + 150); pg.wait_for_timeout(400)
    check(f'no requests with switch off ({len(calls)-n1}, pts {E("gp.pts.length")})', len(calls) - n1 == 4 and E("gp.pts.length") == 6)
    check('no page errors', not errs)
    if errs: print(errs)
    br.close()
print('ALL PASS' if not fails else f'{len(fails)} FAIL'); sys.exit(1 if fails else 0)
