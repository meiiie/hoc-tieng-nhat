#!/usr/bin/env python3
"""Synchronize visible/application versions without changing stored progress."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];v=sys.argv[1]
assert re.fullmatch(r'\d+\.\d+\.\d+',v)
p=ROOT/'version.json';data=json.loads(p.read_text());old=data['version'];data['version']=v;p.write_text(json.dumps(data,separators=(',',':'))+'\n')
for name in ['sw.js','lang-ja.js','README.md','docs/ECOSYSTEM.md']:
 p=ROOT/name;s=p.read_text()
 # Visible labels can lag version.json after an earlier release. Synchronize
 # their explicit contexts rather than assuming every label has the old version.
 s=re.sub(r'htn-v\d+\.\d+\.\d+',lambda _: 'htn-v'+v,s)
 s=re.sub(r'Phiên bản \d+\.\d+\.\d+',lambda _: 'Phiên bản '+v,s)
 s=re.sub(r'Phiên bản \*\*\d+\.\d+\.\d+\*\*',lambda _: 'Phiên bản **'+v+'**',s)
 p.write_text(s)
for name in ['package.json','package-lock.json']:
 p=ROOT/name;d=json.loads(p.read_text());d['version']=v
 if 'packages' in d:d['packages']['']['version']=v
 p.write_text(json.dumps(d,indent=2)+'\n')
