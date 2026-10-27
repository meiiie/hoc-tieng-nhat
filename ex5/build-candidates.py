#!/usr/bin/env python3
"""Materialize the manually reviewed Phase A decisions using pinned local pools. Run from repo root."""
import json,sys,re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from phase_analyzer import evidence
from japanese_morphology import HAN,analyze,verify_dictionary,hira
from example_lemmas import allowed,entries,lexical_form
from tatoeba import match_word
root=Path(__file__).resolve().parents[1];ws=json.load(open('ex5/missing-words.json'));pool=json.load(open('.cache/ex5/review-pool.json'))
licensed=[];authored=[];issues=[];seen=set()
verify_dictionary()
for line in Path('ex5/editorial-decisions.tsv').read_text().splitlines():
 c=line.split('|');i=int(c[0]);assert i not in seen,i;seen.add(i);w=ws[i]
 if c[1]=='L':
  assert len(c)==5,(i,len(c));idx,senseidx=int(c[2]),int(c[3]);r=dict(pool[w['id']][idx]);vi=c[4]
  old=r.pop('existingTranslation',None)
  if old and not old['machine']:
   if vi!='=' and vi!=old['text']:
    r['vi_refinement']={'text':vi,'machine':True,'translator':'OpenAI Codex','reason':'Optional localized wording; the supplied human translation is retained in vi as requested.','licence':'CC BY 2.0 FR'}
   vi=old['text'];translation={**old,'text':vi}
  else:
   assert vi!='=',i
   translation={'text':vi,'lang':'vie','machine':True,'translator':'OpenAI Codex','method':'Translated directly from Japanese by the authoring assistant; not native reviewed.'}
   if old and old.get('text'):translation['previous_candidate']=old
  r['vi']=vi;r['translation']=translation;r['machine']=translation['machine'];r['target_surface']=r['match']['surface']
  licensed.append(r)
 else:
  assert len(c)==7,(i,len(c));senseidx=int(c[2]);ja,target,vi,why=c[3:]
  assert target in ja,(i,target,ja)
  r={'id':w['id'],'level':w['level'],'ja':ja,'target_surface':target,'vi':vi,'rationale':why,'machine':True,'author':'OpenAI Codex','native_reviewed':False}
  m=match_word(w,ja)
  alias=None
  if not m:
   forms=set(allowed(w))|{k['text'] for k in entries()[w['jmdict']]['kana'] if hira(k['text'])==hira(w['kana'])}
   for f in sorted(forms):
    if f not in ja:continue
    # A kana spelling must retain lexical identity; replacing the headword
    # with arbitrary kana would bypass the existing homophone safeguards.
    if not re.search(HAN,f) and f!=w['kanji']:
     ft=analyze(f)
     if len(ft)!=1 or hira(lexical_form(ft[0].get('lemma','')))!=hira(w['kana']):continue
     if re.search(HAN,w['kanji']) and re.search(r'-[A-Za-z]',ft[0].get('lemma','')):continue
    m=match_word({**w,'kanji':f},ja)
    if m:alias=f;break
  if not m:
   ts0=analyze(ja); starts={t['start'] for t in ts0}; ends={t['end'] for t in ts0}
   positions=[j for j in range(len(ja)) if ja.startswith(target,j)]
   start=max(positions,key=lambda j:(j in starts)+(j+len(target) in ends));m={'start':start,'end':start+len(target),'surface':target,'kind':'phaseA-review'}
  if alias:m['jmdictAlias']=alias
  r['match']=m;authored.append(r)
 sense=next(s for s in w['senses'] if s['index']==senseidx)
 r['sense']={'jmdict':w['jmdict'],'index':senseidx,'index_base':1,'gloss':[g['text'] for g in sense['gloss']],'part_of_speech':sense['partOfSpeech'],'misc':sense['misc'],'applies_to_kanji':sense['appliesToKanji'],'applies_to_kana':sense['appliesToKana']}
 r['target']={'kanji':w['kanji'],'kana':w['kana']}
 r['native_reviewed']=False
 r['review']={'reviewer':'OpenAI Codex','sense_alignment':'assistant-reviewed','Japanese_and_Vietnamese':'assistant-reviewed; no native-speaker certification'}
 if c[1]=='L':
  r['changes']=r.get('changes','Japanese sentence copied verbatim from the source.')
  r['translation']['licence']=r['licence'] if r['translation']['machine'] else r['translation'].get('licence','CC BY 2.0 FR')
  r['translation']['licence_url']=r['licence_url'] if r['translation']['machine'] else 'https://creativecommons.org/licenses/by/2.0/fr/'
  r['attribution']=f"{r['author']} — {r['source']}, {r['source_id']}; {r['url']}; {r['licence']} ({r['licence_url']}). {r['changes']}"
  if r['translation']['machine']:r['attribution']+=' Vietnamese translation added by OpenAI Codex; machine-generated, not native reviewed.'
 r['analysis'],ann=evidence(w,r);r.update(ann)
 if not r['analysis']['strict_match']:
  issues.append({'index':i,'id':w['id'],'word':w['kanji'],'reading':w['kana'],'ja':r['ja'],'target':r['target_surface'],'status':r['analysis']['status'],'lemma_confirmed':r['analysis']['lemma_confirmed'],'tokens':[(t['surface'],t.get('lemma'),t['reading']) for t in r['analysis']['target_tokens']]})
for name,data in [('licensed-candidates.json',licensed),('authored.json',authored)]:Path('ex5',name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
Path('ex5/analyzer-review.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n')
print('reviewed',len(seen),'licensed',len(licensed),'authored',len(authored),'strict exceptions',len(issues))
print('status',__import__('collections').Counter(r['status'] for r in issues))
