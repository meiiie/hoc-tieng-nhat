const test=require('node:test'),assert=require('node:assert/strict'),J=require('../ja-phone.js'),voc=require('../vendor/ja-phone-vocab.json');
const ph=k=>J.morae(k).map(m=>m.ph.join(''));
test('kana to OpenJTalk morae: sokuon, n, long vowels, yoon, particles',()=>{
 assert.deepEqual(ph('がっこう'),['ga','cl','ko','o']);assert.deepEqual(ph('せんせい'),['se','N','se','e']);
 assert.deepEqual(ph('きょう'),['kyo','o']);assert.deepEqual(ph('コーヒー'),['ko','o','hi','i']);assert.deepEqual(ph('ほんとう'),['ho','N','to','o']);
 assert.deepEqual(ph('ちょっと'),['cho','cl','to']);assert.deepEqual(ph('ふね'),['fu','ne'])});
test('devoiced vowels are accepted variants',()=>{const m=J.morae('です');assert.deepEqual(m[1].alt,[['s','U']]);assert.ok(J.morae('あした')[1].alt.some(a=>a.join('')==='shI'))});
/* synthetic CTC posteriors: blank-separated one-hot frames for a phoneme string */
function logits(seq){const V=Object.keys(voc).length,fr=[];const push=id=>{const r=new Float32Array(V).fill(-8);r[id]=4;fr.push(r)};push(0);push(0);for(const p of seq.split(' ')){push(voc[p]);push(voc[p]);push(0)}push(0);const T=fr.length,o=new Float32Array(T*V);fr.forEach((r,t)=>o.set(r,t*V));return {o,T,V}}
const sc=(said,kana)=>{const {o,T,V}=logits(said);return J.score(o,T,V,voc,kana)};
test('the right word scores high, a different word low',()=>{assert.ok(sc('g a cl k o o','がっこう').score>=95);assert.ok(sc('s e N s e e','がっこう').score<30)});
test('dropping っ, ん or a long vowel is flagged on that mora',()=>{
 const a=sc('g a k o o','がっこう');assert.ok(a.score<75);assert.notEqual(a.morae[1].st,'ok');
 const b=sc('k a j i','かんじ');assert.ok(b.score<75);assert.notEqual(b.morae[1].st,'ok');
 const c=sc('o b a s a N','おばあさん');assert.ok(c.score<80);assert.ok(c.morae.some(m=>m.st!=='ok'))});
test('devoiced です scores like voiced',()=>{assert.ok(sc('d e s U','です').score>=95);assert.ok(sc('d e s u','です').score>=95)});
