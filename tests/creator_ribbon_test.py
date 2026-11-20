"""Creator codes: a box under Share the app; each private code unlocks one special ribbon (first: Creator, gold and black). Server on :8765."""
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
        E("S.tab='unit';render()"); pg.wait_for_timeout(200)
        pg.click('main [data-a=shareapp]'); pg.wait_for_timeout(300)
        check('Share the app has a Creator code box', E("!!document.querySelector('#hsBody #creCode')"))
        E("S.tab='creator';render()")
        check('no code box on the Creator page any more', not E("!!document.querySelector('main #creCode')"))
        E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='unit';render()"); pg.click('main [data-a=shareapp]'); pg.wait_for_timeout(300)
        pg.fill('#creCode', 'CRT-WRON-GCOD'); pg.click('[data-a=crego]'); pg.wait_for_timeout(600)
        check('a wrong code does nothing', not E("!!S.rb.aw.cre") and "isn't right" in E("document.getElementById('creMsg').textContent"))
        pg.fill('#creCode', ' ' + CODE.lower() + ' '); pg.click('[data-a=crego]'); pg.wait_for_timeout(1500)
        check('the right code (any case, spaces ok) earns it', E("!!S.rb.aw.cre"))
        check('every code maps to a real hidden ribbon', E("CRE_CODES.length>=1&&CRE_CODES.every(c=>/^[0-9a-f]{64}$/.test(c.h)&&RB_BY[c.id]&&RB_BY[c.id].area==='Hidden')"))
        check('Ribbon earned pop-up shows Creator', 'Creator' in E("document.getElementById('rbSheet').innerText"))
        check('kept in backup', E("cleanBackup(makeBackup()).rb.tally.cre") == 1)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
