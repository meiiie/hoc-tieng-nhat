'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const levels=[5,4,3,2,1],all=levels.flatMap(n=>JSON.parse(fs.readFileSync(`data/n${n}.json`))),kanji=JSON.parse(fs.readFileSync('data/kanji.json')),kana=JSON.parse(fs.readFileSync('data/kana.json'));const method='dịch từ JMdict (tiếng Anh), cần người bản ngữ kiểm tra';
test('all levels have substantial complete data',()=>{for(const n of levels){const ws=all.filter(w=>w.level===n);assert.ok(ws.length>600);for(const w of ws){for(const f of ['id','kanji','kana','romaji','pos','v'])assert.ok(typeof w[f]==='string'&&w[f].trim(),`${w.id} ${f}`);assert.ok(w.en.length&&w.jmdict,w.id);assert.equal(w.viMethod,method);assert.ok(Object.hasOwn(w,'pitch')&&Object.hasOwn(w,'example'))}}});
test('word ids are globally unique and readings are kana',()=>{assert.equal(new Set(all.map(w=>w.id)).size,all.length);for(const w of all)assert.match(w.kana,/^[ぁ-ゖァ-ヺー]+$/,w.id)});
test('Vietnamese has no empty text, obvious untranslated English or emoji',()=>{for(const w of all){assert.doesNotMatch(w.v,/\b(?:the|something|someone|especially|usually|being|having|person|thing|one\x27s|to be|and|with|from)\b/i,w.id);assert.doesNotMatch(JSON.stringify(w),/\p{Extended_Pictographic}/u,w.id);assert.notEqual(w.v,w.en[0],w.id)}});
test('all N5 kanji have real KanjiVG stroke files',()=>{for(const w of all.filter(w=>w.level===5))for(const c of w.kanji)if(/[一-龯]/.test(c)){assert.ok(kanji[c]?.strokes,`${c} in ${w.kanji}`);assert.ok(fs.existsSync(kanji[c].strokes))}});
test('Han Viet matches KANJIDIC2 Vietnam readings wherever supplied',()=>{const original=JSON.parse(fs.readFileSync('/workspace/japanese/src/kanjidic2-all-3.6.2.json')).characters;const map=new Map(original.map(x=>[x.literal,(x.readingMeaning?.groups||[]).flatMap(g=>g.readings.filter(r=>r.type==='vietnam').map(r=>r.value.toLowerCase()))]));for(const w of all)for(const c of w.kanji){const rs=map.get(c)||[];if(rs.length){assert.ok(kanji[c].hv.length);for(const r of rs)assert.ok(w.hv.includes(r),`${w.id} ${c} ${r}`)}}});
test('pitch indices are bounded by mora count; audio paths correspond to files',()=>{const K=require('../ja-kana');for(const w of all){if(w.pitch)for(const a of w.pitch)assert.ok(Number.isInteger(a)&&a>=0&&a<=K.morae(w.kana).length,`${w.kanji} ${w.kana} ${a}`);if(w.audio){assert.match(w.audio,new RegExp(`^audio/n${w.level}/w/${w.id}\\.mp3$`));assert.ok(fs.statSync(w.audio).size>256)}}});
test('kana inventory covers both scripts and each required group',()=>{for(const script of ['hiragana','katakana'])for(const group of ['gojuon','dakuten','yoon'])assert.ok(kana.filter(w=>w.script===script&&w.group===group).length>=25);for(const w of kana)assert.ok(w.romaji)});
test('source files contain a translation for every delivered word',()=>{const lines=fs.readFileSync('data/sources/vi-glosses.tsv','utf8').trim().split('\n');assert.equal(lines.length,all.length+1);const ids=new Set(lines.slice(1).map(l=>l.split('\t')[0]));for(const w of all)assert.ok(ids.has(w.id))});

test('every published romaji retains the reading and mora boundaries',()=>{const K=require('../ja-kana');for(const w of all)assert.equal(K.soundKey(w.romaji),K.soundKey(w.kana),`${w.id} ${w.kana} ${w.romaji}`)});
test('Tatoeba examples have exact word blanks, short sentences and per-sentence attribution',()=>{
 const check=s=>{assert.ok(Number.isInteger(s.id)&&s.id>0);assert.ok(s.username&&s.username!=='\\N');assert.equal(s.url,`https://tatoeba.org/sentences/show/${s.id}`);assert.equal(s.license,'CC BY 2.0 FR')};
 for(const [n,min] of [[5,600],[4,580],[3,1600],[2,1400],[1,2300]])assert.ok(all.filter(w=>w.level===n&&w.example).length>min,`N${n} example coverage`);
 for(const w of all){const e=w.example;if(!e)continue;check(e);assert.equal(e.lang,'jpn');assert.ok([...e.text].length<=25);assert.ok(Array.isArray(e.furigana));
  const m=e.match;assert.ok(['exact','lemma'].includes(m.kind));if(m.kind==='exact')assert.ok([w.kanji,w.kana].includes(m.surface));else {assert.ok(m.lemma&&['動詞','形容詞'].includes(m.pos));assert.equal(require('../ja-kana').soundKey(m.targetReading),require('../ja-kana').soundKey(w.kana));assert.ok(m.surfaceReading&&m.lexicalEnd<=m.end);}assert.equal(e.text.slice(m.start,m.end),m.surface);
  const t=e.translation;assert.ok(t.text.trim());assert.equal(t.license,'CC BY 2.0 FR');assert.equal(t.lang,'vie');assert.equal(typeof t.machine,'boolean');assert.equal(typeof t.pivot,'boolean');
  if(t.machine){assert.equal(t.pivot,false);check(t.from);assert.equal(t.from.lang,'eng');assert.deepEqual(t.links,[[e.id,t.from.id]])}
  else{check(t);if(t.pivot){check(t.via);assert.equal(t.via.lang,'eng');assert.deepEqual(t.links,[[e.id,t.via.id],[t.via.id,t.id]])}else assert.deepEqual(t.links,[[e.id,t.id]])}
 }
});

