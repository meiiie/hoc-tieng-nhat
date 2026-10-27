#!/usr/bin/env python3
"""Local, offline MT drafts for attributed English-linked examples; no agent/network.

Writes candidates outside release data. Read Japanese/English/Vietnamese together,
correct or exclude unsuitable candidates, then import into the durable source TSV.
All resulting translations remain machine:true and require native-speaker review.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('selection', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'.cache/example-mt-drafts.json')
    args = parser.parse_args()
    selected = json.loads(args.selection.read_text())
    existing = {int(r['id']) for r in csv.DictReader(
        (ROOT/'data/sources/tatoeba-vi-machine.tsv').open(), delimiter='\t')}
    work = {e['id']: e for e in selected.values()
            if e['translation']['machine'] and e['id'] not in existing}
    model = ROOT/'.cache/opus-en-vi'
    tokenizer = AutoTokenizer.from_pretrained(model, local_files_only=True)
    torch.set_num_threads(1)
    translator = AutoModelForSeq2SeqLM.from_pretrained(model, local_files_only=True).eval()
    rows = json.loads(args.output.read_text()) if args.output.exists() else {}
    pending = [e for k, e in sorted(work.items()) if str(k) not in rows]
    for start in range(0, len(pending), 24):
        batch = pending[start:start+24]
        tokens = tokenizer(['>>vie<< '+e['translation']['from']['text'] for e in batch],
                           return_tensors='pt', padding=True, truncation=False)
        with torch.inference_mode():
            generated = translator.generate(**tokens, num_beams=4, max_new_tokens=128)
        results = tokenizer.batch_decode(generated, skip_special_tokens=True)
        for e, result in zip(batch, results):
            text = result.strip()
            assert text, ('empty draft', e['id'])
            rows[str(e['id'])] = {'ja': e['text'], 'en': e['translation']['from']['text'],
                                 'vi': text, 'reviewed': False}
        args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=1)+'\n')
        print(min(start+24, len(pending)), '/', len(pending), 'drafted', flush=True)
    manifest = {'model': 'Helsinki-NLP/opus-mt-en-vi', 'modelLicense': 'Apache-2.0',
                'modelUrl': 'https://huggingface.co/Helsinki-NLP/opus-mt-en-vi',
                'engine': 'Transformers '+transformers.__version__+' / PyTorch '+torch.__version__+' float32 CPU',
                'languageToken': '>>vie<<', 'decoderStartToken': tokenizer.convert_ids_to_tokens(translator.config.decoder_start_token_id),
                'beamSize': 4, 'batchSize': 24, 'maxNewTokens': 128,
                'drafts': len(rows), 'review': 'Candidates only; no native-speaker review',
                'hashes': {str(p.relative_to(ROOT/'.cache')): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in [model/'pytorch_model.bin', model/'source.spm', model/'target.spm',
                                     model/'vocab.json', model/'config.json']}}
    args.output.with_suffix('.method.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
