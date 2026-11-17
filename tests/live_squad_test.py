"""Live squad against an in-memory stand-in for the Supabase functions (the real ones are tested in SQL). Server on :8765."""
import sys, json, re, uuid, hashlib, random, time
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
DB = {'squads': {}, 'members': {}, 'blocked': set(), 'calls': [], 'down': False, 'bad_headers': 0}
H = lambda k: hashlib.sha256(k.encode()).hexdigest() if isinstance(k, str) and re.fullmatch(r'[0-9a-f]{64}', k) else None
def code(): return ''.join(random.choice('ABCDEFGHJKMNPQRSTVWXYZ23456789') for _ in range(8))
def rpc(fn, a):
    sq, mem = DB['squads'], DB['members']
    if fn == 'create_squad':
        h = H(a['p_leader_key']); s = next((x for x in sq.values() if x['lh'] == h), None)
        if not s: s = {'id': str(uuid.uuid4()), 'name': a['p_name'][:40], 'code': code(), 'lh': h}; sq[s['id']] = s
        return {'squad_id': s['id'], 'join_code': s['code'], 'name': s['name']}
    if fn == 'my_squad':
        s = next((x for x in sq.values() if x['lh'] == H(a['p_leader_key'])), None)
        return s and {'squad_id': s['id'], 'join_code': s['code'], 'name': s['name']}
    if fn == 'join_squad':
        c = re.sub(r'[^A-Za-z0-9]', '', a['p_code']).upper(); s = next((x for x in sq.values() if x['code'] == c), None); h = H(a['p_member_key'])
        if not s or (s['id'], h) in DB['blocked']: return None
        m = next((x for x in mem.values() if x['sid'] == s['id'] and x['mh'] == h), None)
        if not m: m = {'id': str(uuid.uuid4()), 'sid': s['id'], 'mh': h, 'summary': {}, 'joined_at': '2026-11-17T10:00:00Z'}; mem[m['id']] = m
        m['name'] = a['p_name'][:40]; m['updated_at'] = '2026-11-17T10:00:00Z'
        return {'squad_id': s['id'], 'squad_name': s['name']}
    if fn == 'push_summary':
        m = next((x for x in mem.values() if x['sid'] == a['p_squad'] and x['mh'] == H(a['p_member_key'])), None)
        if not m: return None
        m['summary'] = a['p_summary']; m['name'] = a['p_name']; m['updated_at'] = '2026-11-17T12:00:00Z'; return m['updated_at']
    if fn == 'leave_squad':
        m = next((x for x in mem.values() if x['sid'] == a['p_squad'] and x['mh'] == H(a['p_member_key'])), None)
        if m: del mem[m['id']]
        return bool(m)
    s = sq.get(a.get('p_squad'))
    ok = s and s['lh'] == H(a.get('p_leader_key'))
    if fn == 'leader_roster':
        return [{'id': m['id'], 'name': m['name'], 'summary': m['summary'], 'updated_at': m['updated_at'], 'joined_at': m['joined_at']} for m in mem.values() if m['sid'] == s['id']] if ok else None
    if fn == 'remove_member':
        m = mem.get(a['p_member'])
        if not ok or not m or m['sid'] != s['id']: return False
        DB['blocked'].add((s['id'], m['mh'])); del mem[m['id']]; return True
    if fn == 'reset_code':
        if not ok: return None
        s['code'] = code(); return s['code']
    if fn == 'delete_squad':
        if not ok: return False
        for k in [k for k, m in mem.items() if m['sid'] == s['id']]: del mem[k]
        del sq[s['id']]; return True
    raise Exception('unknown ' + fn)
