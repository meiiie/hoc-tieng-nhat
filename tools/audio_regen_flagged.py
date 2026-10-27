"""Re-synthesise MP3s that failed the round trip (score < 60) with punctuation or kanji context, and keep a new take only when the
recogniser agrees with the kana clearly better (>= 85 and at least 20 points above the old take). Same voice, rate and encoding as gen-audio.py.
Usage: python3 tools/audio_regen_flagged.py [model_dir]. Resumable: ids already in data/sources/audio-regenerated.json are skipped."""
import json,sys,os,subprocess,tempfile,base64,shutil,numpy as np,onnxruntime as ort
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];MODEL=sys.argv[1] if len(sys.argv)>1 else str(ROOT.parent/'model')
s=ort.InferenceSession(MODEL+'/onnx/model_q4.onnx');EDGE=shutil.which('edge-tts') or '/home/box/.local/bin/edge-tts'
node=subprocess.Popen(['node',str(ROOT/'tools/score-one.js')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
def score(path,kana):
  x=np.frombuffer(subprocess.run(['ffmpeg','-v','quiet','-i',str(path),'-f','f32le','-ac','1','-ar','16000','-'],capture_output=True).stdout,np.float32)
  x=np.concatenate([np.zeros(2400,np.float32),x,np.zeros(2400,np.float32)]);lg=s.run(None,{'input_values':x[None]})[0][0].astype(np.float32)
  node.stdin.write(json.dumps({'kana':kana,'T':lg.shape[0],'V':lg.shape[1],'logits':base64.b64encode(lg.tobytes()).decode()})+'\n');node.stdin.flush();return json.loads(node.stdout.readline())
rt=json.load(open(ROOT/'data/sources/audio-roundtrip.json'));words={w['id']:w for lv in ['n5','n4','n3','n2','n1'] for w in json.load(open(ROOT/f'data/{lv}.json'))}
prev=json.load(open(ROOT/'data/sources/audio-regenerated.json')) if (ROOT/'data/sources/audio-regenerated.json').exists() else {'rows':[]}
done={r['id'] for r in prev['rows']};log=list(prev['rows'])
for f in [x for x in rt['flagged'] if x['id'] not in done]:
  w=words[f['id']];dst=ROOT/w['audio'];best=None
  texts=[w['kana']+'。','「'+w['kana']+'」']+([w['kanji']+'。'] if w['kanji']!=w['kana'] else [])
  with tempfile.TemporaryDirectory() as td:
    for i,t in enumerate(texts):
      raw=Path(td)/f'{i}.raw.mp3';enc=Path(td)/f'{i}.mp3'
      try:
        subprocess.run([EDGE,'--voice','ja-JP-NanamiNeural','--text',t,'--write-media',str(raw)],check=True,capture_output=True,timeout=60)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-ac','1','-ar','24000','-b:a','32k',str(enc)],check=True,timeout=60)
      except Exception as e: continue
      r=score(enc,w['kana'])
      if best is None or r['score']>best[0]: best=(r['score'],t,enc,r['heard'])
    row={'id':w['id'],'kana':w['kana'],'old':f['score'],'oldHeard':f['heard']}
    if best and best[0]>=85 and best[0]>=f['score']+20:
      shutil.copy(best[2],dst);row.update(replaced=True,new=best[0],text=best[1],heard=best[3])
    else: row.update(replaced=False,bestCandidate=best and best[0])
    log.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
out={'rule':'replace only when candidate >= 85 and >= old + 20','attempted':len(log),'replaced':sum(r['replaced'] for r in log),'rows':log}
json.dump(out,open(ROOT/'data/sources/audio-regenerated.json','w'),ensure_ascii=False,indent=1)
print(json.dumps({k:out[k] for k in ['attempted','replaced']}))
