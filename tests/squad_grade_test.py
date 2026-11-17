"""Checks for Grade a squad (AFT scoresheet). Server on :8765: python3 tests/squad_grade_test.py"""
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
        E("S.squad.members=[{n:'SPC Diaz',d:today(),v:1},{n:'PFC Lee',d:today(),v:1}];S.tab='assess';render()"); pg.wait_for_timeout(200)
        E("document.querySelector('[data-a=sgnew]').click()"); pg.wait_for_timeout(200)
        check('roster names prefilled', E("S.sg.cur.rows.map(r=>r.n)") == ['SPC Diaz', 'PFC Lee'])
        check('grader prefilled', E("typeof S.sg.cur.by==='string'"))
        # fill row 0 through the inputs
        for t, v in [('age', '28'), ('mdl', '200'), ('hrp', '20'), ('sdc', '2:30'), ('plk', '1:30'), ('run', '18:30')]:
            pg.fill(f'[data-f=sgf][data-t="0:{t}"]', v)
        pg.select_option('[data-f=sgf][data-t="0:sex"]', 'm')
        pg.wait_for_timeout(200)
        s = E("sgScore(S.sg.cur.rows[0])")
        check('row scores like the calculator', s and s['t'] == E("(()=>{Object.assign(S.aft,{age:'28',sex:'m',std:'g'});S.aft.in={mdl:'200',hrp:'20',sdc:'2:30',plk:'1:30',run:'18:30'};return aftScore().t})()"))
        check('row result shown', '327' in pg.locator('[data-sgrow="0"]').inner_text() and 'PASS' in pg.locator('[data-sgrow="0"]').inner_text().upper())
        check('incomplete row says so', E("sgScore(S.sg.cur.rows[1])") is None or E("sgScore(S.sg.cur.rows[1]).all") is False)
        tsv = E("sgTSV(S.sg.cur)")
        lines = tsv.split('\n')
        check('tsv header', lines[0].startswith('Name\tAge\tSex\tStandard\t3-Rep Max Deadlift'))
        check('tsv row', lines[1].split('\t')[0] == 'SPC Diaz' and lines[1].split('\t')[-2] == '327' and lines[1].split('\t')[-1] == 'Pass')
        check('tsv no tabs injected', E("(()=>{const r=S.sg.cur.rows[1];r.n='A\\tB\\nC';return sgTSV(S.sg.cur).split('\\n').length})()") == 3)
        E("S.sg.cur.rows[1].n='PFC Lee'")
        E("document.querySelector('[data-a=sgadd]').click()"); pg.wait_for_timeout(150)
        check('add row', E("S.sg.cur.rows.length") == 3)
        E("document.querySelector('[data-a=sgrm][data-v=\"2\"]').click()"); pg.wait_for_timeout(150)
        check('remove row', E("S.sg.cur.rows.length") == 2)
        E("window.print=()=>{window._printed=1};document.querySelector('[data-a=sgprint]').click()"); pg.wait_for_timeout(200)
        check('print sheet built', E("window._printed") == 1 and 'SPC Diaz' in E("document.getElementById('sgPrint').innerText") and 'signature' in E("document.getElementById('sgPrint').textContent").lower())
        E("window.print=()=>{};sgPrint(S.sg.cur)"); pg.emulate_media(media='print'); pg.wait_for_timeout(150)
        check('print sheet visible when printing', E("getComputedStyle(document.getElementById('sgPrint')).display") == 'block')
        pg.emulate_media(media='screen')
        E("document.querySelector('[data-a=sgdone]').click()"); pg.wait_for_timeout(150)
        check('finish moves to history', E("S.sg.cur") is None and E("S.sg.hist.length") == 1)
        c = E("sgClean({cur:{d:'2026-11-17',by:'SGT X',rows:[{n:'<b>A</b>',age:'999999',sex:'q',std:'z',in:{mdl:'200',xx:'1'}},'junk']},hist:[{d:'bad'},{d:'2026-11-01',by:'',rows:[]}]})")
        check('clean row', c['cur']['rows'] == [{'n': '<b>A</b>', 'age': '999', 'sex': '', 'std': 'g', 'in': {'mdl': '200'}}])
        check('clean hist', len(c['hist']) == 1)
        check('backup key', E("BK_KEYS.includes('sg')"))
        check('names escaped', '<b>A</b>' not in E("(()=>{S.sg=sgClean({cur:{d:'2026-11-17',by:'',rows:[{n:'<b>A</b>'}]},hist:[]});return sgHtml()})()"))
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
