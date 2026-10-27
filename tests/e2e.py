import sys as _s,os as _o;_s.path.insert(0,_o.path.dirname(__file__));from onboard import onboard
import os
PREFIX=os.environ.get("REPORT_PREFIX", "")
"""Neko Japanese browser gates, adapted from the Chinese browser suite.
Serve: python3 -m http.server 8931; run: python3 tests/e2e.py http://localhost:8931/ all
"""
import sys,json,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8931/'
WHICH=sys.argv[2] if len(sys.argv)>2 else 'all'
ROOT=Path(__file__).resolve().parents[1];REPORTS=ROOT.parent/'reports';REPORTS.mkdir(exist_ok=True)
AXE=(ROOT/'node_modules/axe-core/axe.min.js').read_text()
results={}
def run(kind):
 checks=[];errors=[];violations={};audio_requests=[];audio_levels=[]
 with sync_playwright() as p:
  browser=getattr(p,kind).launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--autoplay-policy=no-user-gesture-required'] if kind=='chromium' else [])
  ctx=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,reduced_motion='reduce')
  if kind=='chromium':ctx.grant_permissions(['microphone'])
  pg=ctx.new_page();pg.on('pageerror',lambda e:errors.append(str(e)));pg.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  pg.on('request',lambda request:audio_requests.append(request.url) if '/audio/' in request.url else None)
  E=pg.evaluate
  def ok(name):checks.append(name);print(kind,'PASS',name,flush=True)
  def go(route=''):
   target=BASE+('#/'+route if route else '')
   if pg.url==target:pg.reload()
   else:pg.goto(target)
   pg.wait_for_selector('.view');pg.wait_for_timeout(180)
  def settle():
   E("Promise.all(document.getAnimations().filter(a=>a.effect?.getComputedTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{})))")
  try:
   go();pg.wait_for_selector('#nm');E('navigator.serviceWorker.ready');assert not audio_requests,'audio must not be in the shell'
   for theme in ['light','dark']:
    E("theme=>{S.set.theme=theme;applyTheme()}",theme);E(AXE);bad=E("axe.run(document).then(r=>r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})))")
    if bad:violations[theme+':onboarding']=bad
   E("S.set.theme='light';applyTheme()");onboard(pg,'kana','Bạn');pg.wait_for_selector('.kana-grid');assert E('S.user.style')=='cards' and E('S.user.start')=='kana';ok('onboarding starts with kana and a five-word goal')
   assert E('S.user.goal')=='5'
   pg.locator('.kana-cell').first.click();pg.wait_for_selector('.kana-detail');snap=E('JSON.stringify(S.srs)');pg.click('#kana-quiz');pg.locator('[data-option]').first.click();pg.wait_for_selector('#kana-next');assert E('S.kanaPractice.answered')==1;assert E('JSON.stringify(S.srs)')==snap;ok('kana tables, playback, quiz and practice isolation')
   go('kana');pg.click('[data-script="katakana"]');assert pg.locator('.kana-cell b').first.inner_text()=='ア'
   pg.click('[data-group="dakuten"]');assert pg.locator('.kana-cell').count()==25;pg.click('[data-group="yoon"]');assert pg.locator('.kana-cell').count()==36
   pg.click('[data-script="hiragana"]');assert pg.locator('.kana-cell b').first.inner_text()=='きゃ';ok('both kana scripts and dakuten/yoon groups')
   go();pg.wait_for_selector('.v-home');E('S.set.autoplay=false;save()');assert E('deck().every(w=>w.level===5)');pg.click('[data-jlpt="4"]');pg.wait_for_selector('#early-open');assert 'N4' in pg.text_content('#sheet');pg.click('#early-open');assert E('S.jaUnlocked[4]');ok('manual early level unlock')
   E("S.set.f={cefr:'N5'};S.jaUnlocked={5:true};S.srs={};S.introductions={};S.sess={};save()")
   go('review');pg.wait_for_selector('.fc');assert pg.locator('.face.f ruby rt').count()>0;before=E('JSON.stringify(S.srs)');pg.click('#show');pg.wait_for_selector('#gr:not(.hidden)');pg.click('[data-g="3"]');pg.wait_for_timeout(250);assert E('JSON.stringify(S.srs)')!=before;pg.click('#undo');assert E('JSON.stringify(S.srs)')==before;ok('scheduled rating and undo restore exact card state')
   pg.locator('[data-g="3"]').click();pg.wait_for_timeout(150);awaited=E('save().then(()=>JSON.stringify(S.srs))');pg.reload();pg.wait_for_selector('.fc');assert E('JSON.stringify(S.srs)')==awaited;ok('IndexedDB reload persistence')
   E("S.srs={};S.sess={};S.introductions={};S.studyDay=null;S.bury=null;FC=null;save()")
   go('review');before=E('JSON.stringify(S.srs)')
   def drag(dx,dy):
    box=pg.locator('.fc').bounding_box();x=box['x']+90;y=box['y']+110
    pg.dispatch_event('.fc','pointerdown',{'pointerId':9,'pointerType':'touch','clientX':x,'clientY':y,'buttons':1})
    pg.dispatch_event('.fc','pointermove',{'pointerId':9,'pointerType':'touch','clientX':x+dx,'clientY':y+dy,'buttons':1})
    pg.dispatch_event('.fc','pointerup',{'pointerId':9,'pointerType':'touch','clientX':x+dx,'clientY':y+dy,'buttons':0})
    pg.wait_for_timeout(550)
   drag(2,100);assert not pg.locator('.fc').evaluate("e=>e.classList.contains('flip')");assert E('JSON.stringify(S.srs)')==before
   drag(150,0);pg.wait_for_selector('.fc.flip');assert E('JSON.stringify(S.srs)')==before
   drag(150,0);assert E('JSON.stringify(S.srs)')!=before;pg.click('#undo');assert E('JSON.stringify(S.srs)')==before;ok('touch scroll does not flip; front swipe reveals; back swipe rates; undo restores')
   go();pg.click('#settings');pg.wait_for_selector('#sheet:not(.hidden)');pg.wait_for_timeout(100)
   assert E("document.activeElement.classList.contains('sheet-close')&&document.querySelector('main').inert")
   pg.keyboard.press('Shift+Tab');assert E("document.activeElement.closest('#sheet')!==null")
   pg.keyboard.press('Escape');assert E("document.activeElement.id==='settings'&&!document.querySelector('main').inert");ok('sheets trap focus, close by keyboard and restore header focus')
   go('settings');pg.wait_for_selector('#sheet:not(.hidden)');pg.click('.sheet-close');pg.wait_for_function("location.hash==='#/'&&document.querySelector('#sheet').classList.contains('hidden')");ok('direct settings route opens and closes to home')
   pg.click('#settings')
   with pg.expect_download() as download:pg.click('#exp')
   exported=json.loads(Path(download.value.path()).read_text());assert exported['app']=='hoc-tieng-nhat';assert exported['schema']==11
   original=exported['data']['srs'];E("S.notes.backupFixture='before import';save()")
   pg.on('dialog',lambda dialog:dialog.accept())
   pg.set_input_files('#impf',{'name':'neko.json','mimeType':'application/json','buffer':json.dumps(exported).encode()});pg.wait_for_selector('#sheet.hidden',state='attached')
   assert E('JSON.stringify(S.srs)')==json.dumps(original,separators=(',',':'))
   assert E("Object.keys(localStorage).filter(k=>k.startsWith('htn-core-before-import-')).some(k=>JSON.parse(localStorage[k]).notes.backupFixture==='before import')")
   pg.click('#settings');safe=E('JSON.stringify(S.srs)')
   for payload in ['{broken',json.dumps({'app':'hoc-tu-vung','data':exported['data']})]:
    pg.set_input_files('#impf',{'name':'invalid.json','mimeType':'application/json','buffer':payload.encode()});pg.wait_for_timeout(150);assert E('JSON.stringify(S.srs)')==safe
   pg.keyboard.press('Escape');pg.reload();pg.wait_for_selector('.v-home');assert E('JSON.stringify(S.srs)')==safe;ok('JSON export/import, pre-import snapshot and rejected malformed or other-app backups')
   # Exercise Settings against a real, filtered one-word set at every available MP3 level.
   audio_snap=E('JSON.stringify(S.srs)')
   for level in [5,4,3,2,1]:
    sample=E("n=>words.find(w=>w.level===n&&w.audio)||null",level)
    if not sample:continue
    E("async w=>{S.jaUnlocked[w.level]=true;S.star={[w.id]:true};S.set.f={cefr:'N'+w.level,star:true};FC=null;await (await caches.open('htn-audio-v1')).delete(w.audio);await save()}",sample)
    go('settings');pg.wait_for_selector('#dl');pg.click('#dl')
    pg.wait_for_function("document.querySelector('#dlst').textContent==='Đã lưu 1/1 tệp âm thanh'&&!document.querySelector('#dl').disabled")
    assert E("async url=>!!(await (await caches.open('htn-audio-v1')).match(url))",sample['audio'])
    pg.keyboard.press('Escape');audio_levels.append(level)
   assert E('JSON.stringify(S.srs)')==audio_snap
   E("S.star={};S.set.f={cefr:'N5'};FC=null;save()")
   ok('audio stays lazy; Settings downloads/cache preserve progress at every available level')
   # Isolate practice from the scheduled fixture; the English failure-forward exception is tested below.
   E("S.srs={};S.sess={};S.introductions={};S.studyDay=null;S.bury=null;FC=null;save()")
   snapshot=E('JSON.stringify(S.srs)')
   go('cards');pg.wait_for_selector('.fc');pg.click('#nK');pg.wait_for_timeout(300);pg.click('#nL');pg.wait_for_timeout(300)
   go('learn');pg.wait_for_selector('.opt');pg.locator('.opt').first.click();pg.wait_for_selector('#nx')
   go('listen');pg.wait_for_selector('#ti');pg.fill('#ti','xyz');pg.click('#ck');pg.wait_for_selector('#nx')
   go('test');pg.wait_for_selector('#sub');pg.click('#sub');pg.wait_for_selector('#rt')
   go('match');pg.click('#go');pg.wait_for_selector('.tile');tiles=E("Array.from(document.querySelectorAll('.tile')).map((x,i)=>({i,text:x.textContent}))");pg.locator('.tile').nth(0).click();pg.locator('.tile').nth(1).click()
   go('cram');pg.wait_for_selector('.fc');pg.click('#show');pg.click('[data-g="3"]');pg.wait_for_timeout(180)
   assert E('JSON.stringify(S.srs)')==snapshot;assert E('Object.values(S.ev).flat().length')>3;ok('cards, learn, listen, test, match and cram keep SRS byte-identical')
   # Exercise the real core cloze step and each source label with released examples.
   for mode in ['direct','pivot','machine']:
    fixture=E("mode=>{const w=words.find(w=>w.level===5&&w.example&&(mode==='machine'?w.example.translation.machine:mode==='pivot'?w.example.translation.pivot:!w.example.translation.machine&&!w.example.translation.pivot));S.star={[w.id]:true};S.set.f={cefr:'N5',star:true};S.srs={};S.introductions={};S.studyDay=null;S.bury=null;S.sess={};FC=null;save();return w}",mode)
    go('review');pg.click('#show');pg.wait_for_selector('.fc.flip .ja-example')
    assert fixture['example']['text'] in pg.locator('.face.b .ja-example').inner_text()
    expected={'direct':'bản dịch tiếng Việt trên Tatoeba','pivot':'dịch qua câu tiếng Anh','machine':'bản dịch máy, cần kiểm tra'}[mode]
    assert expected in pg.locator('.face.b .ja-example').inner_text()
    pg.locator('.face.b .ja-example-source summary').click()
    assert pg.locator('.face.b .ja-example-source a').first.get_attribute('href')==fixture['example']['url']
   E("id=>{S.learn={[id]:2};S.sess={};save()}",fixture['id'])
   go('learn');pg.wait_for_selector('.cloze .gap');assert 'bản dịch máy, cần kiểm tra' in pg.text_content('main')
   pg.fill('#ti',fixture['kana']);pg.click('#ck');pg.wait_for_selector('#fb .fb.ok')
   assert E('id=>S.learn[id]',fixture['id'])==3;assert E('JSON.stringify(S.srs)')=='{}'
   ok('attributed direct/pivot/machine examples and exact cloze preserve scheduled progress')
   forward=E("(()=>{const w=words.find(w=>w.level===5);S.star={[w.id]:true};S.set.f={cefr:'N5',star:true};S.srs[w.id]={...SRS.fresh(),state:'review',s:31,d:4,int:30,due:SRS.dayAt(Date.now(),20),last:Date.now(),reps:4};FC=null;S.sess={};save();return w.id})()")
   go('cards');pg.click('#nL');pg.wait_for_timeout(300);assert E('id=>S.srs[id].due===SRS.dayAt(Date.now(),1)&&S.srs[id].s===31&&S.srs[id].int===30',forward);ok('English failed-recall exception advances due date without changing memory state')
   E("S.set.f={cefr:'N5'};S.star={};S.sess={};S.srs={};S.introductions={};S.bury=null;save()")
   E("(()=>{const xs=words.filter(w=>w.level===5);for(const w of xs.slice(0,Math.ceil(xs.length*.8)))S.srs[w.id]={...SRS.fresh(),state:'review',s:3,d:4,due:Date.now()+86400000};S.jaUnlocked={5:true};LANG._unlock()})()")
   assert E('S.jaUnlocked[4]');ok('80 percent graduated automatically unlocks N4')
   E("S.srs={};S.introductions={};S.sess={};S.set.f={cefr:'N5'};save()")
   word=E("words.find(w=>w.kanji==='学校').id")
   go('write?w='+word);pg.wait_for_selector('#stroke-box svg path.stroke-path');assert pg.locator('.stroke-path').count()>=5;pg.click('#trace');pg.wait_for_selector('.stroke-path.target');assert 'Viết nét' in pg.text_content('#stroke-status');ok('KanjiVG animation and tracing mode render')
   # Trace every stroke with touch pointer events along the authored path.
   count=pg.locator('.stroke-path').count()
   for i in range(count):
    pts=E("i=>{const svg=document.querySelector('#stroke-box svg'),p=svg.querySelectorAll('.stroke-path')[i],m=svg.getScreenCTM();return Array.from({length:45},(_,k)=>{const q=p.getPointAtLength(k*p.getTotalLength()/44),v=svg.createSVGPoint();v.x=q.x;v.y=q.y;const z=v.matrixTransform(m);return {x:z.x,y:z.y}})}",i)
    # Synthetic pointers cannot capture; dispatch to the SVG throughout.
    E("document.querySelector('#stroke-box svg').setPointerCapture=()=>{}")
    pg.dispatch_event('#stroke-box svg','pointerdown',{'pointerId':1,'pointerType':'touch','clientX':pts[0]['x'],'clientY':pts[0]['y'],'buttons':1})
    for point in pts[1:-1]:pg.dispatch_event('#stroke-box svg','pointermove',{'pointerId':1,'pointerType':'touch','clientX':point['x'],'clientY':point['y'],'buttons':1})
    pg.dispatch_event('#stroke-box svg','pointerup',{'pointerId':1,'pointerType':'touch','clientX':pts[-1]['x'],'clientY':pts[-1]['y'],'buttons':0})
   assert 'Đã viết xong' in pg.text_content('#stroke-status');assert E('JSON.stringify(S.srs)')=='{}';ok('touch tracing completes strokes and preserves SRS')
   go('speak?w='+word);pg.wait_for_selector('.pitch-svg');assert 'mora' in pg.text_content('main');pg.click('#mora-play');pg.wait_for_selector('.mora-row .beat');ok('pitch pattern and timed mora practice')
   if kind=='chromium':
    pg.click('#mic');pg.wait_for_selector('[data-state="rec"]');pg.wait_for_function("['result','error'].includes(document.querySelector('#sarea').dataset.state)",timeout=18000);assert 'ước lượng' in pg.text_content('#sarea') or 'Chưa nhận' in pg.text_content('#sarea');assert pg.locator('.score').count()==0;ok('fake microphone capture, honest estimate or abstention')
   E("window.savedMedia=navigator.mediaDevices;Object.defineProperty(navigator,'mediaDevices',{value:undefined,configurable:true});route()")
   assert 'Micro chưa khả dụng' in pg.text_content('#sarea');assert pg.locator('#mic').count()==0;assert pg.locator('#mora-play').is_enabled()
   E("Object.defineProperty(navigator,'mediaDevices',{value:window.savedMedia,configurable:true});delete window.savedMedia;route()");ok('no-microphone fallback retains listening and mora practice')
   # Check the actual dictionary credit, variant selector, and unresolved fallback.
   pitch_snapshot=E('JSON.stringify(S.srs)')
   added=E("words.find(w=>w.pitchSource==='unidic-2.1.2'&&w.pitch.length>1)")
   assert added
   go('speak?w='+added['id']);pg.wait_for_selector('.pitch-svg');assert 'UniDic 2.1.2' in pg.text_content('.ja-pitch-source')
   old_points=pg.locator('.pitch-svg polyline').get_attribute('points');pg.select_option('#accent',str(added['pitch'][-1]));assert pg.locator('.pitch-svg polyline').get_attribute('points')!=old_points
   missing=E('words.find(w=>w.pitch===null).id');go('speak?w='+missing);assert pg.locator('.pitch-svg').count()==0;assert 'Chưa có nguồn' in pg.text_content('.ja-pitch-source');assert 'Kanjium' not in pg.text_content('.ja-pitch-source')
   assert E('JSON.stringify(S.srs)')==pitch_snapshot
   ok('licensed pitch sources, variants and missing-accent fallback render honestly')
   go('review');pg.wait_for_selector('.fc');pg.click('#voice');assert pg.locator('.fc ruby').count()==0;pg.click('#voice');assert pg.locator('.fc ruby').count()>0;ok('furigana toggle on both card faces')
   go();pg.click('#settings');pg.wait_for_selector('#sheet:not(.hidden)');pg.click('[data-set="romaji"][data-v="on"]');pg.keyboard.press('Escape');go('review');pg.wait_for_selector('.ja-romaji');ok('romaji settings toggle')
   # Full route accessibility in both themes, including transient sheets and the back face.
   for theme in ['light','dark']:
    E("theme=>{S.set.theme=theme;save();applyTheme()}",theme)
    for route in ['', 'kana','review','cards','learn','hard','listen','match','test','cram','write?w='+word,'speak?w='+word,'list','stats']:
     
     if route=='review':E("if(S.sess?.review)S.sess.review.flipped=false;save()")
     go(route);settle();assert E('document.documentElement.scrollWidth<=innerWidth'),(theme,route,'horizontal overflow');E(AXE)
     bad=E("axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}).then(r=>r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})))")
     if bad:violations[theme+':'+route]=bad
     if route=='review':
      pg.click('#show');settle();bad=E("axe.run(document).then(r=>r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})))")
      if bad:violations[theme+':review-back']=bad
      pg.locator('.face.b .ja-example-source summary').click();settle();bad=E("axe.run(document).then(r=>r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})))")
      if bad:violations[theme+':example-attribution']=bad
    go('settings');settle();E(AXE);bad=E("axe.run(document).then(r=>r.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})))")
    if bad:violations[theme+':settings']=bad
    pg.keyboard.press('Escape')
   (REPORTS/f'{PREFIX}axe-{kind}.json').write_text(json.dumps(violations,ensure_ascii=False,indent=2)+'\n');assert not violations,json.dumps(violations,ensure_ascii=False)[:2500];ok('axe clean: all routes and card backs, light and dark')
   go();E('navigator.serviceWorker.ready');pg.wait_for_function('!!navigator.serviceWorker.controller');saved=E('save().then(()=>JSON.stringify([S.srs,S.ev,S.pron]))')
   ctx.set_offline(True);pg.reload();pg.wait_for_selector('.v-home');assert E('words.length')>8000;assert E('JSON.stringify([S.srs,S.ev,S.pron])')==saved;go('kana');pg.wait_for_selector('.kana-grid');go('write?w='+word);pg.wait_for_selector('.stroke-path');ok('offline reload, all levels, kana and lazily cached strokes');ctx.set_offline(False)
   assert not errors,errors;ok('no page errors or console errors')
   oc=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True);op=oc.new_page();op.goto(BASE)
   op.wait_for_selector('#nm');assert op.locator('.seg i').count()==5
   op.fill('#nm','Darren');op.click('#nx');op.click('[data-start="n4"]');assert op.get_attribute('[data-start="n4"]','aria-checked')=='true'
   op.click('#back');assert op.input_value('#nm')=='Darren';op.click('#nx');assert op.get_attribute('[data-start="n4"]','aria-checked')=='true'
   op.click('#nx');op.click('[data-goal="10"]');op.click('#nx');op.click('[data-style="learn"]');op.click('#nx');op.wait_for_selector('.plan');op.click('#nx');op.wait_for_selector('.v-home')
   u=op.evaluate('({u:S.user,f:S.set.f,o:S.jaUnlocked,chip:document.querySelector("#filt").textContent.trim()})')
   assert u['u']['goal']=='10' and u['u']['style']=='learn' and u['f']=={'cefr':'N4'} and u['o'].get('4') and not u['o'].get('3') and u['chip']=='Chọn bộ từ',u
   oc.close();ok('five-step onboarding wizard: back keeps draft, N4 start unlocks N5+N4 only')
   # New contexts isolate schema fixtures from the established IndexedDB record.
   for fixture in ['migration','corrupt','newer','idb-corrupt']:
    fc=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True);fp=fc.new_page();fixture_errors=[];fp.on('pageerror',lambda e:fixture_errors.append(str(e)));fp.goto(BASE);fp.wait_for_selector('#nm')
    state={'v':7,'user':{'done':True,'goal':'5'},'set':{'autoplay':False,'f':{}},'srs':{'fixture':{'state':'review','due':4102444800000,'s':31,'d':4,'int':30}},'ev':{'fixture':[[123,'f',1]]},'revlog':[[123,'fixture',3,'review',30]],'notes':{'fixture':'giữ lại'}}
    if fixture=='newer':state['v']=99;state.pop('set')
    fp.evaluate("async s=>{const db=await new Promise(ok=>{const r=indexedDB.open('hoc-tieng-nhat',1);r.onsuccess=()=>ok(r.result)});await new Promise(ok=>{const t=db.transaction('progress','readwrite');t.objectStore('progress').clear();t.oncomplete=ok});db.close();localStorage.setItem('htn-core',JSON.stringify(s));localStorage.setItem('htv2','english');localStorage.setItem('htt-core','chinese')}",state)
    if fixture=='corrupt':fp.evaluate("s=>{localStorage.setItem('htn-core-bak',JSON.stringify(s));localStorage.setItem('htn-core','{broken')}",state)
    if fixture=='idb-corrupt':fp.evaluate("async s=>{const db=await new Promise(ok=>{const r=indexedDB.open('hoc-tieng-nhat',1);r.onsuccess=()=>ok(r.result)});await new Promise(ok=>{const t=db.transaction('progress','readwrite'),st=t.objectStore('progress');st.put('broken','current');st.put(s,'daily-backup');t.oncomplete=ok});db.close()}",state)
    fp.reload();fp.wait_for_selector('.view');fp.wait_for_timeout(250)
    assert fp.evaluate('JSON.stringify(S.srs)')==json.dumps(state['srs'],separators=(',',':'));assert fp.evaluate("S.notes.fixture")=='giữ lại';assert fp.evaluate("localStorage.getItem('htv2')")=='english';assert fp.evaluate("localStorage.getItem('htt-core')")=='chinese'
    if fixture=='newer':
     assert fp.evaluate('S.v')==99;assert fp.locator('#settings').is_disabled()
     assert fp.evaluate("JSON.parse(localStorage.getItem('htn-core'))")==state
     assert fp.evaluate("async()=>{await save();const db=await new Promise(ok=>{const r=indexedDB.open('hoc-tieng-nhat',1);r.onsuccess=()=>ok(r.result)});const value=await new Promise(ok=>{const r=db.transaction('progress').objectStore('progress').get('current');r.onsuccess=()=>ok(r.result)});db.close();return value}")==state
    elif fixture=='corrupt':assert fp.evaluate("Object.keys(localStorage).some(k=>k.startsWith('htn-core-corrupt-'))")
    elif fixture=='migration':assert fp.evaluate("!!localStorage.getItem('htn-core-pre-v7')")
    assert not fixture_errors,fixture_errors;ok(fixture+' preserves cards, notes and other applications');fc.close()
   return {'baseUrl':BASE,'version':E("fetch('version.json').then(r=>r.json()).then(v=>v.version)"),'audioLevelsTested':audio_levels,'passed':len(checks),'failed':0,'checks':checks,'consoleErrors':errors,'axeViolations':violations}
  except Exception as e:
   traceback.print_exc();pg.screenshot(path=str(REPORTS/f'{PREFIX}failure-{kind}.png'),full_page=True);return {'baseUrl':BASE,'audioLevelsTested':audio_levels,'passed':len(checks),'failed':1,'checks':checks,'error':str(e),'consoleErrors':errors,'axeViolations':violations}
  finally:browser.close()
for kind in (['chromium','webkit'] if WHICH=='all' else [WHICH]):results[kind]=run(kind)
(REPORTS/(PREFIX+'e2e.json')).write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:{'passed':v['passed'],'failed':v['failed']} for k,v in results.items()}),flush=True)
sys.exit(1 if any(v['failed'] for v in results.values()) else 0)
