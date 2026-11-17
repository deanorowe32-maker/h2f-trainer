"""Platoon program (8-week block pushed by a leader). Server on :8765."""
import sys, json
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
        # ---------- Task 1: data core ----------
        blank = E("JSON.stringify(prBlank('RTP',mkey(0)))")
        bo = json.loads(blank)
        check('T1 blank 8x5', len(bo['w']) == 8 and all(len(w['d']) == 5 for w in bo['w']))
        check('T1 blank focus', [d['f'] for d in bo['w'][0]['d']] == E("PR_FOCUS"))
        check('T1 clean keeps blank', E(f"JSON.stringify(prClean({blank}))") == blank)
        check('T1 clean rejects junk', E("prClean({})") is None and E(f"(()=>{{const o={blank};o.w.pop();return prClean(o)}})()") is None and E(f"(()=>{{const o={blank};o.s='nope';return prClean(o)}})()") is None)
        r = E(f"""(()=>{{const o={blank};o.w[0].d[1].r=[{{p:'M',id:'zzz'}},{{p:'M',id:'bench',rx:'x'.repeat(40),rpe:11,pct:'56'}}];return JSON.stringify(prClean(o).w[0].d[1].r)}})()""")
        rr = json.loads(r)
        check('T1 clean rows', len(rr) == 1 and rr[0]['id'] == 'bench' and len(rr[0]['rx']) == 30 and 'rpe' not in rr[0] and rr[0]['pct'] == 56)
        check('T1 suggest majority', E("grpSuggest({sh:58,bp:280,dl:420})") == 'A')
        check('T1 suggest tie lower', E("grpSuggest({sh:70,bp:310})") == 'C')
        check('T1 suggest empty', E("grpSuggest({})") == '')
        E("S.prog=prBlank('RTP',mkey(0))")
        check('T1 week of', E("prWeekOf(mkey(0))") == 0 and E("prWeekOf(mkey(8))") == -1 and E("prWeekOf(mkey(7))") == 7)
        check('T1 weekend no day', E("(()=>{const d=monday(0);d.setDate(d.getDate()+5);return prDayAt(dk(d))})()") is None)
        check('T1 weekday day', E("prDayAt(mkey(0))&&prDayAt(mkey(0)).f") == 'anaerobic')
        E("S.maxes.bench={v:300,u:'lb',d:today()};S.assess.unit='lb'")
        check('T1 load pct', E("prLoad({p:'M',id:'bench',pct:50})") == '50% → 150 lb')
        E("delete S.maxes.bench;S.grp={g:'A',w0:{}}")
        check('T1 load group', E("prLoad({p:'M',id:'bench',g:{A:'185–150 lb'}})") == 'A group: 185–150 lb')
        E("S.grp={g:'',w0:{}}")
        check('T1 load none', E("prLoad({p:'M',id:'bench',pct:50,g:{A:'x'}})") == '')
        E("S.assess.unit='kg';S.maxes.bench={v:100,u:'kg',d:today()}")
        check('T1 load kg', E("prLoad({p:'M',id:'bench',pct:50})").endswith(' kg'))
        E("S.assess.unit='lb';delete S.maxes.bench")
        E("S.grp={g:'B',w0:{sh:61}}")
        bk = E("(()=>{const c=cleanBackup(makeBackup());return JSON.stringify([c.prog&&c.prog.n,c.grp])})()")
        check('T1 backup', bk == '["RTP",{"g":"B","w0":{"sh":61}}]')
        E("save()"); A.reload(); A.wait_for_timeout(900)
        check('T1 reopen boots', E("BOOTED") == True and E("S.prog&&S.prog.n") == 'RTP')
        check('no page errors', not errs)
    except Exception as e:
        check('exception: ' + str(e)[:300], False)
    print(errs)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL ' + str(len(fails))))
sys.exit(1 if fails else 0)
