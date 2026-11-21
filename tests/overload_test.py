"""Coach weight hint: finished last time adds one step; unfinished or a lighter day repeats; bodyweight moves get no hint; deload tip after four strong weeks. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
MON = "(()=>{const O=Date,off=new O('2026-11-24T09:00:00').getTime()-O.now();class D extends O{constructor(...a){super(...(a.length?a:[O.now()+off]))}static now(){return O.now()+off}};window.Date=D})()"
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); pg = ctx.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.add_init_script(MON)
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(300)
        pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(1000)
        E = pg.evaluate
        setup = "(done,lite)=>{S.week=0;S.plan[0]=[{id:'bsq',rx:'4x5',w:'135',done},{id:'hrpu',rx:'3x10',w:'20',done:true}];S.plan[1]=[{id:'bsq',rx:'4x5',w:''},{id:'hrpu',rx:'3x10',w:''}];if(lite)S.plan[1][0].rx0='4x5';S.tab='train';S.day=1;save();render()}"
        E(f"({setup})(true,false)"); pg.wait_for_timeout(150)
        t = E("document.querySelector('.lastw')?.textContent||''")
        check('done last time: coach says try 140 lb', 'try 140 lb' in t and 'Last time: 135 lb' in t)
        check('hand-release push-up (bodyweight) gets no coach line', E("[...document.querySelectorAll('.lastw')].filter(x=>x.querySelector('.nextw')).length") == 1)
        pg.click('.nextw [data-a=uselw]'); pg.wait_for_timeout(100)
        check('Use 140 fills the weight', E("S.plan[1][0].w") == '140')
        E(f"({setup})(false,false)"); pg.wait_for_timeout(100)
        t = E("document.querySelector('.lastw')?.textContent||''")
        check('not done last time: repeat, no new weight', 'repeat it' in t and 'try' not in t)
        E(f"({setup})(true,true)"); pg.wait_for_timeout(100)
        check('lighter session: keep the same weight', 'Lighter session today' in E("document.querySelector('.lastw')?.textContent||''"))
        E("S.assess.unit='kg';render()"); E(f"({setup})(true,false)"); pg.wait_for_timeout(100)
        check('kg steps by 2.5', 'try 137.5 kg' in E("document.querySelector('.lastw')?.textContent||''"))
        E("S.assess.unit='lb';save()")
        # deload tip: 3 workout days in each of the last 4 weeks, none this week
        E("(()=>{S.hist=[];for(let w=1;w<=4;w++)for(let d=0;d<3;d++){const m=monday(-w);m.setDate(m.getDate()+d);m.setHours(10);S.hist.push({id:'h'+w+d,ts:m.getTime(),day:'Mon',type:'x',ms:6e5,d:1,n:1})}save();S.tab='today';render()})()"); pg.wait_for_timeout(100)
        check('deload tip after four strong weeks', 'Four strong weeks in a row' in E("document.getElementById('coach').textContent"))
        E("(()=>{S.hist=S.hist.filter(x=>x.ts>=monday(-3).getTime());save();render()})()"); pg.wait_for_timeout(100)
        check('no deload tip after three', 'Four strong weeks' not in E("document.getElementById('coach').textContent"))
        check('no page errors', not errs)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
