"""Reopen the app after using every feature: data must survive and the app must draw. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    pg.evaluate("""S.squad.name='SSG T';S.squad.members=[{v:1,n:'SPC A',d:today()}];sgAct('sgnew');S.sg.cur.rows[0].age='28';sgAct('sgdone');sgAct('sgnew');
      S.aft.goal=400;chLog(chState(today()).day.k,50,today());S.sleep.log[slKey(0)]=7;save()""")
    pg.wait_for_timeout(800)
    for i in range(2):
        pg.close(); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(1200)
        check(f'reopen {i}: data kept', pg.evaluate("!!S.sg.cur&&S.sg.hist.length===1&&S.aft.goal===400&&S.sleep.log[slKey(0)]===7"))
        check(f'reopen {i}: today drawn', len(pg.evaluate("document.getElementById('view').innerText")) > 200)
    # simulate a crash during startup: the safety screen must appear with a restorable backup code
    def boom(route):
        body = route.fetch().text().replace('render();BOOTED=true;', "throw new Error('boom');render();BOOTED=true;")
        route.fulfill(body=body, headers={'content-type': 'text/html'})
    saved = pg.evaluate("localStorage.getItem('h2f.v1')")
    ctx2 = b.new_context(service_workers='block'); pg2 = ctx2.new_page()
    # seed this phone's saved data before the app's own script runs (a first visit would save a blank state on close)
    ctx2.add_init_script("if(location.hostname==='localhost')localStorage.setItem('h2f.v1'," + __import__('json').dumps(saved) + ")")
    pg2.route('**/', boom); pg2.goto('http://localhost:8765/'); pg2.wait_for_timeout(1000)
    code = pg2.evaluate("(document.querySelector('#bootFail textarea')||{}).value||''")
    check('crash shows safety screen', pg2.locator('#bootFail').count() == 1 and code.startswith('H2FBACKUP1:'))
    pg2.close()
    r = pg.evaluate('(c)=>{try{const o=cleanBackup(c);return [!!o,o.aft&&o.aft.goal]}catch(e){return String(e)}}', code); print('   restore:', r); check('safety code restores', r == [True, 400])
    check('no safety screen normally', pg.locator('#bootFail').count() == 0)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
