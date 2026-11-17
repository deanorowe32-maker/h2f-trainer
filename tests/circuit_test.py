"""Circuit workout format. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E = pg.evaluate
    try:
        # pick a weekday that is upper; make it today's weekday when it's a weekday
        wd = E("(new Date().getDay()+6)%7")
        d = wd if wd < 5 else 0
        E(f"S.week=0;S.day={d};S.types[{d}]='upper';S.plan[{d}]=genDay('upper');S.tab='train';trEdit=true;render()"); pg.wait_for_timeout(200)
        check('circuit chip shown', pg.locator('#view [data-a=fmt][data-v=c]').count() == 1)
        E("document.querySelector('#view [data-a=fmt][data-v=c]').click()"); pg.wait_for_timeout(200)
        check('fmt is c', E(f"S.fmt[{d}]") == 'c')
        check('defaults', E(f"JSON.stringify([S.dcir[{d}].mode,S.dcir[{d}].work,S.dcir[{d}].rest,S.dcir[{d}].rounds,S.dcir[{d}].rrest])") == '["t",40,20,3,90]')
        check('summary says circuit', ', circuit' in pg.locator('#view .editday > summary').inner_text())
        check('circuit card', pg.locator('#view .cicard').count() == 1 and pg.locator('#view .cicard [data-a=ciopen]').count() == 1)
        check('main list still editable', pg.locator('#view [data-a=add][data-sec=M]').count() == 1)
        # clamping
        check('clean clamps', E("JSON.stringify(ciClean({mode:'x',work:5,rest:999,rounds:0,rrest:-1,reps:{bsq:'500',zz:3}}))") == '{"mode":"t","work":40,"rest":20,"rounds":3,"rrest":90,"reps":{"zz":3}}')
        # edit settings via inputs
        pg.fill('#view [data-f=ci][data-k=rounds]', '2'); pg.fill('#view [data-f=ci][data-k=rest]', '0'); pg.wait_for_timeout(100)
        check('input saved', E(f"S.dcir[{d}].rounds") == 2 and E(f"S.dcir[{d}].rest") == 0)
        # timed phases
        n = E(f"ciIds({{plan:S.plan}},{d}).length")
        ph = E(f"ciPhases(S.dcir[{d}],ciIds({{plan:S.plan}},{d})).map(x=>x.k).join('')")
        check('timed sequence', ph == 'w' * n + 'R' + 'w' * n)
        E(f"S.dcir[{d}].rest=15")
        ph = E(f"ciPhases(S.dcir[{d}],ciIds({{plan:S.plan}},{d})).map(x=>x.k).join('')")
        check('timed sequence with rest', ph == ('wr' * (n - 1) + 'w') + 'R' + ('wr' * (n - 1) + 'w'))
        # run timed
        E("render()"); pg.wait_for_timeout(100)
        E("document.querySelector('#view [data-a=ciopen]').click()"); pg.wait_for_timeout(200)
        check('sheet open', not E("document.getElementById('ciSheet').hidden"))
        check('shows work', 'Work' in pg.locator('#ciBody').text_content() and pg.locator('#ciClock').count() == 1)
        E("CI.acc=CI.ph[0].s*1000+10;CI.start=Date.now()"); pg.wait_for_timeout(400)
        check('auto advances to rest', E("CI.idx") == 1 and 'Rest' in pg.locator('#ciBody').text_content())
        E("document.querySelector('#ciBody [data-a=cigo]').click()"); pg.wait_for_timeout(100)
        check('pause', E("CI.on") == False)
        E("document.querySelector('#ciBody [data-a=ciskip]').click()"); pg.wait_for_timeout(100)
        check('skip', E("CI.idx") == 2)
        E("CI.idx=CI.ph.length-1;CI.acc=0;CI.on=true;CI.start=Date.now()-CI.ph[CI.idx].s*1000-50"); pg.wait_for_timeout(400)
        check('done screen', E("CI.done") == True and 'Circuit done' in pg.locator('#ciBody').text_content())
        if wd < 5:
            check('mark done offered', pg.locator('#ciBody [data-a=tddone]').count() == 1)
            E("document.querySelector('#ciBody [data-a=tddone]').click()"); pg.wait_for_timeout(200)
            check('marked done as circuit', E("S.hist[0]&&S.hist[0].type").endswith('circuit') and E("document.getElementById('ciSheet').hidden"))
        # reps mode
        E(f"S.dcir[{d}].mode='r';S.dcir[{d}].rounds=1;render()"); pg.wait_for_timeout(100)
        check('reps inputs', pg.locator('#view [data-f=cirep]').count() == n)
        first = E(f"ciIds({{plan:S.plan}},{d})[0]")
        pg.fill(f'#view [data-f=cirep][data-v="{first}"]', '12'); pg.wait_for_timeout(100)
        check('rep saved', E(f"S.dcir[{d}].reps['{first}']") == 12)
        check('reps phases manual', E(f"ciPhases(S.dcir[{d}],ciIds({{plan:S.plan}},{d})).every(x=>x.k!=='w'||x.s===null)"))
        E("document.querySelector('#view [data-a=ciopen]').click()"); pg.wait_for_timeout(200)
        check('reps target shown', '12 reps' in pg.locator('#ciBody').text_content() and pg.locator('#ciBody [data-a=cinext]').count() == 1)
        for _ in range(2 * n + 2):
            if E("CI.done"): break
            if E("CI.ph[CI.idx].s===null"): E("document.querySelector('#ciBody [data-a=cinext]').click()")
            else: E("document.querySelector('#ciBody [data-a=ciskip]').click()")
            pg.wait_for_timeout(50)
        check('reps finish', E("CI.done"))
        E("document.querySelector('#ciBody [data-a=cistop]').click()"); pg.wait_for_timeout(100)
        check('close', E("document.getElementById('ciSheet').hidden"))
        # stop needs two taps mid-run
        E("document.querySelector('#view [data-a=ciopen]').click()"); pg.wait_for_timeout(100)
        E("document.querySelector('#ciBody [data-a=cistop]').click()"); pg.wait_for_timeout(100)
        check('stop arms', not E("document.getElementById('ciSheet').hidden") and 'Tap again' in pg.locator('#ciBody').text_content())
        E("document.querySelector('#ciBody [data-a=cistop]').click()"); pg.wait_for_timeout(100)
        check('stop ends', E("document.getElementById('ciSheet').hidden"))
        # Today card
        if wd < 5:
            E("S.tab='today';render()"); pg.wait_for_timeout(200)
            t = pg.locator('#view').inner_text()
            check('today circuit text', f'Circuit: {n} exercises × 1 round' in t and pg.locator('#view [data-a=ciopen]').count() >= 1)
        # week list
        E("S.tab='train';render()"); pg.wait_for_timeout(100)
        check('week list Ci', '<i>Ci</i>' in E("document.getElementById('view').innerHTML"))
        # print
        check('print weekly', 'Circuit' in E("prHtml('train',false)") and 'Circuit' in E("prHtml('mo',false)"))
        # PT share round trip
        c = E("JSON.stringify(ptClean(ptMake()))")
        check('pt share keeps circuit', E(f"(()=>{{const c={c};return c.fmt[{d}]==='c'&&c.dcir[{d}].mode==='r'&&c.dcir[{d}].reps['{first}']===12}})()"))
        check('pt summary circuit', 'circuit' in E(f"ptSummary({c})[{d}]"))
        check('pt rejects circuit on non-lift day', E("(()=>{const o=ptMake();o.types[1]='aerobic';o.fmt[1]='c';return ptClean(o).fmt[1]})()") == 'n')
        # backup round trip
        r = E(f"(()=>{{const c=cleanBackup(makeBackup());return c.fmt[{d}]==='c'&&c.dcir[{d}].reps['{first}']===12&&c.dcir[{d}].mode==='r'}})()")
        check('backup keeps circuit', r)
        # survives reload
        E("save()"); pg.reload(); pg.wait_for_timeout(900)
        check('reload keeps', E(f"S.fmt[{d}]") == 'c' and E(f"S.dcir[{d}].reps['{first}']") == 12)
        # switching week and back keeps it
        E("wkGo(1);wkGo(0)"); pg.wait_for_timeout(100)
        check('week switch keeps', E(f"S.fmt[{d}]") == 'c' and E(f"S.dcir[{d}].mode") == 'r')
        check('no page errors', not errs)
    except Exception as e:
        check('exception: ' + str(e)[:300], False)
    print(errs)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL ' + str(len(fails))))
sys.exit(1 if fails else 0)
