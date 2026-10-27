#!/usr/bin/env python3
"""Resumable Nanami audio generation. Aborts after three consecutive network failures.
Existing successful files are preserved. Re-run build-data.py afterwards to bind real files.
"""
import argparse, asyncio, json, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
async def main():
 ap=argparse.ArgumentParser();ap.add_argument('--levels',nargs='+',default=['n5','n4']);ap.add_argument('--limit',type=int,default=0);a=ap.parse_args()
 words=[w for l in a.levels for w in json.loads((ROOT/'data'/f'{l}.json').read_text())];words=words[:a.limit] if a.limit else words
 result={'voice':'ja-JP-NanamiNeural','requested':len(words),'generated':0,'existing':0,'errors':[],'bitrate':'32k','status':'running'};failures=0
 for w in words:
  dst=ROOT/'audio'/f"n{w['level']}"/'w'/f"{w['id']}.mp3";dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists() and dst.stat().st_size>256:result['existing']+=1;continue
  with tempfile.TemporaryDirectory() as td:
   raw=Path(td)/'raw.mp3'
   proc=await asyncio.create_subprocess_exec('/home/box/.local/bin/edge-tts','--voice',result['voice'],'--text',w['kana'],'--write-media',str(raw),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   try:
    stdout,stderr=await asyncio.wait_for(proc.communicate(),timeout=35)
    if proc.returncode or not raw.exists() or raw.stat().st_size<256:raise RuntimeError(stderr.decode()[-700:])
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-ac','1','-ar','24000','-b:a','32k',str(dst)],check=True)
    result['generated']+=1;failures=0
   except Exception as e:
    if proc.returncode is None:proc.kill();await proc.wait()
    result['errors'].append({'id':w['id'],'error':str(e) or 'timeout'});failures+=1
   print(json.dumps({k:v for k,v in result.items() if k!='errors'},ensure_ascii=False),flush=True)
   (ROOT/'data/sources/audio-generation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
   if failures>=3:result['status']='network-failed';break
 else:result['status']='complete'
 (ROOT/'data/sources/audio-generation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':asyncio.run(main())
