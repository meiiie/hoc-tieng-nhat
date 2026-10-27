'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const E=require('../ja-examples');
const read=p=>JSON.parse(fs.readFileSync(p));
const final=read('ex5/final.json'),byId=new Map(final.map(r=>[r.id,r]));
const inputs=new Map([...read('ex5/authored.json'),...read('ex5/licensed-candidates.json')].map(r=>[r.id,r]));
const reviews=new Map(read('ex5/review.json').map(r=>[r.id,r]));
const published=read('ex5/released-levels.json');
const words=[5,4,3,2,1].flatMap(n=>read(`data/n${n}.json`));
const AI='Câu do AI viết, cần kiểm tra',MACHINE='bản dịch máy, cần kiểm tra';
test('review decisions preserve passes, apply exact fixes, and distinguish one rewrite self-check from review',()=>{
 assert.equal(final.length,1409);assert.equal(byId.size,1409);
 for(const r of final){const original=inputs.get(r.id),review=reviews.get(r.id),c=r.final_candidate;
  assert.equal(r.review_verdict,review.verdict);
  if(review.verdict==='pass'){assert.equal(r.final_status,'accepted_pass');assert.deepEqual(c,original);}
  if(review.verdict==='fix'){assert.equal(c.ja,review.suggested_ja);assert.equal(c.vi,review.suggested_vi);assert.equal(r.fix_selfcheck.verdict,'pass');}
  if(review.verdict==='reject'){
   assert.equal(r.rewrite_selfcheck.attempt,1);assert.equal(r.rewrite_selfcheck.independent_review,false);
   assert.ok(r.rewrite_attempt);assert.notEqual(r.rewrite_attempt.ja,original.ja);
   if(r.final_status==='dropped'){assert.equal(c,null);assert.equal(r.rewrite_selfcheck.verdict,'fail');}
   else{assert.equal(r.rewrite_selfcheck.verdict,'pass');assert.ok(Object.values(r.rewrite_selfcheck.criteria).every(v=>v==='pass'));assert.deepEqual(c,r.rewrite_attempt);}
  }
  if(c){assert.equal(c.ja.slice(c.match.start,c.match.end),c.match.surface);assert.ok(c.match.surface);assert.equal(c.native_reviewed,false);}
 }
});
test('published new examples retain target lemma evidence, selected sense, labels and source attribution',()=>{
 for(const w of words){const r=byId.get(w.id);if(!r)continue;
  if(!published.includes(w.level)||r.final_status==='dropped'){assert.equal(w.example,null,w.id);continue;}
  const c=r.final_candidate,e=w.example,html=E.render(e),t=e.translation;
  assert.equal(e.text,c.ja);assert.equal(t.text,c.vi);assert.deepEqual(e.match,c.match);
  assert.equal(c.sense.jmdict,w.jmdict);assert.ok(c.sense.gloss.length&&c.sense.part_of_speech.length);
  assert.equal(c.analysis.unknown_target,false);
  assert.ok(c.analysis.target_tokens.length);assert.equal(e.text.slice(e.match.start,e.match.end),e.match.surface);
  // Non-strict target readings are explicitly editorial, never guessed ruby.
  if(!c.analysis.strict_match){let pos=0;for(const s of e.furigana){const end=pos+s.base.length;if(pos<e.match.end&&end>e.match.start)assert.ok(!s.ruby,w.id);pos=end;}}
  if(t.machine){assert.equal(t.label,MACHINE);assert.ok(html.includes(MACHINE));assert.ok(t.translator);}
  if(e.source==='ai'){
   assert.equal(e.label,AI);assert.ok(html.includes(AI));assert.ok(html.includes('ja-example-ai'));
   assert.doesNotMatch(html,/tatoeba/i);assert.doesNotMatch(JSON.stringify(e),/tatoeba/i);
   assert.equal(c.source,undefined);assert.equal(e.id,'ai:'+w.id);assert.equal(t.machine,true);
   assert.ok([...e.text].length<=25);
  }else{
   assert.ok(['tatoeba','kftt','wiktionary','knbc'].includes(e.source));assert.ok([...e.text].length<=35);
   assert.equal(e.sourceName,c.source);assert.equal(e.label,c.source);assert.equal(e.id,c.source_id);
   assert.equal(e.username,c.author);assert.equal(e.url,c.url);assert.equal(e.license,c.licence);assert.equal(e.licenseUrl,c.licence_url);
   assert.equal(t.license,c.translation.licence);assert.ok(html.includes(c.source));assert.ok(html.includes(c.author.replace(/&/g,'&amp;')));
   assert.ok(html.includes(c.licence));assert.equal(e.changes,c.changes);assert.equal(e.attribution,c.attribution);
   if(e.source!=='tatoeba')assert.doesNotMatch(html,/Tatoeba/);
   const original=inputs.get(w.id);
   if(e.text!==original.ja){assert.equal(e.original_ja,original.ja);assert.match(e.changes,/adapted/i);assert.doesNotMatch(e.changes,/copied verbatim/);}
   if(!original.translation.machine&&t.text!==original.vi){
    assert.equal(t.machine,true);assert.equal(t.original.text,original.vi);assert.equal(t.original.username,original.translation.username);
    assert.equal(t.original.url,original.translation.url);assert.ok(html.includes(original.translation.username));
   }
  }
 }
});
