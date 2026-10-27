#!/usr/bin/env python3
"""Validate Phase A provenance/coverage/ruby, without writing application data.

Run from the repository root with .cache/content-venv/bin/python ex5/validate.py.
Requires the pinned external inputs listed in input-manifest.json. A successful
run is structural/provenance verification, not a native-language certification.
"""
import csv
import hashlib
import html
import json
import re
import subprocess
import sys
import tarfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from example_lemmas import entries
from japanese_morphology import HAN, verify_dictionary
from tatoeba import match_word
from phase_analyzer import evidence


def read(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


manifest = read('ex5/input-manifest.json')
assert verify_dictionary() == manifest['dictionary_binary_sha256']
for item in manifest['files']:
    path = ROOT / item['path']
    assert path.stat().st_size == item['bytes'], item['path']
    assert sha(path) == item['sha256'], item['path']
print('Input hashes verified:', len(manifest['files']), flush=True)

words = read('ex5/missing-words.json')
by_id = {w['id']: w for w in words}
baseline = [w for n in range(5, 0, -1) for w in read(f'data/n{n}.json') if not w.get('example')]
assert len(words) == len(by_id) == len(baseline) == 1409
assert [{k: v for k, v in w.items() if k != 'senses'} for w in words] == baseline
assert Counter(w['level'] for w in words) == {5: 35, 4: 14, 3: 50, 2: 305, 1: 1005}
licensed, authored = read('ex5/licensed-candidates.json'), read('ex5/authored.json')
rows = licensed + authored
assert len(rows) == len({r['id'] for r in rows}) == 1409
assert {r['id'] for r in rows} == by_id.keys()
assert not ({r['id'] for r in licensed} & {r['id'] for r in authored})
decisions = (ROOT / 'ex5/editorial-decisions.tsv').read_text().splitlines()
assert len(decisions) == 1409
assert {int(r.split('|')[0]) for r in decisions} == set(range(1409))
assert {words[int(r.split('|')[0])]['id'] for r in decisions if r.split('|')[1] == 'L'} == {r['id'] for r in licensed}

for r in rows:
    w = by_id[r['id']]
    assert r['level'] == w['level']
    assert r['vi'].strip() and r['ja'].strip() and r['target_surface'] in r['ja'], r['id']
    assert re.search('[。！？!?]$', r['ja']), r['id']
    assert r['native_reviewed'] is False
    s = entries()[w['jmdict']]['sense'][r['sense']['index'] - 1]
    assert r['sense']['jmdict'] == w['jmdict'] and r['sense']['index_base'] == 1
    assert r['sense']['index'] in [s0['index'] for s0 in w['senses']], r['id']
    assert r['sense']['gloss'] == [g['text'] for g in s['gloss']], r['id']
    for key, original in [('part_of_speech', 'partOfSpeech'), ('misc', 'misc'),
                          ('applies_to_kanji', 'appliesToKanji'), ('applies_to_kana', 'appliesToKana')]:
        assert r['sense'][key] == s[original], (r['id'], key)
    assert '*' in s['appliesToKanji'] or w['kanji'] in s['appliesToKanji']
    assert '*' in s['appliesToKana'] or w['kana'] in s['appliesToKana']
    m = r['match']
    assert r['ja'][m['start']:m['end']] == m['surface']
    # A noun/adverb's exact match may omit the authored usage's した ending;
    # a verb match may include an auxiliary beyond the authored lexical span.
    spans = [(i, i + len(r['target_surface'])) for i in range(len(r['ja']))
             if r['ja'].startswith(r['target_surface'], i)]
    assert any((a <= m['start'] and m['end'] <= b) or
               (m['start'] <= a and b <= m['end']) for a, b in spans), (r['id'], m)
    if m['kind'] != 'phaseA-review':
        matched = match_word(w, r['ja'])
        if not matched and m.get('jmdictAlias'):
            matched = match_word({**w, 'kanji': m['jmdictAlias']}, r['ja'])
        assert matched and all(matched[k] == m[k] for k in ('start', 'end', 'surface', 'kind')), r['id']
    calculated, ruby = evidence(w, r)
    assert calculated == r['analysis'], r['id']
    assert not calculated['unknown_target'], r['id']
    assert all(r[key] == value for key, value in ruby.items()), r['id']
    assert ''.join(sg['base'] for sg in r['furigana']) == r['ja']
    position = 0
    for sg in r['furigana']:
        end = position + len(sg['base'])
        assert sg['base']
        if 'ruby' in sg:
            assert re.fullmatch(HAN + '+', sg['base']) and re.fullmatch('[ぁ-ゖー]+', sg['ruby'])
            assert any(e['start'] <= position and end <= e['end'] for e in r['furiganaEvidence'])
            if not calculated['strict_match']:
                assert not (position < m['end'] and end > m['start']), r['id']
        position = end
    if r in authored:
        assert len(r['ja']) <= 25 and r['rationale'].strip() and r['machine'] is True
    else:
        assert len(r['ja']) <= 35 and r['author'] and r['url'] and r['attribution'] and r['licence_url']
        assert r['vi'] == r['translation']['text'] and r['machine'] == r['translation']['machine']

print('Coverage, senses, target evidence and ruby verified: 1409', flush=True)

def detailed(name, wanted):
    found = {}
    with (ROOT.parent / 'src/tatoeba' / name).open() as f:
        for c in csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
            if int(c[0]) in wanted:
                found[int(c[0])] = c
    assert set(found) == wanted
    return found


tatoeba = [r for r in licensed if r['source'] == 'Tatoeba']
jp = detailed('jpn.tsv', {r['source_id'] for r in tatoeba})
human = [r['translation'] for r in licensed if not r['machine']]
vi = detailed('vie.tsv', {r['id'] for r in human})
needed_links = {tuple(link) for t in human for link in t['links']}
found_links = set()
with (ROOT.parent / 'src/tatoeba/links.csv').open() as f:
    for line in f:
        edge = tuple(map(int, line.split()))
        if edge in needed_links:
            found_links.add(edge)
        if edge[::-1] in needed_links:
            found_links.add(edge[::-1])
assert needed_links == found_links
excluded = read('data/sources/tatoeba-exclusions.json')
for r in tatoeba:
    c = jp[r['source_id']]
    assert r['ja'] == c[2] and r['author'] == c[3] and c[3] not in ('', '\\N')
    assert str(r['source_id']) not in excluded
    assert r['url'] == 'https://tatoeba.org/sentences/show/' + c[0]
    assert r['licence'] == 'CC BY 2.0 FR'
for t in human:
    c = vi[t['id']]
    assert t['text'] == c[2] and t['username'] == c[3] and c[3] not in ('', '\\N')

with tarfile.open(ROOT / '.cache/ex5/kftt-data-1.0.tar.gz') as corpus:
    memo = {}
    for r in licensed:
        if r['source'] != 'KFTT 1.0':
            continue
        path = r['archive_path']
        if path not in memo:
            memo[path] = corpus.extractfile(path).read().decode().splitlines()
            memo[path[:-3] + '.en'] = corpus.extractfile(path[:-3] + '.en').read().decode().splitlines()
        assert r['ja'] == memo[path][r['line'] - 1]
        assert r['en'] == memo[path[:-3] + '.en'][r['line'] - 1]
        assert r['source_id'] == Path(path).name + ':' + str(r['line'])
        assert r['licence'] == 'CC BY-SA 3.0'

pages = {}
for path in (ROOT / '.cache/ex5/wiktionary').glob('*.json'):
    for page in json.loads(path.read_text())['query']['pages'].values():
        if 'revisions' in page:
            pages[(page['pageid'], page['revisions'][0]['revid'])] = page
for r in licensed:
    if r['source'] != 'Japanese Wiktionary':
        continue
    p = pages[(r['page_id'], r['revision'])]
    rev = p['revisions'][0]
    raw = rev['slots']['main']['*'].splitlines()[r['line'] - 1]
    assert raw == r['source_wikitext'] and p['title'] == r['page_title']
    assert rev['timestamp'] == r['revision_timestamp']
    assert r['url'].endswith('oldid=' + str(r['revision']))
    assert re.match(r'^#[:*][^:*#]', raw)
    s = re.sub(r'^#[:*]\s*', '', raw)
    assert not re.search(r'\{\{|<|https?://|『|』|（|\(|\[\[w:|—|--|―', s)
    s = re.sub(r'\[\[([^\[\]]+)\]\]', lambda m: m[1].split('|')[-1], s)
    s = html.unescape(s.replace("'''", '').replace("''", '')).strip()
    assert s == r['ja'] and r['licence'] == 'CC BY-SA 4.0'

with tarfile.open(ROOT / '.cache/ex5/KNBC_v1.0_090925.tar.bz2') as corpus:
    for r in licensed:
        if not r['source'].startswith('KNBC'):
            continue
        raw = corpus.extractfile(r['archive_path']).read().decode('euc_jp')
        assert '括弧' not in raw
        lines = raw.splitlines()
        s = ''.join(line.split(' ', 1)[0] for line in lines if line and line[0] not in '#*+@' and line != 'EOS')
        assert s == r['ja'] and re.search(r'S-ID:(\S+)', lines[0])[1] == r['source_id']
        assert r['licence'] == 'BSD-3-Clause (Japanese text)'
    assert corpus.extractfile('KNBC_v1.0_090925/README.txt').read().decode('euc_jp') == (ROOT / 'ex5/licences/KNBC-README.txt').read_text()
assert {r['source'] for r in licensed} == {'Tatoeba', 'KFTT 1.0', 'Japanese Wiktionary', 'KNBC 1.0 (2009-09-25)'}
print('Sentence provenance and existing human Vietnamese verified:', len(licensed), flush=True)

subprocess.run(['git', 'diff', '--exit-code', manifest['baseline_commit'], '--', '.', ':!ex5'], cwd=ROOT, check=True, capture_output=True)
status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True)
assert all(line[3:].startswith('ex5/') for line in status.splitlines()), status
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'examples-v5'
summary = {'scope': 'Phase A only; structural/provenance checks passed; native-language review not performed',
    'baseline_commit': manifest['baseline_commit'], 'outside_ex5_unchanged': True,
    'total': len(rows), 'licensed': len(licensed), 'authored': len(authored),
    'by_level': {str(n): {'licensed': sum(r['level'] == n for r in licensed), 'authored': sum(r['level'] == n for r in authored)} for n in range(5, 0, -1)},
    'sources': dict(Counter(r['source'] for r in licensed)),
    'existing_human_vi': len(human), 'licensed_machine_vi': sum(r['machine'] for r in licensed),
    'optional_machine_vi_refinements': sum('vi_refinement' in r for r in licensed),
    'authored_machine_vi': len(authored), 'native_reviewed': 0,
    'analysis': dict(Counter(r['analysis']['status'] for r in rows)),
    'all_targets_machine_confirmed': all(r['analysis']['lemma_confirmed'] for r in rows),
    'targets_without_machine_confirmation': [r['id'] for r in rows if not r['analysis']['lemma_confirmed']],
    'ruby_sentences': sum(any('ruby' in s for s in r['furigana']) for r in rows),
    'ruby_spans': sum(sum('ruby' in s for s in r['furigana']) for r in rows),
    'max_authored_characters': max(map(lambda r: len(r['ja']), authored)),
    'max_licensed_characters': max(map(lambda r: len(r['ja']), licensed)),
    'licensed_over_25': sum(len(r['ja']) > 25 for r in licensed),
    'tatoeba_length_only': sum(r.get('rejected_only_by_length', False) for r in licensed),
    'distinct_japanese': len({r['ja'] for r in rows}),
    'candidate_sha256': {name: sha(ROOT / 'ex5' / name) for name in ('licensed-candidates.json', 'authored.json')}}
(ROOT / 'ex5/validation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'targets_without_machine_confirmation'}, ensure_ascii=False, indent=2))
