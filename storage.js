/* Japanese storage adapter: transactional IndexedDB, local mirror, quarantine and additive migration snapshots. */
(function(root){'use strict';
const KEY='htn-core',DB='hoc-tieng-nhat';let db=null,fallback=false,backupDay='',chain=Promise.resolve();
const valid=x=>!!x&&typeof x==='object'&&!Array.isArray(x)&&(!x.srs||typeof x.srs==='object'&&!Array.isArray(x.srs));
const get=k=>{try{return localStorage.getItem(k)}catch{return null}};
const put=(k,v)=>{try{localStorage.setItem(k,v);return true}catch{return false}};
function parse(raw){try{const v=typeof raw==='string'?JSON.parse(raw):raw;return valid(v)?v:null}catch{return null}}
function tx(action){return new Promise((resolve,reject)=>{const t=db.transaction('progress','readwrite');t.oncomplete=resolve;t.onerror=t.onabort=()=>reject(t.error||new Error('Không lưu được'));try{action(t.objectStore('progress'))}catch(e){t.abort();reject(e)}})}
function read(k){return new Promise((resolve,reject)=>{const q=db.transaction('progress').objectStore('progress').get(k);q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)})}
function mirror(state){const raw=JSON.stringify(state),day=new Date().toLocaleDateString('sv');if(backupDay!==day){const previous=get(KEY);if(parse(previous))put(KEY+'-bak',previous);else put(KEY+'-bak',raw);backupDay=day}return put(KEY,raw)}
const api={
 async load(legacy){let local=parse(get(KEY));const raw=get(KEY);if(raw&&!local){put(KEY+'-corrupt-'+Date.now(),raw);local=parse(get(KEY+'-bak'));}
  let seed=local||legacy;
  try{db=await new Promise((resolve,reject)=>{const q=indexedDB.open(DB,1);q.onupgradeneeded=()=>{if(!q.result.objectStoreNames.contains('progress'))q.result.createObjectStore('progress')};q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error);q.onblocked=()=>reject(new Error('Bộ nhớ đang bận'))});db.onversionchange=()=>db.close();
   const current=await read('current');let stored=parse(current);
   if(current&&!stored){await tx(s=>s.put(current,'corrupt-'+Date.now()));stored=parse(await read('daily-backup'));}
   if(stored&&(!seed?.saved||!(seed.saved>stored.saved)))seed=stored;
   if(!valid(seed))seed={};if(+seed.v<11&&Object.keys(seed).length)await tx(s=>s.put(seed,'pre-v'+(seed.v||2)));
   await tx(s=>s.put(seed,'current'));mirror(seed);return seed;
  }catch(e){fallback=true;return seed}
 },
 save(state){const snapshot=structuredClone(state);chain=chain.catch(()=>{}).then(async()=>{if(!valid(snapshot))throw new Error('Tiến độ không hợp lệ');if(fallback){if(!mirror(snapshot))throw new Error('Bộ nhớ đầy');return}
   if(!db)throw new Error('Bộ nhớ chưa sẵn sàng');const day=new Date().toLocaleDateString('sv');const needs=backupDay!==day;
   await tx(s=>{s.put(snapshot,'current');if(needs)s.put(snapshot,'daily-backup')});mirror(snapshot);
  });return chain},
 async backup(state){const k='before-import-'+Date.now();if(!put(KEY+'-'+k,JSON.stringify(state))&&fallback)throw new Error('Không sao lưu được');if(db)await tx(s=>s.put(state,k));},
 get mode(){return fallback?'localStorage':'IndexedDB'},key:KEY,database:DB,valid
};root.ProgressStore=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(globalThis);
