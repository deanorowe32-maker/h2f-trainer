"""Check script for Challenges. Run with the site served on :8765:
   python3 -m http.server 8765 &  python3 tests/challenges_test.py [1|2|3|all]"""
import sys
from playwright.sync_api import sync_playwright
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'all'
def want(n): return STAGE in ('all', str(n)) or (STAGE.isdigit() and int(STAGE) >= n)
fails = []
def check(name, ok):
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok: fails.append(name)

def fresh(pg):
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')")
    pg.reload(); pg.wait_for_timeout(900)

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(700); fresh(pg)
    E = pg.evaluate

    if want(1):
        try:
            check('day 0 push-up', E("chDayKey('2026-01-05')") == 'pu')
            check('day 11 wraps', E("chDayKey('2026-01-16')") == 'pu')
            check('day -1 back squat', E("chDayKey('2026-01-04')") == 'bsq')
            check('week 0', E("chWeekKey('2026-01-11')") == 'pu')
            check('week 1', E("chWeekKey('2026-01-12')") == 'bws')
            check('week start', E("chWeekStart('2026-11-17')") == '2026-11-16')
            check('Nov lift bench', E("chMonthLift('2026-11-17')") == 'bench')
            check('Memorial Day 2027', E("(chSpecial('2027-05-31')||{}).id") == 'md')
            check('MD window opens', E("chSpecial('2027-05-28')") is not None)
            check('MD window before', E("chSpecial('2027-05-27')") is None)
            check('Vets Day window', E("(chSpecial('2026-11-14')||{}).id") == 'vd')
            check('Vets Day closed', E("chSpecial('2026-11-15')") is None)
            check('level easy', E("chLevel(60,[50,100,150])") == 1)
            check('level hard', E("chLevel(150,[50,100,150])") == 3)
            check('level none', E("chLevel(49,[50,100,150])") == 0)
            # RF1 midnight
            E("chLog('pu',40,'2026-11-16');chLog('pu',30,'2026-11-17')")
            check('dates kept apart', E("[chSum('pu','2026-11-16','2026-11-16'),chSum('pu','2026-11-17','2026-11-17')]") == [40, 30])
            # undo
            check('undo last', E("chUndo('2026-11-17')") is True and E("chSum('pu','2026-11-17','2026-11-17')") == 0)
            check('undo leaves other day', E("chSum('pu','2026-11-16','2026-11-16')") == 40)
            # RF2 km
            E("S.assess.unit='kg'")
            check('km parsed to miles', abs(E("chParse('mi','5')") - 3.107) < 0.01)
            check('km shown', E("chShow('mi',3.107)") == '5.0 km')
            E("S.assess.unit='lb'")
            check('mi shown', E("chShow('mi',3.107)") == '3.1 mi')
            # RF3 junk
            check('junk rejected', E("['','abc','-5','0','99999'].map(x=>chParse('reps',x))") == [None]*5)
            check('plank cap', E("chParse('min','601')") is None and E("chParse('min','6.5')") == 6.5)
            # RF4 clean
            bad = "{log:{'2026-11-17':{pu:50,zz:3,bws:'x'},'bad-date':{pu:5},'2026-11-18':{run:2.5}},w:{'2026-11-17':{dl:'135 lb',pu:{}}},sp:{'2027-md':{items:[1,1,0,'x',1],lvl:9},'junk':{}},last:[{d:'2026-11-17',k:'pu',n:50},{d:'x',k:'pu',n:1}]}"
            c = E(f"chClean({bad})")
            check('clean keeps good', c['log'] == {'2026-11-17': {'pu': 50}, '2026-11-18': {'run': 2.5}})
            check('clean weights', c['w'] == {'2026-11-17': {'dl': '135 lb'}})
            check('clean special', c['sp'] == {'2027-md': {'items': [True, True, False, False, True], 'lvl': 0}})
            check('clean last', c['last'] == [{'d': '2026-11-17', 'k': 'pu', 'n': 50}])
            # RF5 week across months
            E("S.ch=chClean(null);chLog('run',2,'2026-11-30');chLog('run',3,'2026-12-06')")
            st = E("chState('2026-12-06')")
            check('week spans months', st['week']['start'] == '2026-11-30' and E("chSum('run','2026-11-30','2026-12-06')") == 5)
            check('month splits', E("chState('2026-11-30').month.miles") == 2 and st['month']['miles'] == 3)
            check('state shape', set(st) >= {'day', 'week', 'month', 'special'})
            check('state init', E("!!S.ch&&typeof S.ch.log==='object'"))
            check('backup key', E("BK_KEYS.includes('ch')"))
        except Exception as e:
            check('stage 1 ran: ' + str(e).splitlines()[0], False)

    if want(2):
        try:
            fresh(pg)
            E("window.chDayKey=()=>'pu';S.tab='today';render()"); pg.wait_for_timeout(300)
            check('card present', pg.locator('#chcard').count() == 1)
            check('three rows', [pg.locator(f'#chcard [data-row={r}]').count() for r in ('day', 'week', 'month')] == [1, 1, 1])
            check('library link', pg.locator('#chcard [data-row=day] [data-a=info][data-v=pu]').count() == 1)
            E("document.querySelector('[data-a=chopen][data-v=day]').click()"); pg.wait_for_timeout(200)
            check('sheet open', E("!document.getElementById('chSheet').hidden"))
            pg.fill('#chAmt', 'abc'); E("document.querySelector('[data-a=chadd]').click()"); pg.wait_for_timeout(200)
            check('invalid marked', pg.locator('#chAmt[aria-invalid=true]').count() == 1 and E("chSum('pu',today(),today())") == 0)
            pg.fill('#chAmt', '60'); E("document.querySelector('[data-a=chadd]').click()"); pg.wait_for_timeout(300)
            check('logged 60', E("S.ch.log[today()].pu") == 60)
            check('row shows 60 / 100', '60 / 100' in pg.locator('#chcard [data-row=day]').inner_text())
            check('saved', E("JSON.parse(localStorage.getItem('h2f.v1')).ch.log[today()].pu") == 60)
            E("document.querySelector('[data-a=chopen][data-v=day]').click()"); pg.wait_for_timeout(200)
            E("document.querySelector('[data-a=chundo]').click()"); pg.wait_for_timeout(300)
            check('undo', E("chSum('pu',today(),today())") == 0)
            E("document.querySelector('[data-a=chopen][data-v=lift]').click()"); pg.wait_for_timeout(200)
            check('weight field for lift', pg.locator('#chWt').count() == 1 and 'good form' in pg.locator('#chSheet').inner_text())
            E("document.getElementById('chSheet').hidden=true")
            E("document.querySelector('[data-a=chfold]').click()"); pg.wait_for_timeout(200); E("render()")
            check('fold persists', E("S.ch.fold") is True and pg.locator('#chcard [data-row=day]').count() == 0)
            check('folded summary', 'Today: Push-up' in pg.locator('#chcard .chsum').inner_text())
            check('workout first on Today', E("(c=>c.contains('tdwide')||c.contains('tdhero'))([...document.querySelectorAll('#view > section,#view > div')][0].classList)"))
            E("document.querySelector('[data-a=chfold]').click()"); pg.wait_for_timeout(200)
            E("window.chSpecial=()=>({id:'md',year:2027,date:'2027-05-31',from:'2027-05-28',to:'2027-06-03'});render()"); pg.wait_for_timeout(200)
            check('memorial row', pg.locator('#chcard [data-row=md]').count() == 1)
            check('level locked', E("[...document.querySelectorAll('[data-a=chmdlvl]')].every(b=>b.disabled)"))
            for i in range(5):
                E(f"document.querySelector('[data-a=chmditem][data-v=\"{i}\"]').click()"); pg.wait_for_timeout(120)
            check('level unlocked', E("[...document.querySelectorAll('[data-a=chmdlvl]')].every(b=>!b.disabled)"))
            E("document.querySelector('[data-a=chmdlvl][data-v=\"2\"]').click()"); pg.wait_for_timeout(200)
            check('memorial done', E("S.ch.sp['2027-md'].lvl") == 2)
            check('no Murph', 'murph' not in pg.locator('#chcard').inner_text().lower())
            pg.screenshot(path='/tmp/ch.png', full_page=False)
        except Exception as e:
            check('stage 2 ran: ' + str(e).splitlines()[0], False)

    if want(3):
        try:
            fresh(pg)
            E("S.rb=rbClean(null);S.ch=chClean(null);S.tab='unit';render()")  # pagehide re-saves S on reload; pg.wait_for_timeout(300)
            check('109 to earn', pg.locator('#rbcase .rbhead b').inner_text() == '109 ribbons to earn')
            check('challenge area listed', 'Challenge' in pg.locator('#rbcase').inner_text())
            ts0 = E("rbCount('tsol').n")
            E("chLog('pu',50,'2026-01-05');rbCheck()")
            check('chpu awarded', E("S.rb.aw.chpu&&S.rb.aw.chpu.n") == 1)
            E("chLog('pu',50,'2026-01-16');rbCheck()")
            check('chpu twice', E("S.rb.aw.chpu.n") == 2)
            E("chLog('pu',49,'2026-01-27');rbCheck()")
            check('below easy no star', E("S.rb.aw.chpu.n") == 2)
            E("chUndo('2026-01-16');rbCheck()")
            check('undo keeps award', E("S.rb.aw.chpu.n") == 2)
            E("chLog('pu',250,'2026-01-06');rbCheck()")
            check('weekly awarded', E("S.rb.aw.chwk&&S.rb.aw.chwk.n") == 1)
            check('wrong-day log no daily', E("!S.rb.aw.chbws"))
            E("S.ch.sp['2027-md']={items:[true,true,true,true,true],lvl:1};rbCheck()")
            check('memorial awarded', E("!!S.rb.aw.chmd"))
            E("chLog('stepup',250,'2026-11-09');rbCheck()")
            check('vets awarded', E("!!S.rb.aw.chvd"))
            E("chLog('run',20,'2026-03-02');chLog('bsq',300,'2026-03-03');rbCheck()")
            check('monthly awarded', E("!!S.rb.aw.chmo"))
            check('tsol unchanged', E("rbCount('tsol').n") == ts0)
            check('closest never challenge', E("RB.filter(r=>r.area==='Challenge').length") == 23 and E("(()=>{const b=rbNext();return !b||b.r.area!=='Challenge'})()"))
            code = E("makeBackup()")
            E("S.ch=chClean(null)")
            ok = E(f"(()=>{{const c=cleanBackup({code!r});if(!c)return false;applyBackup(c);return chSum('pu','2026-01-05','2026-01-05')===50}})()")
            check('backup round trip', ok)
        except Exception as e:
            check('stage 3 ran: ' + str(e).splitlines()[0], False)


    if STAGE in ('all', '4'):
        try:
            fresh(pg)
            E("S.rb=rbClean(null);S.ch=chClean(null)")
            ny = E("chSpecial('2026-12-30')")
            check('h NY window crosses year', ny and ny['id'] == 'ny' and ny['year'] == 2027)
            check('h NY closed Jan 5', E("chSpecial('2027-01-05')") is None)
            check('h NY uses 27', '27 burpees' in ' '.join(E("HOL.find(h=>h.id==='ny').items(2027)")))
            check('h Easter 2027', E("chEaster(2027)") == '2027-03-28')
            check('h Easter 2028', E("chEaster(2028)") == '2028-04-16')
            check('h Thanksgiving 2026', (E("chSpecial('2026-11-26')") or {}).get('id') == 'tg')
            check('h Labor Day 2026', (E("chSpecial('2026-09-07')") or {}).get('id') == 'lab')
            check('h Halloween', (E("chSpecial('2026-10-31')") or {}).get('id') == 'hw')
            check('h Army Birthday', (E("chSpecial('2026-06-14')") or {}).get('id') == 'ab')
            check('h Army targets 2026', E("HOL.find(h=>h.id==='ab').t(2026)") == [126, 251, 377])
            check('h Memorial still', (E("chSpecial('2027-05-31')") or {}).get('id') == 'md')
            check('h Vets still', (E("chSpecial('2026-11-11')") or {}).get('id') == 'vd')
            c = E("chClean({sp:{'2027-xm':{items:Array(12).fill(true),lvl:2},'2027-zz':{items:[true],lvl:1},'2027-hw':{items:[true,true,true,true,true],lvl:1}}})")
            check('h clean xm kept', c['sp'].get('2027-xm', {}).get('lvl') == 2 and len(c['sp']['2027-xm']['items']) == 12)
            check('h clean zz dropped', '2027-zz' not in c['sp'])
            check('h clean hw trimmed', len(c['sp'].get('2027-hw', {}).get('items', [])) == 3)
            before = E("JSON.stringify(chState('2026-07-04'))")
            E("chLog('hid4',900,'2026-07-04')")
            check('h logs isolated', E("JSON.stringify((({special,...r})=>r)(chState('2026-07-04')))") == E(f"JSON.stringify((({{special,...r}})=>r)({before}))"))
            E("rbCheck()")
            check('h id4 ribbon', E("!!S.rb.aw.chid4"))
            E("S.ch.sp['2026-xm']={items:Array(12).fill(true),lvl:1};rbCheck()")
            check('h xmas ribbon', E("!!S.rb.aw.chxm"))
            check('h 109 shown', E("RB_SHOW.length") == 109)
            check('h md vd ribbons still', E("(()=>{S.ch.sp['2027-md']={items:[true,true,true,true,true],lvl:1};chLog('stepup',250,'2026-11-10');return [rbChCount('chmd'),rbChCount('chvd')]})()") == [1, 1])
            E("S.ch=chClean(null);S.ch.fold=false;window.chSpecial=()=>({id:'xm',year:2026,date:'2026-12-25',from:'2026-12-22',to:'2026-12-28'});S.tab='today';render()"); pg.wait_for_timeout(200)
            check('h xmas 12 chips', pg.locator('#chcard [data-row=xm] [data-a=chmditem]').count() == 12)
            check('h xmas locked', E("[...document.querySelectorAll('#chcard [data-row=xm] [data-a=chmdlvl]')].every(b=>b.disabled)"))
            check('h xmas line', 'like the song' in pg.locator('#chcard [data-row=xm]').inner_text().lower())
            for i in range(12):
                E(f"document.querySelector('[data-row=xm] [data-a=chmditem][data-v=\"{i}\"]').click()"); pg.wait_for_timeout(60)
            E("document.querySelector('[data-row=xm] [data-a=chmdlvl][data-v=\"1\"]').click()"); pg.wait_for_timeout(200)
            check('h xmas done via UI', E("S.ch.sp['2026-xm'].lvl") == 1)
            E("S.assess.unit='kg';window.chSpecial=()=>({id:'tg',year:2026,date:'2026-11-26',from:'2026-11-23',to:'2026-11-29'});render()"); pg.wait_for_timeout(200)
            check('h tg row', pg.locator('#chcard [data-row=tg] [data-a=chopen][data-v=hol]').count() == 1)
            E("document.querySelector('[data-row=tg] [data-a=chopen]').click()"); pg.wait_for_timeout(200)
            pg.fill('#chAmt', '5'); E("document.querySelector('[data-a=chadd]').click()"); pg.wait_for_timeout(300)
            check('h tg logged km', abs((E("S.ch.log[today()]&&S.ch.log[today()].htg") or 0) - 3.107) < 0.01)
            check('h tg shows km', 'km' in pg.locator('#chcard [data-row=tg]').inner_text())
            E("S.assess.unit='lb'")
            pg.screenshot(path='/tmp/hol.png')
        except Exception as e:
            check('stage 4 ran: ' + str(e).splitlines()[0], False)

    if STAGE in ('all', 'fix'):
        try:
            fresh(pg)
            E("S.rb=rbClean(null);S.ch=chClean(null);S.assess.unit='kg'")
            n = E("chParse('mi','3.2')")
            check('fix km target meets', E(f"chLevel({n},[2,3,5])") == 1)
            check('fix km daily ribbon', E(f"(()=>{{S.ch=chClean(null);chLog('run',{n},'2026-01-11');return rbChCount('chrun')}})()") == 1)
            check('fix comma decimal', abs((E("chParse('mi','5,5')") or 0) - 3.418) < 0.01)
            E("S.assess.unit='lb';S.ch=chClean(null);chLog('pu',40,'2026-01-05');chLog('dl',20,'2026-01-05')")
            check('fix undo by key', E("chUndo('2026-01-05','pu')") is True and E("[chSum('pu','2026-01-05','2026-01-05'),chSum('dl','2026-01-05','2026-01-05')]") == [0, 20])
            E("""S.ch=chClean(null);for(let i=0;i<1500;i++){const d=chDk(CH_EPOCH+i*864e5);chLog(chDayKey(d),200,d);chLog('run',3,d)}""")
            ms = E("(()=>{const t=performance.now();for(let i=0;i<5;i++)['chwk','chmo','chpu','chrun'].forEach(rbChCount);return (performance.now()-t)/5})()")
            print('   rbChCount x4 ms', round(ms, 1))
            check('fix fast ribbon counts', ms < 25)
            want_counts = [115, 49]  # reference: slow pre-fix algorithm on this same data
            check('fix counts match reference', E("['chwk','chmo'].map(rbChCount)") == want_counts)
        except Exception as e:
            check('fix ran: ' + str(e).splitlines()[0], False)

    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails)))
sys.exit(1 if fails else 0)
