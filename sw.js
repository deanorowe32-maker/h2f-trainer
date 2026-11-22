/* H2F Trainer offline cache, version e1ec7r1c9 */
const V='h2f-e1ec7r1c25',SHELL=["/", "/index.html", "/manifest.webmanifest", "/icons/icon-192.png", "/icons/apple-touch-icon.png", "/fonts/manrope-latin.woff2", "/fonts/chakra-petch-600.woff2", "/ph/body-m-front.webp?v=4", "/ph/body-m-back.webp?v=4", "/ph/body-f-front.webp?v=4", "/ph/body-f-back.webp?v=4"];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  const u=new URL(r.url);
  /* Tour video: straight to the network so phones can stream it in ranges */
  if(u.origin===location.origin&&u.pathname.startsWith('/video/'))return;
  /* The page itself: fresh when online, saved copy when not */
  /* Weak signal: wait at most 3 s for the network, then open the saved copy; the fresh page still saves for next time */
  if(r.mode==='navigate'){const net=fetch(r).then(res=>{if(res.ok){const c=res.clone();caches.open(V).then(x=>x.put('/index.html',c))}return res});
    e.waitUntil(net.catch(()=>{}));
    e.respondWith(caches.match('/index.html').then(hit=>hit?Promise.race([net.catch(()=>hit),new Promise(ok=>setTimeout(()=>ok(hit),3000))]):net));return}
  /* Photos, icons, fonts: saved copy first, fetched once */
  const keep=u.origin===location.origin||(/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)||u.hostname==='cdn.jsdelivr.net');
  if(!keep)return;
  e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{if(res.ok||res.type==='opaque'){const c=res.clone();caches.open(V).then(x=>x.put(r,c))}return res})));
});
/* Reminder notifications sent by the push server function */
self.addEventListener('push',e=>{let m={};try{m=e.data?e.data.json():{}}catch(_){m={body:e.data&&e.data.text()}}
  e.waitUntil(self.registration.showNotification(m.title||'H2F Trainer',{body:m.body||'',icon:'/icons/icon-192.png',badge:'/icons/favicon-32.png',tag:'h2f-'+(m.url||'r'),data:{url:m.url||'/'}}))});
self.addEventListener('notificationclick',e=>{e.notification.close();const url=(e.notification.data&&e.notification.data.url)||'/';
  e.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(cs=>{for(const c of cs){if('focus' in c){c.navigate(url).catch(()=>{});return c.focus()}}return self.clients.openWindow(url)}))});
