"""App tour is the tutorial video. Server on :8765."""
import sys, os, re
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
check('video and poster files exist, video under 12 MB', os.path.exists('video/tour.mp4') and os.path.exists('video/tour.jpg') and os.path.getsize('video/tour.mp4') < 12e6)
sw = open('sw.js').read()
check('service worker leaves video requests to the network', re.search(r"/video/", sw) is not None)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(800)
    E = pg.evaluate
    E("localStorage.setItem('h2f.access',CODE_HASH);showGate(false);tourMaybe()"); pg.wait_for_timeout(300)
    check('first unlock shows the tour video', not pg.locator('#tourSheet').is_hidden() and pg.locator('#tourSheet video[src*="video/tour.mp4"]').count() == 1)
    check('video has a poster, controls and plays inline', E("(v=>!!v&&v.poster.includes('video/tour.jpg')&&v.controls&&v.playsInline)(document.querySelector('#tourSheet video'))"))
    pg.click('#tourSheet [data-a=tourdone]'); pg.wait_for_timeout(450)
    check('done closes it and remembers', pg.locator('#tourSheet').is_hidden() and E("localStorage.getItem('h2f.tour')==='1'"))
    E("tourMaybe()"); pg.wait_for_timeout(100)
    check('does not show again', pg.locator('#tourSheet').is_hidden())
    E("S.tab='unit';render()"); pg.click('#view [data-a=touropen]'); pg.wait_for_timeout(200)
    check('App tour in Unit opens the video', not pg.locator('#tourSheet').is_hidden() and pg.locator('#tourSheet video').count() == 1)
    E("const v=document.querySelector('#tourSheet video');v.muted=true;v.play().catch(()=>{})"); pg.wait_for_timeout(300)
    pg.click('#tourSheet [data-a=tourdone]'); pg.wait_for_timeout(200)
    check('closing stops playback', E("!document.querySelector('#tourSheet video')||document.querySelector('#tourSheet video').paused"))
    pg.click('#view [data-a=touropen]'); pg.wait_for_timeout(200)
    E("const v=document.querySelector('#tourSheet video');v.muted=true;v.play().catch(()=>{})"); pg.wait_for_timeout(300)
    E("document.getElementById('tourSheet').hidden=true"); pg.wait_for_timeout(200)
    check('swiping the drawer away also stops playback', E("document.querySelector('#tourSheet video').paused"))
    for w,h in [(1440,900),(1920,1080),(390,844),(390,667)]:
        pg.set_viewport_size({'width':w,'height':h}); pg.wait_for_timeout(100)
        # a closing sheet fades out before it is gone: decide on the hidden attribute, not on what is still painted
        if E("document.getElementById('tourSheet').hidden"):
            pg.wait_for_function("getComputedStyle(document.getElementById('tourSheet')).display==='none'", timeout=3000)
            pg.click('#view [data-a=touropen]')
        pg.wait_for_timeout(450)
        r = E("(()=>{const v=document.querySelector('#tourSheet video').getBoundingClientRect(),b=document.querySelector('#tourSheet [data-a=tourdone]').getBoundingClientRect(),p=document.querySelector('#tourSheet .panel').getBoundingClientRect();return {vw:v.width,vh:v.height,bb:b.bottom,pw:p.width,ih:innerHeight}})()")
        check(f'{w}x{h}: video box is tall like the video (no side bars)', abs(r['vh']/r['vw'] - 16/9) < 0.05)
        check(f'{w}x{h}: Start training is on screen without scrolling', r['bb'] <= r['ih'])
        check(f'{w}x{h}: video fits the drawer width', r['vw'] <= r['pw'])
    pg.set_viewport_size({'width':390,'height':844})
    check('old step tour is gone', E("typeof TOUR==='undefined'"))
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
