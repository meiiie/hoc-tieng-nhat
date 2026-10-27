#!/usr/bin/env python3
"""Join candidate pools and preserve directly linked Vietnamese as an option."""
import csv
import json
import re
from collections import Counter, defaultdict
from mine import CACHE, ROOT, WORDS, analyze, score

pool = json.loads((CACHE / 'corpus-pool.json').read_text())
for ident, rows in json.loads((CACHE / 'extra-pool.json').read_text()).items():
    pool.setdefault(ident, []).extend(rows)
jids = {r['source_id'] for rs in pool.values() for r in rs if r['source'] == 'Tatoeba'}
vi = {}
with (ROOT.parent / 'src/tatoeba/vie.tsv').open() as f:
    for c in csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
        if c[3] not in ('', '\\N'):
            vi[int(c[0])] = {'id': int(c[0]), 'text': c[2], 'username': c[3],
                'url': 'https://tatoeba.org/sentences/show/' + c[0], 'licence': 'CC BY 2.0 FR',
                'machine': False, 'pivot': False}
links = defaultdict(set)
with (ROOT.parent / 'src/tatoeba/links.csv').open() as f:
    for line in f:
        a, b = map(int, line.split())
        if a in jids:
            links[a].add(b)
        if b in jids:
            links[b].add(a)
en_ids = set()
with (ROOT.parent / 'src/tatoeba/eng.tsv').open() as f:
    for c in csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
        if c[3] not in ('', '\\N'):
            en_ids.add(int(c[0]))
associations = defaultdict(list)
for row in json.loads((CACHE / 'jmdict-examples.json').read_text()):
    associations[row['source_id']].append(row)
for ident, rows in pool.items():
    for row in rows:
        if row['source'] == 'Tatoeba':
            sid = row['source_id']
            vis = links[sid] & vi.keys()
            if vis:
                vid = min(vis, key=lambda i: (len(vi[i]['text']), i))
                row['existingTranslation'] = {**vi[vid], 'links': [[sid, vid]]}
            row['original_rejection_reasons'] = (
                (['length>25'] if len(row['ja']) > 25 else []) +
                (['alternate-JMdict-spelling'] if row['match'].get('jmdictAlias') else []) +
                ([] if vis or links[sid] & en_ids else ['no-named-English-or-Vietnamese-link']))
            row['rejected_only_by_length'] = row['original_rejection_reasons'] == ['length>25']
            row['jmdict_example_links'] = [r for r in associations[str(sid)] if
                any('jpn' in a.values() and txt == row['ja'] for a, txt in r['sentences'])]
    unique = {(r['source'], str(r['source_id']), r['ja']): r for r in rows}
    def rank(r):
        ts = analyze(r['ja'])
        ts = [t for t in ts if t.get('pos1') != '補助記号']
        fragment = not ts or ts[-1].get('pos1') in ('名詞', '接尾辞', '接頭辞', '記号')
        return fragment, r['source'] != 'Tatoeba', *score(r)
    pool[ident] = sorted(unique.values(), key=rank)
(CACHE / 'review-pool.json').write_text(json.dumps(pool, ensure_ascii=False, indent=1) + '\n')
print('covered', len(pool), 'by level', dict(Counter(w['level'] for w in WORDS if w['id'] in pool)))
print('direct vi', sum(any(r.get('existingTranslation') and not r['existingTranslation']['machine'] for r in rows) for rows in pool.values()))
