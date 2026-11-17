"""Checks for the AFT "What do I need?" planner. Server on :8765: python3 tests/aft_need_test.py"""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(800)
    E = pg.evaluate
    try:
        E("Object.assign(S.aft,{age:'28',sex:'m',std:'g'});S.aft.in={mdl:'200',hrp:'20',sdc:'2:30',plk:'1:30',run:'18:30'}")
        s = E("aftScore()")
        plan = E("aftPlan(aftScore(),350)")
        check('plan reaches target', plan['t'] >= 350)
        check('every event at 60+', all(x >= 60 for x in plan['p']))
        check('never lowers an event', all(a >= b for a, b in zip(plan['p'], s['p'])))
        check('raw results score as planned', E("(()=>{const s=aftScore(),pl=aftPlan(s,350);return AFT_EV.every(([k],i)=>aftPts(k,s.g,s.fem,pl.r[i])>=pl.p[i])})()"))
        check('weakest raised first', E("(()=>{const s=aftScore(),pl=aftPlan(s,s.t+1),i=s.p.indexOf(Math.min(...s.p));return pl.p[i]>s.p[i]})()"))
        check('500 caps at 100s', E("aftPlan(aftScore(),500).p") == [100] * 5)
        check('already there', E("aftPlan(aftScore(),100).done") is True)
        E("S.aft.in={mdl:'200'}")
        check('missing events count as 0 and get planned', E("aftPlan(aftScore(),300).p.every(x=>x>=60)"))
        E("S.aft.in={mdl:'200',hrp:'20',sdc:'2:30',plk:'1:30',run:'18:30'};S.tab='assess';render()"); pg.wait_for_timeout(300)
        E("aftUpd()"); pg.wait_for_timeout(100)
        check('planner shown', pg.locator('#aftRes .aftneed').count() == 1)
        E("document.querySelector('#aftRes [data-a=aftgoal][data-v=\"400\"]').click()"); pg.wait_for_timeout(200)
        check('goal remembered', E("S.aft.goal") == 400)
        check('planner table rows', pg.locator('#aftRes .aftneed tbody tr').count() == 5)
        check('no age message', E("(()=>{S.aft.age='';return aftResHtml().includes('aftneed')})()") is False)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
