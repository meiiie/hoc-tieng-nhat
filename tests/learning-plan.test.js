const {test} = require('node:test');
const assert = require('node:assert/strict');
const P = require('../learning-plan.js');
const start = new Date(2026, 9, 26, 4).getTime();
const now = start + 3600000, end = start + 86400000;
const words = ['a','b','c'].map(id => ({id}));
const cards = words.flatMap(w => [{cid:w.id,w,dir:'en'},{cid:w.id+'~r',w,dir:'vi'}]);
const state = () => ({srs:{}, introductions:{}, studyDay:{start,words:[],directions:[]}});
const queue = (s, extra={}) => P.queue({cards,srs:s.srs,introductions:s.introductions,
  usage:P.usage(s,start),newIds:words.map(w=>w.id),limit:2,buried:{},now,dayEnd:end,...extra});

test('fresh words have one direction, capped by unique words',()=>{
  const q=queue(state());assert.deepEqual(q.fresh.map(x=>x.cid),['a','b']);assert.equal(q.directions.length,0);
});
test('changing selection cannot reset the daily word quota',()=>{
  const s=state();P.record(s,cards[0],now,start);s.srs.a={state:'learn',due:now+600000};
  assert.deepEqual(queue(s,{newIds:['b','c']}).fresh.map(x=>x.cid),['b']);
});
test('reverse direction is a separate bounded workload, never another word',()=>{
  const s=state();s.introductions.a=start-86400000;s.srs.a={state:'review',due:end+86400000};
  const q=queue(s,{newIds:['a','b','c']});assert.equal(q.fresh.length,2);assert.equal(q.directions.length,1);
  P.record(s,cards[1],now,start);assert.deepEqual(P.usage(s,start),{words:0,directions:1});
});
test('siblings are excluded even when in learning state',()=>{
  const s=state();s.srs.a={state:'review',due:now-1};s.srs['a~r']={state:'learn',due:now-1};
  const q=queue(s,{buried:{a:'a'}});assert.equal(q.learning.length,0);assert.equal(q.review[0].cid,'a');
});
test('due reviews outside selected lesson remain eligible and precede new words',()=>{
  const s=state();s.srs.c={state:'review',due:now-1};s.introductions.c=0;
  const q=queue(s,{newIds:['a']});assert.equal(P.next(q,now).cid,'c');
});
test('zero new-word goal still allows due review, but no new directions',()=>{
  const s=state();s.srs.a={state:'review',due:now-1};s.introductions.a=0;
  const q=queue(s,{limit:0});assert.equal(q.fresh.length+q.directions.length,0);assert.equal(P.next(q,now).cid,'a');
});
test('changing settings invalidates an ineligible resumed new card',()=>{
  assert.equal(P.next(queue(state(),{limit:0}),now,'a'),null);
});
test('a resumed card does not jump over a due learning card',()=>{
  const s=state();s.srs.c={state:'learn',due:now-1};
  assert.equal(P.next(queue(s),now,'a').cid,'c');
});
test('same study day survives midnight; exactly the next 04:00 resets usage',()=>{
  const s=state();P.record(s,cards[0],end-1,start);
  assert.equal(P.usage(s,start).words,1);assert.equal(P.usage(s,end).words,0);
  P.record(s,cards[2],end,end);assert.deepEqual(s.studyDay.words,['b']);
});
test('a skipped day never accumulates quota',()=>{
  const s=state();s.studyDay.start=start-3*86400000;
  assert.equal(queue(s).fresh.length,2);
});
test('manual word restart does not erase first introduction and consumes direction budget',()=>{
  const s=state();s.introductions.a=0;P.record(s,cards[0],now,start);
  assert.equal(s.introductions.a,0);assert.deepEqual(P.usage(s,start),{words:0,directions:1});
});
test('suspended words do not unexpectedly introduce their sibling',()=>{
  const s=state();s.srs.a={state:'review',due:now-1,susp:true};s.introductions.a=0;
  assert.equal(queue(s).directions.length,0);
});
test('new-word order follows supplied recommendations rather than packaging',()=>{
  assert.deepEqual(queue(state(),{newIds:['c','b','a']}).fresh.map(x=>x.cid),['c','b']);
});