def handle(route):
    req = route.request; fn = req.url.rsplit('/', 1)[1]
    hd = req.headers
    if hd.get('apikey') != 'sb_publishable_14PpYWw6-npA1FW08cMHKA_hT5LQqsH' or 'authorization' in hd: DB['bad_headers'] += 1
    if DB['down']: return route.fulfill(status=503, body='down')
    a = json.loads(req.post_data or '{}'); DB['calls'].append(fn)
    try: out = rpc(fn, a)
    except Exception as e:
        print('   stand-in server error in', fn, repr(e)); return route.fulfill(status=500, body='err')
    route.fulfill(status=200, content_type='application/json', body=json.dumps(out))
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    def phone(name):
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', permissions=['clipboard-read', 'clipboard-write'])
        ctx.route('**/rest/v1/rpc/*', handle); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(name + ': ' + str(e)[:150]))
        pg.goto('http://localhost:8765/'); pg.wait_for_timeout(500)
        pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
        return ctx, pg
    try:
        lctx, L = phone('leader'); sctx, P = phone('soldier')
        # leader creates
        L.evaluate("S.tab='unit';render();sqMode='sq';sqShow()"); L.wait_for_timeout(200)
        L.fill('#lsName', '2nd Squad'); L.evaluate("document.querySelector('[data-a=lscreate]').click()"); L.wait_for_timeout(600)
        code_txt = L.locator('.lscode').inner_text()
        check('leader gets a join code', re.fullmatch(r'[A-Z2-9]{4}-[A-Z2-9]{4}', code_txt) is not None)
        check('keys not in backup', L.evaluate("(()=>{const o=lsGet(),b=makeBackup();return !b.includes(o.lk)&&!b.includes(o.mk)&&!b.includes('h2f.cloud')})()"))
        # soldier joins
        P.evaluate("S.squad.name='SPC Diaz';S.squad.inc.nu=0;S.tab='unit';render();sqMode='me';sqShow()"); P.wait_for_timeout(200)
        consent = P.locator('#sqBody .lsbox').inner_text()
        check('consent lists shared fields', "You'll share:" in consent and 'Training' in consent and 'Nutrition' not in consent)
        P.fill('#lsCode', code_txt.lower()); P.evaluate("document.querySelector('[data-a=lsjoin]').click()"); P.wait_for_timeout(800)
        m = list(DB['members'].values())
        check('fix nothing sent before confirming', len(m) == 1 and m[0]['summary'] == {})
        check('fix confirm names the squad', 'Share these with 2nd Squad' in P.locator('#sqBody .lsbox').inner_text())
        DB['down'] = True; P.evaluate("document.querySelector('[data-a=lsshare]').click()"); P.wait_for_timeout(600); DB['down'] = False
        check('fix no false sent message', 'was sent' not in P.locator('#sqBody .lsbox').inner_text() and "Couldn't reach" in P.locator('#sqBody .lsbox').inner_text())
        P.evaluate("document.querySelector('[data-a=lssend]').click()"); P.wait_for_timeout(600)
        m = list(DB['members'].values())
        check('joined and summary sent', len(m) == 1 and m[0]['name'] == 'SPC Diaz' and m[0]['summary'].get('n') == 'SPC Diaz' and 'tr' in m[0]['summary'] and 'nu' not in m[0]['summary'])
        check('soldier sees shared status', 'Shared with 2nd Squad' in P.locator('#sqBody .lsbox').inner_text())
        # toggling a field resends
        P.evaluate("document.querySelector('[data-a=sqinc][data-v=\"tr\"]').click()"); P.wait_for_timeout(500)
        check('turning a field off updates the server', 'tr' not in list(DB['members'].values())[0]['summary'])
        # auto send on open: only when an hour has passed
        n0 = DB['calls'].count('push_summary')
        P.reload(); P.wait_for_timeout(2200)
        check('no resend within the hour', DB['calls'].count('push_summary') == n0)
        P.evaluate("(()=>{const o=lsGet();o.mem.last=Date.now()-2*3600e3;lsSet(o)})()"); P.reload(); P.wait_for_timeout(2200)
        check('resends on open after an hour', DB['calls'].count('push_summary') == n0 + 1)
        # leader sees live member and board
        L.evaluate("document.querySelector('[data-a=lsrefresh]').click()"); L.wait_for_timeout(600)
        body = L.locator('#sqBody').inner_text()
        check('leader sees live Soldier', 'SPC Diaz' in body and 'LIVE' in body.upper())
        check('live member feeds roll-up', L.evaluate("ruOwn().n") == 1)
        check('fix same name never hides a Soldier', L.evaluate("(()=>{S.squad.members=[sqClean({v:1,n:'SPC Diaz',d:'2026-11-01'})];return sqMembersAll().length})()") == 2)
        check('fix future dates clamped', L.evaluate("(()=>{const o=lsGet(),r=o.cache.rows;r.push({id:'f1',name:'SPC Diaz',summary:{v:1,n:'SPC Diaz',d:'9999-12-31'},joined_at:'2026-11-17T00:00:00Z'});lsSet(o);const ok=lsLive().every(m=>m.d<=today());r.pop();lsSet(o);return ok})()"))
        L.evaluate("S.squad.members=[]")
        check('server text escaped', L.evaluate("(()=>{const o=lsGet();o.cache.rows=[{id:'x',name:'<img src=x onerror=alert(1)>',summary:{},joined_at:'2026-11-17T00:00:00Z'}];lsSet(o);sqShow();return !document.querySelector('#sqBody img')})()"))
        L.evaluate("document.querySelector('[data-a=lsrefresh]').click()"); L.wait_for_timeout(500)
        # leader removes soldier (two taps)
        mid = list(DB['members'].values())[0]['id']
        L.evaluate(f"document.querySelector('[data-a=lsrm][data-v=\"{mid}\"]').click()"); L.wait_for_timeout(200)
        L.evaluate(f"document.querySelector('[data-a=lsrm][data-v=\"{mid}\"]').click()"); L.wait_for_timeout(600)
        check('remove deletes on server', len(DB['members']) == 0)
        check('fix remove suggests resetting the code', 'reset the join code' in L.locator('#sqBody').inner_text().lower())
        P.evaluate("S.tab='unit';render();sqMode='me';sqShow()"); P.evaluate("document.querySelector('[data-a=lssend]').click()"); P.wait_for_timeout(600)
        check('removed soldier is told', 'no longer in' in P.locator('#sqBody').inner_text() and P.evaluate("lsGet().mem") is None)
        P.fill('#lsCode', code_txt); P.evaluate("document.querySelector('[data-a=lsjoin]').click()"); P.wait_for_timeout(600)
        check('removed soldier cannot rejoin', "didn't work" in P.locator('#sqBody').inner_text())
        # second soldier joins then leaves
        tctx, T = phone('soldier2')
        T.evaluate("S.squad.name='PFC Lee';S.tab='unit';render();sqMode='me';sqShow()"); T.fill('#lsCode', code_txt); T.evaluate("document.querySelector('[data-a=lsjoin]').click()"); T.wait_for_timeout(700); T.evaluate("document.querySelector('[data-a=lsshare]').click()"); T.wait_for_timeout(500)
        check('second soldier joined', len(DB['members']) == 1)
        T.evaluate("document.querySelector('[data-a=lsleave]').click()"); T.wait_for_timeout(150); T.evaluate("document.querySelector('[data-a=lsleave]').click()"); T.wait_for_timeout(600)
        check('leave deletes data', len(DB['members']) == 0 and 'deleted from the server' in T.locator('#sqBody').inner_text())
        # leader key moves to a new phone
        key = L.evaluate("lsGet().lk"); nctx, N = phone('newphone')
        N.evaluate("S.tab='unit';render();sqMode='sq';sqShow()"); N.evaluate("document.querySelector('#sqBody details.cmx').open=true"); N.fill('#lsKeyIn', key)
        N.evaluate("document.querySelector('[data-a=lsadopt]').click()"); N.wait_for_timeout(700)
        check('leader key works on a new phone', '2nd Squad' in N.locator('#sqBody').inner_text())
        # server down: graceful
        DB['down'] = True
        N.evaluate("document.querySelector('[data-a=lsrefresh]').click()"); N.wait_for_timeout(600)
        check('server down handled', "Couldn't reach" in N.locator('#sqBody').inner_text())
        DB['down'] = False
        # reset code, delete squad
        L.evaluate("document.querySelector('#sqBody .lsbox details').open=true;document.querySelector('[data-a=lsreset]').click()"); L.wait_for_timeout(150)
        L.evaluate("document.querySelector('[data-a=lsreset]').click()"); L.wait_for_timeout(600)
        check('reset gives a new code', L.locator('.lscode').inner_text() != code_txt)
        L.evaluate("document.querySelector('#sqBody .lsbox details').open=true;document.querySelector('[data-a=lsdel]').click()"); L.wait_for_timeout(150)
        L.evaluate("document.querySelector('[data-a=lsdel]').click()"); L.wait_for_timeout(600)
        check('delete squad clears server', len(DB['squads']) == 0 and L.evaluate("lsGet().lead") is None)
        check('only apikey header sent', DB['bad_headers'] == 0)
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
