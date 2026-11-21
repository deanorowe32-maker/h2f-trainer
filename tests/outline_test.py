"""Gold outline: an SVG dash runs around each top-level card (Safari froze the old CSS --ea animation), keeps its place across redraws, both directions, none with reduced motion. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
OFF = "(s)=>{const r=document.querySelector(s+'>.erun path.zz.k0');return r?parseFloat(getComputedStyle(r).strokeDashoffset):null}"
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        for rm in ['no-preference', 'reduce']:
            pg = b.new_page(viewport={'width': 390, 'height': 844}, reduced_motion=rm); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            pg.goto('http://localhost:8765/'); pg.wait_for_timeout(300)
            pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
            if rm == 'reduce':
                check('reduced motion: no running line shown', pg.evaluate("[...document.querySelectorAll('.erun')].every(e=>getComputedStyle(e).display==='none')"))
            else:
                check('Today cards have a running line', pg.evaluate("document.querySelectorAll('#view .erun').length") >= 3)
                check('no CSS animation of --ea left (Safari froze it)', '--ea' not in pg.evaluate("document.documentElement.outerHTML.split('</style>')[0]"))
                a1, c1 = pg.evaluate(OFF, '.tdwide'), pg.evaluate(OFF, '.coach'); pg.wait_for_timeout(600)
                a2, c2 = pg.evaluate(OFF, '.tdwide'), pg.evaluate(OFF, '.coach')
                check('line runs forward', a2 < a1)
                check('coach line runs the other way', c2 > c1)
                pg.evaluate("render()"); pg.wait_for_timeout(50); a3 = pg.evaluate(OFF, '.tdwide')
                check('a redraw keeps its place (no jump back to the start)', a3 is not None and abs(a3 - a2) < 15)
                check('one line per card, nested cards get none', pg.evaluate("[...document.querySelectorAll('#view .erun')].every(e=>e.parentElement.querySelectorAll(':scope>.erun').length===1&&!e.parentElement.matches(ERUN_NO))"))
                pg.evaluate("S.tab='train';render()"); pg.wait_for_timeout(200)
                check('cards on other tabs get the line', pg.evaluate("document.querySelectorAll('#view .sec>.erun').length") > 0)
                ALL = '.grp,.tdcard,.start,.bodyx,section.card,.sec,.tdwide,.tdgrid,.coach,.chcard,.rbnext,.plan,.stats,.times,.pdays,.mgrid,.inj,.evcard,.cur,.strip,.sched,.editday,.howto,.gtsum,.note,.urow.sqhero'
                still = []
                for tab in ['today', 'train', 'lib', 'assess', 'pt', 'sleep', 'nut', 'mind', 'spirit', 'unit', 'fm', 'creator']:
                    pg.evaluate(f"S.tab='{tab}';render()"); pg.wait_for_timeout(120)
                    m = pg.evaluate(f"[...document.querySelectorAll('#view :is({ALL})')].filter(e=>!e.matches(ERUN_NO)&&!e.closest('[hidden]')&&e.offsetWidth&&!e.querySelector(':scope>.erun')).map(e=>e.className)")
                    if m: still.append(f'{tab}: {m}')
                check('every bordered box on every tab has a running line (Recovery, Readiness, Unit were still)' + (f' {still}' if still else ''), not still)
                check('line does not catch taps', pg.evaluate("getComputedStyle(document.querySelector('.erun')).pointerEvents") == 'none')
                check('last item in a card still has no bottom rule', pg.evaluate("(()=>{const it=[...document.querySelectorAll('.sec .item')].find(i=>i.parentElement.lastElementChild.classList.contains('erun')&&i.nextElementSibling&&i.nextElementSibling.classList.contains('erun'));return !it||getComputedStyle(it).borderBottomWidth==='0px'})()"))
            check(f'no page errors ({rm})', not errs); pg.close()
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
