'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),P=require('../ja-pitch');
const f0=(hz,n=24)=>Array(n).fill(hz);
function sine(hz,seconds=.5,sr=16000){return Float32Array.from({length:seconds*sr},(_,i)=>.3*Math.sin(2*Math.PI*hz*i/sr))}
test('F0 extracts a synthetic 180 Hz tone',()=>{const f=P.track(sine(180),16000).f0.filter(x=>x>0);assert.ok(f.length>20);assert.ok(Math.abs(f.reduce((a,b)=>a+b,0)/f.length-180)<2)});
test('F0 rejects silence',()=>{assert.ok(P.track(new Float32Array(16000)).f0.every(x=>x===null));assert.equal(P.analyse(new Float32Array(16000),16000,'あめ',1).ok,false)});
test('expected fall and rise compare against measured shape',()=>{assert.equal(P.compare([...f0(200),...f0(140)],[1,0]).kind,'similar');assert.equal(P.compare([...f0(140),...f0(200)],[1,0]).kind,'compare');assert.equal(P.compare([...f0(140),...f0(200),...f0(200)],[0,1,1]).kind,'similar')});
test('comparison is invariant to speaker pitch baseline',()=>{const a=[...f0(100),...f0(140),...f0(100)];assert.equal(P.compare(a,[0,1,0]).kind,P.compare(a.map(x=>x*2),[0,1,0]).kind)});
test('unknown accent, one mora and mostly unvoiced audio abstain',()=>{assert.equal(P.analyse(sine(180),16000,'ねこ',null).ok,false);assert.equal(P.compare(f0(180),[1]).ok,false);assert.equal(P.compare([180,...Array(100).fill(0),180],[0,1]).ok,false)});
test('single isolated word cannot distinguish heiban from odaka',()=>{assert.deepEqual(P.pattern(3,0),P.pattern(3,3));assert.notDeepEqual(P.pattern(3,0,true),P.pattern(3,3,true))});
test('synthetic PCM rising and falling words run through full analysis',()=>{const x=new Float32Array(16000);x.set(sine(200));x.set(sine(140),8000);const r=P.analyse(x,16000,'あめ',1);assert.ok(r.ok);assert.equal(r.kind,'similar');assert.equal(r.transitions.length,1)});
