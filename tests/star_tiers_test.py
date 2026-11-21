"""Repeat stars: bronze for each repeat, silver for every 5, gold for every 25. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E = pg.evaluate
    st = lambda n: E(f"rbStars({n})")
    check('first earn: no stars', st(1) == {'gold':0,'silver':0,'bronze':0})
    check('3rd earn: 2 bronze', st(3) == {'gold':0,'silver':0,'bronze':2})
    check('6th earn: 1 silver', st(6) == {'gold':0,'silver':1,'bronze':0})
    check('26th earn: 1 gold', st(26) == {'gold':1,'silver':0,'bronze':0})
    check('32nd earn: gold, silver, bronze', st(32) == {'gold':1,'silver':1,'bronze':1})
    check('devices show gold first', E("rbDevices(32).join('')") == 'gsb')
    svg = E("rbSvg('ff',300,32)")
    check('ribbon draws a gold, a silver and a bronze star', all(f'rbstar-{t}' in svg for t in 'gsb'))
    check('bronze star is bronze, not gold', E("(()=>{const d=document.createElement('div');d.innerHTML=rbSvg('ff',300,2);const g=d.querySelector('radialGradient[id^=b] stop[offset=\".5\"]');return g.getAttribute('stop-color')})()") != '#e3b23c')
    check('no page errors', not errs)
    b.close()
print('RESULT', 'FAIL '+str(len(fails)) if fails else 'OK'); sys.exit(1 if fails else 0)