test('learner choices can promote any word without completing a level',()=>{
  const base=['common-a1','less-common-b1','chosen-c1','practiced-b2'];
  const s={star:{'chosen-c1':true},ev:{'practiced-b2':[[100,'l',1]]}};
  assert.deepEqual(P.orderIds(base,s),['chosen-c1','practiced-b2','common-a1','less-common-b1']);
  assert.deepEqual(base,['common-a1','less-common-b1','chosen-c1','practiced-b2']);
  assert.deepEqual(P.orderIds(base,{}),base);
});

test('v10 removes lesson scope while retaining progress, quota, preferences and other sessions',()=>{
  const s={set:{lesson:'A1-001',f:{lesson:'A1-001',star:true},retention:0.95},
    user:{goal:'25'},srs:{a:{state:'review',due:now}},notes:{a:'keep'},
    introductions:{a:now},studyDay:{start,words:['a'],directions:[]},
    sess:{review:{cur:'a'},learn:{i:3},_last:'review'}};
  const before=structuredClone(s);P.removeLessonScope(s);
  for(const key of ['srs','notes','introductions','studyDay','user'])assert.deepEqual(s[key],before[key]);
  assert.deepEqual(s.set,{f:{star:true},retention:0.95});
  assert.equal(s.migrationV10.lesson,'A1-001');
  assert.deepEqual(s.sess,{learn:{i:3}});
});
test('migration preserves cards and notes; removes obsolete scope; recovers first introductions',()=>{
  const s={user:{goal:'all'},set:{f:{day:'day01',page:'p1',star:true}},notes:{a:'keep'},
    srs:{a:{state:'review',due:now},b:{state:'review',due:end}},
    revlog:[[now,'a',3,'new',0]],sess:{review:{cur:'a'},learn:{i:3}}};
  const before=structuredClone(s.srs);P.migrate(s,start);
  assert.deepEqual(s.srs,before);assert.equal(s.notes.a,'keep');assert.equal(s.user.goal,'25');
  assert.deepEqual(s.set.f,{star:true});assert.equal(s.migrationV9.filter.day,'day01');
  assert.equal(s.introductions.b,0);assert.equal(s.introductions.a,now);assert.equal(P.usage(s,start).words,1);
  assert.equal(s.sess.review,undefined);assert.equal(s.sess.learn.i,3);
});
test('migration keeps zero and explicit numeric pace; rejects NaN and unlimited',()=>{
  for(const value of ['0','5','10','25'])assert.equal(P.limit(value),+value);
  for(const value of ['50','all',undefined,'NaN',-1,Infinity])assert.equal(P.limit(value),25);
});

test('day groups grow automatically, never exceed 25, and preserve earlier membership',()=>{
  const ids=Array.from({length:4961},(_,i)=>'p1-'+String(i+1).padStart(3,'0'));
  const days=P.groups(ids);assert.equal(days.length,199);
  assert.equal(days.at(-1).wordIds.length,11);assert.equal(days.at(-1).id,'day199');
  assert.equal(days.slice(0,-1).every(d=>d.wordIds.length===25),true);
  assert.deepEqual(days.flatMap(d=>d.wordIds),ids);
  assert.deepEqual(P.groups([...ids].reverse()),days);
  const more=[...ids,...Array.from({length:39},(_,i)=>'p1-'+(4962+i))];
  const extended=P.groups(more);assert.equal(extended.length,200);
  assert.deepEqual(extended.slice(0,198),days.slice(0,198));
  assert.equal(P.groups([...more,'p1-5001']).length,201);
  assert.throws(()=>P.groups(['p1-001','p1-001']),/Duplicate/);
});

test('Japanese release ids retain exact coverage through the shared deterministic grouping',()=>{
  const fs=require('node:fs'),path=require('node:path'),root=path.join(__dirname,'..');
  const words=[5,4,3,2,1].flatMap(n=>JSON.parse(fs.readFileSync(path.join(root,`data/n${n}.json`))));
  const days=P.groups(words.map(w=>w.id));assert.equal(days.length,Math.ceil(words.length/25));
  assert.deepEqual(new Set(days.flatMap(d=>d.wordIds)),new Set(words.map(w=>w.id)));
  assert.deepEqual(P.groups(words.map(w=>w.id).reverse()),days);
});

