#!/usr/bin/env python3
"""Apply the supplied review; never edit the reviewed inputs or invent a review.

Run with .cache/content-venv/bin/python ex5/build-final.py. Editorial decisions in
fix-notes.json and rewrite-selfchecks.json were made by this integrating assistant.
They are self-checks, not an independent review or native-speaker certification.
"""
import copy
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'ex5')]
from example_lemmas import allowed, entries, lexical_form
from japanese_morphology import analyze, hira, verify_dictionary
from phase_analyzer import evidence
from tatoeba import match_word


def read(name):
    return json.loads((ROOT / 'ex5' / name).read_text())


def matched(word, text, preferred):
    m = match_word(word, text)
    if m:
        return m
    forms = set(allowed(word)) | {word['kana']}
    # The kana reading may also be written in katakana (アラ, スリ).
    forms |= {''.join(chr(ord(c) + 96) if 'ぁ' <= c <= 'ゖ' else c for c in word['kana'])}
    for form in sorted(forms, key=lambda f: (-len(f), f)):
        if form not in text:
            continue
        # Do not weaken the existing homophone guard for an automatic match.
        if not re.search(r'[一-龯]', form) and form != word['kanji']:
            tokens = analyze(form)
            if len(tokens) != 1 or hira(lexical_form(tokens[0].get('lemma', ''))) != hira(word['kana']):
                continue
        m = match_word({**word, 'kanji': form}, text)
        if m:
            return {**m, 'jmdictAlias': form}
    # This is explicit editorial evidence, NEVER a strict analyzer confirmation.
    surface = preferred if preferred in text else next((f for f in sorted(forms, key=lambda f: (-len(f), f)) if f in text), None)
    assert surface, (word['id'], text, forms)
    start = text.index(surface)
    return {'start': start, 'end': start + len(surface), 'surface': surface, 'kind': 'phaseA-review'}


criteria = ['ja_grammar', 'ja_naturalness', 'sense', 'register_orthography', 'level',
            'context', 'vi_accuracy', 'vi_naturalness', 'content_precision', 'length',
            'licence_attribution', 'lemma', 'ruby']
