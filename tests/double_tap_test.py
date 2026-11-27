"""Quick double taps on water and plate buttons count twice and don't zoom. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails=[]
def check(n,ok):
    print(('PASS ' if ok else 'FAIL ')+n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=3);pg=c.new_page();E=pg.evaluate
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/');pg.wait_for_timeout(400)
    E("localStorage.clear();sessionStorage.setItem('h2f.boot','1');localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')");pg.reload();pg.wait_for_timeout(1500)
    E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true)");pg.add_style_tag(content='#rbSheet{display:none!important}')
    check('buttons use touch-action manipulation',E("getComputedStyle(document.querySelector('button')).touchAction")=='manipulation')
    E("S.tab='nut';render()");pg.wait_for_timeout(400)
    sel='[data-a=hyd][data-v="1"]'
    if E(f"!!document.querySelector('{sel}')"):
        n0=E("S.hyd.n");pg.locator(sel).first.scroll_into_view_if_needed();pg.tap(sel);pg.wait_for_timeout(60);pg.tap(sel);pg.wait_for_timeout(300)
        check('double tap adds two cups',E("S.hyd.n")==n0+2)
    g='.g4g-g';pg.locator(g).scroll_into_view_if_needed();g0=E("(g4gS()[today()]||'').length")
    pg.tap(g);pg.wait_for_timeout(60);pg.tap(g);pg.wait_for_timeout(300)
    check('double tap adds two Green items',E("(g4gS()[today()]||'').length")==g0+2)
    check('page not zoomed',E("visualViewport.scale")==1)
    check('no errors '+';'.join(errs),not errs)
    b.close()
print('RESULT '+('OK' if not fails else 'FAIL %d'%len(fails)));sys.exit(1 if fails else 0)
