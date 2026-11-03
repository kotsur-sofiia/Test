const CACHE='luna-diary-v98';
const ASSETS=['./','./index.html','./style.css','./mobile.css','./capture.css','./profile.css','./aesthetic.css','./garden.css','./linen.css','./clear-glass.css','./phone-layout.css','./minimal.css','./day-map.css?v=45','./diary.css?v=45','./nature-editorial.css?v=64','./liquid-glass.css?v=47','./milk-sand.css?v=96','./typography.css?v=97','./assets/fonts/NotoSerif-Regular.woff','./assets/fonts/NotoSerifDisplay-Regular.woff','./assets/fonts/Inter-Regular.woff','./assets/fonts/Inter-SemiBold.woff','./assets/clay-grain.svg','./assets/glass-sand-grain.svg','./assets/recommendation-shore.webp','./assets/recommendation-food.webp','./assets/recommendation-rest.webp','./assets/sand-waterfall.webp','./assets/shoreline-water.webp','./assets/pearl-topics.webp','./assets/pearl-diary.webp','./assets/wild-pearl-diary.webp','./assets/cycle-twig.webp','./assets/cycle-olive.webp','./assets/cycle-pearl.webp','./assets/cycle-pearl-warm.webp','./assets/sand-matched-cycle-pearl.webp','./assets/beach-sand.webp','./assets/beach-sand-horizontal.webp','./assets/beach-sand-natural.webp','./assets/beach-water.webp','./assets/sand-cycle-ring.webp','./assets/pearl-rolled-ring.webp','./assets/pearl-trail-natural.webp','./assets/reference-sand-ring.webp','./assets/natural-sand-trail.webp','./assets/shore-canvas.svg?v=95','./assets/shore-phone.webp','./assets/shore-desktop.webp','./assets/shore-foam-phone.svg','./assets/shore-foam-desktop.svg','./woman-config.js?v=45','./cycle-model.js?v=84','./cycle-care.js?v=71','./day-map.js?v=66','./topic-reorder.js?v=45','./period-dates.js?v=45','./period-editor.js?v=45','./assets/nature-topics.webp','./assets/dew-monstera.webp','./assets/linen-olive.webp','./assets/olive-leaves.webp','./assets/olive-leaves.webp?background=23','./assets/fonts/CormorantGaramond-Italic.woff','./daily-affirmation.js?v=45','./assets/garden-spa.webp','./assets/fonts/Nunito.woff','./assets/fonts/Comfortaa.ttf','./assets/fonts/Caveat.woff','./assets/mineral-landscape.svg','./assets/fonts/Manrope.woff','./assets/fonts/CormorantGaramond.woff','./profile-model.js','./profile.js?v=45','./capture-parser.js','./capture.js?v=45','./app.js?v=45','./voice.js?v=45','./navigation.js?v=98','./profile-parser.js','./norms.js','./manifest.webmanifest','./icon.svg','./icon-192.png','./icon-512.png'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS.map(path=>new Request(new URL(path,self.location.href),{cache:'reload'})))).then(()=>self.skipWaiting()));});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>(key.startsWith('little-steps-')||key.startsWith('luna-diary-'))&&key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim()));});
// Refresh the document online; keep a complete local fallback for offline navigation.
self.addEventListener('fetch',event=>{
 if(event.request.method!=='GET'||new URL(event.request.url).origin!==self.location.origin)return;
 // Regional fonts join the offline cache after their first use, without
 // downloading every writing system during a Russian installation.
 if(event.request.destination==='font'){
  event.respondWith(caches.open(CACHE).then(async cache=>{
   const cached=await cache.match(event.request);if(cached)return cached;
   const response=await fetch(event.request);
   if(response.ok)await cache.put(event.request,response.clone()).catch(()=>{});
   return response;
  }));return;
 }
 if(event.request.mode==='navigate'){
  const response=fetch(event.request,{cache:'no-store'}).then(result=>({page:result,copy:result.clone()}));
  event.waitUntil(response.then(async result=>{if(result.copy.ok){const cache=await caches.open(CACHE);await cache.put(new URL('./index.html',self.location.href),result.copy);}}).catch(()=>{}));
  event.respondWith(response.then(result=>result.page).catch(async()=>await caches.match('./index.html')||await caches.match('./')));return;
 }
 event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request)));
});
