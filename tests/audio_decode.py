"""Decode every expected MP3 and inspect the original Nanami encoding contract."""
import argparse,concurrent.futures,hashlib,json,subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--levels',nargs='+',default=['n5','n4','n3','n2','n1']);ap.add_argument('--report',type=Path,default=ROOT.parent/'reports/audio-decode-2.json');a=ap.parse_args()
words=[w for n in a.levels for w in json.loads((ROOT/'data'/f'{n}.json').read_text())]
def check(w):
 p=ROOT/'audio'/f"n{w['level']}"/'w'/f"{w['id']}.mp3"
 try:
  info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=codec_name,sample_rate,channels,bit_rate','-of','json',str(p)],stderr=subprocess.PIPE))['streams'][0]
  assert info=={'codec_name':'mp3','sample_rate':'24000','channels':1,'bit_rate':'32000'},info
  result=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-'],capture_output=True,timeout=20)
  assert result.returncode==0 and not result.stderr,result.stderr.decode(errors='replace')
  return {'id':w['id'],'level':w['level'],'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'ok':True}
 except Exception as e:return {'id':w['id'],'level':w['level'],'ok':False,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(check,words))
expected={f"audio/n{w['level']}/w/{w['id']}.mp3" for w in words};actual={str(p.relative_to(ROOT)) for n in a.levels for p in (ROOT/'audio'/n/'w').glob('*.mp3')}
result={'levels':a.levels,'expected':len(words),'decoded':sum(r['ok'] for r in rows),'failed':[r for r in rows if not r['ok']],'bytes':sum(r.get('bytes',0) for r in rows),'format':{'codec':'mp3','sampleRate':24000,'channels':1,'bitrate':32000},'orphans':sorted(actual-expected),'missing':sorted(expected-actual),'files':rows}
a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))
raise SystemExit(1 if result['failed'] or result['orphans'] or result['missing'] else 0)
