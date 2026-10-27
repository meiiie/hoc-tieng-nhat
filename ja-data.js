/* Startup catalogue and on-demand content. No progress is stored or migrated here. */
(function(){'use strict';
const LEVELS=[5,4,3,2,1],CACHE='htn-content-v1';
let index,words=[],byId=new Map(),kanji=null;
const loaded=new Set(),pending=new Map();
const aliases=w=>({w:w.kanji,vi:w.v,lv:'N'+w.level,cefr:['N'+w.level],page:'n'+w.level,tags:[],ex:w.example?.text||'',exvi:w.example?.translation?.text||''});
async function init(){
 const r=await fetch('data/index.json');if(!r.ok)throw Error('index');index=await r.json();
 words=LEVELS.flatMap(level=>{const entry=index.levels[level],missing=new Set(entry.withoutAudio),cefr=['N'+level];
  return entry.ids.map(id=>({id,level,lv:cefr[0],cefr,page:'n'+level,tags:[],audio:missing.has(id)?null:`audio/n${level}/w/${id}.mp3`}))});
 byId=new Map(words.map(w=>[w.id,w]));return words;
}
async function content(file,required=false){
 const url=new URL(file+'?v='+index.files[file].revision,document.baseURI).href;
 let cache;try{cache=await caches.open(CACHE)}catch(e){if(required)throw e}
 const saved=await cache?.match(url);if(saved)return saved;
 try{const r=await fetch(url);if(!r.ok)throw Error(file);
  // Also covers a learner opening a level before the first SW takes control.
  try{await cache?.put(url,r.clone())}catch(e){if(required)throw e}
  return r;
 }catch(e){const previous=await cache?.match(new URL(file,document.baseURI).href,{ignoreSearch:true});if(previous)return previous;throw e}
}
function once(key,job){if(!pending.has(key))pending.set(key,job().finally(()=>pending.delete(key)));return pending.get(key)}
function loadLevel(n){
 if(loaded.has(n))return null;
 return once(n,async()=>{const rows=await (await content(`data/n${n}.json`)).json();
  const ids=index.levels[n].ids;
  if(rows.length!==ids.length||rows.some((w,i)=>w.id!==ids[i]||w.level!==n))throw Error('level index mismatch');
  // Hydrate in place so core queues and wordIndex keep the same references/order.
  for(const w of rows)Object.assign(byId.get(w.id),w,aliases(w));loaded.add(n);
 });
}
function loadKanji(){if(kanji)return null;return once('kanji',async()=>{kanji=await (await content('data/kanji.json')).json()})}
async function downloadAll(progress){let saved=0;const files=Object.keys(index.files);for(const file of files){await content(file,true);progress(++saved,files.length)}return files.length}
window.JaData={init,loadLevel,loadKanji,downloadAll,isLoaded:n=>loaded.has(n),get kanji(){return kanji||{}},get bytes(){return Object.values(index?.files||{}).reduce((n,f)=>n+f.bytes,0)}};
})();
