"""Watching the app tour video to the end earns the red, white and blue Orientation ribbon. Server on :8765."""
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
    try:
        check('ribbon exists, in Unit', E("!!RB_BY.vid&&RB_BY.vid.area==='Unit'"))
        check('red, white and blue', E("(()=>{const c=new Set(RB_BY.vid.stripes.map(s=>s[1]));return c.size===3&&c.has('sc')&&c.has('wh')&&c.has('ro')})()"))
        check('listed in the medal case', E("RB_SHOW.some(r=>r.id==='vid')"))
        E("tourShow()"); pg.wait_for_timeout(300)
        # skipping to the end does not count
        E("tourTick(0,85);tourTick(84,85);tourTick(85,85)")
        check('skipping to the end does not earn it', not E("!!S.rb.aw.vid"))
        # watching most of it does
        E("tourShow();for(let t=0;t<=80;t+=.25)tourTick(t,85)"); pg.wait_for_timeout(1300)
        check('video is wired up', E("!!document.querySelector('#tourBody video')"))
        check('watching to the end earns it', E("!!S.rb.aw.vid"))
        check('earned once', E("rbCount('vid').n") == 1)
        check('kept in backup', E("cleanBackup(makeBackup()).rb.tally.vid") == 1)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
