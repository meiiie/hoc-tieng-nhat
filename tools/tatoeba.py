#!/usr/bin/env python3
"""Select attributed Tatoeba examples with exact or guarded lemma/surface matching.
Authoring dependency: fugashi 1.5.2 + unidic-lite 1.0.8; never shipped to browsers.
The supplied detailed exports have six columns: id, lang, text, owner, created, modified.
"""
import argparse,csv,hashlib,json,re,unicodedata
from collections import defaultdict,Counter
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
from japanese_morphology import analyze, verify_dictionary
from example_lemmas import allowed, candidates_for, exact_lexeme_ok, match_lemma
LICENSE='CC BY 2.0 FR'
def hira(s):
 return ''.join(chr(ord(c)-96) if 'ァ'<=c<='ヶ' else c for c in unicodedata.normalize('NFKC',s))
@lru_cache(maxsize=1)
def tagger():
 from fugashi import Tagger
 return Tagger()
def spans(text):
 return [(t['start'],t['end'],t['surface'],t['reading']) for t in analyze(text)]
def match_word(word,text,tokens=None):
 tokens=spans(text) if tokens is None else tokens
 analyzed=analyze(text)
 for form in dict.fromkeys([word['kanji'],word['kana']]):
  for i,t in enumerate(tokens):
   for j in range(i,len(tokens)):
    start,end=t[0],tokens[j][1]
    if end-start>len(form):break
    selected=analyzed[i:j+1]
    if text[start:end]==form and ''.join(x[3] for x in tokens[i:j+1])==hira(word['kana']) and exact_lexeme_ok(word,selected):
     return {'start':start,'end':end,'surface':form,'kind':'exact'}
 return match_lemma(word,text,analyzed)
def tier(example):
 t=example['translation']
 return 2 if t['machine'] else 1 if t['pivot'] else 0
def better(candidate,existing):
 # Human direct > human pivot > machine. Ties retain existing unless shorter.
 return tier(candidate)<tier(existing) or (tier(candidate)==tier(existing)<2 and len(candidate['text'])<len(existing['text']))
def sentences(path,lang):
 with path.open(encoding='utf8') as f:
  for c in csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE):
   if len(c)!=6:raise ValueError((path,'expected six detailed-export columns',c[:1]))
   if c[1]!=lang:raise ValueError((path,'language',c[:2]))
   if c[3] in ('','\\N'):continue  # Ownerless sentences cannot meet per-author attribution.
   yield {'id':int(c[0]),'lang':lang,'text':c[2],'username':c[3],'license':LICENSE,'url':f'https://tatoeba.org/sentences/show/{c[0]}'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=ROOT.parent/'src/tatoeba');ap.add_argument('--levels',nargs='+',type=int,default=[5,4]);a=ap.parse_args()
 verify_dictionary()
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
 forms=defaultdict(list);lemma_forms=defaultdict(list)
 for w in words:
  if 'động từ' in w['pos'] or 'tính từ' in w['pos']:
   for form in allowed(w):lemma_forms[form].append(w)
  for form in set([w['kanji'],w['kana']]):forms[form].append(w)
 excluded=json.loads((ROOT/'data/sources/tatoeba-exclusions.json').read_text())
 existing=json.loads((ROOT/'data/sources/tatoeba-examples.json').read_text())
 best={};scores={}
 for w in words:
  old=existing.get(w['id'])
  if old and str(old['id']) not in excluded:
   m=match_word(w,old['text'])
   if m:best[w['id']]={**old,'match':m};scores[w['id']]=(tier(old),0 if tier(old)==2 else len(old['text']))
 for s in rows:
  if str(s['id']) in excluded:continue
  ts=spans(s['text']);candidates=candidates_for(analyze(s['text']),lemma_forms)
  for i in range(len(ts)):
   for j in range(i,min(i+10,len(ts))):
    for w in forms.get(s['text'][ts[i][0]:ts[j][1]],[]):candidates[w['id']]=w
  for ident,w in candidates.items():
   m=match_word(w,s['text'],ts)
   if m is None:continue
   score=(tier(s),len(s['text']))
   if ident not in best or score<scores[ident]:best[ident]={**s,'match':m};scores[ident]=score
 out=ROOT/'.cache'/('examples-'+ '-'.join(map(str,a.levels))+'.json');out.write_text(json.dumps(best,ensure_ascii=False,indent=1)+'\n')
 changes={k:[] for k in ['retained','replaced','filled','removed']}
 for w in words:
  ident=w['id'];old=existing.get(ident);new=best.get(ident)
  key='filled' if new and not old else 'removed' if old and not new else 'retained' if old and new and old['id']==new['id'] else 'replaced' if old and new else None
  if key:changes[key].append({'word':ident,'before':old['id'] if old else None,'after':new['id'] if new else None,'match':new['match']['kind'] if new else None})
 (ROOT/'data/sources'/('tatoeba-selection-'+ '-'.join(map(str,a.levels))+'.json')).write_text(json.dumps({'levels':a.levels,'counts':{k:len(v) for k,v in changes.items()},'changes':changes},ensure_ascii=False,indent=1)+'\n')
 print('Selected',out,{k:len(v) for k,v in changes.items()},flush=True)
 for n in a.levels:
  selected=[best[w['id']] for w in words if w['level']==n and w['id'] in best]
  print(n,len(selected),dict(Counter('machine' if s['translation']['machine'] else 'pivot' if s['translation']['pivot'] else 'direct' for s in selected)),flush=True)
 meta={'license':LICENSE,'licenseUrl':'https://creativecommons.org/licenses/by/2.0/fr/','exportColumns':['id','lang','text','username','created','modified'],'retrieved':'2026-10-27','selection':'one named sentence, 4–25 characters, punctuation-terminated; exact token reading or UniDic lemma + POS + JMdict spelling/reading; actual contiguous inflected surface including auxiliaries; retain existing unless better translation tier or shorter human example at same tier (retain existing machine examples); conservative offline ruby in annotate-examples.py','tokenizer':'fugashi 1.5.2 / unidic-lite 1.0.8 (UniDic 2.1.2)','sources':{p.name:hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in [a.source/n for n in ['jpn.tsv','vie.tsv','eng.tsv','links.csv']]}}
 (ROOT/'data/sources/tatoeba-method.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
