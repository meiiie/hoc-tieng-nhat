"""Check each added accent against the installed lexical entry or pinned Kanjium row."""
import hashlib,json,re,subprocess,sys
from collections import Counter
from pathlib import Path
import fugashi,unidic_lite
ROOT=Path(__file__).resolve().parents[1]
# When reviewing the draft outside tools/tests, provide the repository and overlay explicitly.
DRAFT='--draft' in sys.argv
args=[s for s in sys.argv[1:] if s!='--draft']
if args:ROOT=Path(args[0]).resolve()
SOURCE=Path(args[1]) if len(args)>1 else ROOT/'data/sources/pitch-additions.json'
BASELINE='479f1841ee6c403adb1fe658e2c35e4f4431f169'
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(SOURCE.parent))
from pitch_sources import hira,allowed_lemmas
additions=json.loads(SOURCE.read_text());method=json.loads(SOURCE.with_name('pitch-method.json').read_text())
assert len(additions)>900
assert hashlib.sha256((Path(unidic_lite.DICDIR)/'sys.dic').read_bytes()).hexdigest()==method['unidic']['files']['sys.dic']
jm={x['id']:x for x in json.loads((ROOT.parent/'src/jmdict-eng-3.6.2.json').read_text())['words']}
words={w['id']:w for n in range(5,0,-1) for w in json.loads((ROOT/f'data/n{n}.json').read_text())}
original={w['id']:w for n in range(5,0,-1) for w in json.loads(subprocess.check_output(['git','show',f'{BASELINE}:data/n{n}.json'],cwd=ROOT))}
assert set(words)==set(original)
tagger=fugashi.Tagger('-a');verified=Counter();unchanged=0
for ident,w in words.items():
 old=original[ident]
 if old['pitch'] is not None:
  assert w['pitch']==old['pitch'];assert ident not in additions;unchanged+=1
 if ident not in additions:continue
 row=additions[ident];assert old['pitch'] is None
 assert (row['form'],row['reading'],row['jmdict'])==(w['kanji'],w['kana'],w['jmdict'])
 if not DRAFT:assert w['pitch']==row['pitch'] and w['pitchSource']==row['source']
 if row['source']=='unidic-2.1.2':
  assert row['license']=='BSD-3-Clause'
  lemmas=allowed_lemmas(w,jm[w['jmdict']]);assert sorted(lemmas)==row['allowedLemmas']
  real=[n.feature._asdict() for n in tagger.parseToNodeList(w['kanji']) if not n.is_unk and n.surface==w['kanji']]
  assert row['records']
  for record in row['records']:
   f=record['features'];assert f in real;assert record['surface']==f['orth']==f['orthBase']==w['kanji']
   assert hira(f['kana'])==hira(f['kanaBase'])==hira(w['kana']);assert f['aModeType']=='*'
   assert re.fullmatch(r'\d+(?:,\d+)*',f['aType']);assert list(map(int,f['aType'].split(',')))==row['pitch']
   assert hira(re.sub(r'-[A-Za-z].*$','',f['lemma'])) in {hira(s) for s in lemmas}
 elif row['source']=='kanjium':
  assert row['license']=='CC-BY-SA-4.0'
  for record in row['records']:
   path=ROOT/'.cache/pitch-research'/record['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==method['kanjium']['files'][record['file']]['sha256']
   assert path.read_text().splitlines()[record['line']-1]==record['raw']
   assert record['form']==w['kanji'] and hira(record['reading'])==hira(w['kana'])
   assert list(map(int,record['acc_pos'].split(',')))==row['pitch']
 else:raise AssertionError(row['source'])
 verified[row['source']]+=1
assert unchanged==7096
result={'sourceEntriesVerified':dict(verified),'total':sum(verified.values()),'originalPitchUnchanged':unchanged,'wordIdsPreserved':len(words),'baseline':BASELINE,'draft':DRAFT}
(ROOT.parent/'reports'/('pitch-provenance-draft.json' if DRAFT else 'pitch-provenance.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
