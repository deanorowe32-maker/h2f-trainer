"""Audit fixes: own font (P1), two open copies (R1), one name per feature (D1), Squad up top (D2). Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
U = 'http://localhost:8765/'
def fresh(pg):
    pg.goto(U); pg.wait_for_timeout(500)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        # P1: the font comes with the app
        ctx = b.new_context(service_workers='block'); pg = ctx.new_page(); reqs = []
        pg.on('request', lambda r: reqs.append(r.url))
        fresh(pg); pg.wait_for_timeout(800)
        check('no request to Google Fonts', not any('fonts.g' in u for u in reqs))
        check('font file served by the app', any(u.startswith(U) and u.endswith('.woff2') for u in reqs))
        check('font loads', pg.evaluate("document.fonts.check('700 16px Manrope')") and pg.evaluate("[...document.fonts].some(f=>f.family.replace(/\"/g,'')==='Manrope'&&f.status==='loaded')"))
        ctx.close()
        # R1: two copies open
        ctx = b.new_context(); a = ctx.new_page(); fresh(a); c = ctx.new_page(); c.goto(U); c.wait_for_timeout(1000)
        a.evaluate("S.sleep.wake='04:44';save()"); c.wait_for_timeout(2500)
        check('other copy picks up the change', c.evaluate("typeof S!=='undefined'&&S.sleep.wake==='04:44'"))
        c.evaluate("S.aft.age='33';save()"); a.wait_for_timeout(2500)
        check('both changes kept', a.evaluate("(()=>{const x=JSON.parse(localStorage.getItem('h2f.v1'));return x.sleep.wake==='04:44'&&x.aft.age==='33'})()"))
        a.reload(); a.wait_for_timeout(900)
        check('both changes survive a reload', a.evaluate("S.sleep.wake==='04:44'&&S.aft.age==='33'"))
        ctx.close()
        # R1 follow-up: moving around (tab switches, no data change) must not make two copies reload each other
        ctx = b.new_context(); a = ctx.new_page(); fresh(a); c = ctx.new_page(); c.goto(U); c.wait_for_timeout(1000)
        n = {'a': 0, 'c': 0}
        a.on('load', lambda: n.__setitem__('a', n['a'] + 1)); c.on('load', lambda: n.__setitem__('c', n['c'] + 1))
        c.evaluate("S.tab='lib';render()"); c.wait_for_timeout(300); a.evaluate("S.tab='sleep';render();flushNow()"); c.wait_for_timeout(4000)
        check(f'no reload loop between two copies ({n})', n['a'] == 0 and n['c'] == 0)
        a.evaluate("S.sleep.wake='05:10';save()"); c.wait_for_timeout(2500)
        check('a real change still reaches the other copy, once', c.evaluate("S.sleep.wake") == '05:10' and n['c'] == 1)
        ctx.close()
        # D1 and D2
        pg = b.new_page(viewport={'width': 390, 'height': 844}); fresh(pg)
        pg.evaluate("S.tab='pt';render()"); pg.wait_for_timeout(200)
        txt = pg.evaluate("document.querySelector('main').innerText")
        check('recovery screen title', pg.evaluate("document.querySelector('main h2').textContent") == 'Recovery Training Plan')
        check('no PT-plan wording on the recovery screen', 'PT plan' not in txt and 'Injury PT' not in txt)
        check('tab bar says Recovery', 'Recovery' in pg.evaluate("document.querySelector('nav.tabs').innerText") and 'Rehab' not in pg.evaluate("document.querySelector('nav.tabs').innerText"))
        for t, lab in [('assess', 'Test'), ('nut', 'Fuel'), ('creator', None)]:
            pg.evaluate(f"S.tab='{t}';render()"); pg.wait_for_timeout(150)
            h = pg.evaluate("document.querySelector('main h2').textContent"); sub = pg.evaluate(f"SUBLAB['{t}']")
            check(f'{t}: switch label matches title ({sub} / {h})', h.lower().endswith(sub.lower()) or h.lower() == sub.lower())
        pg.evaluate("S.tab='unit';render()"); pg.wait_for_timeout(200)
        check('Squad sits above the medal case', pg.evaluate("document.querySelector('main [data-a=sqopen]').getBoundingClientRect().top < document.querySelector('#rbcase').getBoundingClientRect().top"))
        check('no visible Rehab wording left', 'Rehab' not in pg.evaluate("(()=>{let s='';['today','pt','unit','train'].forEach(t=>{S.tab=t;render();s+=document.body.innerText});return s})()"))
        # A1: tour video has captions
        pg.evaluate("tourShow()"); pg.wait_for_timeout(300)
        tr = pg.evaluate("(()=>{const t=document.querySelector('#tourBody video track');return t?[t.kind,t.getAttribute('src'),t.srclang,t.default]:null})()")
        check('tour video has an English captions track', bool(tr) and tr[0] == 'captions' and tr[2] == 'en')
        vtt = pg.evaluate("fetch('video/tour.vtt').then(r=>r.ok?r.text():'')")
        check('captions file is WebVTT with the opening line', vtt.startswith('WEBVTT') and 'This is H2F Trainer.' in vtt)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
