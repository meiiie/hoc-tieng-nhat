#!/usr/bin/env python3
"""Build deterministic JLPT data from licensed, read-only sources and reviewed TSVs.
Usage: python3 tools/build-data.py --source ../src [--draft]
Draft mode permits pending Vietnamese translations while authoring; release mode refuses them.
"""
import argparse, csv, hashlib, json, re, shutil, subprocess, unicodedata
from pathlib import Path
from collections import defaultdict, Counter
ROOT=Path(__file__).resolve().parents[1]
METHOD='dịch từ JMdict (tiếng Anh), cần người bản ngữ kiểm tra'
def dump(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=1)+'\n',encoding='utf8')
def readtsv(path):
 return list(csv.DictReader(path.open(encoding='utf8'),delimiter='\t')) if path.exists() else []
def writetsv(path,fields,rows):
 with path.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def hira(s):return ''.join(chr(ord(c)-96) if 'ァ'<=c<='ヶ' else c for c in unicodedata.normalize('NFKC',s))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=ROOT.parent/'src');ap.add_argument('--draft',action='store_true');args=ap.parse_args();src=args.source;out=ROOT/'data';out.mkdir(exist_ok=True)
 vocab=json.loads((src/'JLPT_vocab_ALL.json').read_text());jlptkanji=json.loads((src/'JLPT_kanji_ALL.json').read_text());jm=json.loads((src/'jmdict-eng-3.6.2.json').read_text());kd=json.loads((src/'kanjidic2-all-3.6.2.json').read_text())
 fixes={(r['kanji'],r['reading']):r for r in readtsv(out/'sources/entry-fixes.tsv')}
 tatoeba_examples=json.loads((out/'sources/tatoeba-examples.json').read_text()) if (out/'sources/tatoeba-examples.json').exists() else {}
 pitch_additions=json.loads((out/'sources/pitch-additions.json').read_text()) if (out/'sources/pitch-additions.json').exists() else {}
 vi={r['id']:r for r in readtsv(out/'sources/vi-glosses.tsv')}
 selections={(r['kanji'],r['reading']):r['jmdict'] for r in readtsv(out/'sources/sense-selection.tsv')}
 pairs=defaultdict(list);kana=defaultdict(list)
 for e in jm['words']:
  for r in e['kana']:
   kana[hira(r['text'])].append(e)
   for k in e['kanji']:
    if '*' in r['appliesToKanji'] or k['text'] in r['appliesToKanji']:pairs[(k['text'],hira(r['text']))].append(e)
 def choose(es,form,reading):
  if (form,reading) in selections:
   selected=next(e for e in jm['words'] if e['id']==selections[(form,reading)])
   assert selected in es,(form,reading,'selection not among matched entries')
   return selected
  return sorted(es,key=lambda e:(not any(k['common'] and k['text']==reading for k in e['kana']),not (hira(form)==hira(reading) and any('uk' in x['misc'] for x in e['sense'])),any(x in ('arch','obs','rare') for x in e['sense'][0]['misc']),int(e['id'])))[0] if es else None
 def senses(e,form,reading):
  return [s for s in e['sense'] if ('*' in s['appliesToKanji'] or form in s['appliesToKanji']) and ('*' in s['appliesToKana'] or reading in s['appliesToKana'])]
 records={};unmatched=[];matches=Counter();source_rows=0;quarantined=[];raw_matches=0
 for form,rs in vocab.items():
  for r in rs:
   source_rows+=1;reading=r['reading'];level=r['level'];original=[form,reading];fix=fixes.get((form,reading),{});f=fix.get('form') or form;reading=fix.get('kana') or reading
   raw_exact=bool(pairs.get((form,hira(r['reading']))) or (hira(form)==hira(r['reading']) and kana.get(hira(r['reading']))));raw_matches+=int(raw_exact)
   if fix.get('exclude')=='yes':
    quarantined.append({'kanji':form,'reading':r['reading'],'level':'N'+str(level),'reason':fix['reason']});matches['quarantined']+=1
    unmatched.append({'kanji':form,'reading':r['reading'],'level':'N'+str(level),'status':'quarantined','corrected_form':'','corrected_reading':'','jmdict':''});continue
   if not re.fullmatch('[ぁ-ゖァ-ヺー]+',reading):raise ValueError(('invalid reading, add reviewed fix',form,reading))
   es=pairs.get((f,hira(reading)),[])
   if hira(f)==hira(reading):es=es or kana.get(hira(reading),[])
   e=choose(es,f,reading);status='exact' if e else 'unmatched'
   if fix.get('jmdict'):e=next(x for x in jm['words'] if x['id']==fix['jmdict']);status='reviewed-link'
   matches[status]+=1
   if not raw_exact:unmatched.append({'kanji':form,'reading':r['reading'],'level':'N'+str(level),'status':status,'corrected_form':f,'corrected_reading':reading,'jmdict':e['id'] if e else ''})
   ident='j'+hashlib.sha256((f+'\0'+reading).encode()).hexdigest()[:12]
   if ident in records:records[ident]['level']=max(records[ident]['level'],level);continue
   ss=senses(e,f,reading) if e else [];ss=ss or (e['sense'][:1] if e else [])
   gloss=list(dict.fromkeys(g['text'] for s in ss for g in s['gloss'] if g['lang']=='eng'))
   pos=list(dict.fromkeys(p for s in ss for p in s['partOfSpeech']))
   labels=[]
   for p in pos:
    label=('tính từ đuôi i' if p.startswith('adj-i') else 'tính từ đuôi na' if p=='adj-na' else 'tính từ' if p.startswith('adj') else 'động từ' if p.startswith('v') else {'n':'danh từ','n-pr':'danh từ riêng','n-pref':'danh từ làm tiền tố','n-suf':'danh từ làm hậu tố','num':'số từ','cop':'hệ từ','aux-adj':'tính từ phụ trợ','n-adv':'danh từ chỉ thời gian','n-t':'danh từ chỉ thời gian','pn':'đại từ','adv':'phó từ','adv-to':'phó từ','int':'thán từ','conj':'liên từ','exp':'cụm từ','pref':'tiền tố','suf':'hậu tố','ctr':'từ đếm','prt':'trợ từ','aux':'trợ từ','aux-v':'trợ động từ'}.get(p,'từ ngữ'))
    if label not in labels:labels.append(label)
   examples=[x for s in ss for x in s.get('examples',[])];example=examples[0] if examples else None
   records[ident]={'id':ident,'kanji':f,'kana':reading,'romaji':'','level':level,'pos':', '.join(labels[:2]) or 'từ ngữ','en':gloss,'hv':'','pitch':None,'example':tatoeba_examples.get(ident,example),'jmdict':e['id'] if e else None,'match':status,'sourceForm':original,'v':vi.get(ident,{}).get('vi',''),'viMethod':METHOD}
 words=sorted(records.values(),key=lambda w:(-w['level'],hira(w['kana']),w['kanji']))
 missing=[w['id'] for w in words if not w['v'].strip()]
 if missing and not args.draft:raise SystemExit(f'Release build refused: {len(missing)} untranslated entries remain')
 (out/'strokes').mkdir(exist_ok=True)
 romaji=json.loads(subprocess.check_output(['node','-e',"const k=require('./ja-kana.js');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>process.stdout.write(JSON.stringify(JSON.parse(s).map(k.toRomaji))))"],input=json.dumps([w['kana'] for w in words]).encode(),cwd=ROOT))
 accents=defaultdict(list)
 for line in (src/'accents.txt').read_text().splitlines():
  cols=line.split('\t')
  if len(cols)>=3:
   a=[int(n) for n in re.findall(r'(?<![\w])\d+',cols[2])];accents[(cols[0],hira(cols[1]))]=a
 chars={x['literal']:x for x in kd['characters']};needed=set(jlptkanji)
 for w in words:needed.update(c for c in w['kanji'] if '\u3400'<=c<='\u9fff')
 kanji={};stroke_dir=src/'kanjivg/kanji'
 for c in sorted(needed):
  x=chars.get(c,{});rs=[r for g in (x.get('readingMeaning') or {}).get('groups',[]) for r in g['readings']]
  path=f'data/strokes/{ord(c):05x}.svg';p=stroke_dir/f'{ord(c):05x}.svg'
  if p.exists():shutil.copyfile(p,ROOT/path)
  kanji[c]={'hv':list(dict.fromkeys(r['value'].lower() for r in rs if r['type']=='vietnam')),'on':[r['value'] for r in rs if r['type']=='ja_on'],'kun':[r['value'] for r in rs if r['type']=='ja_kun'],'level':jlptkanji.get(c),'strokes':path if p.exists() else None,'strokeCount':(x.get('misc',{}).get('strokeCounts') or [None])[0]}
 for w,r in zip(words,romaji):
  w['romaji']=r;w['hv']=' · '.join('/'.join(kanji[c]['hv']) for c in w['kanji'] if c in kanji and kanji[c]['hv']);w['pitch']=accents.get((w['kanji'],hira(w['kana']))) or None
  w['pitchSource']='kanjium' if w['pitch'] is not None else None
  if w['id'] in pitch_additions:
   addition=pitch_additions[w['id']]
   assert w['pitch'] is None,('pitch overlay must not replace existing Kanjium',w['id'])
   assert (addition['form'],addition['reading'],addition['jmdict'])==(w['kanji'],w['kana'],w['jmdict']),('pitch key mismatch',w['id'])
   assert addition['source'] in ('kanjium','unidic-2.1.2') and addition['pitch'],('invalid pitch source',w['id'])
   w['pitch']=addition['pitch'];w['pitchSource']=addition['source']
  w['audio']=f"audio/n{w['level']}/w/{w['id']}.mp3" if (ROOT/f"audio/n{w['level']}/w/{w['id']}.mp3").exists() else None
  if w['id'] in vi:assert vi[w['id']]['kanji']==w['kanji'] and vi[w['id']]['reading']==w['kana'],('translation key mismatch',w['id'])
 kana_cards=[]
 base=['あいうえお','かきくけこ','さしすせそ','たちつてと','なにぬねの','はひふへほ','まみむめも','や ゆ よ','らりるれろ','わ   を','ん'];dakuten=['がぎぐげご','ざじずぜぞ','だぢづでど','ばびぶべぼ','ぱぴぷぺぽ'];yoon=[i+j for i in 'きぎしじちぢにひびぴみり' for j in 'ゃゅょ']
 for script in ['hiragana','katakana']:
  for group,rows in [('gojuon',base),('dakuten',dakuten),('yoon',yoon)]:
   vals=[(c,col+1) for row in rows for col,c in enumerate(row) if c!=' '] if group!='yoon' else [(c,i%3+1) for i,c in enumerate(rows)]
   for val,column in vals:
    text=''.join(chr(ord(c)+96) for c in val) if script=='katakana' else val
    refs=[]
    for c in text:
     p=stroke_dir/f'{ord(c):05x}.svg';path=f'data/strokes/{ord(c):05x}.svg'
     if p.exists():shutil.copyfile(p,ROOT/path);refs.append(path)
    kana_cards.append({'id':'kana-'+ '-'.join(f'{ord(c):x}' for c in text),'kana':text,'script':script,'group':group,'column':column,'strokes':refs})
 roman=json.loads(subprocess.check_output(['node','-e',"const k=require('./ja-kana.js');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>process.stdout.write(JSON.stringify(JSON.parse(s).map(k.toRomaji))))"],input=json.dumps([w['kana'] for w in kana_cards]).encode(),cwd=ROOT))
 for w,r in zip(kana_cards,roman):w['romaji']=r
 dump(out/'kana.json',kana_cards);dump(out/'kanji.json',kanji)
 for n in range(5,0,-1):dump(out/f'n{n}.json',[w for w in words if w['level']==n])
 writetsv(out/'sources/unmatched.tsv',['kanji','reading','level','status','corrected_form','corrected_reading','jmdict'],unmatched)
 dump(ROOT/'.cache/translation-worklist.json',words)
 writetsv(out/'sources/quarantined.tsv',['kanji','reading','level','reason'],quarantined)
 meta={'version':json.loads((ROOT/'version.json').read_text())['version'],'sourceDate':jm['dictDate'],'sourceHeadwords':len(vocab),'sourceRows':source_rows,'uniqueWords':len(words),'matches':dict(matches),'rawExactMatches':raw_matches,'matchRate':round(raw_matches/source_rows*100,4),'correctedMatchRate':round(matches['exact']/(source_rows-len(quarantined))*100,4),'unmatched':len(unmatched),'kana':len(kana_cards),'kanji':len(kanji),'levels':{f'N{n}':{'words':sum(w['level']==n for w in words),'vi':sum(w['level']==n and bool(w['v']) for w in words),'hanViet':sum(w['level']==n and bool(w['hv']) for w in words),'pitch':sum(w['level']==n and w['pitch'] is not None for w in words),'audio':sum(w['level']==n and w['audio'] is not None for w in words),'examples':sum(w['level']==n and w['example'] is not None for w in words),'exampleHumanDirect':sum(w['level']==n and w['example'] is not None and not w['example']['translation']['machine'] and not w['example']['translation']['pivot'] for w in words),'exampleHumanPivot':sum(w['level']==n and w['example'] is not None and w['example']['translation']['pivot'] for w in words),'exampleMachine':sum(w['level']==n and w['example'] is not None and w['example']['translation']['machine'] for w in words)} for n in range(5,0,-1)},'sources':{f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in ['JLPT_vocab_ALL.json','JLPT_kanji_ALL.json','jmdict-eng-3.6.2.json','kanjidic2-all-3.6.2.json','accents.txt']}}
 for n in range(5,0,-1):
  es=[w['example'] for w in words if w['level']==n and w['example']]
  meta['levels'][f'N{n}'].update({'exampleLemma':sum(e['match']['kind']=='lemma' for e in es),
   'furiganaFull':sum(bool(e.get('furiganaEvidence')) and not e.get('furiganaSkipped') for e in es),
   'furiganaPartial':sum(bool(e.get('furiganaEvidence')) and bool(e.get('furiganaSkipped')) for e in es),
   'furiganaTokensSkipped':sum(len(e.get('furiganaSkipped',[])) for e in es)})
 dump(out/'meta.json',meta);print(json.dumps(meta,ensure_ascii=False,indent=2));print('Pending Vietnamese:',len(missing))
if __name__=='__main__':main()
