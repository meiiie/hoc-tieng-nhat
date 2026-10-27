#!/usr/bin/env python3
"""Resumable, chunked Nanami generation; same voice/encoding as the original N5/N4.
Only decoded MP3 files are atomically published. Re-run build-data.py to bind files.
"""
import argparse,asyncio,json,shutil,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VOICE='ja-JP-NanamiNeural'
def describe(exc):
 return (str(exc).strip().splitlines()[-1] if str(exc).strip() else 'timeout').split('?',1)[0]
async def retry(action,attempts=5,delay=3,sleep=asyncio.sleep,on_error=None):
 for attempt in range(attempts):
  try:return await action()
  except Exception as exc:
   if on_error:on_error(attempt+1,exc)
   if attempt+1==attempts:raise
   await sleep(min(60,delay*2**attempt))
async def command(*args,timeout=40):
 proc=await asyncio.create_subprocess_exec(*map(str,args),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
 try:
  stdout,stderr=await asyncio.wait_for(proc.communicate(),timeout)
  if proc.returncode:raise RuntimeError(stderr.decode(errors='replace')[-700:] or f'exit {proc.returncode}')
  return stdout
 except BaseException:
  if proc.returncode is None:proc.kill();await proc.wait()
  raise
async def generate(w,dst):
 with tempfile.TemporaryDirectory(prefix='.nanami-',dir=dst.parent) as td:
  raw=Path(td)/'raw.mp3';encoded=Path(td)/'encoded.mp3'
  await command(shutil.which('edge-tts') or '/home/box/.local/bin/edge-tts','--voice',VOICE,'--text',w['kana'],'--write-media',raw,timeout=45)
  if not raw.exists() or raw.stat().st_size<256:raise RuntimeError('empty TTS response')
  await command('ffmpeg','-v','error','-y','-i',raw,'-ac','1','-ar','24000','-b:a','32k',encoded)
  await command('ffmpeg','-v','error','-xerror','-i',encoded,'-f','null','-')
  if encoded.stat().st_size<256:raise RuntimeError('empty encoded audio')
  encoded.replace(dst)
async def main():
 ap=argparse.ArgumentParser();ap.add_argument('--levels',nargs='+',default=['n5','n4']);ap.add_argument('--limit',type=int,default=0);ap.add_argument('--offset',type=int,default=0);ap.add_argument('--chunk-size',type=int,default=100);ap.add_argument('--workers',type=int,default=4);ap.add_argument('--attempts',type=int,default=5);a=ap.parse_args()
 if not all(l in ['n5','n4','n3','n2','n1'] for l in a.levels) or a.workers<1 or a.chunk_size<1 or a.attempts<1 or a.offset<0 or a.limit<0:ap.error('invalid level/count')
 allwords=[w for l in a.levels for w in json.loads((ROOT/'data'/f'{l}.json').read_text())]
 words=allwords[a.offset:];words=words[:a.limit] if a.limit else words
 path=ROOT/'data/sources'/('audio-generation-'+'-'.join(a.levels)+'.json')
 result={'voice':VOICE,'input':'kana','sampleRate':24000,'channels':1,'bitrate':'32k','levels':a.levels,'requested':len(words),'offset':a.offset,'generated':0,'existing':0,'errors':[],'retryEvents':[],'chunkSize':a.chunk_size,'workers':a.workers,'status':'running','chunksCompleted':0}
 failures=0;started=time.monotonic()
 def dst(w):return ROOT/'audio'/f"n{w['level']}"/'w'/f"{w['id']}.mp3"
 def snapshot():
  result['available']=sum(dst(w).exists() and dst(w).stat().st_size>256 for w in allwords);result['totalLevelWords']=len(allwords);result['seconds']=round(time.monotonic()-started,1)
  temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
 async def worker(queue):
  nonlocal failures
  while not queue.empty() and failures<3:
   w=queue.get_nowait();target=dst(w);target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists() and target.stat().st_size>256:result['existing']+=1;queue.task_done();continue
   try:
    await retry(lambda:generate(w,target),attempts=a.attempts,on_error=lambda attempt,exc:result['retryEvents'].append({'id':w['id'],'attempt':attempt,'error':describe(exc)}))
    result['generated']+=1;failures=0
   except Exception as exc:
    result['errors'].append({'id':w['id'],'error':describe(exc)});failures+=1
   finally:
    queue.task_done();snapshot()
    if result['generated']%10==0 or failures:print(json.dumps({k:result[k] for k in ['generated','existing','available','totalLevelWords','seconds','status']},ensure_ascii=False),flush=True)
 for i in range(0,len(words),a.chunk_size):
  queue=asyncio.Queue()
  for w in words[i:i+a.chunk_size]:queue.put_nowait(w)
  await asyncio.gather(*(worker(queue) for _ in range(a.workers)))
  if failures>=3:result['status']='network-failed';break
  result['chunksCompleted']+=1;snapshot();print('CHUNK',result['chunksCompleted'],'available',result['available'],flush=True)
  await asyncio.sleep(1)
 else:result['status']='complete' if not result['errors'] else 'partial'
 snapshot();print(json.dumps(result,ensure_ascii=False),flush=True)
 return 0 if result['status']=='complete' else 1
if __name__=='__main__':raise SystemExit(asyncio.run(main()))
