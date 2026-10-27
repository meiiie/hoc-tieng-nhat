"""Validate every shipped sentence, owner and graph edge against the original exports."""
import csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from tatoeba import ROOT,sentences,match_word
src=ROOT.parent/'src/tatoeba';words=[w for n in range(5,0,-1) for w in json.loads((ROOT/f'data/n{n}.json').read_text())]
excluded=json.loads((ROOT/'data/sources/tatoeba-exclusions.json').read_text())
needed={};edges=set();count=0
for w in words:
 e=w['example']
 if not e:continue
 assert str(e['id']) not in excluded,(w['id'],'excluded sentence',e['id'])
 count+=1;assert match_word(w,e['text'])==e['match'],w['id']
 t=e['translation'];refs=[e]+([t['from']] if t['machine'] else [t]+([t['via']] if t['pivot'] else []))
 for r in refs:needed[(r['lang'],r['id'])]=r
 edges.update(tuple(x) for x in t['links'])
assert count>1000,('no complete example release found',count)
for lang in ['jpn','vie','eng']:
 for s in sentences(src/(lang+'.tsv'),lang):
  key=(lang,s['id'])
  if key in needed:
   expected=needed.pop(key)
   for field in ['text','username','license','url']:assert s[field]==expected[field],(key,field)
assert not needed,list(needed)[:5]
with (src/'links.csv').open() as f:
 for line in f:
  a,b=map(int,line.split());edges.discard((a,b));edges.discard((b,a))
assert not edges,edges
print(f'{count} examples: lexical/surface match, original text/author and every direct/pivot edge verified')
