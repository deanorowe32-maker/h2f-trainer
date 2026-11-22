"""HUD outline: four corner brackets and a scan line on every bordered card, sized in pixels and refit when a card grows
(Safari froze the old --ea animation and did not resize percentage-sized shapes). Still with reduced motion. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
ALL = '.grp,.tdcard,.start,.bodyx,section.card,.sec,.tdwide,.tdgrid,.coach,.chcard,.rbnext,.plan,.stats,.times,.pdays,.mgrid,.inj,.evcard,.cur,.strip,.sched,.editday,.howto,.gtsum,.note,.urow.sqhero'
TABS = ['today', 'train', 'lib', 'assess', 'pt', 'sleep', 'nut', 'mind', 'spirit', 'unit', 'fm', 'creator']
SCANY = "(s)=>{const g=document.querySelector(s+'>.erun .scan');return g?new DOMMatrix(getComputedStyle(g).transform).f:null}"
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        for rm in ['no-preference', 'reduce']:
            pg = b.new_page(viewport={'width': 390, 'height': 844}, reduced_motion=rm); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            pg.goto('http://localhost:8765/'); pg.wait_for_timeout(300)
            pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
            if rm == 'reduce':
                check('reduced motion: scan line hidden', pg.evaluate("[...document.querySelectorAll('.erun .scan')].every(e=>getComputedStyle(e).display==='none')"))
                check('reduced motion: brackets stay still', pg.evaluate("[...document.querySelectorAll('.erun .lk')].every(e=>getComputedStyle(e).animationName==='none')"))
            else:
                check('Today cards have four brackets each', pg.evaluate("[...document.querySelectorAll('#view .erun')].every(v=>v.querySelectorAll('.lk').length===4)") and pg.evaluate("document.querySelectorAll('#view .erun').length") >= 3)
                check('no CSS animation of --ea left (Safari froze it)', not __import__('re').search(r'--ea[:)]', pg.evaluate("[...document.styleSheets].map(s=>{try{return [...s.cssRules].map(r=>r.cssText).join('')}catch(_){return ''}}).join('')")))
                check('outline animations do not share a name with another effect', pg.evaluate("[...document.styleSheets].flatMap(s=>{try{return [...s.cssRules]}catch(_){return []}}).filter(r=>r.type===7&&['ehud','elock'].includes(r.name)).length") == 2)
                y1 = pg.evaluate(SCANY, '.tdwide'); pg.wait_for_timeout(400); y2 = pg.evaluate(SCANY, '.tdwide')
                check(f'scan line moves down ({y1} -> {y2})', y1 is not None and y2 is not None and y2 != y1)
                check('scan lines are not in step across cards', len(set(pg.evaluate("[...document.querySelectorAll('#view .erun .scan')].map(g=>g.style.animationDelay)"))) > 1)
                check('scan line is clipped to the card', pg.evaluate("[...document.querySelectorAll('#view .erun')].every(v=>{const c=v.querySelector('clipPath');return c&&v.querySelector('[clip-path=\"url(#'+c.id+')\"]')})"))
                check('clip ids are unique', pg.evaluate("(()=>{const a=[...document.querySelectorAll('.erun clipPath')].map(c=>c.id);return new Set(a).size===a.length})()"))
                pg.evaluate("document.querySelector('.tdwide').insertAdjacentHTML('afterbegin','<div style=height:150px></div>')"); pg.wait_for_timeout(250)
                fit = pg.evaluate("(()=>{const e=document.querySelector('.tdwide'),v=e.querySelector(':scope>.erun'),c=v.querySelector('clipPath rect');return [e.offsetHeight-1,+v.getAttribute('height'),+c.getAttribute('height')]})()")
                check(f'outline follows the card when it grows {fit}', fit[0] == fit[1] == fit[2])
                pg.evaluate("S.tab='unit';render()"); pg.wait_for_timeout(300)
                tall = pg.evaluate("(()=>{const g=document.querySelector('#rbcase>.erun .scan')||document.querySelector('#view .grp>.erun .scan');return parseFloat(g.style.animationDuration)})()")
                check(f'tall cards scan slower ({tall}s)', tall > 3)
                still = []
                for tab in TABS:
                    pg.evaluate(f"S.tab='{tab}';render()"); pg.wait_for_timeout(120)
                    m = pg.evaluate(f"[...document.querySelectorAll('#view :is({ALL})')].filter(e=>!e.matches(ERUN_NO)&&!e.closest('[hidden]')&&e.offsetWidth&&!e.querySelector(':scope>.erun')).map(e=>e.className)")
                    if m: still.append(f'{tab}: {m}')
                check('every bordered box on every tab has the HUD outline' + (f' {still}' if still else ''), not still)
                check('no outline inside a closed details box', pg.evaluate("(()=>{S.tab='train';render();return !document.querySelector('details>.erun')})()"))
                check('outline does not catch taps', pg.evaluate("getComputedStyle(document.querySelector('.erun')).pointerEvents") == 'none')
                check('last item in a card still has no bottom rule', pg.evaluate("(()=>{const it=[...document.querySelectorAll('.sec .item')].find(i=>i.nextElementSibling&&i.nextElementSibling.classList.contains('erun'));return !it||getComputedStyle(it).borderBottomWidth==='0px'})()"))
            check(f'no page errors ({rm})', not errs); pg.close()
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
