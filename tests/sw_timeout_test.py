"""Weak signal: once installed, the app opens from its saved copy within about 3 s when the network stalls, and still opens normally on a good connection. Starts its own slow server on :8766."""
import sys, os, time, threading, http.server, functools
from playwright.sync_api import sync_playwright
fails = []
def check(n, ok):
    print(('PASS ' if ok else 'FAIL ') + n)
    if not ok: fails.append(n)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SLOW = {'on': False}
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if SLOW['on'] and self.path.split('?')[0] in ('/', '/index.html'): time.sleep(8)
        super().do_GET()
srv = http.server.ThreadingHTTPServer(('localhost', 8766), functools.partial(H, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as p:
    b = p.chromium.launch()
    try:
        ctx = b.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page()
        t0 = time.time(); pg.goto('http://localhost:8766/'); fast = time.time() - t0
        pg.evaluate("navigator.serviceWorker.ready"); pg.wait_for_timeout(1500)
        check('service worker installed', pg.evaluate("!!navigator.serviceWorker.controller") or (pg.reload(), pg.wait_for_timeout(800), pg.evaluate("!!navigator.serviceWorker.controller"))[2])
        check('good connection opens fast', fast < 3)
        SLOW['on'] = True
        pg.reload(wait_until='domcontentloaded'); slow = pg.evaluate("performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd") / 1000
        check(f'stalled network (8 s) still opens in {slow:.1f} s (under 4)', 2.5 < slow < 4)
        check('the app is there', pg.evaluate("typeof S==='object'&&!!document.getElementById('view')"))
    except Exception as e:
        check('ran: ' + str(e).splitlines()[0], False)
    b.close(); srv.shutdown()
print('RESULT ' + ('OK' if not fails else 'FAIL %d' % len(fails))); sys.exit(1 if fails else 0)
