#!/usr/bin/env python3
"""Record Phase A inputs. Run once after research; validation verifies hashes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = []


def record(path, role, url=None):
    path = Path(path)
    with path.open('rb') as f:
        sha = hashlib.file_digest(f, 'sha256').hexdigest()
    files.append({'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT)
                  else '../' + str(path.relative_to(ROOT.parent)),
                  'bytes': path.stat().st_size, 'sha256': sha, 'role': role,
                  **({'url': url} if url else {})})


for name in ('jpn.tsv', 'vie.tsv', 'eng.tsv', 'links.csv'):
    record(ROOT.parent / 'src/tatoeba' / name, 'supplied detailed Tatoeba export', 'https://tatoeba.org/en/downloads')
record(ROOT.parent / 'src/jmdict-eng-3.6.2.json', 'selected senses: jmdict-simplified 3.6.2, dictionary date 2026-10-26', 'https://github.com/scriptin/jmdict-simplified')
for name, url in (
    ('JMdict_e_examp.gz', 'https://www.edrdg.org/pub/Nihongo/JMdict_e_examp.gz'),
    ('kftt-data-1.0.tar.gz', 'https://www.phontron.com/kftt/download/kftt-data-1.0.tar.gz'),
    ('KNBC_v1.0_090925.tar.bz2', 'https://nlp.ist.i.kyoto-u.ac.jp/kuntt/KNBC_v1.0_090925.tar.bz2')):
    record(ROOT / '.cache/ex5' / name, 'downloaded corpus archive', url)
for path in sorted((ROOT / '.cache/ex5/wiktionary').glob('*.json')):
    record(path, 'fixed Wiktionary revisions returned by API', 'https://ja.wiktionary.org/w/api.php')
for name in ('review-pool.json', 'jmdict-examples.json', 'mining-counts.json', 'extra-counts.json'):
    record(ROOT / '.cache/ex5' / name, 'local reproducibility input')
for name in ('tatoeba.py', 'example_lemmas.py', 'japanese_morphology.py'):
    record(ROOT / 'tools' / name, 'unchanged existing analyzer')
for name in ('tatoeba-exclusions.json', 'tatoeba-examples.json'):
    record(ROOT / 'data/sources' / name, 'unchanged baseline example data')
out = {'checked_on': '2026-10-27', 'baseline_commit': 'cceba8b696feb5dce1fb7caa233653aa05775b48',
       'dictionary_binary_sha256': '122c4c91f026bf4b65bbe2dfd8b9f8eeb6ab56d8eb2a7287a68bca75708ba513',
       'files': files}
(ROOT / 'ex5/input-manifest.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print('Recorded', len(files), 'input hashes')
