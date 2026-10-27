import os
PREFIX=os.environ.get("REPORT_PREFIX", "")
"""Measure the actual home after onboarding, keeping the installed service worker.
Lighthouse 13 no longer has PWA; 11.7.1 is used only for that legacy category.
"""
import json,os,subprocess,tempfile,sys
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8931/"
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT.parent/'reports'
with tempfile.TemporaryDirectory(prefix="neko-lighthouse-") as profile, sync_playwright() as p:
 ctx=p.chromium.launch_persistent_context(profile,headless=True,args=['--remote-debugging-port=9225','--no-sandbox'],viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 page=ctx.pages[0];page.goto(BASE);page.wait_for_selector('.view')
 if page.locator('[data-start="n5"]').count():page.click('[data-start="n5"]')
 page.wait_for_selector('.v-home');page.evaluate("S.set.theme='light';S.set.autoplay=false;save()");page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller')
 cases=[('lighthouse','lighthouse-current','performance,accessibility,best-practices'),(str(ROOT/'.cache/lighthouse11/node_modules/.bin/lighthouse'),'lighthouse-pwa-legacy','pwa,accessibility')]
 env={**os.environ,'CHROME_PATH':p.chromium.executable_path}
 summary={}
 for cmd,name,categories in cases:
  name=PREFIX+name
  with (OUT/(name+'.log')).open('w') as log:
   run=subprocess.run([cmd,BASE,'--port=9225','--disable-storage-reset','--only-categories='+categories,'--output=json','--output=html','--output-path='+str(OUT/name),'--quiet'],stdout=log,stderr=subprocess.STDOUT,timeout=200,env=env)
  path=OUT/(name+'.report.json')
  if run.returncode or not path.exists():raise RuntimeError((name,run.returncode,(OUT/(name+'.log')).read_text()[-2500:]))
  r=json.loads(path.read_text());summary[name]={'version':r['lighthouseVersion'],'chromePath':env['CHROME_PATH'],'url':r['finalDisplayedUrl'] if 'finalDisplayedUrl' in r else r['finalUrl'],'scores':{k:round(v['score']*100) for k,v in r['categories'].items()},'warnings':r.get('runWarnings',[])}
  print(json.dumps(summary[name]),flush=True)
 (OUT/(PREFIX+'lighthouse-summary.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');ctx.close()
