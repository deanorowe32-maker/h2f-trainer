"""Four unit ribbons unlocked by private codes (grey and black with a colour): 1st Fires purple, 2nd Fires pink,
3rd Fires yellow, Support red. Codes live outside the repo in ~/.code_<id>. Server on :8765."""
import sys, os
from playwright.sync_api import sync_playwright
RIBS = [('fr1', '1st Fires', 'pu'), ('fr2', '2nd Fires', 'pk'), ('fr3', '3rd Fires', 'ye'), ('sup', 'Support', 'sc')]
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
    html = E("document.documentElement.outerHTML")
    for rid, name, col in RIBS:
        check(f'{name}: hidden ribbon', E(f"!!RB_BY.{rid}&&RB_BY.{rid}.area==='Hidden'&&RB_BY.{rid}.name==='{name}'"))
        check(f'{name}: grey, black and {col} only', E(f"[...new Set(RB_BY.{rid}.stripes.map(x=>x[1]))].sort().join()") == ','.join(sorted(['gy', 'bk', col])))
        check(f'{name}: stripes fill half the ribbon', E(f"RB_BY.{rid}.stripes.reduce((a,x)=>a+x[0],0)") == 50)
        check(f'{name}: has a code', E(f"CRE_CODES.some(c=>c.id==='{rid}')"))
        check(f'{name}: not shown until earned', not E(f"RB_SHOW.some(r=>r.id==='{rid}')"))
    check('grey is its own colour', E("RB_C.gy") == '#6f777d')
    for rid, name, col in RIBS:
        path = os.path.expanduser(f'~/.code_{rid}')
        if not os.path.exists(path):
            print(f'SKIP {name} unlock: {path} not here'); continue
        code = open(path).read().strip()
        check(f'{name} code is not in the app', code not in html and code.replace('-', '') not in html)
        E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='unit';render()")
        E("document.querySelector('main [data-a=shareapp]').click()"); pg.wait_for_timeout(300)
        pg.fill('#creCode', ' ' + code.lower() + ' '); E("document.querySelector('[data-a=crego]').click()"); pg.wait_for_timeout(1200)
        check(f'{name} code unlocks only {name}', E(f"!!S.rb.aw.{rid}") and E("Object.keys(S.rb.aw).filter(k=>['fr1','fr2','fr3','sup'].includes(k)).length") == RIBS.index((rid, name, col)) + 1)
        check(f'{name} kept in backup', E(f"cleanBackup(makeBackup()).rb.tally.{rid}") == 1)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
