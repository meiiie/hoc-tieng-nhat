const V='htn-v1.3.0',DATA='htn-data-v1',AUDIO='htn-audio-v1';
const SHELL=['./','index.html','core/style.css','lang-ja.css','core/app-core.js','core/mascot.js','core/speech.js','core/mic-worklet.js','core/mic-meter.js','lang-ja.js','ja-examples.js','ja-kana.js','ja-pitch.js','ja-pitch-worker.js','ja-engine.js','ja-writing.js','srs.js','storage.js','learning-plan.js','content.js','vendor/ts-fsrs.min.js','manifest.webmanifest','version.json','data/meta.json','data/kana.json','data/kanji.json',...[5,4,3,2,1].map(n=>`data/n${n}.json`),'data/NOTICE.md','data/SOURCES.md','icons/icon.svg','icons/icon-192.png','icons/icon-512.png','icons/maskable-192.png','icons/maskable-512.png','icons/apple-touch-icon.png'];
const URLS=new Set(SHELL.map(x=>new URL(x,self.registration.scope).href));
self.addEventListener('install',e=>e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL.map(u=>new Request(u,{cache:'reload'}))))));
self.addEventListener('message',e=>{if(e.data==='skip'||e.data?.type==='skip')self.skipWaiting()});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>/^htn-(?:v|data-v|audio-v)/.test(k)&&![V,DATA,AUDIO].includes(k)).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
const timeout=(p,ms)=>new Promise((ok,no)=>{const timer=setTimeout(()=>no(Error('timeout')),ms);p.then(x=>{clearTimeout(timer);ok(x)},e=>{clearTimeout(timer);no(e)})});
self.addEventListener('fetch',e=>{const r=e.request,u=new URL(r.url);if(r.method!=='GET'||u.origin!==location.origin)return;
 if(URLS.has(u.href)){e.respondWith(caches.open(V).then(async c=>(await c.match(r))||fetch(r)));return}
 const lazy=u.pathname.includes('/audio/')?AUDIO:/\/(data\/strokes|models)\//.test(u.pathname)?DATA:null;
 if(lazy){e.respondWith(caches.open(lazy).then(async c=>{const saved=await c.match(r);if(saved)return saved;const res=await fetch(r);if(res.ok)e.waitUntil(c.put(r,res.clone()).catch(()=>{}));return res}));return}
 e.respondWith(timeout(fetch(r,{cache:'no-cache'}),4000).then(res=>{if(res.ok)e.waitUntil(caches.open(V).then(c=>c.put(r,res.clone())).catch(()=>{}));return res}).catch(()=>caches.match(r,{ignoreSearch:true}).then(saved=>saved||(r.mode==='navigate'?caches.match('./'):Response.error()))))});
