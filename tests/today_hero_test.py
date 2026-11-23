"""Today hero: workout ring on top, gold Start, list you tick off on Today (ring + count update in place, saved),
collapsible list that remembers its state; other day kinds keep their card. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
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
    pg.add_style_tag(content='#rbSheet{display:none!important}')
    wd = E("(new Date().getDay()+6)%7")
    if wd >= 5:
        print('SKIP weekend: no workout day to test'); b.close(); print('RESULT OK'); sys.exit(0)
    E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='today';render()"); pg.wait_for_timeout(300)
    n = E("wkData(0).plan[(new Date().getDay()+6)%7].filter(x=>EX[x.id]).length")
    check('hero shows the ring first, then title and gold Start', E("!!document.querySelector('#tdhero .reactor')&&!!document.querySelector('#tdhero .tdh1')&&!!document.querySelector('#tdhero .tdgold[data-a=tdtimer]')"))
    check('ring has one segment per exercise', E("document.querySelectorAll('#tdhero .rx-seg').length") == n and n > 0)
    check('list has a tick box per exercise', E("document.querySelectorAll('#tdlist .tdchk').length") == n)
    E("document.querySelectorAll('.tdchk')[0].click();document.querySelectorAll('.tdchk')[1].click()"); pg.wait_for_timeout(200)
    check('ticks save to the plan', E("wkData(0).plan[(new Date().getDay()+6)%7].filter(x=>x.done).length") == 2)
    check('ring lights 2 segments and core says 2', E("document.querySelectorAll('#tdhero .rx-seg.on').length") == 2 and E("document.querySelector('.rx-core b').textContent").startswith('2'))
    check('list header count updates', E("document.getElementById('tdcnt').textContent") == f'2 of {n}')
    check('ticked row struck through, aria-pressed true', E("document.querySelectorAll('.tdrow.done').length") == 2 and E("document.querySelector('.tdchk').getAttribute('aria-pressed')") == 'true')
    E("document.querySelectorAll('.tdchk')[0].click()"); pg.wait_for_timeout(150)
    check('untick works', E("document.querySelectorAll('#tdhero .rx-seg.on').length") == 1)
    E("render()"); pg.wait_for_timeout(200)
    check('state survives a re-render', E("document.querySelectorAll('.tdrow.done').length") == 1)
    E("document.querySelector('[data-a=tdlist]').click()"); pg.wait_for_timeout(600)
    check('list folds and remembers', not E("document.getElementById('tdlist').classList.contains('open')") and E("localStorage.getItem('h2f.tdlist')") == '0' and E("document.getElementById('tdlb').getBoundingClientRect().height") < 2)
    E("render()"); check('still folded after render', not E("document.getElementById('tdlist').classList.contains('open')"))
    E("document.querySelector('[data-a=tdlist]').click()")
    pg.click('#tdlist .tdn >> nth=0'); pg.wait_for_timeout(300)
    check('tapping a name opens exercise info', not E("document.getElementById('infoSheet').hidden"))
    E("document.getElementById('infoSheet').hidden=true")
    check('page fits the screen', E("document.documentElement.scrollWidth") <= 390)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
