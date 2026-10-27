#!/usr/bin/env python3
"""Merge selected examples, refusing to publish untranslated machine drafts."""
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'data/sources/tatoeba-examples.json'
examples=json.loads(path.read_text()) if path.exists() else {}
translations={int(r['id']):r['vi'] for r in csv.DictReader((ROOT/'data/sources/tatoeba-vi-machine.tsv').open(),delimiter='\t')}
methods_path=ROOT/'data/sources/tatoeba-machine-methods.json'
methods=json.loads(methods_path.read_text()) if methods_path.exists() else {}
selected=json.loads(Path(sys.argv[1]).read_text())
# Replacing a level must also remove earlier selections now excluded.
for n in range(5,0,-1):
 ids={w['id'] for w in json.loads((ROOT/f'data/n{n}.json').read_text())}
 if ids & selected.keys():
  for key in ids:examples.pop(key,None)
for key,e in selected.items():
 if e['translation']['machine']:
  e['translation']['text']=translations[e['id']]
  e['translation']['method']=methods.get(str(e['id']),{}).get('method','Codex translation of the linked English sentence, compared with Japanese; not native-speaker verified')
 assert e['translation']['text'].strip(),key
examples.update(selected)
for e in examples.values():
 if e["translation"]["machine"]:
  e["translation"]["license"]="CC BY 2.0 FR"
  e["translation"]["translator"]=methods.get(str(e['id']),{}).get('translator','Codex (AI)')
path.write_text(json.dumps(examples,ensure_ascii=False,indent=1)+'\n')
print('Published source overlay:',len(examples))
