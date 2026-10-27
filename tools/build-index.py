#!/usr/bin/env python3
"""Small startup catalogue; full word records stay byte-for-byte in n1..n5.json."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_index():
    files, levels = {}, {}
    for n in [5, 4, 3, 2, 1]:
        name = f'data/n{n}.json'
        raw = (ROOT / name).read_bytes()
        words = json.loads(raw)
        assert all(w['level'] == n for w in words)
        # The audio path can be reconstructed, but never assume audio exists.
        assert all(not w['audio'] or w['audio'] == f"audio/n{n}/w/{w['id']}.mp3" for w in words)
        levels[str(n)] = {'ids': [w['id'] for w in words],
                          'withoutAudio': [w['id'] for w in words if not w['audio']]}
        files[name] = {'revision': hashlib.sha256(raw).hexdigest()[:16], 'bytes': len(raw)}
    raw = (ROOT / 'data/kanji.json').read_bytes()
    files['data/kanji.json'] = {'revision': hashlib.sha256(raw).hexdigest()[:16], 'bytes': len(raw)}
    ids = [i for level in levels.values() for i in level['ids']]
    assert len(ids) == len(set(ids))
    (ROOT / 'data/index.json').write_text(json.dumps({'levels': levels, 'files': files},
        ensure_ascii=False, separators=(',', ':')) + '\n')


if __name__ == '__main__':
    build_index()
