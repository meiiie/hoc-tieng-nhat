/* F0 contour estimates only. No phoneme recognition or language proficiency score. */
(function(root){'use strict';
const Kana=typeof module!=='undefined'?require('./ja-kana.js'):root.JaKana;
const median=a=>{const b=a.slice().sort((a,b)=>a-b);return b.length?b[b.length>>1]:null};
function pattern(count,accent,particle=false){if(!Number.isInteger(accent)||accent<0||accent>count||count<1)return null;return Array.from({length:count+(particle?1:0)},(_,i)=>accent===1?(i===0?1:0):i===0?0:accent===0||i<accent?1:0)}
function track(x,sr=16000){const win=Math.round(sr*.04),hop=Math.round(sr*.01),lo=Math.floor(sr/500),hi=Math.ceil(sr/70),f0=[],energy=[];
 for(let s=0;s+win+hi<x.length;s+=hop){let e=0;for(let i=0;i<win;i++)e+=x[s+i]*x[s+i];energy.push(e/win);if(e/win<1e-5){f0.push(null);continue}
  const r=new Float64Array(hi+2);let best=0;for(let lag=lo;lag<=hi+1;lag++){let c=0,e2=0;for(let i=0;i<win;i++){c+=x[s+i]*x[s+i+lag];e2+=x[s+i+lag]**2}r[lag]=c/Math.sqrt(e*e2+1e-12);if(lag<=hi)best=Math.max(best,r[lag])}
  let peak=0;for(let l=lo+1;l<=hi;l++)if(r[l]>=best*.85&&r[l]>=r[l-1]&&r[l]>=r[l+1]){peak=l;break}
  if(best<.65||!peak){f0.push(null);continue}const d=r[peak-1]-2*r[peak]+r[peak+1],off=d<0?.5*(r[peak-1]-r[peak+1])/d:0;f0.push(sr/(peak+Math.max(-.5,Math.min(.5,off))))}
 return {f0,energy,hop:.01}}
function compare(f0,expected){if(!expected||expected.length<2)return {ok:false,reason:'Không đủ chuyển động cao độ để so sánh từ một mora.'};
 const first=f0.findIndex(x=>x>0),last=f0.length-1-[...f0].reverse().findIndex(x=>x>0);if(first<0)return {ok:false,reason:'Chưa nhận được cao độ rõ. Bạn có thể nghe lại bản ghi.'};
 const part=f0.slice(first,last+1),voiced=part.filter(x=>Number.isFinite(x)&&x>=70&&x<=500);
 if(voiced.length<Math.max(12,expected.length*4)||voiced.length/part.length<.35)return {ok:false,reason:'Có quá ít đoạn hữu thanh để ước lượng. Hãy nghe và đối chiếu.'};
 const base=median(voiced),contour=part.map(x=>x>=70&&x<=500?12*Math.log2(x/base):null),means=[];
 for(let i=0;i<expected.length;i++){const a=Math.floor(part.length*i/expected.length),b=Math.floor(part.length*(i+1)/expected.length),v=contour.slice(a,b).filter(x=>x!=null);means.push(v.length>=Math.max(3,(b-a)*.25)?median(v):null)}
 const transitions=[];for(let i=1;i<means.length;i++){const a=means[i-1],b=means[i],want=expected[i]-expected[i-1];transitions.push({mora:i+1,expected:want,delta:a==null||b==null?null:+(b-a).toFixed(2),match:a==null||b==null?null:want===0?Math.abs(b-a)<2.5:want*(b-a)>.8})}
 const measured=transitions.filter(x=>x.match!==null);if(measured.length<Math.max(1,transitions.length*.5))return {ok:false,reason:'Các khoảng mora chưa có đủ cao độ rõ để đối chiếu.'};
 return {ok:true,kind:measured.every(x=>x.match)?'similar':'compare',means,contour,transitions,voicedFraction:voiced.length/part.length,frameStart:first,frameEnd:last};
}
function analyse(pcm,sr,kana,accent){const expected=pattern(Kana.morae(kana).length,accent);if(!expected)return {ok:false,reason:'Từ này chưa có mẫu cao độ từ nguồn đã đối chiếu.'};const t=track(pcm,sr);return {...compare(t.f0,expected),expected,duration:pcm.length/sr}}
const api={pattern,track,compare,analyse};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.JaPitch=api;
})(globalThis);
