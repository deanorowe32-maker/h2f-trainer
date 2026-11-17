"""Check script for 'My goal test'. Run with the site served on :8765:
   python3 -m http.server 8765 &  python3 tests/goal_test.py [1|2|3|4|all]"""
import sys, json
from playwright.sync_api import sync_playwright
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'all'
def want(n): return STAGE in ('all', str(n)) or (STAGE.isdigit() and int(STAGE) >= n)
fails = []
def check(name, ok):
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok: fails.append(name)

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(700)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')")
    pg.reload(); pg.wait_for_timeout(1000)
    E = pg.evaluate

    if want(1):
        check('parse 8:30', E("gtParse('time','8:30')") == 510)
        check('parse 8.5', E("gtParse('time','8.5')") == 510)
        check('parse 510', E("gtParse('time','510')") == 510)
        check('parse 8:3x rejected', E("gtParse('time','8:3x')") is None)
        check('parse reps', E("gtParse('reps','45')") == 45)
        check('parse bad reps', E("gtParse('reps','abc')") is None)
        check('pct time 50', E("gtPct({m:'time',base:600,goal:480},540)") == 50)
        check('pct clamps 100', E("gtPct({m:'reps',base:30,goal:40},50)") == 100)
        check('pct clamps 0', E("gtPct({m:'reps',base:30,goal:40},20)") == 0)
        check('fmt time', E("gtFmt('time',510)") == '8:30')
        T = "{id:'t',name:'X',why:'',due:'',appr:{by:'',d:''},ev:[{name:'A',exId:null,m:'reps',unit:'',note:'',base:30,goal:40},{name:'B',exId:null,m:'time',unit:'',note:'',base:600,goal:480}],log:[],done:''}"
        check('not met at start', E(f"gtMet({T})") is False)
        check('met when both reach', E(f"(()=>{{const t={T};t.log.push({{d:'2026-11-17',v:[40,470]}});return gtMet(t)}})()") is True)
        check('latest keeps skipped', E(f"(()=>{{const t={T};t.log.push({{d:'2026-11-10',v:[35,550]}});t.log.push({{d:'2026-11-17',v:[38,null]}});return [gtLatest(t,0),gtLatest(t,1)]}})()") == [38, 550])
        check('state init', E("!!S.goal&&S.goal.cur===null&&Array.isArray(S.goal.past)"))

    if want(2):
        E("S.tab='assess';render()"); pg.wait_for_timeout(300)
        pg.evaluate("document.querySelector('[data-a=gtnew]').click()"); pg.wait_for_timeout(300)
        pg.fill('#gtName', 'Air Assault prep'); pg.fill('#gtWhy', 'Preparing for Air Assault selection.'); pg.fill('#gtDue', '2027-02-15')
        rows = [('Ruck 4 mi', 'time', '', '35 lb', '68:00', '60:00'), ('Trap Bar Deadlift', 'weight', '', '', '225', '275'), ('Hand-Release Push-Up', 'reps', '', '', '32', '45')]
        for i, (n, m, u, note, now, goal) in enumerate(rows):
            if i > 0: pg.evaluate("document.querySelector('[data-a=gtaddev]').click()"); pg.wait_for_timeout(150)
            pg.fill(f'#gtEvName{i}', n); pg.select_option(f'#gtEvM{i}', m); pg.fill(f'#gtEvNote{i}', note); pg.fill(f'#gtEvBase{i}', now); pg.fill(f'#gtEvGoal{i}', goal)
        pg.fill('#gtApprBy', 'SSG Smith'); pg.fill('#gtApprD', '2026-11-17')
        # invalid time keeps editor open
        pg.fill('#gtEvBase0', '68:0x'); pg.evaluate("document.querySelector('[data-a=gtsave]').click()"); pg.wait_for_timeout(300)
        check('invalid time blocks save', E("S.goal.cur===null") and pg.locator('#gtEvBase0[aria-invalid=true]').count() == 1)
        pg.fill('#gtEvBase0', '68:00'); pg.evaluate("document.querySelector('[data-a=gtsave]').click()"); pg.wait_for_timeout(300)
        check('saved 3 events', E("S.goal.cur&&S.goal.cur.ev.length") == 3)
        check('time stored in seconds', E("S.goal.cur.ev[0].base") == 4080)
        check('summary rows', pg.locator('.gtsum tbody tr').count() == 3)
        check('summary heading copy', 'Personal training goal' in pg.locator('.gtsum').inner_text())
        check('approval line', 'Approved by SSG Smith' in pg.locator('.gtsum').inner_text())
        # retest with one blank
        pg.evaluate("document.querySelector('[data-a=gtlogopen]').click()"); pg.wait_for_timeout(200)
        pg.fill('#gtLog0', '64:30'); pg.fill('#gtLog1', '245'); pg.fill('#gtLog2', '')
        pg.evaluate("document.querySelector('[data-a=gtlog]').click()"); pg.wait_for_timeout(300)
        check('retest logged', E("S.goal.cur.log.length") == 1)
        check('skipped keeps baseline', E("gtLatest(S.goal.cur,2)") == 32)
        check('latest deadlift', E("gtLatest(S.goal.cur,1)") == 245)
        pg.evaluate("document.querySelector('[data-a=gtlogopen]').click()"); pg.wait_for_timeout(200)
        pg.fill('#gtLog0', '59:40'); pg.fill('#gtLog1', '275'); pg.fill('#gtLog2', '46')
        pg.evaluate("document.querySelector('[data-a=gtlog]').click()"); pg.wait_for_timeout(300)
        check('goal met banner', pg.locator('.gtmet').count() == 1)
        pg.evaluate("document.getElementById('gt').scrollIntoView()"); pg.wait_for_timeout(200)
        pg.locator('#gt').screenshot(path='/tmp/gt.png')

    if want(3):
        if not E("S.goal.cur"):
            E("S.goal.cur={id:'t1',name:'Mine',why:'',due:'2027-01-01',appr:{by:'',d:''},ev:[{name:'Run',exId:null,m:'time',unit:'',note:'',base:900,goal:840}],log:[],done:''};save()")
        code = E("gtEnc(S.goal.cur)")
        check('round trip', E(f"JSON.stringify(gtDec('{code}'))===JSON.stringify(gtClean(S.goal.cur))"))
        other = E("gtEnc({id:'x',name:'Theirs',why:'w',due:'2027-03-01',appr:{by:'',d:''},ev:[{name:'Row',exId:null,m:'distance',unit:'km',note:'',base:5,goal:6}],log:[],done:''})")
        mine = E("S.goal.cur.name")
        pg.goto(f'http://localhost:8765/#gt={other}'); pg.wait_for_timeout(1200)
        check('shared sheet opens', pg.locator('#gtShared:not([hidden])').count() == 1)
        check('own test untouched', E("S.goal.cur.name") == mine)
        pg.evaluate("document.querySelector('[data-a=gtadopt]').click()"); pg.wait_for_timeout(300)
        check('adopted', E("S.goal.cur.name") == 'Theirs' and E("S.goal.past.some(t=>t.name===" + json.dumps(mine) + ")"))
        txt = E("gtText(S.goal.cur)")
        check('text summary', 'Personal training goal' in txt and 'Row' in txt)

    if want(4):
        if not E("S.goal.cur"):
            E("S.goal.cur={id:'t2',name:'B',why:'',due:'',appr:{by:'',d:''},ev:[{name:'A',exId:null,m:'reps',unit:'',note:'',base:10,goal:12}],log:[],done:''};save()")
        check('backup keeps goal', E("cleanBackup(makeBackup()).goal.cur.name") == E("S.goal.cur.name"))
        check('bad goal ignored', E("(()=>{const o=JSON.parse(JSON.stringify(cleanBackup(makeBackup())));o.goal={cur:{ev:'x'},past:[null,{ev:[]}]};const c=gtCleanStore(o.goal);return c.cur===null&&c.past.length===0})()"))
        E("S.goal.cur.log.push({d:today(),v:[S.goal.cur.ev[0].goal]});save()")
        check('own ribbon', 'own' in [x['id'] for x in E("rbCheck()")] or E("!!S.rb.aw.own"))
        for t in ['today', 'train', 'pt', 'assess', 'unit']:
            E(f"S.tab='{t}';render()"); pg.wait_for_timeout(200)

    check('no page errors', not errs); 
    if errs: print(errs[:3])
    b.close()
print('RESULT', 'OK' if not fails else f'{len(fails)} failed')
sys.exit(1 if fails else 0)
