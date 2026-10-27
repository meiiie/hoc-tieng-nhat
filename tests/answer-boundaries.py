import sys as _s,os as _o;_s.path.insert(0,_o.path.dirname(__file__));from onboard import onboard
import os
PREFIX=os.environ.get("REPORT_PREFIX", "")
"""Exercise the production answer adapter, including a terminal small tsu."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,sys
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8931/"
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ.get('REPORT_DIR',ROOT.parent/'reports'));OUT.mkdir(parents=True,exist_ok=True);rows=[]
with sync_playwright() as p:
 for name in ['chromium','webkit']:
  b=getattr(p,name).launch();pg=b.new_page();pg.goto(BASE);pg.wait_for_selector('#nm')
  pg.evaluate('Promise.all([JaData.loadLevel(3),JaData.loadLevel(4)])')
  r=pg.evaluate("()=>{const w=words.find(w=>w.kanji==='あっ'),ts=accepts(w);return {romaji:w.romaji,correct:checkAns('axtsu',ts).ok,wrong:checkAns('a',ts).ok,boundary:JaKana.soundKey('しんよう')!==JaKana.soundKey('しにょう')}}")
  assert r['romaji']=='axtsu' and r['correct'] and not r['wrong'] and r['boundary']
  reviewed=pg.evaluate("()=>{const w=byId('j5b21d92a7eee'),c=LANG.cloze(w),ts=LANG.clozeTargets(w,c);return {surface:c.ans,correct:LANG.checkAns(c.ans,ts).ok,romaji:LANG.checkAns('goranninarimasu',ts).ok,dictionary:LANG.checkAns(w.kana,ts).ok}}")
  assert reviewed['surface']=='ごらんになります' and reviewed['correct'] and reviewed['romaji'] and not reviewed['dictionary'],reviewed
  rows.append({'browser':name,'passed':4,'failed':0,**r,'reviewedInflection':reviewed});b.close()
(OUT/(PREFIX+'answer-boundaries.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps(rows,ensure_ascii=False))