test('choosing another group allows more new words today without resetting the previous group',()=>{
  const s=state();P.record(s,cards[0],now,start);s.srs.a={state:'review',due:end};
  const group1=['a'],group2=['b','c'];
  assert.equal(queue(s,{newIds:group1,usage:P.usage(s,start,group1),limit:1}).fresh.length,0);
  assert.equal(queue(s,{newIds:group2,usage:P.usage(s,start,group2),limit:1}).fresh.length,1);
  P.record(s,cards[2],now,start);s.srs.b={state:'review',due:end};
  assert.deepEqual(P.usage(s,start),{words:2,directions:0});
  assert.equal(queue(s,{newIds:group1,usage:P.usage(s,start,group1),limit:1}).fresh.length,0);
  assert.equal(queue(s,{newIds:group2,usage:P.usage(s,start,group2),limit:1}).fresh.length,0);
});

test('new reverse cards stay in selected group; due siblings from other groups remain eligible',()=>{
  const s=state();s.introductions.a=0;s.srs.a={state:'review',due:now-1};
  const q=queue(s,{newIds:['b','c']});assert.equal(q.directions.length,0);
  assert.equal(P.next(q,now).cid,'a');
});

test('scoped usage counts directions and is independent of a narrower practice filter',()=>{
  const s=state();s.introductions.a=0;P.record(s,cards[1],now,start);P.record(s,cards[2],now,start);
  const usage=P.usage(s,start,['a','b']);assert.deepEqual(usage,{words:1,directions:1});
  assert.deepEqual(P.usage(s,start,['c']),{words:0,directions:0});
  assert.deepEqual(P.usage(s,end,['a','b']),{words:0,directions:0});
});

test('v11 restores old day and automatic pace while retaining actual study history',()=>{
  const s={...state(),user:{goal:'10'},set:{f:{star:true}},notes:{a:'keep'},
    migrationV9:{goal:'all',filter:{day:'day02'}},sess:{review:{cur:'a'},cards:{i:2}}};
  P.record(s,cards[0],now,start);const before=structuredClone(s);P.restoreDays(s);
  assert.equal(s.set.f.day,'day02');assert.equal(s.set.f.star,true);assert.equal(s.user.goal,'25');
  for(const key of ['studyDay','introductions','srs','notes'])assert.deepEqual(s[key],before[key]);
  assert.deepEqual(s.sess,{cards:{i:2}});
  for(const goal of ['0','5','10','25','50']){
    const x={user:{goal},set:{f:{day:''}}};P.restoreDays(x);
    assert.equal(x.user.goal,goal==='50'?'25':goal);assert.equal(x.set.f.day,'');
  }
});
test('introduction updates are idempotent and undo snapshot restores quota',()=>{
  const s=state(),before=structuredClone(s);P.record(s,cards[0],now,start);P.record(s,cards[0],now,start);
  assert.equal(P.usage(s,start).words,1);Object.assign(s,before);assert.equal(P.usage(s,start).words,0);
});

test('new directions have their own daily cap, even after enabling two-way review',()=>{
  const s=state();for(const w of words){s.introductions[w.id]=0;s.srs[w.id]={state:'review',due:end+1};}
  assert.equal(queue(s).directions.length,2);
  P.record(s,cards[1],now,start);P.record(s,cards[3],now,start);
  assert.equal(queue(s).directions.length,0);assert.equal(P.usage(s,start).words,0);
});

test('burying a whole word hides fresh, review and learning directions',()=>{
  const s=state();s.srs.a={state:'learn',due:now-1};s.srs['b~r']={state:'review',due:now-1};
  const q=queue(s,{buried:{a:'*',b:'*',c:'*'}});
  assert.equal(q.learning.length+q.review.length+q.fresh.length+q.directions.length,0);
});
