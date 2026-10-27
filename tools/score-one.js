/* stdin: {kana,T,V,logits:base64 float32} lines -> stdout score lines (used by audio_regen_flagged.py) */
const J=require('../ja-phone.js'),voc=require('../vendor/ja-phone-vocab.json'),rl=require('readline').createInterface({input:process.stdin});
rl.on('line',l=>{const m=JSON.parse(l),b=Buffer.from(m.logits,'base64'),r=J.score(new Float32Array(b.buffer,b.byteOffset,m.T*m.V),m.T,m.V,voc,m.kana);console.log(JSON.stringify({score:r.score,heard:r.heard}))});
