const C="oja-v7-2",F=["./","index.html","manifest.json","icon.svg"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(F)).catch(()=>{}));self.skipWaiting()});
self.addEventListener("activate",e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener("fetch",e=>{const q=e.request;if(q.method!=="GET"||new URL(q.url).origin!==location.origin)return;
  const nav=q.mode==="navigate";
  e.respondWith(fetch(q.url,{cache:"no-store",credentials:"same-origin"}).then(r=>{if(r.ok){const cp=r.clone();caches.open(C).then(c=>c.put(q,cp))}return r})
    .catch(()=>caches.match(q).then(m=>m||(nav?caches.match("index.html"):Response.error()))))});
