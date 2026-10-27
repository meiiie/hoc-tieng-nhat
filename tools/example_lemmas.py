"""Conjugation matching with lexical spelling, dictionary reading and POS guards."""
import json
import re
from functools import lru_cache
from pathlib import Path
from japanese_morphology import analyze, hira, HAN

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def entries():
    wanted = {w['jmdict'] for n in range(5, 0, -1)
              for w in json.loads((ROOT/f'data/n{n}.json').read_text())}
    data = json.loads((ROOT.parent/'src/jmdict-eng-3.6.2.json').read_text())
    return {e['id']: e for e in data['words'] if e['id'] in wanted}


def lexical_form(text):
    # UniDic's lexical spelling for suru is 為る; both share JMdict's する entry.
    return re.sub(r'為る$', 'する', text.split('-', 1)[0])


@lru_cache(maxsize=20000)
def spellings(form, reading, ident=None):
    allowed = {form}
    if ident:
        e = entries()[ident]
        readings = [r for r in e['kana'] if hira(r['text']) == hira(reading)]
        allowed.update(k['text'] for k in e['kanji'] if any(
            '*' in r['appliesToKanji'] or k['text'] in r['appliesToKanji'] for r in readings))
    return frozenset(lexical_form(s) for s in allowed)


def allowed(word):
    return spellings(word['kanji'], word['kana'], word.get('jmdict'))


def pos_ok(word, token):
    pos = word.get('pos', '')
    return ((token.get('pos1') == '動詞' and 'động từ' in pos)
            or (token.get('pos1') == '形容詞' and 'tính từ' in pos))


def candidates_for(tokens, forms):
    """Index full prefix + lexical lemma, never a substring or a bare reading."""
    candidates = {}
    for i in range(len(tokens)):
        for j in range(i, min(i+10, len(tokens))):
            t = tokens[j]
            if t.get('pos1') not in ('動詞', '形容詞'):
                continue
            prefix = ''.join(x['surface'] for x in tokens[i:j])
            keys = {lexical_form(prefix+t.get('lemma', ''))}
            if re.search(HAN, t.get('orthBase', '')):
                keys.add(lexical_form(prefix+t['orthBase']))
            for key in keys:
                for w in forms.get(key, []):
                    candidates[w['id']] = w
    return candidates


def extend_ending(tokens, index):
    """Include the actual contiguous inflection: 食べました / 高くない / しませんでした.

    Independent verbs/nouns and following clauses are not part of the blank.
    """
    end = index+1
    negative_adjective = tokens[index].get('pos1') == '形容詞'
    while end < len(tokens) and tokens[end-1]['end'] == tokens[end]['start']:
        t = tokens[end]
        if t.get('pos1') == '助動詞' and t.get('lemma') in {
                'ます', 'た', 'ない', 'ず', 'です', 'だ', 'られる', 'れる', 'せる', 'させる', 'たい'}:
            end += 1
        elif negative_adjective and t.get('pos1') == '形容詞' and t.get('lemma') == '無い':
            end += 1
            negative_adjective = False
        elif t.get('pos1') == '助詞' and t.get('pos2') == '接続助詞' and t['surface'] in ('て', 'で'):
            end += 1
            break
        else:
            break
    return end


def match_lemma(word, text, tokens=None):
    tokens = analyze(text) if tokens is None else tokens
    forms = allowed(word)
    for i in range(len(tokens)):
        for j in range(i, min(i+10, len(tokens))):
            t = tokens[j]
            if not pos_ok(word, t) or t['unknown']:
                continue
            prefix = tokens[i:j]
            lemma = lexical_form(''.join(x['surface'] for x in prefix)+t.get('lemma', ''))
            reading = ''.join(x['reading'] for x in prefix)+hira(t.get('kanaBase', ''))
            dictionary_form = lexical_form(''.join(x['surface'] for x in prefix)+t.get('orthBase', ''))
            if re.search(HAN, t.get('orthBase', '')) and dictionary_form not in forms:
                continue  # Shared UniDic lemmas must not override explicit kanji.
            # UniDic groups some spellings (閉める under 締める) and uses 応ずる
            # as the lemma of 応じる. Require explicit target kanji + the same
            # dictionary-form token's lemma/POS; never authorize by reading alone.
            spelling_agrees = False
            if re.search(HAN, t.get('orthBase', '')) and dictionary_form in forms:
                base_tokens = analyze(t['orthBase'])
                spelling_agrees = (len(base_tokens) == 1
                    and lexical_form(base_tokens[0].get('lemma', '')) == lexical_form(t.get('lemma', ''))
                    and base_tokens[0].get('pos1') == t.get('pos1'))
            if (lemma not in forms and not spelling_agrees) or reading != hira(word['kana']):
                continue
            if any(x['unknown'] for x in prefix):
                continue
            # A prefix must be an actual contiguous part of the compound.
            if any(a['end'] != b['start'] for a, b in zip(tokens[i:j], tokens[i+1:j+1])):
                continue
            end_index = extend_ending(tokens, j)
            start, end = tokens[i]['start'], tokens[end_index-1]['end']
            surface = text[start:end]
            if surface in (word['kanji'], word['kana']) or (end_index == j+1 and t['surface'] == t.get('orthBase')):
                continue  # The original exact matcher handles dictionary forms.
            return {'start': start, 'end': end, 'surface': surface, 'kind': 'lemma',
                    'lemma': lemma, 'dictionaryForm': dictionary_form,
                    'targetReading': reading, 'pos': t['pos1'],
                    'surfaceReading': ''.join(x['reading'] for x in tokens[i:end_index]),
                    'lexicalEnd': t['end']}
    return None


def exact_lexeme_ok(word, selected):
    """Kana aliases must identify the target lexeme, not adjacent particles."""
    if not selected:
        return False
    if word.get('pos') == 'thán từ' and not any(t.get('pos1') == '感動詞' for t in selected):
        return False
    surface = ''.join(t['surface'] for t in selected)
    if re.search(HAN, surface):
        return True
    if re.search(HAN, word['kanji']):
        forms = allowed(word)
        lemmas = lexical_form(''.join(t.get('lemma', '').split('-', 1)[0] for t in selected))
        bases = lexical_form(''.join(t.get('orthBase', '') for t in selected))
        if lemmas in forms or (re.search(HAN, bases) and bases in forms):
            return True
        # Kana is the dictionary spelling of these katakana loanwords.
        return bool(re.search('[ァ-ヶ]', word['kana']) and len(selected) == 1
                    and hira(lemmas) == hira(word['kana']))
    if len(selected) > 1 or not pos_ok(word, selected[-1]):
        return True
    t = selected[-1]
    form = lexical_form(''.join(x['surface'] for x in selected[:-1])+t.get('lemma', ''))
    return form in allowed(word)
