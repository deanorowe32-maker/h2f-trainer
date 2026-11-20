"""The app tour (video) is removed: no drawer, no entry points, no pop-up after unlock, no video files. Server on :8765."""
import sys, os
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
check('video files removed', not os.path.exists('video/tour.mp4') and not os.path.exists('video/tour.jpg'))
check('service worker has no video rule', '/video/' not in open('sw.js').read())
src = open('index.html').read()
check('no tour code left', all(k not in src for k in ('tourSheet', 'touropen', 'tourdone', 'tourShow', 'tourMaybe', 'App tour')))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(800)
    pg.evaluate("localStorage.setItem('h2f.access',CODE_HASH)"); pg.reload(); pg.wait_for_timeout(1000)
    check('nothing pops up after unlock', pg.locator('.sheet:not([hidden])').count() == 0)
    pg.evaluate("S.tab='unit';render()"); pg.wait_for_timeout(200)
    check('Unit still renders', pg.locator('#view').inner_text().strip() != '')
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