test('added pitch values retain explicit licensed lexical evidence and source labels',()=>{
 const rows=JSON.parse(fs.readFileSync('data/sources/pitch-additions.json'));
 const report=JSON.parse(fs.readFileSync('data/sources/pitch-method.json'));
 const hira=s=>s.normalize('NFKC').replace(/[ァ-ヶ]/g,c=>String.fromCharCode(c.charCodeAt(0)-96));
 assert.ok(Object.keys(rows).length>900);
 assert.equal(Object.keys(rows).length,report.added);
 assert.equal(all.filter(w=>w.pitch===null).length,report.remainingNull);
 for(const w of all){const r=rows[w.id];
  if(!r){assert.equal(w.pitchSource,w.pitch?'kanjium':null);continue}
  assert.equal(r.form,w.kanji);assert.equal(r.reading,w.kana);assert.equal(r.jmdict,w.jmdict);
  assert.deepEqual(w.pitch,r.pitch);assert.equal(w.pitchSource,r.source);assert.ok(r.records.length);
  if(r.source==='unidic-2.1.2'){
   assert.equal(r.license,'BSD-3-Clause');
   for(const item of r.records){const f=item.features;
    assert.equal(item.surface,w.kanji);assert.equal(f.orth,w.kanji);assert.equal(f.orthBase,w.kanji);
    assert.equal(hira(f.kana),hira(w.kana));assert.equal(hira(f.kanaBase),hira(w.kana));
    assert.equal(f.aModeType,'*');assert.match(f.aType,/^\d+(,\d+)*$/);
    assert.deepEqual(f.aType.split(',').map(Number),w.pitch);
    assert.ok(r.allowedLemmas.map(hira).includes(hira(f.lemma.replace(/-[A-Za-z].*$/,''))));
   }
  }else{assert.equal(r.source,'kanjium');assert.equal(r.license,'CC-BY-SA-4.0');for(const item of r.records){assert.equal(item.form,w.kanji);assert.equal(hira(item.reading),hira(w.kana));assert.deepEqual(item.acc_pos.split(',').map(Number),w.pitch);assert.ok(item.line>0&&item.rowId&&item.raw)}}
 }
});

 test('sentence ruby preserves every base character, excludes kana and retains lexical evidence',()=>{
 const sources=JSON.parse(fs.readFileSync('data/sources/tatoeba-examples.json'));
 const hira=s=>s.normalize('NFKC').replace(/[ァ-ヶ]/g,c=>String.fromCharCode(c.charCodeAt(0)-96));
 for(const w of all){const e=w.example;if(!e)continue;
  assert.equal(e.furigana.map(s=>s.base).join(''),e.text,w.id);
  for(const s of e.furigana){assert.ok(s.base);if(s.ruby){assert.match(s.base,/^[\p{Script=Han}々〆〇]+$/u);assert.match(s.ruby,/^[ぁ-ゖー]+$/)}}
  assert.deepEqual(e, Object.fromEntries(Object.entries(sources[w.id]).filter(([k])=>!['furiganaEvidence','furiganaSkipped'].includes(k))));
  for(const t of sources[w.id].furiganaEvidence){assert.equal(e.text.slice(t.start,t.end),t.surface);assert.ok(t.dictionaryReadings.includes(t.reading));assert.doesNotMatch(t.surface,/今日|一日|^人$/);if(t.source==='unidic-single-reading')assert.equal(t.dictionaryReadings.length,1);else assert.equal(t.source,'unidic-jmdict-target')}
  const start=e.match.start,end=e.match.end;let offset=0,reading='',complete=true;
  for(const s of e.furigana){const next=offset+s.base.length;if(offset>=start&&next<=end){reading+=s.ruby||hira(s.base);if(!s.ruby&&/\p{Script=Han}/u.test(s.base))complete=false}offset=next}
  if(complete)assert.equal(reading,hira(e.match.kind==='lemma'?e.match.surfaceReading:w.kana),w.id+' target reading');
 }
});
