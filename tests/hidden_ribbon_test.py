"""Hidden ribbons: Open Door (email the developer) and Pass It On (share the app). Server on :8765."""
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
        shown = E("RB_SHOW.length")
        check('hidden until earned', not E("RB_SHOW.some(r=>r.id==='pio')") and E("RB.some(r=>r.id==='pio'&&r.area==='Hidden')"))
        E("S.tab='unit';render()"); pg.wait_for_timeout(150)
        check('medal case total unchanged', pg.locator('#rbcase .rbhead b').inner_text() == f'{shown} ribbons to earn')
        E("document.querySelector('[data-a=shareapp]').click()"); pg.wait_for_timeout(300)
        E("document.querySelector('[data-a=sharecopy]').click()"); pg.wait_for_timeout(1500)
        check('copying the link earns it', E("!!S.rb.aw.pio"))
        check('earned once', E("rbCount('pio').n") == 1)
        E("document.getElementById('hsSheet').hidden=true;document.getElementById('rbSheet')&&(document.getElementById('rbSheet').hidden=true);render()"); pg.wait_for_timeout(200)
        check('count includes earned hidden ribbon', f'of {shown + 1} earned' in pg.locator('#rbcase .rbhead').inner_text())
        check('text and email links count too', E("(()=>{document.querySelector('[data-a=shareapp]').click();return [...document.querySelectorAll('#hsBody a[href^=sms],#hsBody a[href^=mailto]')].every(a=>a.hasAttribute('data-pio'))})()"))
        check('kept in backup', E("cleanBackup(makeBackup()).rb.tally.pio") == 1)
        check('both hidden still count', E("(()=>{S.rb.tally.egg=1;rbCheck();return RB.filter(r=>r.area==='Hidden'&&S.rb.aw[r.id]).length})()") == 2)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
