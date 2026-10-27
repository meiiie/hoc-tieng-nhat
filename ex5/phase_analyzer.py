"""Phase A evidence only: never changes the app's matcher or annotations.

The best-path matcher is authoritative for strict_match. Alternate full-surface
UniDic nodes can confirm a dictionary lexeme, but cannot override the best-path
reading for ruby. Unconfirmed target tokens are therefore kept in plain text.
"""
import itertools
import re
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from example_lemmas import allowed, lexical_form
from japanese_morphology import HAN, analyze, annotate, hira, tagger

KEYS = ('start', 'end', 'surface', 'lemma', 'orthBase', 'kanaBase',
        'reading', 'pos1', 'pos2', 'unknown')


@lru_cache(maxsize=8192)
def full_nodes(surface):
    unique = {}
    for node in tagger(True).parseToNodeList(surface):
        if node.is_unk or node.surface != surface or node.feature.orth != surface:
            continue
        f = node.feature._asdict()
        keys = ('lemma', 'orthBase', 'kanaBase', 'kana', 'pos1', 'pos2')
        row = {k: f.get(k, '') for k in keys}
        unique[tuple(row.values())] = row
    return list(unique.values())


def alternate_lexeme(word, selected, match):
    if not selected or selected[0]['start'] != match['start'] or selected[-1]['end'] != match['end']:
        return None
    lexical = list(selected)
    while lexical and (lexical[-1].get('pos1') == '助動詞' or
            (lexical[-1].get('pos1') == '助詞' and lexical[-1]['surface'] in ('て', 'で'))):
        lexical.pop()
    if lexical and lexical[-1].get('lemma') == '為る' and not word['kana'].endswith('する'):
        lexical.pop()
    if not lexical:
        return None
    options = [full_nodes(t['surface']) for t in lexical]
    if any(not opt for opt in options):
        return None
    forms = set(allowed(word)) | {word['kana']}
    # No unconstrained fuzzy match: require both a complete allowed spelling
    # (or its inflected orthographic base) and the exact selected JMdict reading.
    for nodes in itertools.islice(itertools.product(*options), 10000):
        last = nodes[-1]
        inflected = last['pos1'] in ('動詞', '形容詞')
        spelling = ''.join(t['surface'] for t in lexical[:-1]) + (
            last['orthBase'] if inflected else lexical[-1]['surface'])
        reading = ''.join(hira(n['kana']) for n in nodes[:-1]) + hira(
            last['kanaBase'] if inflected else last['kana'])
        if lexical_form(spelling) in forms and reading == hira(word['kana']):
            return {'dictionary_form': spelling, 'dictionary_reading': reading,
                    'nodes': [{**n, 'surface': t['surface']} for t, n in zip(lexical, nodes)],
                    'method': 'full-surface UniDic alternatives; exact JMdict spelling and reading; sense reviewed by assistant'}
    return None


def evidence(word, row):
    match = row['match']
    ts = analyze(row['ja'])
    selected = [t for t in ts if t['start'] < match['end'] and t['end'] > match['start']]
    base = analyze(word['kanji'])
    strict = match['kind'] != 'phaseA-review'
    same = [t.get('lemma') for t in selected] == [t.get('lemma') for t in base]
    alternative = None if strict else alternate_lexeme(word, selected, match)
    status = ('strict-matcher-confirmed' if strict else 'alternative-Unidic-lexeme-confirmed'
              if alternative else 'same-default-lemma-requested-reading-unconfirmed'
              if same and not any(t['unknown'] for t in selected) else 'manual-JMdict-review-only')
    analysis = {'engine': 'fugashi 1.5.2 / UniDic 2.1.2 (unidic-lite 1.0.8)',
        'strict_match': strict, 'target_tokens': [{k: t.get(k) for k in KEYS} for t in selected],
        'target_dictionary_tokens': [{k: t.get(k) for k in KEYS} for t in base],
        'same_lemma_sequence': same, 'unknown_target': any(t['unknown'] for t in selected),
        'status': status, 'alternative_lexeme': alternative,
        'lemma_confirmed': strict or bool(alternative)}
    ann = annotate(word, {'text': row['ja'], 'match': match})
    if not strict:
        # Rebuild only evidence-bearing spans outside the uncertain target.
        # Whole overlapping tokens are suppressed, including fused compounds.
        keep = [e for e in ann['furiganaEvidence'] if not
                (e['start'] < match['end'] and e['end'] > match['start'])]
        safe_ranges = [(e['start'], e['end']) for e in keep]
        position = 0
        for segment in ann['furigana']:
            end = position + len(segment['base'])
            if 'ruby' in segment and not any(a <= position and end <= b for a, b in safe_ranges):
                segment.pop('ruby')
            position = end
        ann['furiganaEvidence'] = keep
        ann['furiganaSkipped'] = [e for e in ann['furiganaSkipped'] if not
                (e['start'] < match['end'] and e['end'] > match['start'])]
        ann['furiganaSkipped'].extend({'start': t['start'], 'end': t['end'], 'surface': t['surface'],
            'reason': 'target-default-reading-or-boundary-unconfirmed'} for t in selected if re.search(HAN, t['surface']))
        ann['furiganaSkipped'].sort(key=lambda e: e['start'])
    return analysis, {k: ann[k] for k in ('furigana', 'furiganaEvidence', 'furiganaSkipped')}
