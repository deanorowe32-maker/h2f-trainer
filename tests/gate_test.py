"""Lock screen: the access code box always accepts typing, on desktop too. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    E = pg.evaluate
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600); E("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(1000)
    check('code box has focus on open', E("document.activeElement.id") == 'gateCode')
    pg.keyboard.type('AB', delay=30)
    check('typing works without clicking first', pg.input_value('#gateCode') == 'AB')
    # a drawer left open behind the lock screen
    E("localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E("S.tab='unit';render()"); pg.click('#view [data-a=sqopen]'); pg.wait_for_timeout(300)
    E("localStorage.removeItem('h2f.access');showGate(true)"); pg.wait_for_timeout(300)
    check('locking closes drawers behind it', E("document.querySelectorAll('.sheet:not([hidden])').length") == 0)
    E("document.getElementById('sqSheet').hidden=false"); pg.wait_for_timeout(200)
    check('a drawer opening behind the lock screen does not take the cursor', E("document.activeElement.id") == 'gateCode')
    pg.keyboard.press('Tab'); pg.keyboard.press('Shift+Tab'); pg.wait_for_timeout(100)
    check('Tab stays on the lock screen', E("document.getElementById('gate').contains(document.activeElement)"))
    E("document.getElementById('gateCode').value=''"); pg.click('#gateCode'); pg.keyboard.type('XYZ', delay=30)
    check('typing works with a drawer open behind', pg.input_value('#gateCode') == 'XYZ')
    E("document.activeElement.blur()"); pg.click('#gate .mark'); pg.keyboard.type('Q', delay=30)
    check('clicking anywhere on the lock screen puts the cursor in the box', pg.input_value('#gateCode').endswith('Q'))
    check('share link uses the h2ftrainer.com address', E("APP_LINK") == 'https://h2ftrainer.com/')
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
