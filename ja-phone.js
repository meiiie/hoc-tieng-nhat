/* Mora-level pronunciation scoring for Japanese.
   Reference: kana -> OpenJTalk phonemes per mora (the label set of the on-device model,
   prj-beatrice/japanese-hubert-base-phoneme-ctc-v4, ONNX q4 by air-air, Apache-2.0).
   Scoring: CTC Viterbi forced alignment of the reference (with accepted variants such as devoiced
   vowels and long-vowel spellings) plus a free greedy decode. Each phoneme gets a goodness score from
   the posterior of the expected phoneme over its aligned frames compared with the best competitor. */
(function(root){'use strict';
const hira=s=>String(s).normalize('NFKC').replace(/[ァ-ヶ]/g,c=>String.fromCharCode(c.charCodeAt(0)-96));
const V={a:'a',i:'i',u:'u',e:'e',o:'o'};
const BASE={};const row=(c,ks,vs='aiueo')=>[...ks].forEach((k,i)=>{if(k!=='_')BASE[k]=(c?[c]:[]).concat(vs[i])});
row('','あいうえお');row('k','かきくけこ');row('s','さ_すせそ');row('t','た__てと');row('n','なにぬねの');row('h','はひふへほ');
row('m','まみむめも');row('r','らりるれろ');row('g','がぎぐげご');row('z','ざ_ずぜぞ');row('d','だ__でど');row('b','ばびぶべぼ');row('p','ぱぴぷぺぽ');
Object.assign(BASE,{'し':['sh','i'],'ち':['ch','i'],'つ':['ts','u'],'ひ':['h','i'],'ふ':['f','u'],'は':['h','a'],'じ':['j','i'],'ぢ':['j','i'],'づ':['z','u'],'や':['y','a'],'ゆ':['y','u'],'よ':['y','o'],'わ':['w','a'],'を':['o'],'ゔ':['v','u'],'ゐ':['i'],'ゑ':['e']});
const YO={'ゃ':'a','ゅ':'u','ょ':'o'};
const PAL={'き':'ky','ぎ':'gy','し':'sh','じ':'j','ち':'ch','ぢ':'j','に':'ny','ひ':'hy','び':'by','ぴ':'py','み':'my','り':'ry'};
const SMALLV={'ぁ':'a','ぃ':'i','ぅ':'u','ぇ':'e','ぉ':'o'};
const SPECIAL={'てぃ':['t','i'],'でぃ':['d','i'],'とぅ':['t','u'],'どぅ':['d','u'],'ふぁ':['f','a'],'ふぃ':['f','i'],'ふぇ':['f','e'],'ふぉ':['f','o'],'しぇ':['sh','e'],'じぇ':['j','e'],'ちぇ':['ch','e'],'つぁ':['ts','a'],'つぃ':['ts','i'],'つぇ':['ts','e'],'つぉ':['ts','o'],'うぃ':['w','i'],'うぇ':['w','e'],'うぉ':['w','o'],'いぇ':['y','e'],'ゔぁ':['v','a'],'ゔぃ':['v','i'],'ゔぇ':['v','e'],'ゔぉ':['v','o'],'くぁ':['kw','a'],'ぐぁ':['gw','a']};
const VOICELESS=new Set(['k','s','sh','t','ch','ts','h','f','p','hy','ky','py','cl']);
const vowelOf=ph=>ph[ph.length-1];
/* morae: [{kana, ph:[...], alt:[[...]...], kind}] */
function morae(kana){const s=hira(kana).replace(/[\s・、。！？!?]/g,'');const out=[];
 for(let i=0;i<s.length;i++){const c=s[i],n=s[i+1];
  if(n&&SPECIAL[c+n]){out.push({kana:c+n,ph:SPECIAL[c+n],kind:'mora'});i++;continue}
  if(n&&YO[n]&&PAL[c]){out.push({kana:c+n,ph:[PAL[c],YO[n]],kind:'mora'});i++;continue}
  if(c==='っ'){out.push({kana:c,ph:['cl'],kind:'sokuon'});continue}
  if(c==='ん'){out.push({kana:c,ph:['N'],kind:'n'});continue}
  if(c==='ー'){const p=out[out.length-1];out.push({kana:c,ph:[p?vowelOf(p.ph):'a'],kind:'long'});continue}
  if(SMALLV[c]){out.push({kana:c,ph:[SMALLV[c]],kind:'mora'});continue}
  const b=BASE[c];if(!b)continue;const p=out[out.length-1],pv=p&&p.kind!=='sokuon'&&p.kind!=='n'?vowelOf(p.ph):null;
  /* long vowels spelled with う after o/u and い after e: accept the vowel itself or the lengthened previous vowel */
  if(c==='う'&&(pv==='o'||pv==='u')){out.push({kana:c,ph:[pv],alt:[['u']],kind:'long'});continue}
  if(c==='い'&&pv==='e'){out.push({kana:c,ph:['e'],alt:[['i']],kind:'long'});continue}
  if(b.length===1&&pv===b[0]){out.push({kana:c,ph:b.slice(),kind:'long'});continue}
  out.push({kana:c,ph:b.slice(),kind:'mora',alt:c==='は'&&i===s.length-1&&i>0?[['w','a']]:c==='へ'&&i===s.length-1&&i>0?[['e']]:undefined})}
 /* devoicing: i/u between voiceless consonants, or word-final after a voiceless consonant (です, ます) */
 out.forEach((m,k)=>{const v=vowelOf(m.ph),c=m.ph[0];if(m.ph.length<2||(v!=='i'&&v!=='u')||!VOICELESS.has(c))return;
  const nx=out[k+1],nc=nx&&nx.ph.length>1?nx.ph[0]:nx&&nx.kind==='sokuon'?'cl':null;
  if((nc&&VOICELESS.has(nc))||(!nx&&(c==='s'||c==='sh'))){const up=m.ph.slice(0,-1).concat(v.toUpperCase());m.alt=(m.alt||[]).concat([up]);m.devoice=true}});
 return out}
function logSoftmax(lg,T,Vn){const o=new Float32Array(T*Vn);for(let t=0;t<T;t++){let m=-1e30;for(let v=0;v<Vn;v++)m=Math.max(m,lg[t*Vn+v]);let s=0;for(let v=0;v<Vn;v++)s+=Math.exp(lg[t*Vn+v]-m);const l=m+Math.log(s);for(let v=0;v<Vn;v++)o[t*Vn+v]=lg[t*Vn+v]-l}return o}
function greedy(lp,T,Vn,inv){const out=[];let prev=-1;for(let t=0;t<T;t++){let b=0,bv=-1e30;for(let v=0;v<Vn;v++)if(lp[t*Vn+v]>bv){bv=lp[t*Vn+v];b=v}if(b!==prev&&b!==0&&inv[b]&&!['pau','sil','SOS','EOS','UNK'].includes(inv[b]))out.push({s:inv[b],t,p:Math.exp(bv)});prev=b}return out}
/* best variant per mora, chosen with soft "or" in a CTC Viterbi over a token graph */
function align(lp,T,Vn,ids,ms){
 /* build token list with per-mora alternatives expanded greedily: try each mora's options and keep the one with best local likelihood after alignment */
 const choice=ms.map(()=>0);let best=null;
 const tokensFor=ch=>{const toks=[];ms.forEach((m,k)=>{const opts=[m.ph].concat(m.alt||[]);opts[ch[k]].forEach(p=>toks.push({p,k,id:ids[p]}))});return toks};
 const viterbi=toks=>{const L=toks.length,S=2*L+1,NEG=-1e30;let prev=new Float64Array(S).fill(NEG),cur=new Float64Array(S);const bp=new Int32Array(T*S);
  const lab=s=>s%2?toks[(s-1)/2].id:0;prev[0]=lp[0];if(S>1)prev[1]=lp[lab(1)];
  for(let t=1;t<T;t++){for(let s=0;s<S;s++){let b=prev[s],a=s;if(s>0&&prev[s-1]>b){b=prev[s-1];a=s-1}if(s>1&&s%2&&lab(s)!==lab(s-2)&&prev[s-2]>b){b=prev[s-2];a=s-2}cur[s]=b+lp[t*Vn+lab(s)];bp[t*S+s]=a}[prev,cur]=[cur,prev]}
  let s=S-1;if(S>1&&prev[S-2]>prev[S-1])s=S-2;const score=prev[s],path=new Int32Array(T);for(let t=T-1;t>=0;t--){path[t]=s;if(t)s=bp[t*S+s]}
  const span=toks.map(()=>[]);for(let t=0;t<T;t++)if(path[t]%2)span[(path[t]-1)/2].push(t);return {score,span}};
 const run=ch=>{const toks=tokensFor(ch);return Object.assign(viterbi(toks),{toks})};
 best=run(choice);
 ms.forEach((m,k)=>{const n=1+(m.alt?m.alt.length:0);for(let o=1;o<n;o++){const ch=choice.slice();ch[k]=o;const r=run(ch);if(r.score>best.score){best=r;choice[k]=o}}});
 return Object.assign(best,{choice})}
let out_dur=[];const LONG_MIN=7;const MORA_HINT={sokuon:'Âm ngắt っ: dừng một nhịp trước phụ âm sau.',n:'Âm ん: giữ trọn một nhịp, đừng nuốt.',long:'Trường âm: kéo dài nguyên âm đủ hai nhịp.',mora:''};
function score(logits,T,Vn,vocab,kana){const inv=[];Object.entries(vocab).forEach(([k,v])=>inv[v]=k);const ids=vocab;
 const lp=logSoftmax(logits,T,Vn),ms=morae(kana);if(!ms.length)return null;const heard=greedy(lp,T,Vn,inv);
 if(!heard.length)return {score:0,empty:true,morae:ms.map(m=>({kana:m.kana,kind:m.kind,score:0,st:'del'})),heard:''};
 const al=align(lp,T,Vn,ids,ms);
 const toks=al.toks,phs=toks.map((tk,i)=>{const fr=al.span[i];if(!fr.length)return {...tk,g:0,heard:null};
  let sum=0,comp=0;const counts={};for(const t of fr){const pe=Math.exp(lp[t*Vn+tk.id]);let bo=0,bi=0;for(let v=1;v<Vn;v++)if(v!==tk.id){const q=Math.exp(lp[t*Vn+v]);if(q>bo){bo=q;bi=v}}sum+=pe;comp+=bo;counts[inv[bi]]=(counts[inv[bi]]||0)+1}
  const pe=sum/fr.length,po=comp/fr.length,rival=Object.entries(counts).sort((a,b)=>b[1]-a[1])[0][0];
  /* goodness of pronunciation: share of probability mass on the expected phoneme versus its strongest rival */
  return {...tk,g:pe/(pe+po+1e-6),pe,rival,frames:fr.length,t0:fr[0],t1:fr[fr.length-1]}});
 /* edit-distance check against what the model heard freely: catches dropped morae that forced alignment would squeeze in */
 const H=heard.map(h=>h.s.toLowerCase()),Rr=toks.map(t=>t.p.toLowerCase()),D=[...Array(Rr.length+1)].map((_,i)=>[...Array(H.length+1)].map((_,j)=>i?j?0:i:j));
 for(let i=1;i<=Rr.length;i++)for(let j=1;j<=H.length;j++)D[i][j]=Math.min(D[i-1][j]+1,D[i][j-1]+1,D[i-1][j-1]+(Rr[i-1]===H[j-1]?0:1));
 const miss=new Array(Rr.length).fill(null);for(let i=Rr.length,j=H.length;i>0;){if(j>0&&D[i][j]===D[i-1][j-1]+(Rr[i-1]===H[j-1]?0:1)){miss[i-1]=Rr[i-1]===H[j-1]?null:'sub:'+H[j-1];i--;j--}else if(D[i][j]===D[i-1][j]+1){miss[i-1]='del';i--}else j--}
 toks.forEach((t,i)=>{phs[i].edit=miss[i]});
 const out=ms.map((m,k)=>{const mine=phs.filter(p=>p.k===k);const g=Math.min(...mine.map(p=>p.g));const worst=mine.reduce((a,b)=>a.g<b.g?a:b);
  let sc=Math.max(0,Math.min(1,(g-.15)/.6));let st=sc>=.75?'ok':sc>=.4?'close':'sub';
  const ed=mine.find(p=>p.edit);const prevV=k>0?phs.filter(p=>p.k===k-1).slice(-1)[0]:null,dur=(worst.frames||0)+(m.kind==='long'&&prevV?prevV.frames||0:0);if(m.kind==='long')out_dur.push(dur);const finalDevoice=k===ms.length-1&&ed&&ed.edit==='del'&&/^[iuIU]$/.test(ed.p)&&VOICELESS.has(m.ph[0]);if(ed&&!finalDevoice){if(ed.edit==='del'){sc=Math.min(sc,m.kind==='long'?.35:.25);st=m.kind==='long'?'short':'del'}else if(sc>.6){sc=.6;st='close'}}
  const opt=al.choice[k];return {kana:m.kana,kind:m.kind,score:sc,st,devoiced:!!(m.devoice&&opt>0&&(m.alt||[])[opt-1]&&/[IU]$/.test(m.alt[opt-1].join(''))),rival:worst.g<.5?worst.rival:null,expected:worst.p,t0:mine[0].t0,t1:mine[mine.length-1].t1,hint:st==='ok'?'':MORA_HINT[m.kind]}});
 /* extra phonemes heard that the reference does not have */
 const refStr=toks.map(t=>t.p.toLowerCase()),hs=heard.map(h=>h.s.toLowerCase());const extra=Math.max(0,hs.length-refStr.length);
 const bad=out.filter(m=>m.st!=='ok').length;let total=out.reduce((s,m)=>s+m.score,0)/out.length;total*=Math.pow(.85,bad)*Math.max(.5,1-.08*extra);
 return {score:Math.round(100*total),morae:out,heard:heard.map(h=>h.s).join(' '),expected:toks.map(t=>t.p).join(' '),extra}}
/* pitch per mora: median F0 (semitones) inside each mora's aligned span, then compare the high/low shape with the dictionary accent */
function pitch(pcm,res,frameSec,accent,JaPitch,PAD){const tr=JaPitch.track(pcm,16000),st=tr.f0.map(f=>f?12*Math.log2(f/100):null);
 const starts=res.morae.map(m=>m.t0),toF=t=>Math.round((t*frameSec-PAD/16000)/tr.hop);
 /* CTC emissions are spiky, so a mora spans from its first emission to the next mora's first emission */
 const means=res.morae.map((m,k)=>{if(m.t0==null)return null;const nx=starts.slice(k+1).find(x=>x!=null);const a=Math.max(0,toF(m.t0)),b=Math.min(st.length,nx!=null?toF(nx):toF(m.t1)+12);
  const v=st.slice(a,b).filter(x=>x!=null).sort((x,y)=>x-y);return v.length?v[v.length>>1]:null});
 const ok=means.filter(x=>x!=null);if(ok.length<2)return {means,ok:false};const mid=ok.slice().sort((a,b)=>a-b)[ok.length>>1];
 const centred=means.map(x=>x==null?null:x-mid);const ref=Number.isInteger(accent)?JaPitch.pattern(res.morae.length,accent,false):null;
 if(!ref)return {means:centred,ok:true,ref:null};
 /* which accent pattern fits the measured contour best (Pearson correlation over morae with a pitch value);
    heiban and odaka sound alike on an isolated word, so they count as the same */
 const n=res.morae.length,idx=centred.map((v,i)=>v==null?null:i).filter(i=>i!=null),fit=[];
 for(let a=0;a<=n;a++){const p=JaPitch.pattern(n,a,false),e=idx.map(i=>p[i]),mv=idx.map(i=>centred[i]),me=e.reduce((s,x)=>s+x,0)/e.length,mm=mv.reduce((s,x)=>s+x,0)/mv.length;let c=0,se=0,sm=0;idx.forEach((_,k)=>{c+=(e[k]-me)*(mv[k]-mm);se+=(e[k]-me)**2;sm+=(mv[k]-mm)**2});fit.push(se&&sm?c/Math.sqrt(se*sm):-1)}
 const heardAcc=fit.indexOf(Math.max(...fit)),same=(x,y)=>x===y||(x===0&&y===n)||(x===n&&y===0);
 const match=n<2?null:same(heardAcc,accent),margin=fit[heardAcc]-Math.max(...fit.filter((_,a)=>!same(a,heardAcc)),-1);
 return {means:centred,ok:true,ref,heard:heardAcc,match,margin,confident:margin>.25,accent}}
const api={pitch,morae,score,logSoftmax,greedy,MORA_HINT};
if(typeof module!=='undefined')module.exports=api;else root.JaPhone=api})(typeof self!=='undefined'?self:this);
