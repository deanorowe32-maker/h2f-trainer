"""Weekly backup reminder on Today. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, permissions=['clipboard-read', 'clipboard-write']); pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E = pg.evaluate
    try:
        E("S.tab='today';render()")
        check('no reminder on a fresh install', pg.locator('#bkRemind').count() == 0)
        E("S.savedAt=Date.now()-86400000;render()")
        check('reminder once there is data', pg.locator('#bkRemind').count() == 1)
        E("document.querySelector('[data-a=bklater]').click()"); pg.wait_for_timeout(150)
        check('later hides it today', pg.locator('#bkRemind').count() == 0 and E("localStorage.getItem('h2f.bkLater')") == E("today()"))
        E("localStorage.removeItem('h2f.bkLater');render()")
        E("document.querySelector('[data-a=bknow]').click()"); pg.wait_for_timeout(300)
        check('copy records the backup', E("localStorage.getItem('h2f.bkAt')") == E("today()"))
        check('copy confirms on the card', 'copied' in pg.locator('#bkRemind').inner_text().lower())
        E("render()")
        check('gone after confirming', pg.locator('#bkRemind').count() == 0)
        check('copied a real backup code', E("navigator.clipboard.readText()").startswith('H2FBACKUP1:'))
        E("localStorage.setItem('h2f.bkAt',chDk(chMs(today())-6*864e5));render()")
        check('quiet for 6 days', pg.locator('#bkRemind').count() == 0)
        E("localStorage.setItem('h2f.bkAt',chDk(chMs(today())-7*864e5));render()")
        check('back after 7 days', pg.locator('#bkRemind').count() == 1 and '7 days' in pg.locator('#bkRemind').inner_text())
        E("openBackup();document.getElementById('bkCopyBtn').click()"); pg.wait_for_timeout(300)
        check('Unit backup copy counts', E("localStorage.getItem('h2f.bkAt')") == E("today()"))
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
