"""Add your exercise: start and finish photos can be picked in the same form. Server on :8765."""
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
    pg.evaluate("openForm('lib')")
    check('form has start and finish photo pickers', pg.locator('#nxPhA').count() == 1 and pg.locator('#nxPhB').count() == 1)
    pg.fill('#nxName', 'Test Lunge'); pg.fill('#nxSteps', 'Step\nReturn')
    pg.set_input_files('#nxPhA', '/tmp/a.png'); pg.set_input_files('#nxPhB', '/tmp/b.png')
    pg.wait_for_timeout(300)
    pg.click('[data-a="savex"]'); pg.wait_for_timeout(1200)
    id_ = pg.evaluate("(S.custom.find(c=>c.name==='Test Lunge')||{}).id")
    check('exercise saved', bool(id_))
    check('start and finish photos saved', pg.evaluate("id=>!!PH[id+':a']&&!!PH[id+':b']", id_))
    check('photos kept after reopen', (pg.reload(), pg.wait_for_timeout(1200), pg.evaluate("id=>!!PH[id+':a']&&!!PH[id+':b']", id_))[2])
    pg.evaluate("openForm('lib')"); pg.fill('#nxName', 'No Photo Move'); pg.fill('#nxSteps', 'Go')
    pg.click('[data-a="savex"]'); pg.wait_for_timeout(600)
    check('photos stay optional', pg.evaluate("S.custom.some(c=>c.name==='No Photo Move')"))
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
