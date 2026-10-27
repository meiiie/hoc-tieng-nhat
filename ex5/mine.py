#!/usr/bin/env python3
"""Read-only Phase A mining. Outputs scratch, never the app's source overlays."""
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from example_lemmas import allowed, candidates_for
from japanese_morphology import analyze, verify_dictionary
from tatoeba import match_word, sentences

CACHE = ROOT / '.cache/ex5'
WORDS = json.loads((ROOT / 'ex5/missing-words.json').read_text())
BY_ID = {w['id']: w for w in WORDS}
FORMS, LEMMAS = defaultdict(list), defaultdict(list)
for w in WORDS:
    for f in set([w['kanji'], w['kana'], *allowed(w)]):
        FORMS[f].append(w)
    if 'động từ' in w['pos'] or 'tính từ' in w['pos']:
        for f in allowed(w):
            LEMMAS[f].append(w)


def matches(text):
    ts = analyze(text)
    candidates = candidates_for(ts, LEMMAS)
    for i in range(len(ts)):
        for j in range(i, min(i + 10, len(ts))):
            for w in FORMS.get(text[ts[i]['start']:ts[j]['end']], []):
                candidates[w['id']] = w
    for ident, w in candidates.items():
        m = match_word(w, text)
        alias = None
        if not m:
            for alias in sorted(allowed(w)):
                if alias == w['kanji'] or alias not in text:
                    continue
                m = match_word({**w, 'kanji': alias}, text)
                if m:
                    break
        if m:
            yield ident, {**m, **({'jmdictAlias': alias} if alias else {})}


def eligible(text):
    return 4 <= len(text) <= 35 and bool(re.search('[。！？!?]$', text)) and not re.search(r'[\s<>\[\]{}]', text)


def score(r):
    t = r.get('existingTranslation') or {}
    tier = 0 if t and not t.get('machine') and not t.get('pivot') else 1 if t and not t.get('machine') else 2
    return tier, len(r['ja']) > 25, len(r['ja']), str(r['source_id'])


def main():
    verify_dictionary()
    excluded = json.loads((ROOT / 'data/sources/tatoeba-exclusions.json').read_text())
    prior = json.loads((ROOT / '.cache/tatoeba-linked.json').read_text())
    translations = {s['id']: s['translation'] for s in prior}
    result = defaultdict(list)
    counts = Counter()
    for s in sentences(ROOT.parent / 'src/tatoeba/jpn.tsv', 'jpn'):
        counts['tatoeba_named'] += 1
        if str(s['id']) in excluded or not eligible(s['text']):
            continue
        counts['tatoeba_eligible'] += 1
        for ident, m in matches(s['text']):
            result[ident].append({'id': ident, 'level': BY_ID[ident]['level'], 'ja': s['text'],
                'source': 'Tatoeba', 'source_id': s['id'], 'url': s['url'],
                'author': s['username'], 'licence': 'CC BY 2.0 FR',
                'licence_url': 'https://creativecommons.org/licenses/by/2.0/fr/',
                'match': m, 'existingTranslation': translations.get(s['id']),
                'selection_change': 'length-26-35' if len(s['text']) > 25 else
                    'JMdict-spelling-alias' if m.get('jmdictAlias') else 'no-linked-translation-required'})
            counts['tatoeba_matched_pairs'] += 1
        if counts['tatoeba_named'] % 50000 == 0:
            print('Tatoeba', counts['tatoeba_named'], 'covered', len(result), flush=True)
    for ident in result:
        result[ident] = sorted(result[ident], key=score)[:8]
    print('Tatoeba coverage', len(result), flush=True)
    (CACHE / 'tatoeba-pool.json').write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    for p in sorted((CACHE / 'kftt-data-1.0/data/orig').glob('*.ja')):
        for n, (ja, en) in enumerate(zip(p.read_text().splitlines(), p.with_suffix('.en').read_text().splitlines()), 1):
            counts['kftt_lines'] += 1
            if not eligible(ja):
                continue
            counts['kftt_eligible'] += 1
            for ident, m in matches(ja):
                result[ident].append({'id': ident, 'level': BY_ID[ident]['level'], 'ja': ja,
                    'source': 'KFTT 1.0', 'source_id': p.name + ':' + str(n),
                    'url': 'https://www.phontron.com/kftt/',
                    'archive_url': 'https://www.phontron.com/kftt/download/kftt-data-1.0.tar.gz',
                    'archive_path': 'kftt-data-1.0/data/orig/' + p.name, 'line': n,
                    'author': 'Japanese Wikipedia contributors; NICT; Graham Neubig (KFTT)',
                    'licence': 'CC BY-SA 3.0', 'licence_url': 'https://creativecommons.org/licenses/by-sa/3.0/',
                    'en': en, 'match': m, 'selection_change': 'new-corpus'})
                counts['kftt_matched_pairs'] += 1
    for ident in result:
        rows = result[ident]
        # Retain choices from both corpora for editorial selection.
        result[ident] = sorted([r for r in rows if r['source'] == 'Tatoeba'], key=score)[:5] + sorted(
            [r for r in rows if r['source'] != 'Tatoeba'], key=score)[:4]
    (CACHE / 'corpus-pool.json').write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    counts['covered'] = len(result)
    counts['covered_by_level'] = dict(Counter(BY_ID[k]['level'] for k in result))
    (CACHE / 'mining-counts.json').write_text(json.dumps(counts, indent=2) + '\n')
    print(json.dumps(counts), flush=True)


if __name__ == '__main__':
    main()
