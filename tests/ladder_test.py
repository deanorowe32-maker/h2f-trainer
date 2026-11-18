"""Exercise progressions and regressions on the info card. Server on :8765."""
import sys, json
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    def phone():
        ctx = b.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
        pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
        return pg
    try:
        A = phone(); E = A.evaluate
        # ---------- Task 1 ----------
        check('T1 chain ids exist', E("LAD_CHAINS.flat().filter(id=>!EX[id])").__len__() == 0)
        check('T1 new exercises', E("['ipu','kpu','bapu','npu'].every(id=>EX[id]&&EX[id].steps.length>=3)"))
        check('T1 pu built-in', E("JSON.stringify(ladFor('pu'))") == '{"e":["kpu"],"h":["hrpu"]}')
        check('T1 merges chains', len(E("ladFor('bws').h")) >= 2)
        E("S.prog=prBlank('x',mkey(0));S.prog.ld={pu:{e:['ipu'],h:[]}}")
        check('T1 program wins over built-in', E("ladFor('pu').e.join()") == 'ipu')
        E("S.lad={pu:{e:['chsq'],h:['pplu']}}")
        check('T1 own edit wins', E("JSON.stringify(ladFor('pu'))") == '{"e":["chsq"],"h":["pplu"]}')
        check('T1 clean', E("JSON.stringify(ladClean({pu:{e:['zzz','pu','kpu','ipu','chsq','bws'],h:'x'},zzz:{e:['pu']}}))") == '{"pu":{"e":["kpu","ipu","chsq"],"h":[]}}')
        E("S.prog=null")
        check('T1 backup', E("JSON.stringify(cleanBackup(makeBackup()).lad)") == '{"pu":{"e":["chsq"],"h":["pplu"]}}')
        E("save()"); A.reload(); A.wait_for_timeout(900)
        check('T1 reopen', E("BOOTED") == True and E("S.lad.pu.h[0]") == 'pplu')
        check('no page errors', not errs)
    except Exception as e:
        check('exception: ' + str(e)[:300], False)
    print(errs)
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL ' + str(len(fails))))
sys.exit(1 if fails else 0)
