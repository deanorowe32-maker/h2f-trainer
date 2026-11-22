"""Goal test editor: each event's exercise can be chosen from the library (search + Choose), or typed. Server on :8765."""
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
    E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='assess';gtDraft=gtToDraft(null);render()"); pg.wait_for_timeout(300)
    check('each event has a Choose from library button', E("document.querySelectorAll('[data-a=gtpick]').length") == E("gtDraft.ev.length") >= 1)
    pg.fill('#gtName', 'Air Assault prep')
    pg.click('[data-a=gtpick][data-i="0"]'); pg.wait_for_timeout(300)
    check('library picker opens', not E("document.getElementById('pickSheet').hidden") and 'Pick event 1' in E("document.getElementById('pickBody').textContent"))
    check('rows say Choose', E("document.querySelector('#pickList [data-a=pick]').textContent") == 'Choose')
    pg.fill('#pickQ', 'plank'); pg.dispatch_event('#pickQ', 'input'); pg.wait_for_timeout(200)
    nm = E("EX[document.querySelector('#pickList [data-a=pick]').dataset.v].name")
    check('search filters the library', 'plank' in nm.lower())
    pg.click('#pickList [data-a=pick]'); pg.wait_for_timeout(300)
    check('picker closes', E("document.getElementById('pickSheet').hidden"))
    check('chosen exercise fills the event', pg.input_value('#gtEvName0') == nm)
    check('other typed fields kept', pg.input_value('#gtName') == 'Air Assault prep')
    check('button now says Change', 'Change' in E("document.querySelector('[data-a=gtpick][data-i=\"0\"]').textContent"))
    pg.fill('#gtEvName0', 'Ruck march 12 mi'); check('typing your own still works', pg.input_value('#gtEvName0') == 'Ruck march 12 mi')
    E("S.tab='train';render()"); pg.wait_for_timeout(200)
    check('picker for Train still adds', E("openPick('train','M');document.querySelector('#pickList [data-a=pick]').textContent") == 'Add')
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
