"""WebKit engine check (closest available to iPhone Safari): load the 63 MB model in the worker and score Nanami recordings."""
import sys,json,os
from playwright.sync_api import sync_playwright
sys.path.insert(0,os.path.dirname(__file__));from onboard import onboard
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8955/'
with sync_playwright() as p:
 b=p.webkit.launch();pg=b.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
 pg.goto(BASE);onboard(pg)
 r=pg.evaluate("""async()=>{const t0=performance.now();await Speech.load(()=>{});const loadMs=performance.now()-t0;const out={loadMs:Math.round(loadMs)};
  for(const [kana,src] of [['がっこう','j42edc1b83779'],['せんせい','j497356cf0646']]){const w=words.find(x=>x.id===src);const pcm=await Speech.decodeUrl(w.audio);
   const a=await Speech.analyze(pcm.slice(),{kana:'がっこう',accent:0});out[w.kana]={score:a.score,ms:a.ms,heard:a.heard}}return out}""")
 print(json.dumps({**r,'errors':errs},ensure_ascii=False))
 assert r['がっこう']['score']>=80 and r['せんせい']['score']<60 and not errs
