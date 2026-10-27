#!/usr/bin/env python3
"""Local authoring helper. All translation text is written by the author, no network translation.
show START COUNT: print source senses; apply FILE: merge numbered Vietnamese lines into the source TSV.
"""
import json,csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ws=json.loads((ROOT/'.cache/translation-worklist.json').read_text());src=ROOT/'data/sources/vi-glosses.tsv'
rows={r['id']:r for r in csv.DictReader(src.open(),delimiter='\t')} if src.exists() else {}
if sys.argv[1]=='show':
 start,count=map(int,sys.argv[2:4])
 for i in range(start,min(len(ws),start+count)):
  w=ws[i]
  print(f"{i} {w['kanji']}({w['kana']}) {'; '.join(w['en'][:3])[:130]}"+((' => '+rows[w['id']]['vi']) if w['id'] in rows else ''))
elif sys.argv[1]=='apply':
 for line in Path(sys.argv[2]).read_text().strip().splitlines():
  n,vi=line.split(' ',1);w=ws[int(n)];assert vi.strip() and '\t' not in vi
  rows[w['id']]={'id':w['id'],'kanji':w['kanji'],'reading':w['kana'],'vi':vi.strip()}
 with src.open('w') as f:
  writer=csv.DictWriter(f,fieldnames=['id','kanji','reading','vi'],delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows[w['id']] for w in ws if w['id'] in rows)
 print(len(rows),'/',len(ws),'translated')
