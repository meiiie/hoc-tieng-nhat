'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
test('startup catalogue preserves every ID, level, order and audio availability',()=>{
 const index=JSON.parse(fs.readFileSync('data/index.json'));
 assert.ok(fs.statSync('data/index.json').size<150000,'catalogue budget');
 for(const n of [5,4,3,2,1]){
  const rows=JSON.parse(fs.readFileSync(`data/n${n}.json`)),entry=index.levels[n];
  assert.deepEqual(entry.ids,rows.map(w=>w.id));assert.ok(rows.every(w=>w.level===n));
  assert.deepEqual(entry.withoutAudio,rows.filter(w=>!w.audio).map(w=>w.id));
  for(const w of rows)assert.equal(entry.withoutAudio.includes(w.id)?null:`audio/n${n}/w/${w.id}.mp3`,w.audio);
 }
 for(const [file,info] of Object.entries(index.files)){
  const bytes=fs.readFileSync(file);assert.equal(info.bytes,bytes.length);
  assert.equal(info.revision,crypto.createHash('sha256').update(bytes).digest('hex').slice(0,16),file+' stale revision');
 }
});
