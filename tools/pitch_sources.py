#!/usr/bin/env python3
"""Extract licensed lexical accents, never compute compound/inflection accents.

Authoring only: fugashi==1.5.2, unidic-lite==1.0.8. The ordinary data build
uses the reviewed JSON overlay and does not require these dependencies.
"""
import argparse
import hashlib
import importlib.metadata
import json
import re
import subprocess
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KANJIUM_COMMIT = '9ebca4589565c696e7c39e089e2e928ad65f678c'
KANJIUM_SHA256 = {'README.md': '2ca73c9cfbe45f9e49db5ab80d514686a34dbcecde0b95040468c0da8ecde94f', 'LICENSE.txt': '638cc6f2d958b1add3883e8d5d73e32ae999ecdc0a4b4d1a83994b3d5b8e69e9', 'data/source_files/0_README.txt': '5d418ca98a4b6b178955a6578949e79f337bc8d9c97b9075bd7317c7512a8439', 'data/source_files/raw/accents.txt': '8bd0dd127dab32ceec94cb03ab1ba6b68858ea73421dfa1731af2f373deb4f20', 'data/source_files/edict.txt': '785dda9a80b982d0cd5e56966572b1488c8e0890961318c1a9ce54d0f6c636e0', 'data/source_files/jukugo.txt': '4a7a9b7c60e235f5050fca95cfadf1c31dc036285ad209313cde3ef0d41ad5bf', 'data/source_files/compverbs.txt': 'f869a6ae377567fe5627e4a0c53c48c8e0cf54c363861e091742ffd5aa64c13a', 'data/source_files/yojijukugo.txt': '6da38b5ac667f47ebec7d57b469264276034586f9432f1b16eb3b73d7a024114'}
UNIDIC_SHA256 = '122c4c91f026bf4b65bbe2dfd8b9f8eeb6ab56d8eb2a7287a68bca75708ba513'
KANJIUM_FILES = ['README.md', 'LICENSE.txt', 'data/source_files/0_README.txt',
                 'data/source_files/raw/accents.txt', *[
                     f'data/source_files/{name}.txt'
                     for name in ['edict', 'jukugo', 'compverbs', 'yojijukugo']]]


def hira(text):
    return ''.join(chr(ord(c)-96) if 'ァ' <= c <= 'ヶ' else c
                   for c in unicodedata.normalize('NFKC', text))


def parse_accents(text):
    if not re.fullmatch(r'\d+(?:,\d+)*', text):
        return None
    return list(dict.fromkeys(map(int, text.split(','))))


def choose_unidic(tagger, form, reading, lemmas):
    """Read all matching lexical nodes; refuse differing ordered accent lists."""
    lemmas = {hira(s) for s in lemmas}
    candidates = []
    for node in tagger.parseToNodeList(form):
        if node.is_unk or node.surface != form:
            continue  # unknown-node display defaults to 0; never trust it
        f = node.feature
        lemma = re.sub(r'-[A-Za-z].*$', '', f.lemma)  # UniDic loanword origin suffix
        if (f.orth != form or f.orthBase != form or
                hira(f.kana) != hira(reading) or hira(f.kanaBase) != hira(reading) or
                hira(lemma) not in lemmas or f.aModeType != '*'):
            continue
        accent = parse_accents(f.aType)
        if accent is not None:
            record = {'surface': node.surface, 'features': f._asdict()}
            if record not in candidates:
                candidates.append(record)
    values = {tuple(parse_accents(r['features']['aType'])) for r in candidates}
    if len(values) != 1:
        return None
    return {'pitch': list(next(iter(values))), 'records': candidates}


