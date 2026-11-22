"""Reminders: workout, bedtime and weekly backup, as calendar events (.ics) or push notifications. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, accept_downloads=True); pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E = pg.evaluate
    try:
        E("S.tab='unit';render()"); pg.wait_for_timeout(200)
        check('Unit has a Reminders row', E("!!document.querySelector('main [data-a=rmdopen]')"))
        pg.click('main [data-a=rmdopen]'); pg.wait_for_timeout(300)
        check('Reminders sheet opens', E("!document.getElementById('rmdSheet').hidden"))
        check('four reminder switches (workout, bedtime, backup, AFT test)', E("document.querySelectorAll('#rmdBody input[type=checkbox]').length") == 4)
        check('workout default 06:00, Mon-Fri', E("document.getElementById('rmdWkT').value") == '06:00' and E("S.rmd.wk.days.join()") == '1,2,3,4,5')
        check('bedtime default is 8 h 15 before wake-up (21:45 for 06:00)', E("document.getElementById('rmdBedT').value") == '21:45')
        check('calendar button waits until something is picked', E("document.querySelector('[data-a=rmdics]').disabled"))
        pg.check('#rmdWk'); pg.check('#rmdBed'); pg.check('#rmdBk'); pg.fill('#rmdWkT', '05:30'); pg.dispatch_event('#rmdWkT', 'change'); pg.wait_for_timeout(100)
        ics = E("rmdIcs()")
        check('calendar file has 3 events with alarms', ics.startswith('BEGIN:VCALENDAR') and ics.count('BEGIN:VEVENT') == 3 and ics.count('BEGIN:VALARM') == 3)
        check('workout repeats Mon-Fri at 05:30 local time', 'RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR' in ics and 'T053000\r\n' in ics and 'T053000Z' not in ics)
        check('bedtime daily, backup Sundays 18:00', 'RRULE:FREQ=DAILY' in ics and 'RRULE:FREQ=WEEKLY;BYDAY=SU' in ics and 'T180000\r\n' in ics)
        check('lines end in CRLF', '\r\n' in ics and '\n' not in ics.replace('\r\n', ''))
        with pg.expect_download() as d:
            pg.click('[data-a=rmdics]')
        check('Add to my calendar downloads h2f-reminders.ics', d.value.suggested_filename == 'h2f-reminders.ics')
        pg.click('#rmdBody [data-day="6"]'); pg.wait_for_timeout(100)
        check('tapping Sat adds it to the workout days', E("S.rmd.wk.days.join()") == '1,2,3,4,5,6')
        pp = E("rmdPrefs()")
        check('notification settings sent to the server', pp == {'wk_on': True, 'wk_time': '05:30', 'wk_days': [1, 2, 3, 4, 5, 6], 'bed_on': True, 'bed_time': '21:45', 'bk_on': True, 'aft_on': False, 'aft_date': None})
        E("save()"); pg.reload(); pg.wait_for_timeout(900)
        check('settings kept after reload', E("S.rmd.wk.on&&S.rmd.wk.t==='05:30'&&S.rmd.bk.on"))
        E("delete window.PushManager;rmdShow()"); pg.click('[data-a=rmdpush]'); pg.wait_for_timeout(400)
        check('unsupported browser gets a clear message', 'calendar' in E("document.getElementById('rmdMsg').textContent").lower())
        sw = E("fetch('/sw.js').then(r=>r.text())")
        check('service worker shows pushed reminders and opens the app on tap', "addEventListener('push'" in sw and "addEventListener('notificationclick'" in sw)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
