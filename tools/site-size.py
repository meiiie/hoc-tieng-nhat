#!/usr/bin/env python3
"""Conservative Pages payload: all Git-tracked/non-ignored release files, no .git/cache.
Use only after generation has finished, so no temporary audio files are present.
"""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
paths=set(subprocess.check_output(['git','ls-files','-co','--exclude-standard','-z'],cwd=ROOT).decode().split('\0'))-{''}
rows=[(p,(ROOT/p).stat().st_size) for p in paths if (ROOT/p).is_file()]
levels={}
for n in range(5,0,-1):
 files=[(p,b) for p,b in rows if p.startswith(f'audio/n{n}/') and p.endswith('.mp3')];levels[f'N{n}']={'files':len(files),'bytes':sum(b for p,b in files)}
objects=dict(line.split(': ',1) for line in subprocess.check_output(['git','count-objects','-v'],cwd=ROOT,text=True).splitlines())
result={'files':len(rows),'siteBytesUpperBound':sum(b for p,b in rows),'audioBytes':sum(x['bytes'] for x in levels.values()),'audioLevels':levels,'largestFile':max(rows,key=lambda x:x[1]),'filesAtLeast100MB':[p for p,b in rows if b>=100_000_000],'gitObjectBytes':1024*(int(objects['size'])+int(objects['size-pack'])),'limits':{'siteBytes':1_000_000_000,'fileBytesConservative':100_000_000,'softBandwidthGBPerMonth':100},'sources':['https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits','https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github'],'checked':'2026-10-27','note':'All tracked/non-ignored files counted conservatively, including developer docs/tests; .git/node_modules/.cache excluded. Git object size is reported separately. No LFS.'}
assert result['siteBytesUpperBound']<result['limits']['siteBytes'];assert not result['filesAtLeast100MB']
print(json.dumps(result,ensure_ascii=False,indent=2))
