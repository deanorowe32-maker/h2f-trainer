"""Gold outline keeps moving (script-driven, survives re-renders, both directions) and stays still with reduced motion. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
EA = "(s)=>parseFloat(getComputedStyle(document.querySelector(s)).getPropertyValue('--ea'))||0"
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        for rm in ['no-preference', 'reduce']:
            pg = b.new_page(viewport={'width': 390, 'height': 844}, reduced_motion=rm); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            pg.goto('http://localhost:8765/'); pg.wait_for_timeout(300)
            pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
            a1, c1 = pg.evaluate(EA, '.tdwide'), pg.evaluate(EA, '.coach'); pg.wait_for_timeout(500)
            a2, c2 = pg.evaluate(EA, '.tdwide'), pg.evaluate(EA, '.coach')
            if rm == 'reduce':
                check('reduced motion: outline stays still', a1 == a2 == 0 and c1 == c2 == 0)
            else:
                check('outline turns forward', (a2 - a1) % 360 > 5)
                check('coach outline turns the other way', (c1 - c2) % 360 > 5)
                check('no CSS animation left on cards (Safari froze it)', pg.evaluate("getComputedStyle(document.querySelector('.tdwide')).animationName") == 'none')
                pg.evaluate("render()"); a3 = pg.evaluate(EA, '.tdwide')
                check('a re-render does not restart it from zero', a3 >= a2 or a3 > 5)
                pg.wait_for_timeout(400); pg.evaluate("S.tab='train';render()"); pg.wait_for_timeout(300)
                check('cards on other tabs move too', pg.evaluate(EA, '.sec') > 0)
            check(f'no page errors ({rm})', not errs); pg.close()
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
