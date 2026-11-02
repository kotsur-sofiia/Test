const CACHE='luna-diary-v43';
const ASSETS=['./','./index.html','./style.css','./mobile.css','./capture.css','./profile.css','./aesthetic.css','./garden.css','./linen.css','./clear-glass.css','./phone-layout.css','./minimal.css','./day-map.css?v=43','./diary.css?v=43','./nature-editorial.css?v=43','./liquid-glass.css?v=43','./assets/clay-grain.svg','./assets/sand-waterfall.webp','./woman-config.js?v=43','./cycle-model.js?v=43','./cycle-care.js?v=43','./day-map.js?v=43','./topic-reorder.js?v=43','./period-dates.js?v=43','./period-editor.js?v=43','./assets/nature-topics.webp','./assets/dew-monstera.webp','./assets/linen-olive.webp','./assets/olive-leaves.webp','./assets/olive-leaves.webp?background=23','./assets/fonts/CormorantGaramond-Italic.woff','./daily-affirmation.js?v=43','./assets/garden-spa.webp','./assets/fonts/Nunito.woff','./assets/fonts/Comfortaa.ttf','./assets/fonts/Caveat.woff','./assets/mineral-landscape.svg','./assets/fonts/Manrope.woff','./assets/fonts/CormorantGaramond.woff','./profile-model.js','./profile.js?v=43','./capture-parser.js','./capture.js?v=43','./app.js?v=43','./voice.js?v=43','./navigation.js?v=43','./profile-parser.js','./norms.js','./manifest.webmanifest','./icon.svg','./icon-192.png','./icon-512.png'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS.map(path=>new Request(new URL(path,self.location.href),{cache:'reload'})))).then(()=>self.skipWaiting()));});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>(key.startsWith('little-steps-')||key.startsWith('luna-diary-'))&&key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim()));});
// Refresh the document online; keep a complete local fallback for offline navigation.
self.addEventListener('fetch',event=>{
 if(event.request.method!=='GET'||new URL(event.request.url).origin!==self.location.origin)return;
 if(event.request.mode==='navigate'){
  const response=fetch(event.request,{cache:'no-store'}).then(result=>({page:result,copy:result.clone()}));
  event.waitUntil(response.then(async result=>{if(result.copy.ok){const cache=await caches.open(CACHE);await cache.put(new URL('./index.html',self.location.href),result.copy);}}).catch(()=>{}));
  event.respondWith(response.then(result=>result.page).catch(async()=>await caches.match('./index.html')||await caches.match('./')));return;
 }
 event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request)));
});
