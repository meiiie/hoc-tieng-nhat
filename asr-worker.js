'use strict';
/* On-device Japanese phoneme recogniser in a worker: japanese-hubert-base-phoneme-ctc-v4 (prj-beatrice, Apache-2.0),
   ONNX 4-bit export by air-air (~63 MB), run with onnxruntime-web (WASM, 1 thread). The model and runtime stay in
   Cache Storage ("htn-engine-v1"), so scoring works offline after the first download. Audio never leaves the device.
   Same message protocol as the English core (status, load, forget, run), so core/speech.js is unchanged. */
importScripts('vendor/ort/ort.wasm.min.js','ja-kana.js','ja-pitch.js','ja-phone.js');
const MODEL='https://huggingface.co/air-air/japanese-hubert-base-phoneme-ctc-v4-ONNX/resolve/a36617c5fbf7cfde02caa067716961c03cf4d87e/onnx/model_q4.onnx';
const CACHE='htn-engine-v1',PAD=2400;let sess=null,loading=null,vocab=null;
ort.env.wasm.numThreads=1;ort.env.wasm.wasmPaths=new URL('vendor/ort/',self.location).href;
async function cached(url,onProg){const c=await caches.open(CACHE);let r=await c.match(url);if(r)return new Uint8Array(await r.arrayBuffer());
 r=await fetch(url,{mode:'cors'});if(!r.ok)throw new Error('http '+r.status);const total=+r.headers.get('content-length')||63e6,rd=r.body.getReader(),parts=[];let got=0,last=0;
 for(;;){const {done,value}=await rd.read();if(done)break;parts.push(value);got+=value.length;if(got-last>5e5){last=got;onProg&&onProg(got,total)}}
 const buf=new Uint8Array(got);let o=0;for(const p of parts){buf.set(p,o);o+=p.length}
 try{await c.put(url,new Response(buf,{headers:{'Content-Type':'application/octet-stream'}}))}catch(e){/* quota: still usable this session */}return buf}
async function load(){if(sess)return;if(loading)return loading;
 loading=(async()=>{vocab=await (await fetch('vendor/ja-phone-vocab.json')).json();
  const buf=await cached(MODEL,(g,t)=>postMessage({type:'progress',got:g,total:t}));postMessage({type:'progress',got:1,total:1,phase:'init'});
  sess=await ort.InferenceSession.create(buf,{executionProviders:['wasm'],graphOptimizationLevel:'all'})})();
 try{await loading}catch(e){loading=null;throw e}}
async function logits(pcm){const x=new Float32Array(pcm.length+2*PAD);x.set(pcm,PAD);
 const r=await sess.run({input_values:new ort.Tensor('float32',x,[1,x.length])}),lg=r.logits;return {data:lg.data,T:lg.dims[1],V:lg.dims[2],frameSec:x.length/16000/lg.dims[1]}}
onmessage=async e=>{const m=e.data;try{
 if(m.type=='status'){const c=await caches.open(CACHE);postMessage({type:'status',cached:!!(await c.match(MODEL)),ready:!!sess});return}
 if(m.type=='load'){await load();postMessage({type:'ready'});return}
 if(m.type=='forget'){sess=null;loading=null;await caches.delete(CACHE);postMessage({type:'status',cached:false,ready:false});return}
 if(m.type=='run'){await load();const t0=performance.now(),{kana,accent}=m.variants,L=await logits(m.pcm);
  const res=JaPhone.score(L.data,L.T,L.V,vocab,kana);res.frameSec=L.frameSec;res.pitch=JaPhone.pitch(m.pcm,res,L.frameSec,accent,JaPitch,PAD);res.ms=Math.round(performance.now()-t0);postMessage({type:'result',id:m.id,res})}
}catch(err){postMessage({type:'error',id:m.id,msg:String(err&&err.message||err)})}};
