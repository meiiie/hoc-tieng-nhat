"""Automated cross-check of Vietnamese meanings against JMdict English glosses (no native reviewer available).
1. Back-translate each Vietnamese meaning to English with Helsinki-NLP/opus-mt-vi-en (Apache-2.0).
2. Compare content words of the back-translation with each JMdict gloss (light stemming, stopwords removed): best containment.
3. Confidence: high >= 0.5, medium > 0, low = no shared content word (needs a look; synonyms also land here). Output data/sources/meaning-check.json {id:[conf, sim, back]}.
This flags likely mistranslations; it cannot prove a meaning is right."""
import json,sys,torch
from pathlib import Path
from transformers import MarianMTModel,MarianTokenizer
import re
ROOT=Path(__file__).resolve().parents[1];torch.set_num_threads(4)
ws=[w for lv in ['n5','n4','n3','n2','n1'] for w in json.load(open(ROOT/f'data/{lv}.json'))]
tok=MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-vi-en');mt=MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-vi-en').eval()
CACHE=ROOT.parent/'.meaning-back.json'
back=json.loads(CACHE.read_text()) if CACHE.exists() else []
for i in range(len(back),len(ws),64):
  b=[w['v'] for w in ws[i:i+64]]
  with torch.no_grad():out=mt.generate(**tok(b,return_tensors='pt',padding=True,truncation=True,max_length=64),max_new_tokens=40,num_beams=1)
  back+=tok.batch_decode(out,skip_special_tokens=True)
  if i%640==0:print(i,flush=True)
CACHE.write_text(json.dumps(back,ensure_ascii=False))
STOP=set('a an the to of be is are in on for with and or one something someone sb sth oneself by as at from that this it its etc'.split())
stem=lambda t:re.sub(r'(ing|ed|es|s|ly)$','',t) if len(t)>4 else t
words=lambda x:{stem(t) for t in re.findall(r"[a-z]+",x.lower()) if t not in STOP}
out={};cnt={'high':0,'medium':0,'low':0}
for w,bk in zip(ws,back):
  b=words(bk);best=0
  for g in w['en']:
    gw=words(g)
    if gw and b:best=max(best,len(b&gw)/min(len(b),len(gw)))
  c='high' if best>=.5 else 'medium' if best>0 else 'low';cnt[c]+=1;out[w['id']]=[c,round(best,2),bk]
(ROOT/'data/sources/meaning-check.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
print(json.dumps(cnt))
