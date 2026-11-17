"""Heat water guide (Fuel), Talk to someone (Mind), Live a value this week (Spirit). Server on :8765."""
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
        # --- heat guide: TB MED 507 (12 Apr 2022) Table 1
        exp = {(1,0):('NL','½'),(1,2):('40/20','¾'),(1,3):('20/40','1'),(2,2):('30/30','1'),(2,3):('15/45','1'),(3,0):('NL','¾'),(3,3):('10/50','1'),(4,1):('50/10','¾'),(4,2):('20/40','1'),(5,0):('NL','1'),(5,1):('20/40','1'),(5,2):('15/45','1'),(5,3):('10/50','1')}
        check('heat table matches TB MED 507', all(tuple(E(f"HEAT[{c-1}].w[{w}]")) == v for (c, w), v in exp.items()))
        check('flag colors', E("HEAT.map(h=>h.flag)") == ['White', 'Green', 'Yellow', 'Red', 'Black'])
        E("S.tab='nut';render()"); pg.wait_for_timeout(200)
        E("document.querySelector('[data-a=heatcat][data-v=\"4\"]').click()"); pg.wait_for_timeout(100)
        E("document.querySelector('[data-a=heatwork][data-v=\"2\"]').click()"); pg.wait_for_timeout(100)
        txt = pg.locator('#heatRes').inner_text()
        check('result shows water and work/rest', '1 quart' in txt and '0.95 L' in txt and 'Work 20 min, rest 40 min' in txt)
        g = pg.locator('#heatGuide').inner_text()
        check('caps shown', '1½ quarts an hour' in g and '12 quarts a day' in g)
        check('source cited', 'TB MED 507' in g)
        check('choice remembered', E("[S.heat.c,S.heat.w]") == [4, 2])
        # --- mind support
        E("S.tab='mind';render()"); pg.wait_for_timeout(150)
        m = E("document.getElementById('view').innerText")
        check('mind has talk to someone', 'Talk to someone' in m and '844-702-5495' in m and '855-422-7719' in m)
        E("document.querySelector('[data-a=mood][data-v=\"0\"]').click()"); pg.wait_for_timeout(150)
        check('low mood brings support up front', E("(()=>{const h=[...document.querySelectorAll('#view h3')].map(x=>x.innerText);return h.indexOf('Talk to someone')===1})()"))
        E("S.tab='spirit';render()"); pg.wait_for_timeout(150)
        check('spirit support keeps new numbers', '855-422-7719' in E("document.getElementById('view').innerText"))
        # --- live a value
        check('asks for values first', 'Pick up to three values' in pg.locator('#vaSec').inner_text())
        E("S.spirit.values=['Respect','Faith','Courage'];render()"); pg.wait_for_timeout(150)
        E("document.querySelector('[data-a=vapick][data-v=\"Respect\"]').click()"); pg.wait_for_timeout(100)
        pg.fill('#vaTxt', 'Thank someone by name'); E("document.querySelector('[data-a=vaset]').click()"); pg.wait_for_timeout(150)
        check('commitment saved for this week', E("S.spirit.va.cur.v") == 'Respect' and E("S.spirit.va.cur.wk") == E("chWeekStart(today())"))
        an0 = E("rbCount('an').n")
        E("document.querySelector('[data-a=vadone]').click()"); pg.wait_for_timeout(150)
        check('done counts as a spirit check-in', E("S.spirit.va.cur.done") == E("today()") and E("rbCount('an').n") == an0 + 1)
        check('done shown', 'Done' in pg.locator('#vaSec').inner_text())
        E("S.spirit.va.cur.wk='2026-01-05';render()")
        check('new week rolls the old one into history', E("S.spirit.va.cur") is None and E("S.spirit.va.hist.length") == 1)
        c = E("cleanBackup(makeBackup()).spirit.va")
        check('backup keeps values in action', c and len(c['hist']) == 1 and c['hist'][0]['v'] == 'Respect')
        cj = E("vaClean({cur:{wk:'x',v:'Respect',t:'a'},hist:[{wk:'2026-01-05',v:'<b>x</b>',t:'a'},{wk:'2026-01-05',v:'Faith',t:'ok',done:'bad'}]})")
        check('clean drops junk', cj == {'cur': None, 'hist': [{'wk': '2026-01-05', 'v': 'Faith', 't': 'ok', 'done': ''}]})
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
