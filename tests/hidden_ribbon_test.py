"""Hidden ribbons: Open Door (email the developer) and Pass It On (share the app). Server on :8765."""
import sys
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, permissions=['clipboard-read', 'clipboard-write']); pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(600)
    pg.evaluate("localStorage.clear();localStorage.setItem('h2f.access',CODE_HASH);localStorage.setItem('h2f.tour','1')"); pg.reload(); pg.wait_for_timeout(900)
    E = pg.evaluate
    try:
        shown = E("RB_SHOW.length")
        check('hidden until earned', not E("RB_SHOW.some(r=>r.id==='pio')") and E("RB.some(r=>r.id==='pio'&&r.area==='Hidden')"))
        E("S.tab='unit';render()"); pg.wait_for_timeout(150)
        check('medal case total unchanged', pg.locator('#rbcase .rbhead b').inner_text() == f'{shown} ribbons to earn')
        E("document.querySelector('[data-a=shareapp]').click()"); pg.wait_for_timeout(300)
        E("document.querySelector('[data-a=sharecopy]').click()"); pg.wait_for_timeout(1500)
        check('copying the link earns it', E("!!S.rb.aw.pio"))
        check('earned once', E("rbCount('pio').n") == 1)
        E("document.getElementById('hsSheet').hidden=true;document.getElementById('rbSheet')&&(document.getElementById('rbSheet').hidden=true);render()"); pg.wait_for_timeout(200)
        check('count includes earned hidden ribbon', f'of {shown + 1} earned' in pg.locator('#rbcase .rbhead').inner_text())
        check('text and email links count too', E("(()=>{document.querySelector('[data-a=shareapp]').click();return [...document.querySelectorAll('#hsBody a[href^=sms],#hsBody a[href^=mailto]')].every(a=>a.hasAttribute('data-pio'))})()"))
        check('kept in backup', E("cleanBackup(makeBackup()).rb.tally.pio") == 1)
        check('both hidden still count', E("(()=>{S.rb.tally.egg=1;rbCheck();return RB.filter(r=>r.area==='Hidden'&&S.rb.aw[r.id]).length})()") == 2)
        # Pass It On: the phone's Share sheet (even when it doesn't report back) and showing the QR code both count
        E("S.rb.tally.pio=0;delete S.rb.aw.pio;document.querySelectorAll('.sheet').forEach(x=>x.hidden=true)")
        E("navigator.share=()=>new Promise(()=>{});document.querySelector('[data-a=shareapp]').click()"); pg.wait_for_timeout(300)
        E("pioNative()"); pg.wait_for_timeout(1300)
        check('tapping Share earns it even if the share sheet never reports back', E("!!S.rb.aw.pio"))
        E("S.rb.tally.pio=0;delete S.rb.aw.pio;document.querySelectorAll('.sheet').forEach(x=>x.hidden=true)")
        pg.clock.install(); E("window.qrcode=()=>({addData(){},make(){},getModuleCount:()=>21,isDark:()=>false});document.querySelector('[data-a=shareapp]').click()"); pg.clock.run_for(3000)
        check('QR code on screen for 3 s is not enough', not E("S.rb.tally.pio"))
        pg.clock.run_for(4000); pg.wait_for_timeout(100)
        check('QR code on screen for 6 s earns it (someone scanned it)', E("S.rb.tally.pio") == 1)
        E("document.querySelectorAll('.sheet').forEach(x=>x.hidden=true)")
        # Seven Taps
        E("document.getElementById('rbSheet')&&(document.getElementById('rbSheet').hidden=true);document.getElementById('hsSheet').hidden=true")
        logo = "document.querySelector('header.top .logo, header.top .appicon')"
        for i in range(6): E(f"{logo}.dispatchEvent(new MouseEvent('click',{{bubbles:true}}))")
        check('six taps is not enough', not E("!!S.rb.aw.st7"))
        E(f"{logo}.dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); pg.wait_for_timeout(1300)
        check('seven taps earns Seven Taps', E("!!S.rb.aw.st7"))
        check('slow taps reset the count', E("(()=>{stTaps=[];const t=Date.now();stTap(t);stTap(t+5000);return stTaps.length})()") == 1)
        # Creator's Word
        E("S.tab='creator';render();window.scrollTo(0,0)"); pg.wait_for_timeout(300)
        check('opening the page is not enough', not E("!!S.rb.aw.crw"))
        E("window.scrollTo(0,document.body.scrollHeight)"); pg.wait_for_timeout(1300)
        check('reading to the end earns Creator\'s Word', E("!!S.rb.aw.crw"))
        # Early Bird
        check('workout at 0545 counts', E("(()=>{const d=new Date();d.setHours(5,45,0,0);S.hist=[{id:'h1',ts:d.getTime(),n:5}];return rbCount('ebd').n})()") == 1)
        check('workout at 0645 does not', E("(()=>{const d=new Date();d.setHours(6,45,0,0);S.hist=[{id:'h1',ts:d.getTime(),n:5}];return rbCount('ebd').n})()") == 0)
        check('all-nighter at 0130 does not', E("(()=>{const d=new Date();d.setHours(1,30,0,0);S.hist=[{id:'h1',ts:d.getTime(),n:5}];return rbCount('ebd').n})()") == 0)
        check('nine hidden ribbons (with Creator codes), none listed', E("RB.filter(r=>r.area==='Hidden').length") == 9 and E("RB_SHOW.length") == shown)
        check('new tallies kept in backup', E("(()=>{const t=cleanBackup(makeBackup()).rb.tally;return [t.st7,t.crw]})()") == [1, 1])
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    check('no page errors', not errs)
    if errs: print(errs[:3])
    b.close()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
