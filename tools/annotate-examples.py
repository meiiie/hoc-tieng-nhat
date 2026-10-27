#!/usr/bin/env python3
"""Add conservative ruby to the source overlay offline; report all skipped kanji tokens."""
import json
from collections import Counter
from pathlib import Path
from japanese_morphology import annotate, verify_dictionary

ROOT = Path(__file__).resolve().parents[1]


def main():
    digest = verify_dictionary()
    path = ROOT/'data/sources/tatoeba-examples.json'
    examples = json.loads(path.read_text())
    levels = {}
    for n in range(5, 0, -1):
        counts, reasons = Counter(), Counter()
        for word in json.loads((ROOT/f'data/n{n}.json').read_text()):
            if word['id'] not in examples:
                continue
            e = examples[word['id']] = annotate(word, examples[word['id']])
            annotated, skipped = len(e['furiganaEvidence']), len(e['furiganaSkipped'])
            counts['examples'] += 1
            counts['full' if annotated and not skipped else 'partial' if annotated else
                   'unannotated' if skipped else 'kanaOnly'] += 1
            counts['tokensAnnotated'] += annotated
            counts['tokensSkipped'] += skipped
            reasons.update(t['reason'] for t in e['furiganaSkipped'])
        levels[f'N{n}'] = {**{k: counts[k] for k in ['examples', 'full', 'partial',
                          'unannotated', 'kanaOnly', 'tokensAnnotated', 'tokensSkipped']},
                          'skipReasons': dict(sorted(reasons.items()))}
    path.write_text(json.dumps(examples, ensure_ascii=False, indent=1)+'\n')
    report = {'analyzer': 'fugashi 1.5.2 (MIT; bundled MeCab BSD-3-Clause)',
              'dictionary': 'unidic-lite 1.0.8 / UniDic 2.1.2 (BSD-3-Clause option)',
              'dictionarySha256': digest, 'levels': levels,
              'countUnit': 'per word example, including repeated sentence IDs; tokensSkipped counts kanji-bearing tokens only',
              'policy': 'All full-surface dictionary nodes must agree, or agree with the matched JMdict target reading. Always skip ambiguous dates/person counters, numbers/counters, proper names, unknowns and nonunique kana alignment. Kana are never ruby bases.'}
    (ROOT/'data/sources/furigana-method.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(levels, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
