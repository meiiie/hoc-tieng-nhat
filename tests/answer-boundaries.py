import os
PREFIX=os.environ.get("REPORT_PREFIX", "")
"""Exercise the production answer adapter, including a terminal small tsu."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,sys
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8931/"
ROOT=Path(__file__).resolve().parents[1];rows=[]
with sync_playwright() as p:
 for name in ['chromium','webkit']:
  b=getattr(p,name).launch();pg=b.new_page();pg.goto(BASE);pg.wait_for_selector('[data-start="n5"]')
  r=pg.evaluate("()=>{const w=words.find(w=>w.kanji==='あっ'),ts=accepts(w);return {romaji:w.romaji,correct:checkAns('axtsu',ts).ok,wrong:checkAns('a',ts).ok,boundary:JaKana.soundKey('しんよう')!==JaKana.soundKey('しにょう')}}")
  assert r['romaji']=='axtsu' and r['correct'] and not r['wrong'] and r['boundary'];rows.append({'browser':name,'passed':3,'failed':0,**r});b.close()
(ROOT.parent/'reports'/(PREFIX+'answer-boundaries.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps(rows,ensure_ascii=False))
