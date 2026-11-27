"""Today ring deck: tap/swipe/dots flip Workout, Sleep, Water, Fuel; ticking still fills the workout ring;
rest-day recovery ring on weekends. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
SAT = """(()=>{const R=Date,F=new R('2026-11-28T10:00:00').getTime(),o=R.now();
class D extends R{constructor(...a){super(...(a.length?a:[F+(R.now()-o)]))}static now(){return F+(R.now()-o)}}window.Date=D})()"""
def boot(pg):
    E = pg.evaluate
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
    E("localStorage.clear();sessionStorage.setItem('h2f.boot','1');localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true)")
    pg.add_style_tag(content='#rbSheet{display:none!important}')
with sync_playwright() as p:
    b = p.chromium.launch()
    # --- weekday (Thursday)
    pg = b.new_page(viewport={'width': 390, 'height': 844}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.add_init_script("(()=>{const R=Date,F=new R('2026-11-26T10:00:00').getTime(),o=R.now();class D extends R{constructor(...a){super(...(a.length?a:[F+(R.now()-o)]))}static now(){return F+(R.now()-o)}}window.Date=D})()")
    boot(pg); E = pg.evaluate
    E("S.tab='today';render()"); pg.wait_for_timeout(300)
    has = E("!!document.querySelector('#rxdeck .reactor.rx-work')")
    check('weekday hero shows the workout ring in a deck', has)
    if has:
        check('four dots: Workout Sleep Water Fuel', E("[...document.querySelectorAll('.rxdot span')].map(x=>x.textContent).join()") == 'Workout,Sleep,Water,Fuel')
        pg.click('.tdchk >> nth=0'); pg.wait_for_timeout(150)
        check('ticking fills a workout segment', E("document.querySelectorAll('.rx-work .rx-seg.on').length") == 1)
        pg.click('#rxdeck .rxring'); pg.wait_for_timeout(200)
        check('tap flips to Sleep', 'sleep' in E("document.querySelector('#rxdeck .rx-core span').textContent"))
        pg.click('.rxdot >> nth=2'); pg.wait_for_timeout(200)
        check('dot jumps to Water 0/8', E("document.querySelector('#rxdeck .rx-core b').textContent") == '0/8')
        pg.click('#rxdeck .rxact [data-a=hyd]'); pg.wait_for_timeout(250)
        check('Add a cup fills the water ring and keeps Water showing', E("document.querySelector('#rxdeck .rx-core b').textContent") == '1/8' and E("document.querySelectorAll('#rxdeck .rx-seg.on').length") == 1)
        pg.locator('#rxdeck .rxring').scroll_into_view_if_needed(); pg.wait_for_timeout(100)
        bx = pg.locator('#rxdeck .rxring').bounding_box(); cx, cy = bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2
        pg.mouse.move(cx + 80, cy); pg.mouse.down(); pg.mouse.move(cx - 80, cy, steps=5); pg.mouse.up(); pg.wait_for_timeout(250)
        check('swipe left goes to Fuel', E("document.querySelector('.rxdot[aria-pressed=true] span').textContent") == 'Fuel')
        pg.mouse.move(cx - 80, cy); pg.mouse.down(); pg.mouse.move(cx + 80, cy, steps=5); pg.mouse.up(); pg.wait_for_timeout(250)
        check('swipe right goes back to Water', E("document.querySelector('.rxdot[aria-pressed=true] span').textContent") == 'Water')
        pg.click('.rxdot >> nth=0'); pg.wait_for_timeout(200)
        check('back on Workout keeps the tick', E("document.querySelectorAll('.rx-work .rx-seg.on').length") == 1)
    pg.close()
    # --- Saturday
    pg = b.new_page(viewport={'width': 390, 'height': 844}); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.add_init_script(SAT); boot(pg); E = pg.evaluate
    E("S.tab='today';render()"); pg.wait_for_timeout(300)
    check('weekend shows the recovery ring', E("!!document.querySelector('#rxdeck .reactor.rx-rest')") and 'Rest day' in E("document.querySelector('#tdhero').textContent"))
    check('recovery starts 0 of 4', E("document.querySelector('#rxdeck .rx-core b').textContent") == '0/4')
    pg.click('[data-a=rsttick][data-v=m]'); pg.wait_for_timeout(200)
    check('ticking mobility fills one segment', E("document.querySelectorAll('.rx-rest .rx-seg.on').length") == 1 and E("S.rest.m") is True)
    E("S.sleep.log[today()]=7.5;S.hyd.n=8;render()"); pg.wait_for_timeout(200)
    check('water and sleep count automatically (3 of 4)', E("document.querySelector('#rxdeck .rx-core b').textContent") == '3/4')
    check('recovery list shows 3 of 4', '3 of 4' in E("document.querySelector('#rstlist').textContent"))
    pg.close()
    check('no page errors: ' + '; '.join(errs), not errs)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
