import sys as _s,os as _o;_s.path.insert(0,_o.path.dirname(__file__));from onboard import onboard
import os
PREFIX=os.environ.get("REPORT_PREFIX", "")
"""Reproducible 390 × 844 touch screenshots; synthetic study fixture only."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT.parent/'screenshots';OUT.mkdir(exist_ok=True)
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8931/'
shots=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 ctx=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True,is_mobile=True,reduced_motion='reduce')
 page=ctx.new_page();page.goto(BASE);onboard(page);page.wait_for_selector('.v-home')
 page.evaluate("S.set.autoplay=false;S.set.gtip=true;S.set.furigana='on';S.set.romaji='off';S.user.name='';save()")
 word=page.evaluate("words.find(w=>w.kanji==='学校').id")
 def go(route):
  page.goto(BASE+'#/'+route);page.wait_for_selector('.view');page.evaluate('route()');page.wait_for_timeout(250)
 def shot(name):
  page.evaluate('document.fonts.ready');page.evaluate("document.querySelector('#toast').classList.remove('on');document.activeElement?.blur();window.scrollTo(0,0)")
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.screenshot(path=str(OUT/(PREFIX+name)),animations='disabled');shots.append(str(OUT/(PREFIX+name)))
 for theme in ['light','dark']:
  page.evaluate("theme=>{S.set.theme=theme;S.set.f={cefr:'N5'};S.star={};S.srs={};S.sess={};S.introductions={};S.bury=null;S.studyDay=null;FC=null;applyTheme();save()}",theme)
  go('');shot(f'{theme}-home.png')
  go('kana');shot(f'{theme}-kana.png')
  page.evaluate("id=>{S.star={[id]:true};S.set.f={cefr:'N5',star:true};S.sess={};save()}",word)
  go('review');page.wait_for_selector('.fc');shot(f'{theme}-review-front.png')
  page.click('#show');page.wait_for_selector('.fc.flip');shot(f'{theme}-review-back.png')
  page.locator('.face.b .ja-example-source summary').click();page.locator('.face.b .ja-example').scroll_into_view_if_needed();shot(f'{theme}-review-example.png')
  page.evaluate("S.set.f={cefr:'N5'};S.star={};save()")
  go('write?w='+word);page.wait_for_selector('.stroke-path');shot(f'{theme}-stroke-order.png')
  go('speak?w='+word);page.wait_for_selector('.pitch-svg');shot(f'{theme}-pitch-practice.png')
  go('list');page.wait_for_selector('.it');shot(f'{theme}-word-list.png')
  go('');page.click('#settings');page.wait_for_selector('#sheet:not(.hidden)');shot(f'{theme}-settings.png');page.keyboard.press('Escape')
 ctx.close();browser.close()
(OUT/(PREFIX+'screenshots.json')).write_text(json.dumps({'viewport':{'width':390,'height':844},'scale':2,'files':shots},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(shots,ensure_ascii=False,indent=2))
