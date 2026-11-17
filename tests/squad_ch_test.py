"""Checks for the squad challenge board. Server on :8765: python3 tests/squad_ch_test.py"""
import sys, json
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(800)
    E = pg.evaluate
    try:
        check('challenges option listed and on', E("SQ_INC.some(([k])=>k==='ch')&&S.squad.inc.ch===1"))
        # soldier side: 3 dailies done in last 7 days
        E("""S.ch=chClean(null);for(let i=0;i<3;i++){const d=chDk(chMs(today())-i*864e5);chLog(chDayKey(d),CH_BY[chDayKey(d)].d[0],d)}
             const ws=chWeekKey(today());chLog(ws,CH_BY[ws].w[1],today())""")
        m = E("sqMake()")
        check('summary carries challenges', m.get('ch', {}).get('dd') == 3 and m['ch']['wk'] == E("chWeekKey(today())") and m['ch']['wl'] >= 2)
        E("S.squad.inc.ch=0")
        check('switch off removes it', 'ch' not in E("sqMake()"))
        E("S.squad.inc.ch=1")
        c = E("sqClean({v:1,n:'A',d:today(),ch:{dd:99,wk:'zz',wt:-4,wl:7,ml:'x'}})")
        check('clean clamps', c['ch'] == {'dd': 7, 'wk': '', 'wt': 0, 'wl': 0, 'ml': 0})
        E("S.squad.name='SPC Test'")
        check('line text', any('Challenges:' in x for x in E("sqLines(sqClean(sqMake()))")))
        # leader side
        wk = E("chWeekKey(today())")
        old = E("chDk(chMs(today())-10*864e5)")
        E(f"""S.squad.members=[{{v:1,n:'SPC Diaz',d:today(),ch:{{dd:5,wk:'{wk}',wt:300,wl:1,ml:1}}}},
            {{v:1,n:'PFC Lee',d:today(),ch:{{dd:6,wk:'{wk}',wt:100,wl:0,ml:0}}}},
            {{v:1,n:'SGT Old',d:'{old}',ch:{{dd:7,wk:'{wk}',wt:999,wl:3,ml:3}}}},
            {{v:1,n:'PV2 None',d:today()}}].map(sqClean)""")
        rows = E("sqBoard().rows.map(r=>r.n)")
        check('ranked by dailies', rows == ['PFC Lee', 'SPC Diaz'])
        check('old summaries left out', E("sqBoard().old") == 1)
        E("sqMode='sq';S.tab='unit';render();sqShow()"); pg.wait_for_timeout(300)
        check('board shown', pg.locator('#sqBody .sqboard').count() == 1 and 'PFC Lee' in pg.locator('#sqBody .sqboard').inner_text())
        txt = E("sqBoardText()")
        check('standings text', txt.splitlines()[1].startswith('1. PFC Lee') and '6 of 7' in txt)
        check('fix copy fallback above squad sheet', E("+getComputedStyle(document.getElementById('gtShared')).zIndex>+getComputedStyle(document.getElementById('sqSheet')).zIndex"))
        E("S.squad.inc.ch=0;S.aft.goal=450")
        r = E("(()=>{const c=cleanBackup(makeBackup());return c?[c.squad.inc.ch,c.aft.goal]:null})()")
        check('fix restore keeps ch off and goal', r == [0, 450])
        check('names escaped on board', E("(()=>{S.squad.members[0].n='<i>x</i>';return sqBoardHtml().includes('<i>x</i>')})()") is False)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
