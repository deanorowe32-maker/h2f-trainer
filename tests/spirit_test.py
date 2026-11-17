"""Spirit screen: one journal (today's prompt folded in); old reflection notes move into the journal. Server on :8765."""
import sys, json
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E = pg.evaluate
    try:
        # an older phone: reflection notes on 3 days, one journal entry on another day
        E("""S.spirit.log={'2026-11-01':'Grateful for my team','2026-11-02':'  ','2026-11-03':'Called home'};
             S.journal.entries=[{id:'j1',d:'2026-11-05',k:'spirit',t:'Long week'}];delete S.spirit.mig;save()""")
        before = E("rbCount('an').n")
        pg.reload(); pg.wait_for_timeout(900)
        ents = E("jrEntries('spirit').map(e=>[e.d,e.t])")
        check('notes moved into journal', ents == [['2026-11-01', 'Grateful for my team'], ['2026-11-03', 'Called home'], ['2026-11-05', 'Long week']])
        check('old notes box emptied', E("Object.keys(S.spirit.log).length") == 0)
        check('check-ins still counted', E("rbCount('an').n") == before == 3)
        pg.reload(); pg.wait_for_timeout(900)
        check('no duplicates on reopen', E("jrEntries('spirit').length") == 3)
        E("S.tab='spirit';render()"); pg.wait_for_timeout(200)
        check('separate reflection box gone', pg.locator('#jrn').count() == 0 and "Today's reflection" not in E("document.getElementById('view').innerText"))
        check('today prompt shown with button', pg.locator('#view [data-a=jrprompt][data-t=spirit]').count() >= 1 and E("document.getElementById('view').innerText.includes(PROMPTS[dayOfYear()%PROMPTS.length])"))
        E("document.querySelector('#view [data-a=jrprompt][data-t=spirit]').click()"); pg.wait_for_timeout(150)
        pg.fill('#jr_spirit', 'Answered today'); E("document.querySelector('[data-a=jrsave][data-t=spirit]').click()"); pg.wait_for_timeout(150)
        check('new entry counts as a check-in', E("rbCount('an').n") == 4)
        c = E("cleanBackup(makeBackup())")
        check('backup has the moved notes', len([e for e in c['journal']['entries'] if e['k'] == 'spirit']) == 4)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
