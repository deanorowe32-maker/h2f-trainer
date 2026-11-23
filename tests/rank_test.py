"""Rank: Readiness Points from logs, time in grade, boards, ceremony, Today card, sheet, squad opt-in, backup. Server on :8765."""
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
    E("S.tab='today';render()"); pg.wait_for_timeout(300)
    check('new user is Recruit with 0 points', E("[rkState().tier,rkState().pts].join()") == '0,0')
    check('no ceremony for a new Recruit', not E("!!document.querySelector('.rkcer')") and E("S.rk.seen") == 0)
    check('Today shows the rank card', 'Recruit' in E("document.getElementById('rkcard').textContent"))
    # Points
    E("""(()=>{const d=x=>dk(new Date(Date.now()-x*864e5));window.K=d(40);S.hist=[{id:'x',ts:new Date(Date.now()-40*864e5).setHours(9),t:'1',d:1,n:1}];S.sleep.log[K]=7.5;S.mind.log[K]={mood:2,g:['','','']};S.nut.wlog[K]=8;S.journal.entries.push({id:'j1',d:K,k:'spirit',t:'x'});rkMemo=null})()""")
    check('one full day = 10+3+2+2+3 = 20', E("rkData().pts[K]") == 20)
    E("S.sleep.log[K]=6;rkMemo=null"); check('under 7 h sleep earns nothing for sleep', E("rkData().pts[K]") == 17)
    E("""(()=>{const m=rkMon(dk(new Date(Date.now()-21*864e5)));S.hist=[0,1,2].map(i=>({id:'w'+i,ts:vzDay(rkAdd(m,i)).setHours(9),t:'1',d:1,n:1}));window.M=m;rkMemo=null})()""")
    check('3rd training day of a week adds the +20 bonus', E("rkData().pts[rkAdd(M,2)]") == 30 and E("rkData().pts[rkAdd(M,0)]") == 10)
    E("""S.aft.hist=[{id:'a1',d:rkAdd(M,3),age:30,std:'g',t:380,p:[80,70,80,70,80],r:[0,0,0,0,0]},{id:'a2',d:rkAdd(M,4),age:30,std:'g',t:420,p:[80,80,90,80,90],r:[0,0,0,0,0]}];rkMemo=null""")
    check('AFT saved 15, improvement adds up to 30 more', E("rkData().pts[rkAdd(M,3)]") == 15 and E("rkData().pts[rkAdd(M,4)]") == 45)
    # Time in grade: 60+ points in 4 days but Striker needs 7 days
    E("""(()=>{S.aft.hist=[];S.journal.entries=[];S.sleep.log={};S.mind.log={};S.nut.wlog={};const s=rkAdd(today(),-3);S.hist=[0,1,2,3].map(i=>({id:'t'+i,ts:vzDay(rkAdd(s,i)).setHours(9),t:'1',d:1,n:1}));rkMemo=null})()""")
    r = E("(()=>{const R=rkState();return [R.tier,R.pts,rkNext(R).tig]})()")
    check(f'points alone do not promote: time in grade (got {r})', r[0] == 0 and r[1] >= 60 and r[2] > 0)
    # Board: lots of history but no AFT pass -> stops at Vanguard
    E("""(()=>{S.hist=[];for(let d=1;d<=70;d++){const t=new Date(Date.now()-d*864e5);if((t.getDay()+6)%7<4)S.hist.push({id:'h'+d,ts:t.setHours(9),t:'1',d:1,n:1})}rkMemo=null})()""")
    check('without a passing AFT the board stops you at Vanguard', E("rkState().tier") == 3 and E("rkNext(rkState()).bd") == 'aft' and not E("rkNext(rkState()).bok"))
    E("""S.aft.hist=[{id:'a1',d:rkAdd(today(),-30),age:30,std:'g',t:412,p:[90,80,85,77,80],r:[0,0,0,0,0]}];rkMemo=null""")
    check('passing AFT clears the Sentinel board', E("rkState().tier") >= 4)
    # Ceremony
    E("S.rk.seen=0;document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);render()"); pg.wait_for_timeout(300)
    check('promotion ceremony shows the new rank', E("!!document.querySelector('.rkcer')") and E("RK[rkState().tier][0]") in E("document.querySelector('.rkcer').textContent"))
    check('ceremony does not block taps', E("getComputedStyle(document.querySelector('.rkcer')).pointerEvents") == 'none')
    check('seen rank saved', E("S.rk.seen") == E("rkState().tier"))
    pg.wait_for_timeout(4000); check('ceremony clears itself', not E("!!document.querySelector('.rkcer')"))
    E("render()"); pg.wait_for_timeout(200); check('no repeat ceremony', not E("!!document.querySelector('.rkcer')"))
    # Card, telemetry, sheet
    check('telemetry shows rank', E("RK[rkState().tier][0]") in E("document.getElementById('fxTele').textContent"))
    E("document.querySelector('[data-a=rkopen]').click()"); pg.wait_for_timeout(200)
    check('sheet lists all 9 tiers with promotion dates', E("document.querySelectorAll('.rkladder li').length") == 9 and E("document.querySelectorAll('.rkladder .rkwhen').length") == E("rkState().tier"))
    check('sheet says these are not Army ranks', 'not Army rank' in E("document.getElementById('rkBody').textContent"))
    E("document.getElementById('rkSheet').hidden=true")
    # Inactive
    E("""(()=>{S.hist=S.hist.filter(x=>x.ts<Date.now()-20*864e5);S.rb.aw={};rkMemo=null})()""")
    check('quiet for 14+ days shows Inactive but keeps rank', E("rkState().inactive") and E("rkState().tier") >= 1)
    # Squad
    check('rank not shared by default', 'rk' not in E("sqMake()"))
    E("S.squad.inc.rk=1;S.squad.name='Test'")
    m = E("sqClean(JSON.parse(sqCode().slice(7)))")
    check('rank shared when switched on', m.get('rk', {}).get('t') == E("rkState().tier"))
    check('squad line reads Rank: name', any(l.startswith('Rank: ' + E("RK[rkState().tier][0]")) for l in E("sqLines(sqClean(JSON.parse(sqCode().slice(7))))")))
    check('bad squad rank dropped', 'rk' not in E("sqClean({v:1,n:'A',d:today(),rk:{t:99,p:5}})"))
    # Backup
    check('backup keeps seen rank and squad switch', E("(()=>{const c=cleanBackup(makeBackup());return c.rk.seen===S.rk.seen&&c.squad.inc.rk===1})()"))
    check('page fits the screen', E("document.documentElement.scrollWidth") <= 390)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
