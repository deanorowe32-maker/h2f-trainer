"""Body weigh-ins with the Army waist-to-height check, the AFT test date (countdown, calendar, push prefs) and the HUD lock screen. Server on :8765."""
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
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500); E("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(900)
    # lock screen
    check('lock screen shows the logo inside the ring', E("!!document.querySelector('#gate .gcore .gring') && !!document.querySelector('#gate .gcore .gatelogo')"))
    check('lock screen has four corner brackets', E("document.querySelectorAll('#gate .gpanel .gk').length") == 4)
    check('lock screen covers the app (opaque)', 'rgb(5, 7, 5)' in E("getComputedStyle(document.getElementById('gate')).backgroundColor") or E("getComputedStyle(document.getElementById('gate')).backgroundColor") == 'rgb(5, 7, 5)')
    pg.fill('#gateCode', 'NOPE'); pg.click('#gate .btn'); pg.wait_for_timeout(200)
    check('wrong code shakes the panel and says so', E("document.getElementById('gate').classList.contains('bad')") and 'not right' in E("document.getElementById('gateErr').textContent"))
    check('ring animation is transform only', E("[...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>r.name==='gspin'&&r.cssText.includes('rotate'))}catch(e){return false}})"))
    E("localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    # body
    E("S.nut.unit='lb';S.nut.hu='in';S.nut.ht='';S.body={log:[]};save();pgShow()"); pg.wait_for_timeout(300)
    check('Progress has a Body section', E("!!document.getElementById('bcpTop')"))
    pg.fill('#bcpW', '182'); pg.fill('#bcpWa', '36.5'); pg.fill('#bcpH', '70'); pg.click('[data-a=bcpsave]'); pg.wait_for_timeout(200)
    check('weigh-in saved in lb and inches', E("JSON.stringify(S.body.log[0])") == '{"d":"%s","w":182,"wa":36.5}' % E("today()"))
    check('weight also updates Fuel', E("S.nut.wt") == '182' and E("S.nut.ht") == '70')
    check('waist to height 36.5/70 = 0.521 meets the standard', E("document.querySelector('#pgrBody .bcpok b').textContent") == '0.521')
    check('max waist for 70 in is under 38.5 in', 'under 38.5 in' in E("document.getElementById('pgrBody').textContent"))
    check('0.550 exactly does not meet the standard', E("bcpRatio(38.5,70)") == 0.55 and not E("bcpRatio(38.5,70)<BCP_STD"))
    E("S.body.log.push({d:'2026-01-01',w:190,wa:null});S.body=bcpClean(S.body);save();pgRefresh()"); pg.wait_for_timeout(200)
    check('weight chart appears with 2 weigh-ins', E("!!document.querySelector('#pgrBody figure.vz')"))
    pg.click('[data-a=bcpunit]'); pg.wait_for_timeout(200)
    check('switch to kg and cm converts Fuel numbers', E("S.nut.unit") == 'kg' and E("S.nut.hu") == 'cm' and E("S.nut.wt") == '82.6' and E("S.nut.ht") == '178')
    check('stored log stays in lb', E("S.body.log[0].w") == 182)
    check('shown in kg', '82.6' in E("document.querySelector('#pgrBody .bcpstats').textContent"))
    pg.fill('#bcpW', '999'); pg.click('[data-a=bcpsave]'); pg.wait_for_timeout(150)
    check('silly weight is refused', 'looks off' in E("document.getElementById('bcpMsg').textContent") and E("S.body.log.length") == 2)
    E("document.querySelector('[data-a=bcpdel][data-v=\"2026-01-01\"]').click()"); pg.wait_for_timeout(150)
    check('remove a weigh-in', E("S.body.log.length") == 1)
    check('damaged body data is cleaned', E("JSON.stringify(bcpClean({log:[null,{d:'x'},{d:'2026-02-02',w:'a',wa:30},{d:'2026-02-02',w:150}]}))") == '{"log":[{"d":"2026-02-02","w":null,"wa":30}]}')
    check('body not in squad share', 'body' not in E("JSON.stringify(sqMake())") if E("typeof sqMake") == 'function' else True)
    # backup keeps body and the AFT date
    E("S.aft.date=dk(new Date(Date.now()+10*864e5));save()")
    c = E("(()=>{const c=cleanBackup(makeBackup());return {b:c.body,d:c.aft.date}})()")
    check('backup keeps weigh-ins and AFT date', c['b']['log'][0]['w'] == 182 and c['d'] == E("S.aft.date"))
    E("document.getElementById('pgrSheet').hidden=true")
    # AFT countdown
    E("S.tab='today';render()"); pg.wait_for_timeout(300)
    check('Today shows the AFT countdown', '10 days' in E("document.getElementById('aftcd').textContent") and 'Sharpen' in E("document.getElementById('aftcd').textContent"))
    E("S.aft.date=today();render()"); check('test day', 'Test day' in E("document.getElementById('aftcd').textContent"))
    E("S.aft.date='2020-01-01';render()"); check('past date hides the countdown', not E("!!document.getElementById('aftcd')"))
    E("S.aft.date=dk(new Date(Date.now()+200*864e5));render()"); check('far date hides the countdown', not E("!!document.getElementById('aftcd')"))
    # reminders
    E("S.aft.date=dk(new Date(Date.now()+30*864e5));rmdShow()"); pg.wait_for_timeout(200)
    check('Reminders has an AFT test row', E("!!document.getElementById('rmdAft') && document.getElementById('rmdAftD').value===S.aft.date"))
    check('no AFT event until switched on', 'AFT test day' not in E("rmdIcs()"))
    pg.check('#rmdAft'); pg.wait_for_timeout(150)
    ics = E("rmdIcs()")
    check('calendar has an all-day AFT event with week and day-before alerts', 'DTSTART;VALUE=DATE:' + E("S.aft.date.replace(/-/g,'')") in ics and 'TRIGGER:-P6DT16H' in ics and 'TRIGGER:-PT16H' in ics)
    check('calendar button turns on with only AFT picked', not E("document.querySelector('[data-a=rmdics]').disabled"))
    check('push prefs carry the AFT date', E("JSON.stringify([rmdPrefs().aft_on,rmdPrefs().aft_date])") == '[true,"%s"]' % E("S.aft.date"))
    pg.fill('#rmdAftD', ''); pg.dispatch_event('#rmdAftD', 'change'); pg.wait_for_timeout(150)
    check('clearing the date stops the AFT alert', E("rmdPrefs().aft_on") is False and E("rmdPrefs().aft_date") is None)
    E("document.getElementById('rmdSheet').hidden=true;S.tab='assess';render()"); pg.wait_for_timeout(300)
    if E("!!document.getElementById('aftNext')"):
        pg.fill('#aftNext', E("dk(new Date(Date.now()+5*864e5))")); pg.dispatch_event('#aftNext', 'change'); pg.wait_for_timeout(150)
        check('AFT page sets the test date', E("aftDays()") == 5)
    else:
        check('AFT page has a test date field', False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
