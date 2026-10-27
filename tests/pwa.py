import os
PREFIX=os.environ.get("REPORT_PREFIX", "")
"""Install, update and offline gates at root and GitHub Pages paths, in both engines."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,threading,traceback,re,sys
BASE=sys.argv[1] if len(sys.argv)>1 else None
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT.parent/'reports'
SW=(ROOT/'sw.js').read_text();CURRENT=re.search(r"const V='([^']+)'",SW)[1];NEXT=CURRENT+'-test-update';STATE={'next':False,'fail':False}
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*_):pass
 def translate_path(self,path):
  if path.startswith('/hoc-tieng-nhat/'):path=path[len('/hoc-tieng-nhat'):]
  return super().translate_path(path)
 def do_GET(self):
  if self.path.endswith('/sw.js'):
   self.send_response(200);self.send_header('Content-Type','text/javascript');self.send_header('Cache-Control','no-store');self.end_headers()
   self.wfile.write((SW.replace(CURRENT,NEXT) if STATE['next'] else SW).encode())
  elif self.path.endswith('/ja-kana.js') and STATE['fail']:self.send_error(503)
  else:super().do_GET()
 def copyfile(self,source,output):
  try:super().copyfile(source,output)
  except (ConnectionAbortedError,ConnectionResetError,BrokenPipeError):pass

server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
try:
 with sync_playwright() as p:
  for kind in ['chromium','webkit']:
   browser=getattr(p,kind).launch()
   for path in ([BASE] if BASE else ['/','/hoc-tieng-nhat/']):
    STATE.update(next=False,fail=False);checks=[]
    context=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
    page=context.new_page();base=BASE or f'http://127.0.0.1:{server.server_port}'+path
    try:
     page.goto(base);page.wait_for_selector('[data-start="n5"]');page.click('[data-start="n5"]');page.wait_for_selector('.v-home')
     page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller')
     manifest=page.evaluate("fetch('manifest.webmanifest').then(r=>r.json())")
     assert manifest['start_url']==manifest['scope']==manifest['id']=='./';assert manifest['lang']=='vi'
     assert page.evaluate("navigator.serviceWorker.getRegistration().then(r=>r.scope)")==base
     if kind=='chromium':
      session=context.new_cdp_session(page);m=session.send('Page.getAppManifest');assert not m.get('errors'),m
      assert not session.send('Page.getInstallabilityErrors')['installabilityErrors']
     checks.append('relative manifest and scope; Chromium CDP installability' if kind=='chromium' else 'relative manifest and scope in WebKit')
     if not BASE:
      page.evaluate("async()=>{S.notes.upgrade='giữ lại';S.srs.fixture={state:'review',due:4102444800000,int:30,s:31.5,d:4.2,reps:4,lapses:0};await save();for(const name of ['another-app','htv-v24','htt-v5.0.0','htn-v0.9.0','htn-data-v0'])await (await caches.open(name)).put('sentinel',new Response('keep'))}")
      progress=page.evaluate('JSON.stringify([S.srs,S.notes])')
      STATE.update(next=True,fail=True)
      page.evaluate("""async()=>{
       const r=await navigator.serviceWorker.getRegistration();
       const end=new Promise(ok=>r.addEventListener('updatefound',()=>{
        const w=r.installing;w.addEventListener('statechange',()=>{if(w.state==='redundant')ok()});
       },{once:true}));await r.update();await end;
      }""")
      assert page.evaluate('navigator.serviceWorker.getRegistration().then(r=>!r.waiting)')
      assert page.evaluate('JSON.stringify([S.srs,S.notes])')==progress
      context.set_offline(True);page.reload();page.wait_for_selector('.v-home');assert page.evaluate('words.length')==8344;context.set_offline(False)
      checks.append('failed shell install leaves previous app usable offline')
      STATE['fail']=False
      page.evaluate('navigator.serviceWorker.getRegistration().then(r=>r.update())')
      page.wait_for_function('navigator.serviceWorker.getRegistration().then(r=>!!r.waiting)')
      assert page.evaluate("v=>caches.keys().then(k=>k.includes(v))",CURRENT)
      page.wait_for_selector('#toast .tact');assert page.locator('#toast .tact').inner_text()=='Tải lại'
      with page.expect_navigation(wait_until='domcontentloaded'):page.click('#toast .tact')
      page.wait_for_function("([old,next])=>caches.keys().then(k=>k.includes(next)&&!k.includes(old))",arg=[CURRENT,NEXT])
      page.wait_for_selector('.v-home');assert page.evaluate('JSON.stringify([S.srs,S.notes])')==progress
      checks.append('complete update waits for Tải lại and preserves progress')
      keys=page.evaluate('caches.keys()');assert 'htn-v0.9.0' not in keys and 'htn-data-v0' not in keys
      for name in ['another-app','htv-v24','htt-v5.0.0']:
       assert page.evaluate("name=>caches.open(name).then(c=>c.match('sentinel')).then(r=>r.text())",name)=='keep'
      checks.append('activation removes own obsolete caches and retains other apps')
     audio=page.evaluate('words.find(w=>w.audio).audio')
     assert page.evaluate("async url=>{const r=await fetch(url);return r.ok&&(await r.arrayBuffer()).byteLength>256}",audio)
     assert page.evaluate("fetch('data/strokes/05b66.svg').then(r=>r.ok)")
     page.wait_for_function("async url=>!!(await (await caches.open('htn-audio-v1')).match(url))",arg=audio)
     context.set_offline(True);page.reload();page.wait_for_selector('.v-home')
     assert page.evaluate('words.length')==8344
     files=['core/mic-worklet.js','core/mic-meter.js','ja-pitch-worker.js','ja-engine.js','icons/maskable-192.png','icons/maskable-512.png','data/n1.json','data/kana.json','data/strokes/05b66.svg',audio]
     assert all(page.evaluate("files=>Promise.all(files.map(async file=>{const r=await fetch(file);return r.ok&&(await r.arrayBuffer()).byteLength>0}))",files))
     checks.append('offline shell, five levels, workers, icons and previously cached audio/strokes')
     row={'browser':kind,'path':path,'passed':len(checks),'failed':0,'checks':checks}
    except Exception as e:
     traceback.print_exc();row={'browser':kind,'path':path,'passed':len(checks),'failed':1,'checks':checks,'error':str(e)}
    finally:context.close()
    results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
   browser.close()
finally:server.shutdown();server.server_close()
(OUT/(PREFIX+'pwa.json')).write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(1 if any(r['failed'] for r in results) else 0)
