"""Pinned, offline Japanese analysis shared by the content authoring tools.

No analyzer or dictionary is shipped to the browser. See data/SOURCES.md.
"""
import hashlib
import re
import unicodedata
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path

HAN = r'[\u3400-\u4dbf\u4e00-\u9fff々〆〇]'
KANA = r'[ぁ-ゖー]+'
UNIDIC_SHA256 = '122c4c91f026bf4b65bbe2dfd8b9f8eeb6ab56d8eb2a7287a68bca75708ba513'


def hira(text):
    return ''.join(chr(ord(c)-96) if 'ァ' <= c <= 'ヶ' else c
                   for c in unicodedata.normalize('NFKC', text))


@lru_cache(maxsize=2)
def tagger(all_nodes=False):
    import fugashi
    import unidic_lite
    assert version('fugashi') == '1.5.2'
    assert version('unidic-lite') == '1.0.8'
    # Explicit dictionary path: installing another UniDic must not change output.
    return fugashi.Tagger(f'-d "{unidic_lite.DICDIR}"' + (' -a' if all_nodes else ''))


def verify_dictionary():
    import unidic_lite
    path = Path(unidic_lite.DICDIR)/'sys.dic'
    with path.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    assert digest == UNIDIC_SHA256, 'Unexpected UniDic binary'
    return digest


@lru_cache(maxsize=150000)
def analyze(text):
    tokens = []
    offset = 0
    for node in tagger()(text):
        start = text.index(node.surface, offset)
        offset = start + len(node.surface)
        features = node.feature._asdict() if not node.is_unk else {}
        tokens.append({'start': start, 'end': offset, 'surface': node.surface,
                       'reading': hira(features.get('kana', '')),
                       'unknown': node.is_unk, **features})
    return tokens


@lru_cache(maxsize=30000)
def dictionary_readings(surface):
    """All full-surface lexical nodes, not only MeCab's best path."""
    return tuple(sorted({hira(node.feature.kana)
                         for node in tagger(True).parseToNodeList(surface)
                         if not node.is_unk and node.surface == surface
                         and node.feature.orth == surface and node.feature.kana}))


def split_ruby(surface, reading):
    """Unique kana-anchor alignment; ruby bases contain kanji only.

    Ambiguous internal okurigana alignment is refused, never guessed.
    """
    chunks = re.findall(HAN+'+|[^\u3400-\u4dbf\u4e00-\u9fff々〆〇]+', surface)
    solutions = []

    def visit(i, offset, segments):
        if len(solutions) > 1:
            return
        if i == len(chunks):
            if offset == len(reading):
                solutions.append(segments)
            return
        base = chunks[i]
        if re.fullmatch(HAN+'+', base):
            for end in range(offset+1, len(reading)+1):
                visit(i+1, end, segments+[{'base': base, 'ruby': reading[offset:end]}])
        elif reading.startswith(hira(base), offset):
            visit(i+1, offset+len(hira(base)), segments+[{'base': base}])

    if re.fullmatch(KANA, reading):
        visit(0, 0, [])
    return solutions[0] if len(solutions) == 1 else None


def ambiguity_reason(token, tokens):
    surface = token['surface']
    if any(s in surface for s in ('今日', '一日')) or surface == '人':
        return 'ambiguous-date-or-person'
    if token.get('pos2') == '数詞' or '助数詞' in token.get('pos3', ''):
        return 'number-or-counter'
    if token.get('pos1') == '接尾辞' and any(
            t['end'] == token['start'] and t.get('pos2') == '数詞' for t in tokens):
        return 'number-or-counter'
    if token.get('pos2') == '固有名詞':
        return 'proper-name'
    if token['unknown']:
        return 'unknown-token'
    return None


def annotate(word, example):
    tokens = analyze(example['text'])
    match = example['match']
    target = [t for t in tokens if match['start'] <= t['start'] and t['end'] <= match['end']]
    target_agrees = (target and target[0]['start'] == match['start']
                     and target[-1]['end'] == match['end']
                     and ''.join(t['reading'] for t in target) == hira(word['kana']))
    segments, evidence, skipped = [], [], []
    offset = 0
    for token in tokens:
        start, end, surface = token['start'], token['end'], token['surface']
        if start > offset:
            segments.append({'base': example['text'][offset:start]})
        offset = end
        if not re.search(HAN, surface):
            segments.append({'base': surface})
            continue
        reason = ambiguity_reason(token, tokens)
        readings = dictionary_readings(surface) if not reason else ()
        source = None
        if not reason:
            if len(readings) == 1 and readings[0] == token['reading']:
                source = 'unidic-single-reading'
            elif target_agrees and token in target and token['reading'] in readings:
                source = 'unidic-jmdict-target'
            else:
                reason = 'multiple-or-missing-readings'
        ruby = split_ruby(surface, token['reading']) if source else None
        if source and not ruby:
            reason = 'ambiguous-kana-alignment'
        detail = {'start': start, 'end': end, 'surface': surface}
        if ruby:
            segments.extend(ruby)
            evidence.append({**detail, 'reading': token['reading'], 'source': source,
                             'dictionaryReadings': list(readings)})
        else:
            segments.append({'base': surface})
            skipped.append({**detail, 'reason': reason})
    if offset < len(example['text']):
        segments.append({'base': example['text'][offset:]})
    assert ''.join(s['base'] for s in segments) == example['text']
    return {**example, 'furigana': segments, 'furiganaEvidence': evidence,
            'furiganaSkipped': skipped}
