"""Backup -> restore gives back the same data (field order aside), including done ticks and lighter-session markers in this and past weeks. Server on :8765."""
import sys, json
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
NORM = "Object.fromEntries(BK_KEYS.map(k=>[k,S[k]]))"
def norm(o):
    return json.dumps(o, sort_keys=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        pg = b.new_page(viewport={'width': 390, 'height': 844}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(300)
        pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
        pg.evaluate("""(()=>{S.plan[1]=[{id:'bsq',rx:'3x5',rx0:'4x5',w:'225',done:true,s:'M'},{id:'bench',rx:'4x6',w:'185'}];
          S.weeks[mkey(-1)]={plan:[[{id:'bsq',rx:'4x5',w:'220',done:true}],[],[],[],[]],types:S.types.slice()};
          S.sleep.log[slKey(1)]=7.5;S.hyd.n=5;const m=monday(0);m.setHours(9);S.hist=[{id:'a',ts:m.getTime(),day:'Mon',type:'x',ms:1e6,d:1,n:1}];save()})()""")
        bk = pg.evaluate("makeBackup()"); before = norm(pg.evaluate(NORM))
        pg.evaluate("(()=>{S.plan[1]=[];S.weeks={};S.hist=[];save()})()")
        pg.evaluate("(t)=>{applyBackup(cleanBackup(t));render()}", bk); pg.wait_for_timeout(300)
        after = pg.evaluate(NORM)
        check('done tick on this week survives a restore', after['plan'][1][0].get('done') is True)
        check('lighter-session marker survives a restore', after['plan'][1][0].get('rx0') == '4x5')
        check('untouched exercise stays not done', 'done' not in after['plan'][1][1])
        wk = pg.evaluate("S.weeks[mkey(-1)]")
        check('done tick in a past week survives a restore', wk and wk['plan'][0][0].get('done') is True)
        A, B = json.loads(before), after
        strip = lambda v: [({x: y for x, y in h.items() if y is not None} if isinstance(h, dict) else h) for h in v] if isinstance(v, list) else v
        diff = [k for k in A if k not in ('weeks', 'curKey') and norm(strip(A[k])) != norm(strip(B.get(k))) and not (k in ('spirit',) and {x: y for x, y in B[k].items() if x != 'va'} == A[k])]
        check('everything else restores the same' + (f' (differs: {diff})' if diff else ''), not diff)
        pg.evaluate("S.week=0;S.day=2;S.tab='train';S.plan[2]=[{id:'bsq',rx:'4x5',w:''}];render()"); pg.wait_for_timeout(200)
        check('coach still sees last time as finished after a restore', 'try 230 lb' in (pg.evaluate("document.querySelector('.lastw')?.textContent||''")))
        check('no page errors', not errs)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
