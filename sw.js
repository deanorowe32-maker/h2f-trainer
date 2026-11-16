/* H2F Trainer offline cache, version 1a469d2835 */
const V='h2f-1a469d2835',SHELL=["/", "/index.html", "/manifest.webmanifest", "/icons/icon-192.png", "/icons/apple-touch-icon.png", "/ph/body-m-front.webp", "/ph/body-m-back.webp", "/ph/body-f-front.webp", "/ph/body-f-back.webp"];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  const u=new URL(r.url);
  /* The page itself: fresh when online, saved copy when not */
  if(r.mode==='navigate'){e.respondWith(fetch(r).then(res=>{const c=res.clone();caches.open(V).then(x=>x.put('/index.html',c));return res}).catch(()=>caches.match('/index.html')));return}
  /* Photos, icons, fonts: saved copy first, fetched once */
  const keep=u.origin===location.origin||(/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)||u.hostname==='cdn.jsdelivr.net');
  if(!keep)return;
  e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{if(res.ok||res.type==='opaque'){const c=res.clone();caches.open(V).then(x=>x.put(r,c))}return res})));
});
