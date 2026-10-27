"""TTS -> phoneme-recogniser round trip, step 1: logits for every MP3.
Usage: python3 tools/audio_roundtrip_logits.py <part> <parts> [model_dir] [out_dir]
model_dir holds onnx/model_q4.onnx from air-air/japanese-hubert-base-phoneme-ctc-v4-ONNX@a36617c."""
import json,sys,os,subprocess,numpy as np,onnxruntime as ort
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
part,n=int(sys.argv[1]),int(sys.argv[2]);MODEL=sys.argv[3] if len(sys.argv)>3 else str(ROOT.parent/'model');OUT=sys.argv[4] if len(sys.argv)>4 else str(ROOT.parent/'qabin')
s=ort.InferenceSession(MODEL+'/onnx/model_q4.onnx')
def load(path):return np.frombuffer(subprocess.run(['ffmpeg','-v','quiet','-i',path,'-f','f32le','-ac','1','-ar','16000','-'],capture_output=True).stdout,np.float32)
def run(x):x=np.concatenate([np.zeros(2400,np.float32),x,np.zeros(2400,np.float32)]);return s.run(None,{'input_values':x[None]})[0][0]
ws=[]
for lv in ['n5','n4','n3','n2','n1']: ws+=json.load(open(ROOT/f'data/{lv}.json'))
os.makedirs(OUT,exist_ok=True)
for i,w in enumerate(ws):
  if i%n!=part or not w.get('audio'): continue
  f=f'{OUT}/{w["id"]}.f32'
  if os.path.exists(f+'.shape'): continue
  lg=run(load(str(ROOT/w['audio'])));lg.astype(np.float32).tofile(f);open(f+'.shape','w').write(f'{lg.shape[0]} {lg.shape[1]}')
