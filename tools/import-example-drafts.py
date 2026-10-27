#!/usr/bin/env python3
"""Import explicitly labelled MT candidates and separately recorded AI spot checks.

No candidate is represented as a human translation or native-speaker reviewed.
Existing translations are preserved. Final example application checks completeness.
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('selection', type=Path)
    p.add_argument('drafts', type=Path)
    p.add_argument('--corrections', type=Path, required=True)
    p.add_argument('--reviewed', type=Path, required=True)
    args = p.parse_args()
    selected = {str(e['id']): e for e in json.loads(args.selection.read_text()).values()
                if e['translation']['machine']}
    drafts = json.loads(args.drafts.read_text())
    corrections = json.loads(args.corrections.read_text())
    reviewed = set(json.loads(args.reviewed.read_text()))
    assert set(corrections) <= reviewed, 'Every correction must have a review record'
    path = ROOT/'data/sources/tatoeba-vi-machine.tsv'
    rows = {r['id']: r for r in csv.DictReader(path.open(), delimiter='\t')}
    method_path = ROOT/'data/sources/tatoeba-machine-methods.json'
    methods = json.loads(method_path.read_text()) if method_path.exists() else {}
    for ident, e in selected.items():
        if ident in rows:
            continue
        d = drafts[ident]
        assert d['ja'] == e['text'] and d['en'] == e['translation']['from']['text'], ident
        vi = re.sub(r'\s+', ' ', corrections.get(ident, d['vi'])).strip()
        assert vi and '<unk>' not in vi and len(vi) < 600, ident
        rows[ident] = {'id': ident, 'vi': vi}
        status = ('corrected by Codex (AI), compared with Japanese' if ident in corrections
                  else 'spot-checked by Codex (AI) against Japanese' if ident in reviewed
                  else 'not individually reviewed against Japanese')
        methods[ident] = {'translator': 'Helsinki-NLP/opus-mt-en-vi (AI)'+(' + Codex (AI)' if ident in corrections else ''),
                          'method': 'Local machine translation of linked English; '+status+'; not native-speaker verified',
                          'aiSpotChecked': ident in reviewed, 'aiCorrected': ident in corrections,
                          'nativeReviewed': False, 'englishSentence': e['translation']['from']['id']}
    with path.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'vi'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows.values())
    method_path.write_text(json.dumps(methods, ensure_ascii=False, indent=1)+'\n')
    manifest = json.loads(args.drafts.with_suffix('.method.json').read_text())
    manifest.update({'importedUniqueSentences': len(methods),
                     'aiSpotChecked': sum(m['aiSpotChecked'] for m in methods.values()),
                     'aiCorrected': sum(m['aiCorrected'] for m in methods.values()),
                     'nativeReviewed': 0,
                     'review': 'Only listed IDs spot-checked/corrected by Codex; all other MT is explicitly unreviewed. All machine:true.'})
    (ROOT/'data/sources/tatoeba-machine-method.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: manifest[k] for k in ['importedUniqueSentences', 'aiSpotChecked', 'aiCorrected', 'nativeReviewed']}))


if __name__ == '__main__':
    main()
