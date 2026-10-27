"""Chromium fake-microphone check of on-device mora scoring: the Nanami recording of the shown word should score high,
   a different word's recording should score low. Downloads the 63 MB model once into a persistent profile."""
import sys,json,tempfile,os
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,os.path.dirname(__file__));from onboard import onboard
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8955/'
WORD='j42edc1b83779';ROOT=Path(__file__).resolve().parents[1];FAKE=ROOT.parent/'fakemic'
PROFILE=os.environ.get('PRON_PROFILE',str(ROOT.parent/'.pron-profile'))
out={}
with sync_playwright() as p:
 for label,wav in [('same',WORD),('other','j497356cf0646')]:
  ctx=p.chromium.launch_persistent_context(PROFILE,headless=True,args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream',f'--use-file-for-fake-audio-capture={FAKE/(wav+".wav")}'],viewport={'width':390,'height':844},is_mobile=True,has_touch=True,permissions=['microphone'])
  print('RUN',label,flush=True);pg=ctx.pages[0] if ctx.pages else ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.goto(BASE);pg.wait_for_selector('.view')
  if pg.locator('#nm').count():onboard(pg)
  pg.wait_for_function('typeof words!=="undefined"&&words.length>0');pg.goto(BASE+'#/speak?w='+WORD);pg.wait_for_timeout(500);pg.evaluate('route()');pg.wait_for_selector('#sarea',timeout=60000);pg.wait_for_timeout(1500)
  if pg.locator('#dlm').count():pg.click('#dlm');pg.wait_for_selector('#sarea[data-state="ready"]',timeout=600000)
  pg.click('#mic');pg.wait_for_selector('#sarea[data-state="scored"], #sarea[data-state="result"], #sarea[data-state="error"]',timeout=60000)
  st=pg.get_attribute('#sarea','data-state');score=pg.locator('.score b').inner_text() if st=='scored' else None
  chips=pg.eval_on_selector_all('.mora-chip','e=>e.map(x=>x.textContent+":"+x.className.split(" ").pop())')
  pg.add_script_tag(path=str(ROOT/'node_modules/axe-core/axe.min.js'));ax=pg.evaluate("axe.run(document).then(r=>r.violations.map(v=>v.id))")
  out[label]={'axe':ax,'state':st,'score':score and int(score),'chips':chips,'errors':errs}
  if label=='same':pg.screenshot(path=str(ROOT.parent/'screenshots'/'pron-scored-same.png'),full_page=True)
  else:pg.screenshot(path=str(ROOT.parent/'screenshots'/'pron-scored-other.png'),full_page=True)
  ctx.close()
print(json.dumps(out,ensure_ascii=False))
assert out['same']['score']>=80 and out['other']['score']<60 and not out['same']['errors'] and not out['same']['axe'] and not out['other']['axe'],out
