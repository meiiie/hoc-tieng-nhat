#!/usr/bin/env python3
"""Generate language hooks from the pinned English gold standard, never hand-edit core.
All replacements assert their counts. Inputs are read-only. Run from any directory.
"""
from pathlib import Path
import argparse,shutil,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--english',type=Path,default=Path('/workspace/english/hoc-tu-vung'));ap.add_argument('--chinese',type=Path,default=Path('/workspace/chinese/hoc-tieng-trung'));a=ap.parse_args();en=a.english;zh=a.chinese
s=(en/'app.js').read_text()
def R(old,new,n=1):
 global s
 assert s.count(old)==n,(s.count(old),old[:100]);s=s.replace(old,new)
def B(start,end,new):
 global s
 assert s.count(start)==s.count(end)==1,(start,end)
 i=s.index(start);j=s.index(end,i);s=s[:i]+new+s[j:]
R("/* Học Từ Vựng. Static PWA with versioned content and local progress. */","/* Generated Neko core. Source and assertions: tools/make-core.py. */\nconst LANG=window.LANG||{};")
R("const DAY=864e5,KEY='htv2',AUDIO_CACHE='htv-audio-v1';","const DAY=864e5,KEY=LANG.key||'htn-core',AUDIO_CACHE=LANG.audioCache||'htn-audio-v1';")
R("retention:0.9,rev:true,fcMode:'sched'}};","retention:0.9,rev:true,fcMode:'sched',...(LANG.setDefaults||{})}};")
R("function migrate(d){d=d&&typeof d=='object'?d:{};let v=+d.v||2;","function migrate(d){d=d&&typeof d=='object'&&!Array.isArray(d)?d:{};if(+d.v>SCHEMA)return {...structuredClone(blank),...d,set:{...structuredClone(blank.set),...d.set}};let v=+d.v||2;\n if(v<SCHEMA&&Object.keys(d).length)lsSet(KEY+'-pre-v'+v,JSON.stringify(d));")
R("const save=()=>{S.v=SCHEMA;","const save=()=>{if(+S.v>SCHEMA)return Promise.resolve(false);S.v=SCHEMA;")
B('async function loadData(){', '\nconst F=()', '''async function loadData(){const x=await LANG.loadData();pages=x.pages;words=x.words;wordIndex=new Map(words.map(w=>[w.id,w]));
 studyOrder=words.map(w=>w.id);studyDays=[];dayIndex=new Map();}
''')
R("function deck(){const f=F();return words.filter(w=>(", "function deck(){const f=F();return words.filter(w=>(!LANG.inDeck||LANG.inDeck(w))&&(")
R("const aurl=(w,kind='w',v=S.set.voice)=>Content.audioURL(w,kind,v);","const aurl=(w,kind='w',v=S.set.voice)=>LANG.aurl(w,kind,v);")
R("function play(w,kind='w',opt={}){if(!w)return;try{","function play(w,kind='w',opt={}){if(!w)return;if(LANG.play&&LANG.play(w,kind,opt))return;try{")
R("$('#title').textContent=title||'Học Từ Vựng';","$('#title').textContent=title||LANG.title||'Học Từ Vựng';")
R("const answerText=w=>w.w.replace(/\\s*\\(.*?\\)/g,'');","const answerText=LANG.answerText;")
B('const norm=s=>','/* ---------- answer checking:',"const norm=LANG.norm,accepts=LANG.accepts;\n")
R('function checkAns(input,targets){const h=norm(input);','function checkAns(input,targets){if(LANG.checkAns)return LANG.checkAns(input,targets);const h=norm(input);')
R('const cloze=w=>Content.cloze(w);','const cloze=w=>LANG.cloze?LANG.cloze(w):Content.cloze(w);')
R("targets=cz?[norm(cz.ans),...accepts(w)]:accepts(w)","targets=cz?(LANG.clozeTargets?LANG.clozeTargets(w,cz):[norm(cz.ans),...accepts(w)]):accepts(w)")
R("${ok?'':'Đáp án: '}<b>${esc(w.w)}</b> ${esc(ipaOf(w))}","${ok?'':'Đáp án: '}<b>${esc(st===2?cloze(w).ans:w.w)}</b> ${esc(st===2&&w.example?.match?.kind==='lemma'?w.example.match.surfaceReading:ipaOf(w))}")
R('<p class="muted" style="margin:0 0 4px">${esc(w.exvi)}</p>', '${LANG.clozeDetails?LANG.clozeDetails(w):esc(w.exvi)}')
R('function backFace(w){return `','function backFace(w){if(LANG.backFace)return LANG.backFace(w);return `')
R('function frontFace(w,dir){return `','function frontFace(w,dir){if(LANG.frontFace)return LANG.frontFace(w,dir);return `')
B('function sheet(html,onClose){', "document.addEventListener('keydown',e=>{if(e.key=='Escape'", """function sheet(html,onClose){const sh=$('#sheet'),opener=document.activeElement,header=document.querySelector('header');
 sh.innerHTML=`<div><div class="grab" aria-hidden="true"></div><button class="ib sheet-close" aria-label="Đóng bảng">${I('x')}</button>${html}</div>`;sh.classList.remove('hidden');app.inert=true;header.inert=true;
 const heading=$('h2',sh);if(heading){heading.id='sheet-heading';sh.setAttribute('aria-labelledby',heading.id)}
 const close=(refresh=true)=>{if(sh.classList.contains('hidden'))return;sh.classList.add('hidden');app.inert=false;header.inert=false;if(refresh&&onClose)onClose();if(opener?.isConnected&&!opener.closest('[inert]'))opener.focus({preventScroll:true})};
 $('.sheet-close',sh).onclick=()=>close();sh.onclick=e=>{if(e.target===sh)close()};sh._close=close;
 sh.onkeydown=e=>{if(e.key!=='Tab')return;const xs=$$('button,a,input,select,textarea,summary,[tabindex="0"]',sh).filter(x=>!x.disabled&&x.getClientRects().length);if(!xs.length)return;const first=xs[0],last=xs.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}};
 requestAnimationFrame(()=>{if(!sh.classList.contains('hidden'))$('.sheet-close',sh).focus({preventScroll:true})});return {sh,close}}
""")
R("function route(){keys=null;", "function route(){if(!$('#sheet').classList.contains('hidden'))$('#sheet')._close?.(false);keys=null;")
R("function openFilter(){const f=F();","function openFilter(){if(LANG.filter)return LANG.filter();const f=F();")
R("<div class=\"opt-row\"><span>Giọng đọc</span>${seg('voice',[['gb','Anh (UK)'],['us','Mỹ (US)']])}</div>","${LANG.settingsTop?LANG.settingsTop(seg):''}")
R("${deck().length} thẻ · khoảng ${Math.ceil(deck().reduce((n,w)=>n+(w.audioBytes?.[S.set.voice]||0),0)/1048576)} MB · giọng ${S.set.voice=='gb'?'Anh':'Mỹ'}. Có thể tiếp tục nếu tải lỗi", "${LANG.audioUrls().length} tệp có sẵn trong bộ đang chọn. Giọng thiết bị phụ thuộc máy.")
R("Content.downloadAudio(selected,voice,c,", "LANG.downloadAudio(selected,voice,c,")
R("tệp giọng ${voice=='gb'?'Anh':'Mỹ'}", "tệp âm thanh")
B(' <div class="eyebrow">Chấm phát âm</div>',' <div class="eyebrow">Giao diện</div>'," ${LANG.settingsPron?LANG.settingsPron(seg):''}\n")
R('Nội dung 26-10-2026 · Giọng đọc tổng hợp Piper và Microsoft · <a href="CONTENT_SOURCES.html" target="_blank" rel="noopener">Nguồn dữ liệu, giấy phép và giới hạn kiểm duyệt</a>',"${LANG.credits}")
R('${LANG.credits}</p>`,route);',"${LANG.credits}</p>`,()=>{if(location.hash==='#/settings')location.hash='#/';else route()});")
B(' if(Speech.supported()){const upd=s=>'," $$('[data-sw]',sh)"," if(LANG.bindSettings)LANG.bindSettings(sh,close);\n")
R("if(k=='voice'||k=='slow')play(words[2]);updVoice();", "if(k=='voice'||k=='slow')play(words[2]);if(LANG.onSet)LANG.onSet(k,v);updVoice();")
R('function onboarding(step=0,draft={...(S.user||{})}){','function onboarding(step=0,draft={...(S.user||{})}){if(LANG.onboarding)return LANG.onboarding(step,draft);')
R("function home(){const d=deck()","function home(){if(LANG.onHome)LANG.onHome();const d=deck()")
R('Chuỗi ${streak} ngày đang chờ bạn, vài câu là đủ.','Bạn có thể học tiếp hoặc nghỉ theo thời gian của mình.')
B(' <div class="day-picker">',' ${resumeBanner()}'," <div class=\"chips ja-levels\">${LANG.homeChips?LANG.homeChips():''}</div>\n")
R("$('#filt').onclick=openFilter;","$('#filt')&&($('#filt').onclick=openFilter);if(LANG.bindHome)LANG.bindHome();")
R("stats:['chart-column','Thống kê','Tiến độ theo cấp độ']};", "stats:['chart-column','Thống kê','Tiến độ theo cấp độ'],...(LANG.modes||{})};")
R('function ipaOf(w){if(w.ipaByVoice', 'function ipaOf(w){if(LANG.ipaOf)return LANG.ipaOf(w);if(w.ipaByVoice')
R('function speak(){const d=deck();', 'function speak(){if(LANG.speak)return LANG.speak();const d=deck();')
R("const LV={A1:1,A2:2,B1:3,B2:4,C1:5,C2:6},", "const LV={A1:1,A2:2,B1:3,B2:4,C1:5,C2:6,...(LANG.lvOrder||{})},")
R("norm(w.vi).includes(q)||(w.meanings||[])","norm(w.vi).includes(q)||(LANG.search&&LANG.search(w,$('#sq').value))||(w.meanings||[])")
R('<h2>${esc(w.w)} ${lifeTag(k)}</h2><p class="muted">${esc(ipaOf(w))} · ${esc(w.vi)}</p>', '<h2>${esc(w.w)} ${lifeTag(k)}</h2><p class="muted">${esc(ipaOf(w))} · ${esc(w.vi)}</p>${LANG.wordExtra?LANG.wordExtra(w):\'\'}')
R("const sp=d.filter(w=>S.speak[w.id]!=null),spa=sp.length?Math.round(sp.reduce((a,w)=>a+S.speak[w.id],0)/sp.length):0,fm=", "const sp=d.filter(w=>(S.pron[w.id]||[]).length),fm=")
R('${sp.length?spa:\'–\'}</b><span class="muted">điểm nói TB (${sp.length} từ)', '${sp.length}</b><span class="muted">từ đã luyện nói')
R("{app:'hoc-tu-vung',schema:SCHEMA", "{app:LANG.app,schema:SCHEMA")
R("a.download=`hoc-tu-vung-tien-do-${today()}.json`", "a.download=`${LANG.app}-tien-do-${today()}.json`")
R("const d=j&&j.app=='hoc-tu-vung'&&j.data?j.data:j;", "if(j?.app&&j.app!==LANG.app)throw new Error('wrong app');const d=j&&j.app===LANG.app&&j.data?j.data:j;")
R("hard:()=>learn('hard'),speak,listen,match,test,list,stats};", "hard:()=>learn('hard'),speak,listen,match,test,list,stats,...(LANG.routes||{})};")
R("if(!words.length)return;if(!S.user", "if(!words.length)return;if(+S.v>SCHEMA){view('Phiên bản mới hơn','<p>Tiến độ được tạo bằng phiên bản mới hơn. Hãy tải lại ứng dụng; dữ liệu của bạn vẫn được giữ nguyên.</p>');return}if(!S.user")
R("const k=location.hash.replace(/^#\\/?/,'');const r=(R[k]||home)();", "const k=location.hash.replace(/^#\\/?/,'').split('?')[0];const r=(R[k]||home)();")
R("const updVoice=()=>{$('#voice').textContent=", "const updVoice=()=>{if(LANG.chip)return LANG.chip.paint();$('#voice').textContent=")
R("$('#voice').onclick=()=>{S.set.voice=", "$('#voice').onclick=()=>{if(LANG.chip)return LANG.chip.click();S.set.voice=")
R(".then(()=>loadPron()).then(()=>{save();route();", ".then(()=>S.v>SCHEMA?null:(LANG.boot?LANG.boot():loadPron())).then(()=>{save();route();")
R("function applyTheme(){const dark=","function applyTheme(){for(const id of ['voice','settings'])$('#'+id).disabled=+S.v>SCHEMA;const dark=")
R("delete d.set.dark", "/* Retain the legacy field for additive recovery. */")
R("addEventListener('click',e=>{if(performance.now()-(window._swipeT||0)<450)","addEventListener('click',e=>{if(window._swipeT!=null&&performance.now()-window._swipeT<450)")
R("lastFlip=0,lastSwipeEnd=0,busy=false;", "lastFlip=-Infinity,lastSwipeEnd=-Infinity,busy=false;")
# A swipe is a rating only after retrieval; on the front it reveals the answer.
R("const cc=makeCard($('#stage'),w,x.dir,right=>answer(right?3:1));", "const cc=makeCard($('#stage'),w,x.dir,right=>{if(ss.flipped)answer(right?3:1);else{ss.flipped=true;put();nx()}});")
R("const selectedUsage=(now=Date.now())=>LearningPlan.usage(S,studyStart(now),selectedDay()?.wordIds);", "const selectedUsage=(now=Date.now())=>LearningPlan.usage(S,studyStart(now));")
R("function deckName(){const f=F(),p=[];", "function deckName(){if(LANG.deckName)return LANG.deckName();const f=F(),p=[];")
R("'':[['Tab','Di chuyển giữa các mục'],['Enter','Mở chế độ']]};", "'':[['Tab','Di chuyển giữa các mục'],['Enter','Mở chế độ']],...(LANG.keys||{})};")
# Language strings: counts are pinned so upstream copy changes fail loudly.
for old,new,n in [('Gõ từ tiếng Anh','Gõ kana, romaji hoặc kanji',2),('Từ tiếng Anh là gì?','Từ tiếng Nhật là gì?',1),('từ tiếng Anh','từ tiếng Nhật',1),('Đổi chiều Anh – Việt','Đổi chiều Nhật – Việt',2),('Việt → Anh','Việt → Nhật',3),('Anh → Việt','Nhật → Việt',1),('Tìm từ hoặc nghĩa','Tìm từ, kana, romaji, Hán Việt hoặc nghĩa',1),('Nghe giọng chuẩn, nói theo, chấm điểm','Nghe và xem phản hồi cao độ ước lượng',1),('Nói theo giọng chuẩn, chấm điểm','Cao độ và nhịp mora, phản hồi ước lượng',1),('Ghép sai bị cộng 1 giây.','Bạn có thể thử lại các cặp chưa khớp.',1),('Chọn ngày khác','Chọn bộ từ khác',2),('Từ mới mỗi nhóm','Từ mới mỗi ngày',1)]:R(old,new,n)
R("lang=\"${x.k}\"", "lang=\"${x.k=='en'?'ja':'vi'}\"")
R('<details class="study-help"><summary>Cách chọn từ và tính lượt học</summary><p>Mỗi nhóm Ngày có tối đa 25 từ. Bạn có thể chọn ngày khác để học tiếp ngay. Từ mới lấy trong bộ đang chọn; thẻ đến hạn vẫn ôn trên toàn thư viện.</p><p>Giới hạn áp dụng riêng cho từng nhóm và làm mới lúc 04:00 giờ thiết bị. Chọn Tất cả dùng giới hạn chung. Chiều mới của từ đã học tính riêng; hai chiều không xuất hiện cùng ngày. Mục tiêu câu trả lời tính theo ngày lịch.</p></details>', '<details class="study-help"><summary>Cách chọn từ và tính lượt học</summary><p>Từ mới lấy trong cấp đã chọn. Các thẻ đến hạn được ôn trước, trên toàn thư viện. Mục tiêu mặc định là 5 từ mới mỗi ngày và làm mới lúc 04:00 giờ thiết bị.</p><p>Chiều mới của từ đã gặp có hạn mức riêng; hai chiều không xuất hiện cùng ngày. Luyện tập ghi lại lần thực hành; khi quên từ đang ôn, ngày ôn có thể được kéo về ngày mai.</p></details>')
s+='\nwindow.CORE={get state(){return S},get words(){return words},save,practice,evidence,rate:gradeCard,life,route,deck,bringForward,migrate};\n'
(ROOT/'core/app-core.js').write_text(s)
for name in ['style.css','mascot.js']:shutil.copyfile(en/name,ROOT/'core'/name)
for name in ['speech.js','mic-meter.js','mic-worklet.js']:shutil.copyfile(zh/'core'/name,ROOT/'core'/name)
for name in ['srs.js','learning-plan.js','content.js']:shutil.copyfile(en/name,ROOT/name)
for name in ['ts-fsrs.min.js','ts-fsrs.LICENSE']:shutil.copyfile(en/'vendor'/name,ROOT/'vendor'/name)
digests={'english':{f:hashlib.sha256((en/f).read_bytes()).hexdigest() for f in ['app.js','storage.js','srs.js','learning-plan.js','content.js','style.css','mascot.js']},'chinese':{f:hashlib.sha256((zh/'core'/f).read_bytes()).hexdigest() for f in ['speech.js','mic-meter.js','mic-worklet.js']}}
(ROOT/'docs/core-provenance.json').write_text(json.dumps(digests,indent=2)+'\n')
print('Generated core/app-core.js with asserted language hooks')
