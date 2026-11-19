"""Remedial PT (ABCP): library, 12-week plan, day cards, runner. Server on :8765."""
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
    check('clean gives defaults for junk', E("JSON.stringify(remClean('x'))") == '{"st":"","days":[0,2,4],"sw":{}}')
    check('clean keeps good data, drops bad', E("(()=>{const r=remClean({st:'2026-11-02',days:[1,1,9,3],sw:{'s_db.0.0':'pu','bad':'pu','s_db.0.1':'nope'}});return r.st==='2026-11-02'&&r.days.join()==='1,3'&&Object.keys(r.sw).join()==='s_db.0.0'})()"))
    check('library: 12 sessions, 3 per kind, all exercises exist', E("REM_LIB.length===12&&['c','s','i','m'].every(k=>REM_LIB.filter(x=>x.k===k).length===3)&&REM_LIB.every(x=>x.b.every(bl=>bl.ids.every(id=>EX[id])))"))
    dur = "(id,w)=>remSess(id,w).ph.reduce((a,p)=>a+(p.s||0),0)"
    check('lighter week 4 is shorter than week 3', E(f"(()=>{{const d={dur};return REM_LIB.every(x=>d(x.id,4)<d(x.id,3))}})()"))
    check('week 11 is longer than week 1', E(f"(()=>{{const d={dur};return REM_LIB.every(x=>d(x.id,11)>d(x.id,1))}})()"))
    check('sessions run 25 to 50 minutes', E(f"(()=>{{const d={dur};return REM_LIB.every(x=>[1,11].every(w=>d(x.id,w)>=1500&&d(x.id,w)<=3000))}})()"))
    check('week number from start date', E("remWeek(today())===1&&remWeek(dk(new Date(Date.now()-8*864e5)))===2&&remWeek(dk(new Date(Date.now()-200*864e5)))===12&&remWeek(dk(new Date(Date.now()+20*864e5)))===1&&remWeek('')===1"))
    check('week plan: cardio, strength, then intervals or mixed', E("remPlan(1).map(s=>REM_BY[s].k).join()==='c,s,i'&&remPlan(2).map(s=>REM_BY[s].k).join()==='c,s,m'&&remPlan(1)[0]!==remPlan(2)[0]"))
    # open from the Main workout quick row
    E("S.tab='train';S.types[0]='upper';S.day=0;render()"); pg.wait_for_timeout(200)
    pg.click('#view .mainquick [data-a=remopen]'); pg.wait_for_timeout(200)
    body = pg.inner_text('#ciBody')
    check('sheet opens with Week 1 of 12 and three sessions', 'Remedial PT' in body and 'Week 1 of 12' in body and body.count('Session ') >= 3)
    check('no personal data fields', pg.locator('#ciBody input:not([type=date])').count() == 0)
    plan_before = E("JSON.stringify([S.plan,S.types,S.fmt])")
    pg.click('#ciBody [data-a=remgo] >> nth=0'); pg.wait_for_timeout(300)
    check('start runs the session in the circuit runner', E("CI.started&&CI.ctx==='rem'") and 'Warm-up' in pg.inner_text('#ciBody'))
    pg.click('#ciBody [data-a=cistop]'); pg.wait_for_timeout(100); pg.click('#ciBody [data-a=cistop]'); pg.wait_for_timeout(200)
    check('stop returns to the Remedial sheet', 'Week 1 of 12' in pg.inner_text('#ciBody') and not pg.locator('#ciSheet').is_hidden())
    check('regular plan untouched', E("JSON.stringify([S.plan,S.types,S.fmt])") == plan_before)
    # pick a session from the library
    pg.click('#ciBody summary:has-text("Pick a session")'); pg.wait_for_timeout(100)
    pg.click('#ciBody [data-a=remgo][data-v=i_hill]'); pg.wait_for_timeout(200)
    check('any library session can be run', E("CI.started&&CI.ctx==='rem'&&CI.ph.some(p=>p.id==='hill')"))
    E("CI.started=false;document.getElementById('ciSheet').hidden=true")
    # day cards
    E("S.rem=remClean({st:prDate(0,0),days:[0,2,4],sw:{}});S.week=0;S.day=0;S.tab='train';render()")
    check('day card on a remedial day', pg.locator('#wkout .remcard').count() == 1)
    E("S.day=2;S.rem.st=prDate(0,3);render()")
    check('no day card before the start date', pg.locator('#wkout .remcard').count() == 0)
    E("S.rem.st=prDate(0,0);S.day=1;render()")
    check('no day card on other days', pg.locator('#wkout .remcard').count() == 0)
    E("S.rem.days=[];S.day=0;render()")
    check('no day cards when no days chosen', pg.locator('#wkout .remcard').count() == 0)
    # swap
    sid = E("remPlan(1)[1]")
    E(f"S.rem.sw['{sid}.0.0']='pu'")
    check('swapped exercise is used', E(f"remSess('{sid}',1).ph.find(p=>p.k==='w'&&!p.nm).id==='pu'"))
    E(f"S.rem.sw['{sid}.0.0']='c_gone'")
    check('missing swap falls back to built-in', E(f"remSess('{sid}',1).ph.find(p=>p.k==='w'&&!p.nm).id===REM_BY['{sid}'].b[0].ids[0]"))
    # backup
    E("S.rem=remClean({st:'2026-11-02',days:[1],sw:{}})")
    check('backup keeps remedial plan', E("(()=>{const c=cleanBackup(makeBackup());return c.rem&&c.rem.st==='2026-11-02'&&c.rem.days.join()==='1'})()"))
    # junk in storage does not crash startup
    E("S.rem={days:'x',sw:5};save()")
    pg.reload(); pg.wait_for_timeout(900)
    check('junk saved data still starts', E("S.rem.days.join()==='0,2,4'") and pg.locator('#view').count() == 1)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
