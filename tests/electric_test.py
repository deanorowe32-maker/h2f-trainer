"""Electric look: always dark (black, forest green, gold), own fonts, Today reactor counts real exercises, effects never block taps. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
MON = "(()=>{const O=Date,off=new O('2026-11-23T09:00:00').getTime()-O.now();class D extends O{constructor(...a){super(...(a.length?a:[O.now()+off]))}static now(){return O.now()+off}};window.Date=D})()"
def fresh(pg):
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(400)
    pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(1200)
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, color_scheme='light', service_workers='block'); pg = ctx.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.add_init_script(MON)
        fresh(pg); E = pg.evaluate
        check('dark even when the phone is in light mode', E("document.documentElement.dataset.theme==='dark'&&getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()==='#050605'"))
        check('gold accent', E("getComputedStyle(document.documentElement).getPropertyValue('--gold').trim()==='#e8bf55'"))
        pg.wait_for_timeout(600)
        check('Manrope served by the app and loaded', E("document.fonts.check('700 16px Manrope')&&[...document.fonts].some(f=>f.family.replace(/\"/g,'')==='Manrope'&&f.status==='loaded')"))
        n = E("(()=>{const W=wkData(0);return W?(W.plan[0]||[]).filter(it=>EX[it.id]).length:0})()")
        check(f'reactor on Today shows 0 of {n}', n > 0 and E("document.querySelector('.reactor')?.getAttribute('aria-label')") == f'0 of {n} exercises done' and E("document.querySelectorAll('.reactor .rx-seg').length") == n)
        E("(()=>{const W=wkData(0);W.plan[0].filter(it=>EX[it.id]).slice(0,2).forEach(it=>it.done=true);save();render()})()"); pg.wait_for_timeout(200)
        check('reactor lights one segment per done exercise', E("document.querySelectorAll('.reactor .rx-seg.on').length") == 2 and E("document.querySelector('.rx-core b').textContent") == f'2/{n}')
        check('effects layer never takes taps', E("getComputedStyle(document.getElementById('efx')).pointerEvents==='none'&&getComputedStyle(document.querySelector('.escan')).pointerEvents==='none'"))
        E("S.tab='train';render()"); pg.wait_for_timeout(100)
        check('switching tabs powers the screen up', E("document.getElementById('view').classList.contains('epwr')"))
        check('every tab still renders', all(E(f"(S.tab='{t}',render(),document.getElementById('view').children.length>1)") for t in ['today','train','pt','assess','lib','fm','nut','sleep','mind','spirit','creator','unit']))
        check('no page errors', not errs)
        ctx.close()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce', service_workers='block'); pg = ctx.new_page(); pg.add_init_script(MON)
        fresh(pg); pg.evaluate("S.tab='train';render()"); pg.wait_for_timeout(100)
        check('reduced motion: no power-up', not pg.evaluate("document.getElementById('view').classList.contains('epwr')"))
        check('reduced motion: cards do not animate', pg.evaluate("getComputedStyle(document.querySelector('.grp,.sec,.tdwide')).animationName") == 'none')
        ctx.close()
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