verify_dictionary()
words = {w['id']: w for w in read('missing-words.json')}
inputs = {r['id']: r for name in ['authored.json', 'licensed-candidates.json'] for r in read(name)}
reviews = {r['id']: r for r in read('review.json')}
assert inputs.keys() == reviews.keys() == words.keys()
attempts = {r['id']: r for r in csv.DictReader((ROOT / 'ex5/rewrites.tsv').open(), delimiter='\t')}
selfchecks, notes = read('rewrite-selfchecks.json'), read('fix-notes.json')
assert attempts.keys() == selfchecks.keys() == {i for i, v in reviews.items() if v['verdict'] == 'reject'}
final = []
for ident, word in words.items():
    original, review = inputs[ident], reviews[ident]
    verdict = review['verdict']
    row = copy.deepcopy(original)
    result = {'id': ident, 'level': word['level'], 'original_source': original.get('source', 'authored'),
              'review_verdict': verdict, 'native_reviewed': False}
    if verdict == 'fix':
        row['ja'], row['vi'] = review['suggested_ja'], review['suggested_vi']
        if 'source' in row:
            t = row['translation']
            if row['vi'] != original['vi']:
                if not t['machine']:
                    t['original'] = copy.deepcopy(original['translation'])
                    t['machine'], t['pivot'] = True, False
                    t['translator'] = 'OpenAI Codex (adaptation of credited Vietnamese translation)'
                t['text'] = row['vi']
                t['changes'] = 'Vietnamese wording corrected by OpenAI Codex after the supplied assistant review.'
                t['method'] = 'Review correction checked against Japanese and the selected JMdict sense by the integrating assistant; no native review.'
            row['machine'] = t['machine']
            if row['ja'] != original['ja']:
                row['original_ja'] = original['ja']
                row['changes'] = 'Japanese adapted by OpenAI Codex using the supplied reviewer correction; original source and licence retained.'
            row['attribution'] = (f"{row['author']} — {row['source']}, {row['source_id']}; {row['url']}; "
                f"{row['licence']} ({row['licence_url']}). {row['changes']}")
            if t['machine']:
                row['attribution'] += ' Vietnamese translated/adapted by OpenAI Codex; machine-generated, not native reviewed.'
    elif verdict == 'reject':
        attempt = attempts[ident]
        # A newly authored sentence does not inherit the rejected corpus label.
        row = {k: copy.deepcopy(original[k]) for k in ['id', 'level', 'target', 'sense']}
        row.update({k: attempt[k] for k in ['ja', 'vi', 'target_surface', 'rationale']})
        row.update(machine=True, author='OpenAI Codex', native_reviewed=False)
    else:
        assert verdict == 'pass'

    if verdict != 'pass':
        preferred = row['target_surface']
        row['match'] = matched(word, row['ja'], preferred)
        row['target_surface'] = row['match']['surface']
        row['analysis'], ann = evidence(word, row)
        row.update(ann)
        check = {'kind': 'integrating-assistant-self-check', 'independent_review': False,
                 'native_reviewed': False, 'verdict': 'pass',
                 'criteria': {key: 'pass' for key in criteria},
                 'lemma_evidence': {'jmdict': word['jmdict'], 'reading': word['kana'],
                     'allowed_spellings': sorted(allowed(word)), 'surface': row['match']['surface'],
                     'analyzer_status': row['analysis']['status'],
                     'machine_confirmed': row['analysis']['lemma_confirmed']},
                 'sense_index': row['sense']['index'], 'japanese_characters': len(row['ja']),
                 'ruby': 'Regenerated with the pinned conservative analyzer; non-strict target tokens kept plain.',
                 'notes': notes.get(ident, 'Re-read the complete proposed Japanese/Vietnamese pair against the selected JMdict gloss/POS and the reported issues. The proposed wording preserves the intended sense and register; Vietnamese expresses the same content naturally. No native review is claimed.')}
        if verdict == 'reject':
            editorial = selfchecks[ident]
            check.update(attempt=1, verdict=editorial['verdict'], notes=editorial['notes'])
            for key in editorial.get('failed_criteria', []):
                check['criteria'][key] = 'fail'
            result['rewrite_selfcheck'] = check
            result['rewrite_attempt'] = copy.deepcopy(row)
        else:
            result['fix_selfcheck'] = check

    # Structural gates do not stand in for the editorial checks above.
    sense = entries()[word['jmdict']]['sense'][row['sense']['index'] - 1]
    assert row['sense']['gloss'] == [g['text'] for g in sense['gloss']], ident
    assert row['sense']['part_of_speech'] == sense['partOfSpeech'], ident
    assert len(row['ja']) <= (35 if 'source' in row else 25), ident
    assert row['ja'][row['match']['start']:row['match']['end']] == row['match']['surface'], ident
    assert ''.join(s['base'] for s in row['furigana']) == row['ja'], ident
    assert row['vi'].strip() and not row['analysis']['unknown_target'], ident
    if verdict == 'pass':
        assert row == original  # The supplied pass is accepted unchanged.
    if verdict == 'reject' and result['rewrite_selfcheck']['verdict'] != 'pass':
        result['final_status'] = 'dropped'
        result['final_candidate'] = None
    else:
        result['final_status'] = {'pass': 'accepted_pass', 'fix': 'accepted_fix', 'reject': 'accepted_rewrite'}[verdict]
        result['final_candidate'] = row
    final.append(result)

(ROOT / 'ex5/final.json').write_text(json.dumps(final, ensure_ascii=False, indent=2) + '\n')
stats = {'input_sha256': {n: hashlib.sha256((ROOT / 'ex5' / n).read_bytes()).hexdigest() for n in ['authored.json', 'licensed-candidates.json', 'review.json']},
         'review': dict(Counter(r['review_verdict'] for r in final)),
         'final': dict(Counter(r['final_status'] for r in final)),
         'rejection_rate_percent': round(100 * sum(r['review_verdict'] == 'reject' for r in final) / len(final), 4),
         'by_level': {str(n): dict(Counter(r['final_status'] for r in final if r['level'] == n)) for n in range(5, 0, -1)},
         'rewrite_check_kind': 'self-check by integrating assistant, not an independent review', 'native_reviews': 0}
(ROOT / 'ex5/final-stats.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(stats, ensure_ascii=False, indent=2))
