#!/usr/bin/env python3
"""Select one attributed, exact-surface Tatoeba example per word (no inferred furigana).
Authoring dependency: fugashi 1.5.2 + unidic-lite 1.0.8; never shipped to browsers.
The supplied detailed exports have six columns: id, lang, text, owner, created, modified.
"""
import argparse,csv,hashlib,json,re,unicodedata
from collections import defaultdict,Counter
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
LICENSE='CC BY 2.0 FR'
def hira(s):
 return ''.join(chr(ord(c)-96) if 'ァ'<=c<='ヶ' else c for c in unicodedata.normalize('NFKC',s))
@lru_cache(maxsize=1)
def tagger():
 from fugashi import Tagger
 return Tagger()
def spans(text):
 out=[];offset=0
 for t in tagger()(text):
  start=text.index(t.surface,offset);offset=start+len(t.surface)
  out.append((start,offset,t.surface,hira(t.feature.kana or '') if not t.is_unk else ''))
 return out
def match_word(word,text,tokens=None):
 tokens=spans(text) if tokens is None else tokens
 for form in dict.fromkeys([word['kanji'],word['kana']]):
  for i,t in enumerate(tokens):
   for j in range(i,len(tokens)):
    start,end=t[0],tokens[j][1]
    if end-start>len(form):break
    if text[start:end]==form and ''.join(x[3] for x in tokens[i:j+1])==hira(word['kana']):
     return {'start':start,'end':end,'surface':form,'kind':'exact'}
 return None
def sentences(path,lang):
 with path.open(encoding='utf8') as f:
  for c in csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE):
   if len(c)!=6:raise ValueError((path,'expected six detailed-export columns',c[:1]))
   if c[1]!=lang:raise ValueError((path,'language',c[:2]))
   if c[3] in ('','\\N'):continue  # Ownerless sentences cannot meet per-author attribution.
   yield {'id':int(c[0]),'lang':lang,'text':c[2],'username':c[3],'license':LICENSE,'url':f'https://tatoeba.org/sentences/show/{c[0]}'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=ROOT.parent/'src/tatoeba');ap.add_argument('--levels',nargs='+',type=int,default=[5,4]);a=ap.parse_args()
 words=[w for n in a.levels for w in json.loads((ROOT/f'data/n{n}.json').read_text())]
 cache=ROOT/'.cache/tatoeba-linked.json'
 if cache.exists():rows=json.loads(cache.read_text())
 else:
  jp={s['id']:s for s in sentences(a.source/'jpn.tsv','jpn') if 4<=len(s['text'])<=25 and re.search('[。！？!?]$',s['text']) and not re.search(r'[\s<>\[\]]',s['text'])}
  vi={s['id']:s for s in sentences(a.source/'vie.tsv','vie')}
  jlinks=defaultdict(set);vlinks=defaultdict(set)
  print('Named short Japanese',len(jp),'Vietnamese',len(vi),flush=True)
  with (a.source/'links.csv').open() as f:
   for line in f:
    x,y=map(int,line.split())
    if x in jp:jlinks[x].add(y)
    if y in jp:jlinks[y].add(x)
    if y in vi:vlinks[x].add(y)
    if x in vi:vlinks[y].add(x)
  wanted=set().union(*jlinks.values())
  en={s['id']:s for s in sentences(a.source/'eng.tsv','eng') if s['id'] in wanted}
  rows=[]
  for ident,s in jp.items():
   direct=sorted(jlinks[ident]&vi.keys());english=sorted(jlinks[ident]&en.keys())
   if direct:
    translation={**vi[min(direct,key=lambda k:(len(vi[k]['text']),k))],'machine':False,'pivot':False,'links':[]};translation['links']=[[ident,translation['id']]]
   else:
    pivots=[(eid,vid) for eid in english for vid in vlinks[eid]]
    if pivots:
     eid,vid=min(pivots,key=lambda pair:(len(vi[pair[1]]['text']),pair))
     translation={**vi[vid],'machine':False,'pivot':True,'via':en[eid],'links':[[ident,eid],[eid,vid]]}
    elif english:
     eid=min(english,key=lambda k:(len(en[k]['text']),k))
     translation={'text':'','lang':'vie','machine':True,'pivot':False,'from':en[eid],'links':[[ident,eid]],'method':'AI translation from linked English; unreviewed by native speakers'}
    else:continue
   rows.append({**s,'furigana':None,'translation':translation})
  cache.write_text(json.dumps(rows,ensure_ascii=False));print('Linked candidates',len(rows),flush=True)
 forms=defaultdict(list)
 for w in words:
  for form in set([w['kanji'],w['kana']]):forms[form].append(w)
 excluded=json.loads((ROOT/'data/sources/tatoeba-exclusions.json').read_text())
 best={};scores={}
 for s in rows:
  if str(s['id']) in excluded:continue
  ts=spans(s['text']);candidates={}
  for i in range(len(ts)):
   for j in range(i,min(i+10,len(ts))):
    for w in forms.get(s['text'][ts[i][0]:ts[j][1]],[]):candidates[w['id']]=w
  for ident,w in candidates.items():
   m=match_word(w,s['text'],ts)
   if m is None:continue
   tr=s['translation'];score=(2 if tr['machine'] else 1 if tr['pivot'] else 0,m['surface']!=w['kanji'],abs(len(s['text'])-12),len(tr['text'] or tr.get('from',{}).get('text','')),s['id'])
   if ident not in best or score<scores[ident]:best[ident]={**s,'match':m};scores[ident]=score
 out=ROOT/'.cache'/('examples-'+ '-'.join(map(str,a.levels))+'.json');out.write_text(json.dumps(best,ensure_ascii=False,indent=1)+'\n')
 print('Selected',out,flush=True)
 for n in a.levels:
  selected=[best[w['id']] for w in words if w['level']==n and w['id'] in best]
  print(n,len(selected),dict(Counter('machine' if s['translation']['machine'] else 'pivot' if s['translation']['pivot'] else 'direct' for s in selected)),flush=True)
 meta={'license':LICENSE,'licenseUrl':'https://creativecommons.org/licenses/by/2.0/fr/','exportColumns':['id','lang','text','username','created','modified'],'retrieved':'2026-10-27','selection':'one named sentence, 4–25 characters, punctuation-terminated; exact surface and UniDic token reading; no inflection matching or generated furigana','tokenizer':'fugashi 1.5.2 / unidic-lite 1.0.8 (UniDic 2.1.2)','sources':{p.name:hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in [a.source/n for n in ['jpn.tsv','vie.tsv','eng.tsv','links.csv']]}}
 (ROOT/'data/sources/tatoeba-method.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
