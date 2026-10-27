/* Kana conversion and mora units. Long-vowel spelling stays visible; answer comparison accepts spoken equivalents. */
(function(root){'use strict';
const hira=s=>String(s).normalize('NFKC').replace(/[ァ-ヶ]/g,c=>String.fromCharCode(c.charCodeAt(0)-96));
const rows=[['','あいうえお'],['k','かきくけこ'],['s','さしすせそ'],['t','たちつてと'],['n','なにぬねの'],['h','はひふへほ'],['m','まみむめも'],['r','らりるれろ'],['g','がぎぐげご'],['z','ざじずぜぞ'],['d','だぢづでど'],['b','ばびぶべぼ'],['p','ぱぴぷぺぽ']];
const R={},K={};rows.forEach(([c,ks])=>[...ks].forEach((k,i)=>{R[c+'aiueo'[i]]=k;K[k]=c+'aiueo'[i]}));
Object.assign(R,{shi:'し',chi:'ち',tsu:'つ',fu:'ふ',ji:'じ',ya:'や',yu:'ゆ',yo:'よ',wa:'わ',wo:'を',wi:'うぃ',we:'うぇ',ye:'いぇ',vu:'ゔ',va:'ゔぁ',vi:'ゔぃ',ve:'ゔぇ',vo:'ゔぉ',she:'しぇ',je:'じぇ',che:'ちぇ',tsa:'つぁ',tsi:'つぃ',tse:'つぇ',tso:'つぉ',ti:'ち',di:'ぢ',tu:'つ',du:'づ',fa:'ふぁ',fi:'ふぃ',fe:'ふぇ',fo:'ふぉ',thi:'てぃ',dhi:'でぃ',twu:'とぅ',dwu:'どぅ',whu:'う',wha:'うぁ',whi:'うぃ',whe:'うぇ',who:'うぉ',kwa:'くぁ',gwa:'ぐぁ'});
Object.assign(K,{'し':'shi','ち':'chi','つ':'tsu','ふ':'fu','じ':'ji','ぢ':'ji','づ':'zu','や':'ya','ゆ':'yu','よ':'yo','わ':'wa','を':'wo','ゐ':'wi','ゑ':'we','ん':'n','ゔ':'vu'});
for(const [c,k] of Object.entries({ky:'き',gy:'ぎ',sh:'し',sy:'し',ch:'ち',ty:'ち',cy:'ち',ny:'に',hy:'ひ',my:'み',ry:'り',by:'び',py:'ぴ',j:'じ',jy:'じ',zy:'じ',dy:'ぢ',fy:'ふ',vy:'ゔ'}))for(const [v,s]of Object.entries({a:'ゃ',u:'ゅ',o:'ょ'}))R[c+v]=k+s;
for(const [c,k]of Object.entries({a:'ぁ',i:'ぃ',u:'ぅ',e:'ぇ',o:'ぉ',ya:'ゃ',yu:'ゅ',yo:'ょ',wa:'ゎ',tsu:'っ',tu:'っ'})){R['x'+c]=k;R['l'+c]=k}
Object.entries(R).forEach(([r,k])=>{if(k.length>1&&!K[k])K[k]=r});
function toKana(value){const greeting=String(value).trim().toLowerCase();if(greeting==='konnichiwa')return 'こんにちは';if(greeting==='konbanwa')return 'こんばんは';const src=hira(value).toLowerCase().replace(/[’]/g,"'").replace(/[āâ]/g,'aa').replace(/[īî]/g,'ii').replace(/[ūû]/g,'uu').replace(/[ēê]/g,'ee').replace(/[ōô]/g,'ou').replace(/\s/g,'');let out='';
 for(let i=0;i<src.length;){const c=src[i],tail=src.slice(i);if(c==='n'){
  if(src[i+1]==="'"){out+='ん';i+=2;continue}
  if(src[i+1]==='n'){out+='ん';i+=/[aiueoy]/.test(src[i+2]||'!')?1:2;continue}
  if(!src[i+1]||!/^[aiueoy]/.test(src[i+1])){out+='ん';i++;continue}}
  if(/[bcdfghjkpqrstvwxyz]/.test(c)&&src[i+1]===c||tail.startsWith('tch')){out+='っ';i++;continue}
  let found=false;for(let n=4;n>0;n--){const k=R[src.slice(i,i+n)];if(k){out+=k;i+=n;found=true;break}}if(!found){out+=c==='-'?'ー':c;i++}}
 return out}
function morae(value){const out=[];for(const c of hira(value)){if(/[ゃゅょぁぃぅぇぉゎ]/.test(c)&&out.length&&!/[っんー]/.test(out.at(-1)))out[out.length-1]+=c;else if(/[ぁ-ゖー]/.test(c))out.push(c)}return out}
function toRomaji(value){if(hira(value)==='こんにちは')return 'konnichiwa';if(hira(value)==='こんばんは')return 'konbanwa';const a=morae(value);let out='';for(let i=0;i<a.length;i++){const m=a[i];if(m==='っ'){const next=K[a[i+1]]||'';out+=next.startsWith('ch')?'t':next[0]||'';continue}if(m==='ー'){out+=(out.match(/[aeiou](?!.*[aeiou])/)||[''])[0];continue}if(m==='ん'){out+=/^[aiueoy]/.test(K[a[i+1]]||'')?"n'":'n';continue}out+=K[m]||K[m[0]]||m}return out}
const soundKey=s=>{const kana=toKana(s);if(!/^[ぁ-ゖー]+$/.test(kana))return hira(s).trim().toLowerCase();let prev='';return morae(kana).map(m=>{if(m==='ー')return (prev.match(/[aiueo]$/)||['ー'])[0];const r=K[m]||m;prev=r;return r}).join('').replace(/ou/g,'oo').replace(/ei/g,'ee').replace(/'/g,'')};
const norm=s=>{const t=String(s).normalize('NFKC').trim().toLowerCase().replace(/[\s。、！？.,!?]/g,'');return /^[a-zāīūēōâîûêô'’-]+$/.test(t)?toKana(t):hira(t)};
function accepts(w,input){const forms=[w.kanji||w.w,w.kana||w.reading,w.romaji].filter(Boolean);if(input===undefined)return [...new Set(forms.flatMap(s=>[norm(s),soundKey(s)]))];const n=norm(input);return !!n&&forms.some(s=>norm(s)===n||soundKey(s)===soundKey(input))}
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function ruby(form,reading,on=true){if(!on||hira(form)===hira(reading))return `<span lang="ja">${escape(form)}</span>`;return `<ruby lang="ja">${escape(form)}<rp>(</rp><rt>${escape(reading)}</rt><rp>)</rp></ruby>`}
const api={hira,toKana,toRomaji,morae,soundKey,norm,accepts,ruby};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.JaKana=api;
})(globalThis);
