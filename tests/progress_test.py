"""Progress sheet: weekly bars, streaks, personal bests from logged weights (past days only), AFT trend; personal-best note on a heavier weight. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
MON = "(()=>{const O=Date,off=new O('2026-11-25T09:00:00').getTime()-O.now();class D extends O{constructor(...a){super(...(a.length?a:[O.now()+off]))}static now(){return O.now()+off}};window.Date=D})()"
SEED = """(()=>{S.week=0;S.hist=[];for(let w=0;w<=5;w++)for(let d=0;d<(w===2?1:3);d++){const m=monday(-w);m.setDate(m.getDate()+d);m.setHours(10);if(m.getTime()<=Date.now())S.hist.push({id:'h'+w+d,ts:m.getTime(),day:'Mon',type:'x',ms:18e5,d:1,n:1})}
  S.plan[0]=[{id:'bsq',rx:'4x5',w:'185'},{id:'hrpu',rx:'3x10',w:'50'}];S.plan[1]=[{id:'bsq',rx:'4x5',w:''}];S.plan[4]=[{id:'bench',rx:'3x5',w:'500'}];
  S.weeks[mkey(-1)]={types:S.types.slice(),plan:[[{id:'bsq',rx:'5x5',w:'175'}],[{id:'bench',rx:'3x5',w:'155'}],[],[],[]],fmt:['n','n','n','n','n'],dst:[null,null,null,null,null],dcir:[null,null,null,null,null]};
  S.aft.hist=[{id:'a2',d:'2026-11-10',age:28,sex:'m',std:'g',r:[],p:[80,70,70,70,70],t:360},{id:'a1',d:'2026-09-01',age:28,sex:'m',std:'g',r:[],p:[70,65,60,60,60],t:315}];save();render()})()"""
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); pg = ctx.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.add_init_script(MON)
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(300)
        pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(1000)
        E = pg.evaluate
        E("S.tab='today';render()"); pg.wait_for_timeout(100)
        check('empty progress opens with guidance', (pg.click('[data-a=pgopen]'), pg.wait_for_timeout(150), 'Type the weight you lift' in E("document.getElementById('pgrBody').textContent"))[2])
        E("document.getElementById('pgrSheet').hidden=true"); E(SEED); pg.wait_for_timeout(300); E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true)")
        pg.click('[data-a=pgopen]'); pg.wait_for_timeout(600)
        T = E("document.getElementById('pgrBody').textContent")
        check('12 weekly bars', E("document.querySelectorAll('#pgrBody .vz-slot').length") == 12 + 2)
        check('current streak 1 (this week 2 days, week 2 one day), best 3', E("[...document.querySelectorAll('#pgrBody .stats b')].slice(1).map(x=>x.textContent).join(',')") == '1,3')
        check('Back Squat best 185 lb', 'Back Squat' in T and '185 lb' in T)
        check('bench best 155, future-day 500 ignored', '155 lb' in T and '500' not in T)
        check('bodyweight move not a personal best', 'Hand-Release' not in T)
        check('AFT trend up 45 points', 'Up 45 points' in T)
        E("document.getElementById('rbSheet').hidden=true"); pg.wait_for_timeout(300)
        pg.screenshot(path='/tmp/progress.png', full_page=False)
        pg.click('#pgrSheet [data-a=sheetclose]'); pg.wait_for_timeout(100)
        E("S.tab='train';S.day=1;render()"); pg.wait_for_timeout(100)
        inp = pg.locator('[data-f=iw][data-k=train][data-i="0"]')
        inp.fill('190'); inp.blur(); pg.wait_for_timeout(150)
        check('heavier weight shows new personal best', 'New personal best: 190 lb, up from 185' in E("document.querySelector('.pbnew')?.textContent||''"))
        inp.fill('180'); inp.blur(); pg.wait_for_timeout(150)
        check('lighter weight clears the note', E("!document.querySelector('.pbnew')"))
        E("S.tab='train';render()"); pg.wait_for_timeout(100)
        check('History has a Progress button', E("!!document.querySelector('#view .sechead [data-a=pgopen]')"))
        check('no page errors', not errs)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
