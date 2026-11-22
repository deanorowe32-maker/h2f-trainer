"""Sending a Soldier-made exercise to another Soldier. Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    def phone():
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, permissions=['clipboard-read', 'clipboard-write']); pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
        pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
        return pg
    try:
        A = phone(); E = A.evaluate
        E("S.tab='lib';render()"); A.wait_for_timeout(200)
        v = E("document.getElementById('view').innerText")
        check('old ambiguous button gone', 'Shared exercises' not in v)
        check('receive button labeled', A.locator('#view [data-a=cmopen]').inner_text().strip().lower() == 'add a shared exercise')
        check('My exercises chip', A.locator('#libChips [data-a=libcat][data-v=mine]').count() == 1)
        E("document.querySelector('#libChips [data-a=libcat][data-v=mine]').click()"); A.wait_for_timeout(150)
        check('empty My exercises explains', 'Add your exercise' in A.locator('#libList').inner_text())
        # create an exercise the normal way
        E("document.querySelector('[data-a=newex]').click()"); A.wait_for_timeout(200)
        A.fill('#nxName', 'Sandbag Shoulder Toss'); A.fill('#nxSteps', 'Squat to the bag\nDrive up and toss it over a shoulder')
        E("saveEx()"); A.wait_for_timeout(200)
        check('offer to share after saving', not E("document.getElementById('cmSheet').hidden") and 'Share it with another Soldier' in A.locator('#cmBody').inner_text())
        cid = E("S.custom[0].id")
        check('offer has share button', A.locator(f'#cmBody [data-a=cmshare][data-v="{cid}"]').count() == 1)
        E("document.getElementById('cmSheet').hidden=true;libC='mine';render()"); A.wait_for_timeout(150)
        check('listed under My exercises with Share', A.locator(f'#libList [data-a=cmshare][data-v="{cid}"]').count() == 1 and 'Sandbag Shoulder Toss' in A.locator('#libList').inner_text())
        check('built-ins not under My exercises', E("document.querySelectorAll('#libList .item').length") == 1)
        E(f"document.querySelector('#libList [data-a=cmshare][data-v=\"{cid}\"]').click()"); A.wait_for_timeout(200)
        msg = E("document.getElementById('xsOut').value")
        check('send sheet has the message', 'H2FEX1:' in msg and 'Sandbag Shoulder Toss' in msg and 'Add a shared exercise' in msg and 'Shared exercises' not in msg)
        check('photos note', "Photos" in A.locator('#cmBody').inner_text())
        # second Soldier receives by pasting
        B = phone(); F = B.evaluate
        F("S.squad.name='PFC Lee';S.tab='lib';render();document.querySelector('[data-a=cmopen]').click()"); B.wait_for_timeout(200)
        check('receive sheet is receive-only', 'Send your exercises' not in B.locator('#cmBody').inner_text())
        B.fill('#xsIn', msg); B.wait_for_timeout(300)
        check('preview shows the exercise', 'Sandbag Shoulder Toss' in B.locator('#cmBody').inner_text())
        F("document.querySelector('[data-a=xsadd]').click()"); B.wait_for_timeout(200)
        check('added to their library', F("Object.values(EX).some(e=>e.custom&&e.name==='Sandbag Shoulder Toss')"))
        # sender name shown when known
        F("xsLoad({from:'SPC Diaz',ex:[{name:'Sandbag Shoulder Toss',cat:'bodyweight',sec:'M',eq:'Sandbag',steps:['a'],cue:'c'}]})"); B.wait_for_timeout(150)
        t = B.locator('#cmBody').inner_text()
        check('says who sent it', 'SPC Diaz sent you an exercise' in t)
        check('duplicate flagged', 'Already in your library' in t and F("document.querySelector('[data-a=xsadd]').disabled"))
        check('sharing still counts toward ribbons', E("S.rb.tally.sh") >= 0)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
