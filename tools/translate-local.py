#!/usr/bin/env python3
"""Reproducible local MT draft support, not an autonomous agent.
Weights: Helsinki-NLP/opus-mt-en-vi (Apache-2.0); outputs derive from CC BY-SA JMdict.
Final reviewed TSV is the build input. This script only writes a separate candidate file.
"""
import csv,json,re,hashlib,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
ROOT=Path(__file__).resolve().parents[1];cache=ROOT/'.cache';words=json.loads((cache/'translation-worklist.json').read_text());existing={x['id'] for x in csv.DictReader((ROOT/'data/sources/vi-glosses.tsv').open(),delimiter='\t')}
torch.set_num_threads(4)
tokenizer=AutoTokenizer.from_pretrained(cache/'opus-en-vi');translator=AutoModelForSeq2SeqLM.from_pretrained(cache/'opus-en-vi').eval()
work=[w for w in words if w['id'] not in existing];out=cache/'mt-candidates.tsv';records=[]
# Translate dominant sense only; do not manufacture a short meaning from Japanese readings.
def source(w):
 text=w['en'][0]
 text=re.sub(r'\([^)]*\)','',text).strip()
 return text
sources=[source(w) for w in work];started=time.time()
with out.open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['id','kanji','reading','en','vi'],delimiter='\t',lineterminator='\n');writer.writeheader()
 for start in range(0,len(work),32):
  texts=sources[start:start+32];tokens=tokenizer(['>>vie<< '+text for text in texts],return_tensors='pt',padding=True,truncation=True)
  with torch.inference_mode():results=translator.generate(**tokens,num_beams=4,max_new_tokens=64)
  decoded=tokenizer.batch_decode(results,skip_special_tokens=True)
  for w,en,result in zip(work[start:start+32],texts,decoded):
   vi=result.strip().strip(' .;:!\"').lower()
   vi=re.sub(r'^(?:để |được dùng để )','',vi);vi=re.sub(r'\s+',' ',vi);vi=vi.replace('\t',' ')
   writer.writerow({'id':w['id'],'kanji':w['kanji'],'reading':w['kana'],'en':en,'vi':vi})
  f.flush();print(start+len(texts),'/',len(work),round(time.time()-started,1),'seconds',flush=True)
meta={'model':'Helsinki-NLP/opus-mt-en-vi','license':'Apache-2.0','engine':'Transformers Marian float32 CPU','beam_size':4,'batch_size':32,'candidateCount':len(work),'source':'first JMdict English gloss; parenthetical notes stripped','postprocessing':'lowercase, trim punctuation, remove leading Vietnamese infinitive marker','weightsSha256':hashlib.sha256((cache/'opus-en-vi/pytorch_model.bin').read_bytes()).hexdigest(),'requiresReview':True}
(cache/'mt-candidate-method.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
