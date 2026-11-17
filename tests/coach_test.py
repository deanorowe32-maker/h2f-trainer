"""On-phone Coach card: rule-based tips from the Soldier's own logs. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E = pg.evaluate
    T = "new Date(today()+'T15:00:00')"
    try:
        t = E(f"coachTips({T})")
        check('fresh install gets one starter tip', len(t) == 1 and t[0]['a'] == 'tdgo')
        E("S.pt.p.pain=8;S.pt.p.area='knee'")
        t = E(f"coachTips({T})")
        check('high pain comes first', 'pain' in t[0]['head'].lower() and t[0]['v'] == 'pt' and ('sick call' in t[0]['txt'] or 'H2F team' in t[0]['txt']))
        E("S.pt.p.pain=3")
        check('normal pain ignored', not any('pain' in x['head'].lower() for x in E(f"coachTips({T})")))
        E("for(let i=0;i<5;i++)S.sleep.log[slKey(i)]=5.5")
        t = E(f"coachTips({T})")
        check('short sleep tip with bedtime', any('5.5 h' in x['txt'] and 'tonight' in x['txt'] for x in t))
        E("S.hist=[{ts:Date.now()-4*864e5,n:5}]")
        check('training gap tip', any('4 days since' in x['head'] for x in E(f"coachTips({T})")))
        E("S.goal.cur={id:'g1',name:'Ruck ready',due:chDk(chMs(today())+9*864e5),ev:[{name:'Push-ups',m:'reps',base:20,goal:40}],log:[]}")
        check('goal test due tip', any('9 days' in x['head'] for x in E(f"coachTips({T})")))
        E("S.hyd={date:today(),n:1}")
        tips = E(f"coachTips({T})")
        check('at most 3 tips', len(tips) <= 3)
        check('ranked by priority', [x['pri'] for x in tips] == sorted([x['pri'] for x in tips], reverse=True))
        E("S.sleep.log={};S.hist=[{ts:Date.now(),n:5}];S.goal.cur=null")
        check('water tip in the afternoon', any(x['a'] == 'hyd' for x in E(f"coachTips({T})")))
        check('no water tip in the morning', not any(x['a'] == 'hyd' for x in E("coachTips(new Date(today()+'T09:00:00'))")))
        E("S.tab='today';render()"); pg.wait_for_timeout(200)
        check('coach card on Today', pg.locator('#coach .coachtip').count() >= 1)
        check('card sits below the workout', E("(()=>{const w=document.querySelector('.tdwide'),c=document.getElementById('coach');return !!(w&&c&&(w.compareDocumentPosition(c)&4))})()"))
        check('tip buttons wired', E("[...document.querySelectorAll('#coach .coachtip button')].every(b=>b.dataset.a)"))
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
