'use strict';
function jaWrite(){const params=new URLSearchParams(location.hash.split('?')[1]||''),word=byId(params.get('w'))||deck().find(w=>/[一-龯]/.test(w.kanji)),text=params.get('kana')||word?.kanji||'あ';let chars=[...text].filter(c=>/[ぁ-ゖァ-ヺ一-龯]/.test(c)),index=0,mode='watch',dead=false,attempt=0,animations=[];
 if(!chars.length)chars=['あ'];
 if(params.get('c')&&chars.includes(params.get('c')))index=chars.indexOf(params.get('c'));
 function stop(){attempt++;animations.forEach(a=>a.cancel());animations=[]}
 async function draw(){stop();const token=attempt,c=chars[index],info=LANG.kanji[c]||{},src=info.strokes||`data/strokes/${c.codePointAt(0).toString(16).padStart(5,'0')}.svg`;
  view('Viết chữ',`${mascot('think','Theo từng nét, chậm một chút cũng được.',{small:true,row:true})}<section class="card ja-write"><div class="chips" aria-label="Chọn chữ">${chars.map((x,i)=>`<button class="chip ${i===index?'on':''}" lang="ja" data-char="${i}" aria-pressed="${i===index}">${esc(x)}</button>`).join('')}</div>
  <h2 lang="ja">${esc(c)}</h2>${word&&!params.has('kana')?`<p>${esc(word.v)} · ${esc(word.kana)}</p>`:''}<div id="stroke-box" class="stroke-box" role="img" aria-label="Thứ tự nét chữ ${esc(c)}"></div>
  <p id="stroke-status" role="status">Đang tải nét chữ…</p><div class="row"><button class="btn sec" id="watch" aria-pressed="${mode==='watch'}">${I('play','s')}Xem nét</button><button class="btn" id="trace" aria-pressed="${mode==='trace'}">${I('pen-line','s')}Tự viết</button></div>
  ${info.hv?.length?`<p>Hán Việt: <b>${esc(info.hv.join(', '))}</b></p>`:''}${info.on?.length?`<p class="reading">Âm on: <span lang="ja">${esc(info.on.join(' · '))}</span></p>`:''}${info.kun?.length?`<p class="reading">Âm kun: <span lang="ja">${esc(info.kun.join(' · '))}</span></p>`:''}</section><p class="hint">Nét chữ: KanjiVG, Ulrich Apel · CC BY-SA 3.0. Luyện viết không thay đổi lịch ôn.</p>`);
  $$('[data-char]').forEach(b=>b.onclick=()=>{index=+b.dataset.char;draw()});$('#watch').onclick=()=>{mode='watch';draw()};$('#trace').onclick=()=>{mode='trace';draw()};
  try{const response=await fetch(src);if(!response.ok)throw new Error('missing');const doc=new DOMParser().parseFromString(await response.text(),'image/svg+xml');if(dead||token!==attempt)return;
   const paths=[...doc.querySelectorAll('path[id]')].filter(p=>/-s\d+$/.test(p.id));if(!paths.length)throw new Error('empty');const NS='http://www.w3.org/2000/svg',svg=document.createElementNS(NS,'svg');svg.setAttribute('viewBox','0 0 109 109');svg.setAttribute('aria-hidden','true');svg.innerHTML='<path class="stroke-grid" d="M54.5 0V109M0 54.5H109M0 0L109 109M109 0L0 109"/>';
   const copies=paths.map(p=>{const x=document.createElementNS(NS,'path');x.setAttribute('d',p.getAttribute('d'));x.setAttribute('class','stroke-path');svg.appendChild(x);return x});$('#stroke-box').appendChild(svg);
   if(mode==='watch'){let delay=0;copies.forEach((p,i)=>{const length=p.getTotalLength();p.style.strokeDasharray=length;p.style.strokeDashoffset=reduce?0:length;if(!reduce){const a=p.animate([{strokeDashoffset:length},{strokeDashoffset:0}],{duration:650,delay,fill:'forwards',easing:'ease-in-out'});animations.push(a);delay+=850}});$('#stroke-status').textContent=`${paths.length} nét. Bấm Xem nét để xem lại.`}
   else trace(svg,copies,c,token);
  }catch(e){if(!dead&&token===attempt)$('#stroke-status').textContent='Nét chữ chưa có trên máy. Hãy mở chữ này khi có mạng rồi thử lại.'}
 }
 function trace(svg,paths,c,token){let current=0,points=[],active=false,misses=0;paths.forEach(p=>p.classList.add('outline'));paths[0].classList.add('target');const guide=document.createElementNS(svg.namespaceURI,'path');guide.setAttribute('class','trace-line');svg.appendChild(guide);svg.style.touchAction='none';
  const status=()=>$('#stroke-status').textContent=`Viết nét ${current+1}/${paths.length} theo đường mờ, từ đầu đến cuối.`;status();
  const point=e=>{const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;return p.matrixTransform(svg.getScreenCTM().inverse())};
  svg.onpointerdown=e=>{if(current>=paths.length||dead)return;e.preventDefault();svg.setPointerCapture(e.pointerId);active=true;points=[point(e)];guide.setAttribute('d',`M${points[0].x} ${points[0].y}`)};
  svg.onpointermove=e=>{if(!active)return;points.push(point(e));guide.setAttribute('d',points.map((p,i)=>`${i?'L':'M'}${p.x} ${p.y}`).join(' '))};
  svg.onpointercancel=()=>{active=false;guide.setAttribute('d','')};
  svg.onpointerup=e=>{if(!active)return;active=false;points.push(point(e));const p=paths[current],length=p.getTotalLength(),samples=Array.from({length:41},(_,i)=>p.getPointAtLength(i*length/40));const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);const nearest=points.map(p=>{let best=0;for(let i=1;i<samples.length;i++)if(distance(p,samples[i])<distance(p,samples[best]))best=i;return best});const covered=samples.filter(s=>points.some(p=>distance(p,s)<10)).length/samples.length;let backwards=0;for(let i=1;i<nearest.length;i++)if(nearest[i]<nearest[i-1]-3)backwards++;
   const good=points.length>=4&&distance(points[0],samples[0])<16&&distance(points.at(-1),samples.at(-1))<16&&covered>.78&&backwards<Math.max(2,points.length*.12)&&points.filter(p=>samples.some(s=>distance(p,s)<12)).length/points.length>.8;
   guide.setAttribute('d','');if(!good){misses++;$('#stroke-status').textContent='Thử lại nét này, từ đầu đến cuối đường gợi ý.';p.classList.toggle('hinted',misses>=3);buzz(15);return}
   p.classList.remove('outline','target','hinted');p.classList.add('complete');current++;misses=0;buzz(8);
   if(current===paths.length){$('#stroke-status').textContent=`Đã viết xong chữ ${c}. Bạn có thể luyện lại.`;moodTo($('.mascot'),'correct');S.writing=S.writing||{};S.writing[c]=(S.writing[c]||0)+1;if(word&&!params.has('kana'))evidence(word,true,'write');save()}
   else{paths[current].classList.add('target');status()}};
 }
 draw();return ()=>{dead=true;stop()};
}
