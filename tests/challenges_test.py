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

    if want(3): pass  # Task 3

    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails)))
sys.exit(1 if fails else 0)
