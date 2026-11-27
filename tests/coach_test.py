import re
"""H2F Coach: off by default and sends nothing; consent copy and 'what gets sent' preview; turning on; suggestion
and typed questions go to the coach function with device id, context and chat; reply shows; errors restore the
question; caps; clear and turn off; reply text is escaped. The function is stubbed."""
import sys, json
from playwright.sync_api import sync_playwright
fails=[]
def check(n,ok):
    print(('PASS ' if ok else 'FAIL ')+n)
    if not ok: fails.append(n)
calls=[];mode={'v':'ok'}
def handle(r):
    if r.request.method=='OPTIONS':return r.fulfill(status=204,headers={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'*'})
    b=json.loads(r.request.post_data);calls.append(b)
    H={'Access-Control-Allow-Origin':'*','Content-Type':'application/json'}
    if mode['v']=='nokey':return r.fulfill(status=503,headers=H,body='{"error":"no key"}')
    if mode['v']=='cap':return r.fulfill(status=429,headers=H,body='{"error":"cap","left":0}')
    if mode['v']=='down':return r.abort()
    r.fulfill(status=200,headers=H,body=json.dumps({'text':'Keep going. **Sleep** 7 h.\n- Step one <img src=x onerror=alert(1)>','left':19}))
with sync_playwright() as p:
    br=p.chromium.launch();ctx=br.new_context(viewport={'width':390,'height':844});pg=ctx.new_page();E=pg.evaluate
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]));dialogs=[];pg.on('dialog',lambda d:(dialogs.append(1),d.dismiss()))
    pg.route('**/functions/v1/coach',handle)
    pg.goto('http://localhost:8765/');pg.wait_for_timeout(400)
    E("localStorage.clear();sessionStorage.setItem('h2f.boot','1');localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')");pg.reload();pg.wait_for_timeout(900)
    pg.add_style_tag(content='#rbSheet{display:none!important}')
    E("S.rk={seen:0};document.querySelectorAll('.sheet').forEach(x=>x.hidden=true);S.tab='today';render()");pg.wait_for_timeout(500)
    check('Coach is a Today section',E("!!document.querySelector('.subnav [data-v=coach]')"))
    pg.click('.subnav [data-v=coach]');pg.wait_for_timeout(500)
    v=E("document.getElementById('view').textContent")
    check('off by default with consent copy',E("!document.getElementById('cxIn')") and 'Cloudflare' in v and 'not medical advice' in v and 'Nothing is sent until you turn Coach on' in v)
    check('what gets sent preview shows the summary',E("document.querySelector('.cxsent pre').textContent.includes('Today:')"))
    check('nothing sent while off',len(calls)==0)
    # seed some data for the context
    E("S.nut.age='28';S.nut.sex='m';S.nut.wt='180';S.nut.ht='70';S.nut.hu='in';S.sleep.log[slKey(1)]=6.5;S.sleep.log[slKey(2)]=7;S.hist=[{id:'h1',ts:Date.now()-864e5,day:'Mon',type:'Ruck · 4.1 mi · 35 lb',ms:3600000,d:1,n:1}];render()")
    pg.click('[data-a=cxon]');pg.wait_for_timeout(300)
    check('turned on shows input and suggestions',E("!!document.getElementById('cxIn')") and E("document.querySelectorAll('[data-a=cxsug]').length")==4)
    pg.click('[data-a=cxsug][data-v="1"]');pg.wait_for_timeout(800)
    c=calls[-1] if calls else {}
    check('suggestion sent with device id, context and chat',len(calls)==1 and len(c.get('dev',''))==16 and c['msgs']==[{'r':'u','t':'Am I on track for my AFT?'}])
    check('context has the logs',all(x in c.get('ctx','') for x in ['age 28','6.8 h average','Ruck · 4.1 mi','AFT: no score saved yet']))
    check('context has no name or location',not re.search(r'-?\d{1,3}\.\d{4,}|latitude|longitude|\blng\b|email|@',c.get('ctx','').lower()))
    check('reply shows',E("document.querySelectorAll('.cxm.ai').length")==1 and 'Sleep' in E("document.querySelector('.cxm.ai').textContent"))
    check('reply is escaped, bold works',E("!document.querySelector('.cxm.ai img')") and E("document.querySelector('.cxm.ai b').textContent")=='Sleep' and not dialogs)
    check('questions left shown','19 questions left today' in E("document.getElementById('cxLeft').textContent"))
    pg.fill('#cxIn','What about my run?');pg.keyboard.press('Enter');pg.wait_for_timeout(800)
    check('Enter sends, with chat history',len(calls)==2 and [m['r'] for m in calls[-1]['msgs']]==['u','a','u'])
    check('chat saved on the phone',E("JSON.parse(localStorage.getItem('h2f.coach')).msgs.length")==4)
    check('chat not in backup',"h2f.coach" not in E("makeBackup()") and 'What about my run' not in E("makeBackup()"))
    mode['v']='down';pg.fill('#cxIn','Offline q');pg.click('[data-a=cxsend]');pg.wait_for_timeout(800)
    check('no signal: message and question restored',E("document.getElementById('cxErr').textContent").startswith('No signal') and E("document.getElementById('cxIn').value")=='Offline q' and E("document.querySelectorAll('.cxm.me').length")==2)
    mode['v']='nokey';pg.click('[data-a=cxsend]');pg.wait_for_timeout(800)
    check('no key: honest message','not switched on' in E("document.getElementById('cxErr').textContent"))
    mode['v']='cap';pg.click('[data-a=cxsend]');pg.wait_for_timeout(800)
    check('cap message',"20 questions" in E("document.getElementById('cxErr').textContent") and '0 questions left' in E("document.getElementById('cxLeft').textContent"))
    pg.click('[data-a=cxclear]');pg.wait_for_timeout(200)
    check('clear chat',E("JSON.parse(localStorage.getItem('h2f.coach')).msgs.length")==0 and E("document.querySelectorAll('[data-a=cxsug]').length")==4)
    pg.click('[data-a=cxoff]');pg.wait_for_timeout(200)
    check('turn off',E("!document.getElementById('cxIn')") and E("!!document.querySelector('[data-a=cxon]')"))
    pg.goto('http://localhost:8765/#coach');pg.wait_for_timeout(900)
    check('#coach link opens Coach',E("S.tab")=='coach')
    check('no page errors',not errs)
    if errs:print(errs)
    br.close()
print('ALL PASS' if not fails else f'{len(fails)} FAIL');sys.exit(1 if fails else 0)
