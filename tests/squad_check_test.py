"""Leader roster: Soldiers with flags (low sleep, no workouts, AFT below standard, old summary) are listed first under 'Check in first'; all-clear message otherwise. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
MON = "(()=>{const O=Date,off=new O('2026-11-25T09:00:00').getTime()-O.now();class D extends O{constructor(...a){super(...(a.length?a:[O.now()+off]))}static now(){return O.now()+off}};window.Date=D})()"
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); pg = ctx.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.add_init_script(MON)
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(300)
        pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(1000)
        E = pg.evaluate
        add = "(o)=>{const c=sqClean(o);c.k=(c.id||'x')+'-'+c.n.toLowerCase().replace(/[^a-z0-9]/g,'');S.squad.members.push(c)}"
        E(f"(()=>{{const add={add};S.squad.members=[];add({{v:1,n:'SPC Adams',d:'2026-11-24',tr:{{c:4}},sl:{{n:6,a:7.4,r:4}}}});add({{v:1,n:'PFC Zed',d:'2026-11-24',tr:{{c:3}},sl:{{n:5,a:7}}}});save()}})()")
        E("S.tab='unit';render();sqMode='sq';sqShow()"); pg.wait_for_timeout(500)
        check('all clear when nobody is flagged', 'All 2 on track' in E("document.querySelector('.sqcheck')?.textContent||''"))
        E(f"(()=>{{const add={add};add({{v:1,n:'SGT Brown',d:'2026-11-24',tr:{{c:0}},sl:{{n:5,a:5.2}}}});add({{v:1,n:'PV2 Cole',d:'2026-11-02',tr:{{c:2}}}});save();sqShow()}})()"); pg.wait_for_timeout(200)
        t = E("document.querySelector('.sqcheck')?.textContent||''")
        check('check-in count 2 of 4', 'Check in first: 2 of 4' in t)
        check('reasons listed', 'Sleep averaging 5.2 h' in t and 'No workouts finished' in t and 'Summary is 23 days old' in t)
        order = E("[...document.querySelectorAll('#sqBody details.cmx[id^=sqm-] summary b')].map(x=>x.textContent.split(' · ')[0])")
        check('flagged Soldiers come first', order[:2] == ['PV2 Cole', 'SGT Brown'] and order[2:] == ['PFC Zed', 'SPC Adams'])
        check('flagged cards carry a Check in tag', E("document.querySelectorAll('#sqBody details.sqatt .sqflag').length") == 2)
        check('name in list jumps to the card', E("!!document.getElementById(document.querySelector('.sqcrow').dataset.jump)"))
        check('no page errors', not errs)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
