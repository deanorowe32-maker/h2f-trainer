"""Exercise names you tap for steps are at least 44 px tall on Today, Train, Library and Recovery. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    # Today only lists exercises on a weekday, so pin the clock to Monday 23 Nov 2026
    pg.add_init_script("(()=>{const O=Date,off=new O('2026-11-23T09:00:00').getTime()-O.now();class D extends O{constructor(...a){super(...(a.length?a:[O.now()+off]))}static now(){return O.now()+off}};window.Date=D})()")
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    try:
        for t in ['today', 'train', 'lib', 'pt']:
            pg.evaluate(f"S.tab='{t}';render()"); pg.wait_for_timeout(200)
            r = pg.evaluate("(()=>{const b=[...document.querySelectorAll('main [data-a=info]')].map(e=>e.getBoundingClientRect()).filter(r=>r.width>0);return [b.length,Math.round(Math.min(...b.map(r=>r.height)))]})()")
            check(f'{t}: {r[0]} exercise buttons, smallest {r[1]} px', r[0] > 0 and r[1] >= 44)
        pg.evaluate("S.tab='today';render()"); pg.wait_for_timeout(200)
        h = pg.evaluate("document.querySelector('.tdrows .item').getBoundingClientRect().height")
        check(f'Today rows stay compact ({round(h)} px)', h <= 50)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
