#!/usr/bin/env python3
"""Release selected levels only; preserve every other field and existing example."""
import copy
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI_LABEL = 'Câu do AI viết, cần kiểm tra'
MACHINE_LABEL = 'bản dịch máy, cần kiểm tra'
SOURCES = {'Tatoeba': 'tatoeba', 'KFTT 1.0': 'kftt', 'Japanese Wiktionary': 'wiktionary', 'KNBC 1.0 (2009-09-25)': 'knbc'}


def translation(t):
    t = copy.deepcopy(t)
    for a, b in [('licence', 'license'), ('licence_url', 'licenseUrl')]:
        if a in t:
            t[b] = t.pop(a)
    t.setdefault('lang', 'vie')
    t.setdefault('pivot', False)
    for key in ['original', 'from', 'via']:
        if key in t:
            t[key] = translation(t[key])
    if t.get('lang') == 'vie' and 'machine' in t:
        t['label'] = MACHINE_LABEL if t['machine'] else ('dịch qua câu tiếng Anh' if t['pivot'] else 'bản dịch tiếng Việt trên Tatoeba')
    return t


def runtime(r):
    licensed = 'source' in r
    e = {'source': SOURCES[r['source']] if licensed else 'ai',
         'sourceName': r['source'] if licensed else 'OpenAI Codex',
         'label': r['source'] if licensed else AI_LABEL,
         'id': r['source_id'] if licensed else 'ai:' + r['id'],
         'lang': 'jpn', 'text': r['ja'], 'username': r['author'],
         'license': r['licence'] if licensed else 'CC BY-SA 4.0',
         'licenseUrl': r['licence_url'] if licensed else 'https://creativecommons.org/licenses/by-sa/4.0/',
         'match': r['match'], 'furigana': r['furigana'], 'nativeReviewed': False}
    if licensed:
        e.update(url=r['url'], changes=r['changes'], attribution=r['attribution'], translation=translation(r['translation']))
        for key in ['history_url', 'archive_url', 'archive_path', 'line', 'revision', 'page_title', 'original_ja']:
            if key in r:
                e[key] = r[key]
        if r.get('licence_file'):
            e['licenseFile'] = 'ex5/' + r['licence_file']
    else:
        e.update(changes='Japanese and Vietnamese authored by OpenAI Codex; assistant reviewed; no native-speaker review.',
                 attribution='OpenAI Codex (AI); CC BY-SA 4.0; method and review in docs/DATA.md and ex5/final.json.',
                 translation={'text': r['vi'], 'lang': 'vie', 'machine': True, 'pivot': False,
                    'translator': 'OpenAI Codex', 'license': 'CC BY-SA 4.0',
                    'licenseUrl': 'https://creativecommons.org/licenses/by-sa/4.0/', 'label': MACHINE_LABEL,
                    'method': 'Composed with the Japanese example by OpenAI Codex; assistant reviewed, not native reviewed.'})
    return e


if __name__ == '__main__':
    levels = [int(n) for n in sys.argv[1:]]
    assert levels and set(levels) <= {1, 2, 3, 4, 5}
    final = json.loads((ROOT / 'ex5/final.json').read_text())
    overlay_path = ROOT / 'data/sources/examples-v5.json'
    overlay = json.loads(overlay_path.read_text()) if overlay_path.exists() else {}
    old = json.loads((ROOT / 'data/sources/tatoeba-examples.json').read_text())
    for n in levels:
        path = ROOT / f'data/n{n}.json'
        words = json.loads(path.read_text())
        before = copy.deepcopy(words)
        by_id = {w['id']: w for w in words}
        for result in final:
            if result['level'] != n or result['final_status'] == 'dropped':
                continue
            ident = result['id']
            assert ident not in old, ident
            example = runtime(result['final_candidate'])
            assert by_id[ident]['example'] is None or by_id[ident]['example'] == example, ident
            by_id[ident]['example'] = example
            overlay[ident] = {**example, **{k: result['final_candidate'][k] for k in ['furiganaEvidence', 'furiganaSkipped']}}
        assert [{k: v for k, v in w.items() if k != 'example'} for w in words] == [{k: v for k, v in w.items() if k != 'example'} for w in before]
        path.write_text(json.dumps(words, ensure_ascii=False, indent=1) + '\n')
    overlay_path.write_text(json.dumps(overlay, ensure_ascii=False, indent=1) + '\n')
    published = sorted({w['level'] for n in range(1, 6) for w in json.loads((ROOT / f'data/n{n}.json').read_text()) if w['id'] in overlay}, reverse=True)
    (ROOT / 'ex5/released-levels.json').write_text(json.dumps(published) + '\n')
    meta = json.loads((ROOT / 'data/meta.json').read_text())
    meta['version'] = json.loads((ROOT / 'version.json').read_text())['version']
    counts = {}
    for n in range(5, 0, -1):
        ws = json.loads((ROOT / f'data/n{n}.json').read_text())
        es = [w['example'] for w in ws if w['example']]
        stats = meta['levels'][f'N{n}']
        stats.update(examples=len(es),
            exampleHumanDirect=sum(not e['translation']['machine'] and not e['translation']['pivot'] for e in es),
            exampleHumanPivot=sum(e['translation']['pivot'] for e in es),
            exampleMachine=sum(e['translation']['machine'] for e in es),
            exampleLemma=sum(e['match']['kind'] == 'lemma' for e in es))
        # Source evidence remains in final.json, outside lazy runtime payloads.
        evidence = {r['id']: r['final_candidate'] for r in final if r['final_candidate']}
        audit = [old.get(w['id']) or evidence[w['id']] for w in ws if w['example']]
        stats.update(furiganaFull=sum(bool(e['furiganaEvidence']) and not e['furiganaSkipped'] for e in audit),
            furiganaPartial=sum(bool(e['furiganaEvidence']) and bool(e['furiganaSkipped']) for e in audit),
            furiganaTokensSkipped=sum(len(e['furiganaSkipped']) for e in audit))
        counts[f'N{n}'] = {'words': len(ws), 'tatoeba_before': sum(w['id'] in old for w in ws),
            'new_licensed': dict(Counter(w['example']['sourceName'] for w in ws if w['id'] in overlay and w['example']['source'] != 'ai')),
            'ai_authored': sum(w['id'] in overlay and w['example']['source'] == 'ai' for w in ws),
            'still_missing': sum(w['example'] is None for w in ws)}
    (ROOT / 'data/meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1) + '\n')
    (ROOT / 'ex5/release-counts.json').write_text(json.dumps(counts, ensure_ascii=False, indent=2) + '\n')
    doc = ROOT / 'docs/DATA.md'
    text = doc.read_text()
    start, end = '<!-- examples-v5-counts:start -->', '<!-- examples-v5-counts:end -->'
    table = ['| Cấp | Tatoeba trước | Tatoeba mới | KFTT mới | Wiktionary mới | KNBC mới | AI mới | Còn thiếu |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for level, c in counts.items():
        new = c['new_licensed']
        table.append(f"| {level} | {c['tatoeba_before']} | {new.get('Tatoeba', 0)} | {new.get('KFTT 1.0', 0)} | {new.get('Japanese Wiktionary', 0)} | {new.get('KNBC 1.0 (2009-09-25)', 0)} | {c['ai_authored']} | {c['still_missing']} |")
    a, b = text.index(start) + len(start), text.index(end)
    doc.write_text(text[:a] + '\n' + '\n'.join(table) + '\n' + text[b:])
    subprocess.run(['python3', str(ROOT / 'tools/build-index.py')], check=True)
    print(json.dumps(counts, ensure_ascii=False, indent=2))
