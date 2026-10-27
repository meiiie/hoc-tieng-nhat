'use strict';
const JaEngine=(()=>{let worker=null,id=0;const pending=new Map();
 const stop=()=>{worker?.terminate();worker=null;for(const p of pending.values()){clearTimeout(p.timer);p.reject(new Error('Đã dừng phân tích'))}pending.clear()};
 function run(pcm,sr,kana,accent){if(!worker){worker=new Worker('ja-pitch-worker.js');worker.onerror=stop;worker.onmessage=({data})=>{const p=pending.get(data.id);if(!p)return;clearTimeout(p.timer);pending.delete(data.id);data.error?p.reject(new Error(data.error)):p.resolve(data.result)}}
  return new Promise((resolve,reject)=>{const k=++id,timer=setTimeout(stop,20000);pending.set(k,{resolve,reject,timer});worker.postMessage({id:k,pcm,sr,kana,accent},[pcm.buffer])})}
 return {run,stop};})();
