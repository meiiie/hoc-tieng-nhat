"""Reproduce lemma, sense and conservative ruby evidence for all final decisions.
Run with .cache/content-venv/bin/python tests/final_examples.py.
This is a data/provenance gate, not an independent linguistic review.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'ex5')]
from example_lemmas import allowed, entries
from japanese_morphology import verify_dictionary
from phase_analyzer import evidence
from tatoeba import match_word
from integrate import runtime

read = lambda p: json.loads((ROOT / p).read_text())
manifest = read('ex5/final-stats.json')
for name, expected in manifest['input_sha256'].items():
    assert hashlib.sha256((ROOT / 'ex5' / name).read_bytes()).hexdigest() == expected
assert verify_dictionary() == read('ex5/input-manifest.json')['dictionary_binary_sha256']
words = {w['id']: w for w in read('ex5/missing-words.json')}
published = {w['id']: w for n in range(1, 6) for w in read(f'data/n{n}.json')}
levels = read('ex5/released-levels.json')
checked = 0
for decision in read('ex5/final.json'):
    row = decision['final_candidate'] or decision['rewrite_attempt']
    word = words[row['id']]
    m, sense = row['match'], row['sense']
    actual = entries()[word['jmdict']]['sense'][sense['index'] - 1]
    assert sense['jmdict'] == word['jmdict']
    assert sense['gloss'] == [g['text'] for g in actual['gloss']]
    assert sense['part_of_speech'] == actual['partOfSpeech']
    assert sense['misc'] == actual['misc']
    assert '*' in actual['appliesToKanji'] or word['kanji'] in actual['appliesToKanji']
    assert '*' in actual['appliesToKana'] or word['kana'] in actual['appliesToKana']
    assert row['ja'][m['start']:m['end']] == m['surface']
    if m['kind'] != 'phaseA-review':
        found = match_word(word, row['ja'])
        if not found and m.get('jmdictAlias'):
            alias = m['jmdictAlias']
            assert alias in allowed(word) or alias in [word['kana'], ''.join(chr(ord(c)+96) if 'ぁ' <= c <= 'ゖ' else c for c in word['kana'])]
            found = match_word({**word, 'kanji': alias}, row['ja'])
        assert found and all(found[k] == m[k] for k in ['start', 'end', 'surface', 'kind']), row['id']
    calculated, ann = evidence(word, row)
    assert row['analysis'] == calculated, row['id']
    assert all(row[k] == value for k, value in ann.items()), row['id']
    assert not calculated['unknown_target'], row['id']
    assert ''.join(s['base'] for s in row['furigana']) == row['ja']
    if word['level'] in levels and decision['final_candidate']:
        assert published[word['id']]['example'] == runtime(row), word['id']
    elif decision['final_status'] == 'dropped':
        assert published[word['id']]['example'] is None
    checked += 1
print(f'{checked} decisions: pinned inputs, target lemma/span, selected sense, ruby reproduction and released runtime passed; no native certification')
