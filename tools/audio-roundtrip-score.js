/* TTS -> recogniser round trip, step 2: score every MP3 against its own kana with the same scorer the app uses.
   Usage: node tools/audio-roundtrip-score.js [logit_dir]  -> data/sources/audio-roundtrip.json */
const fs=require('fs'),path=require('path'),J=require('../ja-phone.js'),voc=require('../vendor/ja-phone-vocab.json');
const ROOT=path.join(__dirname,'..'),DIR=process.argv[2]||path.join(ROOT,'..','qabin');
const rows=[];for(const lv of ['n5','n4','n3','n2','n1'])for(const w of JSON.parse(fs.readFileSync(path.join(ROOT,`data/${lv}.json`)))){
 const f=path.join(DIR,w.id+'.f32');if(!fs.existsSync(f+'.shape')){rows.push({id:w.id,level:lv,kana:w.kana,missing:true});continue}
 const [T,V]=fs.readFileSync(f+'.shape','utf8').split(' ').map(Number),b=fs.readFileSync(f),r=J.score(new Float32Array(b.buffer,b.byteOffset,T*V),T,V,voc,w.kana);
 rows.push({id:w.id,level:lv,kana:w.kana,score:r.score,heard:r.heard,expected:r.expected,bad:r.morae.filter(m=>m.st!=='ok').map(m=>m.kana+':'+m.st)})}
const done=rows.filter(r=>!r.missing),band=(a,b)=>done.filter(r=>r.score>=a&&r.score<b).length,per={};
for(const r of done){const p=per[r.level]=per[r.level]||{n:0,ge85:0,lt60:0};p.n++;if(r.score>=85)p.ge85++;if(r.score<60)p.lt60++}
const flagged=done.filter(r=>r.score<60).sort((a,b)=>a.score-b.score);
const out={method:'Each Nanami MP3 is decoded to 16 kHz, passed through japanese-hubert-base-phoneme-ctc-v4 (ONNX q4) and scored against the word\'s own kana with ja-phone.js. Low scores mean the recording, the kana, or the recogniser disagree; they need a listen, not an automatic fix.',
 model:'air-air/japanese-hubert-base-phoneme-ctc-v4-ONNX@a36617c5fbf7cfde02caa067716961c03cf4d87e',total:rows.length,scored:done.length,missing:rows.length-done.length,
 bands:{'85-100':band(85,101),'60-84':band(60,85),'0-59':band(0,60)},perLevel:per,flagged};
fs.writeFileSync(path.join(ROOT,'data/sources/audio-roundtrip.json'),JSON.stringify(out,null,1)+'\n');console.log(JSON.stringify({...out,flagged:flagged.length}))
