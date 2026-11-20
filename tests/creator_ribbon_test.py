"""Creator ribbon: hidden, gold and black, earned only with the creator's private code on the Creator page. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
CODE = open('/home/claude/.creator_code').read().strip()
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E = pg.evaluate
    try:
        check('Creator ribbon exists, hidden', E("!!RB_BY.cre&&RB_BY.cre.area==='Hidden'&&RB_BY.cre.name==='Creator'"))
        check('says Built H2F Trainer', E("RB_BY.cre.rule").startswith('Built H2F Trainer'))
        check('gold and black, gold widest', E("(()=>{const s=RB_BY.cre.stripes;const c=new Set(s.map(x=>x[1]));const w=s.reduce((a,x)=>x[0]>a[0]?x:a);return c.has('go')&&c.has('bk')&&w[1]==='go'})()"))
        check('not in the medal case until earned', not E("RB_SHOW.some(r=>r.id==='cre')"))
        check('the code itself is not in the app', CODE not in E("document.documentElement.outerHTML") and CODE.replace('-', '') not in E("document.documentElement.outerHTML"))
        E("S.tab='creator';render()"); pg.wait_for_timeout(200)
        pg.click('[data-a=crecode]'); pg.wait_for_timeout(200)
        E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true)")
        pg.fill('#creCode', 'CRT-WRON-GCOD'); pg.click('[data-a=crego]'); pg.wait_for_timeout(600)
        check('a wrong code does nothing', not E("!!S.rb.aw.cre") and "isn't right" in E("document.getElementById('creMsg').textContent"))
        E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true)")  # Creator's Word may pop up at the end of the page
        pg.fill('#creCode', ' ' + CODE.lower() + ' '); pg.click('[data-a=crego]'); pg.wait_for_timeout(1500)
        check('the right code (any case, spaces ok) earns it', E("!!S.rb.aw.cre"))
        check('Ribbon earned pop-up shows Creator', 'Creator' in E("document.getElementById('rbSheet').innerText"))
        check('kept in backup', E("cleanBackup(makeBackup()).rb.tally.cre") == 1)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