def allowed_lemmas(word, entry):
    readings = [r for r in entry['kana'] if hira(r['text']) == hira(word['kana'])]
    # A reading alone may name a different lexeme (e.g. 総/そう versus ソウ,
    # a personal name). Authorize actual spellings, never a reading alias.
    return {word['kanji']} | {
        k['text'] for k in entry['kanji']
        if any('*' in r['appliesToKanji'] or k['text'] in r['appliesToKanji'] for r in readings)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def main():
    import fugashi
    import unidic_lite
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--download', action='store_true', help='fetch pinned Kanjium files into .cache')
    ap.add_argument('--output', type=Path, help='default: data/sources/pitch-additions.json')
    args = ap.parse_args()
    root = args.root.resolve()
    cache = root/'.cache/pitch-research'
    output = args.output or root/'data/sources/pitch-additions.json'
    manifest = {'commit': KANJIUM_COMMIT, 'files': {}}
    for name in KANJIUM_FILES:
        path = cache/name
        url = f'https://raw.githubusercontent.com/mifunetoshiro/kanjium/{KANJIUM_COMMIT}/{name}'
        if args.download:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(urllib.request.urlopen(url, timeout=40).read())
        assert sha(path) == KANJIUM_SHA256[name], f'Changed Kanjium input: {name}'
        manifest['files'][name] = {'url': url, 'bytes': path.stat().st_size, 'sha256': sha(path)}
    assert (cache/'data/source_files/raw/accents.txt').read_bytes() == (root.parent/'src/accents.txt').read_bytes()
    dic = Path(unidic_lite.DICDIR)
    assert sha(dic/'sys.dic') == UNIDIC_SHA256, 'Unexpected dictionary; review before using a different version'
    assert importlib.metadata.version('unidic-lite') == '1.0.8'
    assert importlib.metadata.version('fugashi') == '1.5.2'

    # Select gaps using the original Kanjium input, so rerunning after a build is stable.
    original = set()
    for line in (root.parent/'src/accents.txt').read_text().splitlines():
        cols = line.split('\t')
        if len(cols) >= 3 and re.findall(r'(?<![\w])\d+', cols[2]):
            original.add((cols[0], hira(cols[1])))
    words = [w for n in range(5, 0, -1) for w in json.loads((root/f'data/n{n}.json').read_text())
             if (w['kanji'], hira(w['kana'])) not in original]
    jm = {x['id']: x for x in json.loads((root.parent/'src/jmdict-eng-3.6.2.json').read_text())['words']}
    extra = defaultdict(list)
    for name in ['edict', 'jukugo', 'compverbs', 'yojijukugo']:
        filename = f'data/source_files/{name}.txt'
        for number, line in enumerate((cache/filename).read_text().splitlines(), 1):
            row = line.split('\t')
            form, reading = (row[3], row[2]) if name == 'edict' else (row[2], row[3])
            accent = parse_accents(row[7])
            if accent is not None:
                extra[(form, hira(reading))].append({'file': filename, 'line': number,
                    'rowId': row[0], 'form': form, 'reading': reading, 'acc_pos': row[7],
                    'raw': line, 'pitch': accent})
    tagger = fugashi.Tagger('-a')
    overlay, skipped = {}, []
    for w in words:
        base = {'form': w['kanji'], 'reading': w['kana'], 'jmdict': w['jmdict']}
        records = extra.get((w['kanji'], hira(w['kana'])), [])
        values = {tuple(r['pitch']) for r in records}
        if len(values) == 1:
            overlay[w['id']] = {**base, 'pitch': list(next(iter(values))),
                'source': 'kanjium', 'license': 'CC-BY-SA-4.0', 'records': records}
            continue
        lemmas = allowed_lemmas(w, jm[w['jmdict']])
        result = choose_unidic(tagger, w['kanji'], w['kana'], lemmas)
        if result:
            overlay[w['id']] = {**base, **result, 'source': 'unidic-2.1.2',
                'license': 'BSD-3-Clause', 'allowedLemmas': sorted(lemmas)}
        else:
            skipped.append({'id': w['id'], **base, 'level': w['level'],
                'reason': 'No unambiguous exact lexical form/reading/lemma with explicit accent; no synthesis'})
    selected = list(overlay.values())
    morae = json.loads(subprocess.check_output(['node', '-e',
        "const k=require('./ja-kana');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>process.stdout.write(JSON.stringify(JSON.parse(s).map(x=>k.morae(x).length))))"],
        input=json.dumps([x['reading'] for x in selected]).encode(), cwd=root))
    for row, count in zip(selected, morae):
        assert all(0 <= a <= count for a in row['pitch']), row
    counts = {f'N{n}': {'before': sum(1 for w in json.loads((root/f'data/n{n}.json').read_text())
                                   if (w['kanji'], hira(w['kana'])) in original),
                        'added': sum(w['id'] in overlay for w in words if w['level'] == n),
                        'remainingNull': sum(w['id'] not in overlay for w in words if w['level'] == n)}
              for n in range(5, 0, -1)}
    method = {'checked': '2026-10-27', 'beforeNull': len(words), 'added': len(overlay),
        'remainingNull': len(skipped), 'sourcesAdded': dict(Counter(r['source'] for r in selected)),
        'levels': counts, 'kanjium': manifest,
        'unidic': {'version': '2.1.2', 'package': 'unidic-lite==1.0.8', 'reader': 'fugashi==1.5.2',
            'source': 'https://clrd.ninjal.ac.jp/unidic/en/back_number_en.html',
            'packageSource': 'https://github.com/polm/unidic-lite',
            'license': 'BSD-3-Clause', 'copyright': 'Copyright (c) 2011-2013, The UniDic Consortium',
            'files': {name: sha(dic/name) for name in ['sys.dic', 'BSD', 'COPYING', 'AUTHORS']},
            'terms': 'https://clrd.ninjal.ac.jp/unidic/faq.html',
            'fieldDefinition': 'https://clrd.ninjal.ac.jp/unidic/UNIDIC_manual.pdf#page=27'},
        'method': 'Exact lexical surface + orthBase + kana/kanaBase. Lemma must match the selected JMdict entry, allowing the documented ASCII loanword-origin suffix. Only explicit numeric aType, aModeType=*, non-unknown nodes. All matching nodes must agree including variant preference order. No compound, inflection or unknown-word accent rules. Existing Kanjium values unchanged.'}
    write(output, overlay)
    write(output.with_name('pitch-method.json'), method)
    write(output.with_name('pitch-unresolved.json'), skipped)
    print(json.dumps({k: method[k] for k in ['beforeNull','added','remainingNull','sourcesAdded','levels']}, indent=2))


if __name__ == '__main__':
    main()
