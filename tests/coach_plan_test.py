"""Coach Jolt plans: a reply with a [PLAN] block shows a plan card (block hidden from the text), keeps only Library
exercises, saves into this or next week's Plan, and Undo puts the week back. The coach function is stubbed."""
import sys, json
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
REPLY = """Here is a simple week to build your run and strength.
[PLAN]
Mon | Upper body | armc - 1x10; Push-Up - 3x15; pull - 3xmax; Laser Sword Curl - 3x10; chest - 2x45 s
Wed | Aerobic | legsw - 1x10/side; z2 - 30 min, talking pace; ewalk - 5 min
Fri | Lower body | bws: 1x10; bsq - 4x5; rdl 3x8; pig - 2x45 s/side
Sat | Aerobic | ruck - 6 mi
[/PLAN]"""
calls = []
def handle(r):
    if r.request.method == 'OPTIONS': return r.fulfill(status=204, headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'})
    calls.append(json.loads(r.request.post_data))
    r.fulfill(status=200, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}, body=json.dumps({'text': REPLY, 'left': 19}))
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 390, 'height': 844}); E = pg.evaluate
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.route('**/functions/v1/coach', handle)
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(400)
    E("localStorage.clear();sessionStorage.setItem('h2f.boot','1');localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    pg.add_style_tag(content='#rbSheet{display:none!important}')
    E("S.rk={seen:0};document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='coach';render()"); pg.wait_for_timeout(300)
    pg.click('[data-a=cxon]'); pg.wait_for_timeout(200)
    check('plan suggestion offered', E("[...document.querySelectorAll('[data-a=cxsug]')].some(b=>b.textContent.includes('PT plan'))"))
    pg.click('[data-a=cxsug][data-v="4"]'); pg.wait_for_timeout(800)
    txt = E("document.querySelector('.cxm.ai p').textContent")
    check('plan block hidden from the reply text', '[PLAN]' not in txt and 'armc' not in txt and 'simple week' in txt)
    check('plan card shows Mon, Wed, Fri', 'Plan: Mon, Wed, Fri' in E("document.querySelector('.cxplan b').textContent"))
    check('unknown exercise left out and said so', '1 exercise not in the Library was left out' in E("document.querySelector('.cxplan').textContent"))
    before_tue = E("JSON.stringify(S.plan[1])"); before_mon = E("JSON.stringify(S.plan[0])")
    pg.click('[data-a=cxsave][data-v="1:0"]'); pg.wait_for_timeout(300)
    check('saved: Monday is the coach workout', E("S.types[0]") == 'upper' and E("S.plan[0].map(x=>x.id).join()") == 'armc,pu,pull,chest' and E("S.plan[0][1].rx") == '3×15')
    check('saved: Friday lower body with 4 items', E("S.types[4]") == 'lower' and E("S.plan[4].map(x=>x.id).join()") == 'bws,bsq,rdl,pig')
    check('Tuesday untouched', E("JSON.stringify(S.plan[1])") == before_tue)
    check('Saved message and Undo shown', "Saved to this week's plan" in E("document.querySelector('.cxplan').textContent") and E("!!document.querySelector('[data-a=cxundo]')"))
    pg.click('[data-a=cxundo]'); pg.wait_for_timeout(300)
    check('Undo restores Monday', E("JSON.stringify(S.plan[0])") == before_mon and E("!!document.querySelector('[data-a=cxsave]')"))
    pg.click('[data-a=cxsave][data-v="1:1"]'); pg.wait_for_timeout(300)
    nk = E("mkey(1)")
    check('next week saved without changing this week', E("JSON.stringify(S.plan[0])") == before_mon and E(f"S.weeks['{nk}'].types[2]") == 'aerobic' and E(f"S.weeks['{nk}'].plan[2].map(x=>x.id).join()") == 'legsw,z2,ewalk')
    E("wkGo(1);render()"); pg.wait_for_timeout(200)
    check('opening next week shows the coach plan', E("S.types[0]") == 'upper' and E("S.plan[0][0].id") == 'armc')
    E("S.tab='coach';render()"); pg.wait_for_timeout(200)
    check('plan card survives reload of chat', E("!!document.querySelector('.cxplan')"))
    pg.fill('#cxIn', 'thanks'); pg.click('[data-a=cxsend]'); pg.wait_for_timeout(600)
    check('history sent back has no plan block', all('[PLAN]' not in m['t'] for m in calls[-1]['msgs']))
    check('no page errors ' + '; '.join(errs), not errs)
    br.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
