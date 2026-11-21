"""Upgrades: swap a lift for one that works the same muscles, last-week recap on Today, squad check-in text, new-version bar. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
def clock(iso):
    return "(()=>{const O=Date,off=new O('%s').getTime()-O.now();class D extends O{constructor(...a){super(...(a.length?a:[O.now()+off]))}static now(){return O.now()+off}};window.Date=D})()" % iso
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); pg = ctx.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.add_init_script(clock('2026-11-24T09:00:00'))  # Tuesday
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(300)
        pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(1000)
        E = pg.evaluate

        # --- swap ---
        E("S.week=0;S.tab='train';S.day=1;S.plan[1]=[{id:'bsq',rx:'4x5',w:'135',done:true,s:'M'}];save();render()"); pg.wait_for_timeout(150)
        pg.click('.item .nm[data-a=info][data-v=bsq]'); pg.wait_for_timeout(150)
        rows = E("[...document.querySelectorAll('#infoBody .swaprow')].map(x=>x.dataset.v)")
        check('info sheet offers swaps', 0 < len(rows) <= 6 and 'bsq' not in rows)
        same = E("(rows)=>rows.every(id=>SWAPFAM.includes(EX[id].cat)&&EX[id].sec==='M'&&musclesOf(id).some(m=>musclesOf('bsq').includes(m)))", rows)
        check('swaps are strength moves that share a muscle', same)
        check('swaps cover more than one kind of gear', E("(rows)=>new Set(rows.map(id=>EX[id].cat)).size", rows) >= 3)
        first = rows[0] if rows else ''
        pg.click('#infoBody .swaprow'); pg.wait_for_timeout(150)
        it = E("S.plan[1][0]")
        check('swap replaces the exercise and keeps sets and reps', it['id'] == first and it['rx'] == '4x5' and not it.get('w') and not it.get('done') and it.get('s') == 'M')
        check('sheet closes after a swap', E("document.getElementById('infoSheet').hidden"))
        E("S.tab='lib';render()"); pg.wait_for_timeout(150)
        E("openInfo('bsq')"); pg.wait_for_timeout(100)
        check('no swap section when opened outside a workout row', E("!document.querySelector('#infoBody .swaprow')"))
        pg.click('#infoBody [data-a=closeinfo]'); pg.wait_for_timeout(200)

        # --- recap ---
        E("""(()=>{S.hist=[];for(let d=0;d<3;d++){const m=monday(-1);m.setDate(m.getDate()+d);m.setHours(10);S.hist.push({id:'h'+d,ts:m.getTime(),day:'Mon',type:'x',ms:6e5,d:1,n:1})}
          S.weeks[mkey(-1)]={plan:[[{id:'bench',rx:'4x6',w:'185',done:true}],[],[],[],[]],types:S.types.slice()};
          S.weeks[mkey(-2)]={plan:[[{id:'bench',rx:'4x6',w:'175',done:true}],[],[],[],[]],types:S.types.slice()};
          S.sleep.log[slKey(3)]=7;S.sleep.log[slKey(4)]=6;S.sleep.log[slKey(1)]=4;save();S.tab='today';render()})()"""); pg.wait_for_timeout(200)
        t = E("document.getElementById('recap')?.textContent||''")
        check('recap shows on Tuesday', 'Last week' in t)
        check('recap counts workout days and the streak week', '3 workout days, a streak week' in t)
        check('recap lists the new personal best', '1 new personal best' in t and '185 lb' in t)
        check('recap sleep averages last week only', '6.5 h sleep' in t and 'over 2 nights' in t)
        pg.click('#recap [data-a=pgopen]'); pg.wait_for_timeout(200)
        check('recap opens Progress', not E("document.getElementById('pgrSheet').hidden"))
        E("document.querySelector('#pgrSheet [data-a=sheetclose]').click()"); pg.wait_for_timeout(200)
        check('Progress closes', E("document.getElementById('pgrSheet').hidden"))
        check('recap is hidden Thursday to Sunday', E("recapHtml(new Date('2026-11-26T09:00:00'))") == '')

        # --- squad check-in text ---
        add = "(o)=>{const c=sqClean(o);c.k=(c.id||'x')+'-'+c.n.toLowerCase().replace(/[^a-z0-9]/g,'');S.squad.members.push(c)}"
        E(f"(()=>{{const add={add};S.squad.members=[];add({{v:1,n:'SGT Brown',d:'2026-11-24',tr:{{c:0}},sl:{{n:5,a:5.2}}}});add({{v:1,n:'SPC Adams',d:'2026-11-24',tr:{{c:4}},sl:{{n:6,a:7.4}}}});save()}})()")
        E("S.tab='unit';render();sqMode='sq';sqShow()"); pg.wait_for_timeout(400)
        E("document.getElementById('rbSheet').hidden=true")  # a ribbon earned from the test data
        check('flagged Soldier gets a check-in button', E("document.querySelectorAll('.sqcheck [data-a=sqping]').length") == 1)
        check('check-in text is kind and names them', E("sqPingText('SGT Brown')") == 'Hey SGT Brown, checking in. How are you doing this week? Anything I can help with?')
        E("(()=>{window.__shared=null;navigator.share=o=>{window.__shared=o.text;return Promise.resolve()}})()")
        pg.click('.sqcheck [data-a=sqping]'); pg.wait_for_timeout(150)
        check('button opens the share sheet with the text', (E("window.__shared") or '').startswith('Hey SGT Brown'))
        check('check-in button is a 44 px tap target', E("document.querySelector('.sqping').getBoundingClientRect().height") >= 44)

        # --- new version bar ---
        E("updBar();updBar()")
        check('new-version bar shows once', E("document.querySelectorAll('#updBar').length") == 1)
        r = E("(()=>{const r=document.getElementById('updBar').getBoundingClientRect(),n=document.querySelector('nav#tabs').getBoundingClientRect();return {l:r.left,r:r.right,b:r.bottom,nt:n.top,w:innerWidth}})()")
        check('bar sits above the tab bar and fits the screen', r['b'] <= r['nt'] and r['l'] >= 0 and r['r'] <= r['w'])
        check('no page errors', not errs)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
