"""Sleep bed/wake times + rhythm + caffeine cut-off, Go for Green plate check + folded heat guide, and backup keeps them. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    E = pg.evaluate
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
    E("localStorage.clear();sessionStorage.setItem('h2f.boot','1');localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true)")
    pg.add_style_tag(content='#rbSheet{display:none!important}')  # ribbon pop-ups are covered by their own tests
    # --- Sleep
    E("S.tab='sleep';render()"); pg.wait_for_timeout(200)
    pg.fill('#sl_b', '22:45'); pg.fill('#sl_w', '06:15'); pg.dispatch_event('#sl_w', 'input')
    check('bed/wake fills hours across midnight', pg.input_value('#sl_h') == '7.5')
    pg.click('[data-a=slsave]'); pg.wait_for_timeout(200)
    check('night saves bed and wake times', E("JSON.stringify([S.sleep.log[today()],S.sleep.meta[today()].b,S.sleep.meta[today()].w])") == '[7.5,"22:45","06:15"]')
    E("[[1,'23:30','07:45',8.25],[2,'00:30','06:00',5.5]].forEach(([o,bb,ww,h])=>{const k=slKey(o);S.sleep.log[k]=h;S.sleep.meta[k]={r:0,c:false,s:false,b:bb,w:ww}});render()"); pg.wait_for_timeout(200)
    r = E("slRhythm()")
    check('wake spread 06:00 to 07:45 = 105 min', r['w'] == 105)
    check('bedtime spread treats 00:30 as late (22:45 to 00:30 = 105 min)', r['b'] == 105)
    check('short of 7 h counts only short nights (5.5 -> 1.5 h)', r['short'] == 1.5 and r['n'] == 3)
    t = E("document.querySelector('.slrh').textContent")
    check('rhythm card shows spreads and shortfall', '1h 45m' in t and 'a bit uneven' in t and '1.5 h' in t)
    E("S.sleep.wake='06:00';S.tab='today';render()"); pg.wait_for_timeout(200)
    check('Today shows caffeine cut-off (4:15 PM for a 6:00 wake)', 'Last caffeine by 4:15 PM' in E("document.querySelector('.tdcut').textContent"))
    check('caffeine line sits inside the sleep text, not on top of it', E("document.querySelector('.tdcut').parentElement.matches('.tdcard p.tag')") and E("document.querySelectorAll('.tdgrid .tdcard')[0].querySelectorAll(':scope > p').length") == 1)
    # --- Fuel
    E("S.tab='nut';render()"); pg.wait_for_timeout(200)
    check('heat guide folded by default', E("!document.getElementById('heatGuide').open"))
    for c in 'ggyr': pg.click(f'[data-a=g4g][data-v={c}]'); pg.wait_for_timeout(60)
    check('plate check counts taps', E("S.nut.g4g[today()]") == 'ggyr' and E("document.querySelector('[data-v=g] b').textContent") == '2')
    check('today summary 50% Green', '4 items, 50% Green' in E("document.getElementById('g4gSum').textContent"))
    check('week bar drawn', E("!!document.querySelector('.g4gbar')"))
    pg.click('[data-a=g4gundo]'); pg.wait_for_timeout(100)
    check('undo removes last item', E("S.nut.g4g[today()]") == 'ggy')
    E("document.getElementById('heatGuide').open=true"); pg.wait_for_timeout(100)
    pg.click('[data-a=heatcat][data-v="3"]'); pg.wait_for_timeout(150)
    check('heat guide stays open and works after picking a flag', E("document.getElementById('heatGuide').open") and 'Category 3' in E("document.getElementById('heatGuide').textContent"))
    # --- Backup
    c = E("cleanBackup(makeBackup())")
    check('backup keeps bed/wake', c['sleepMeta'][E("today()")]['b'] == '22:45')
    check('backup keeps plate check', c['nut']['g4g'][E("today()")] == 'ggy')
    check('backup drops junk', E("(()=>{const o=JSON.parse(makeBackup().slice(BK_TAG.length));o.nut.g4g={'2026-01-01':'gxz','bad':'g'};return JSON.stringify(cleanBackup(BK_TAG+JSON.stringify(o)).nut.g4g)})()") == '{}')
    check('page fits the screen', E("document.documentElement.scrollWidth") <= 390)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
