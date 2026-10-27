"""Exercise actual UniDic nodes, ambiguous readings and every released ruby segment."""
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from japanese_morphology import annotate, analyze, hira, split_ruby, verify_dictionary


class FuriganaTest(unittest.TestCase):
    def test_okurigana_and_ambiguous_alignment(self):
        self.assertEqual(split_ruby('食べ', 'たべ'), [{'base': '食', 'ruby': 'た'}, {'base': 'べ'}])
        self.assertEqual(split_ruby('高かっ', 'たかかっ'), [{'base': '高', 'ruby': 'たか'}, {'base': 'かっ'}])
        self.assertIsNone(split_ruby('甲あ乙', 'ああああ'))
        self.assertIsNone(split_ruby('食べ', 'しょく'))

    def test_dates_people_and_unknowns_remain_plain(self):
        w = {'kanji': '今日', 'kana': 'きょう'}
        e = {'text': '今日は一日、三人で学校へ行く。', 'match': {'start': 0, 'end': 2}}
        result = annotate(w, e)
        skipped = {t['surface']: t['reason'] for t in result['furiganaSkipped']}
        for surface in ['今日', '一日', '三', '人']:
            self.assertIn(surface, skipped)
        self.assertIn({'base': '学校', 'ruby': 'がっこう'}, result['furigana'])
        self.assertTrue(any(s.get('ruby') for s in result['furigana']))

    def test_every_released_example_and_target_reading(self):
        verify_dictionary()
        for n in range(5, 0, -1):
            for w in json.loads((ROOT/f'data/n{n}.json').read_text()):
                e = w['example']
                if not e:
                    continue
                self.assertEqual(annotate(w, e), e, w['id'])
                m = e['match']
                ts = [t for t in analyze(e['text']) if m['start'] <= t['start'] and t['end'] <= m['end']]
                self.assertEqual(''.join(t['reading'] for t in ts), hira(w['kana']), w['id'])


if __name__ == '__main__':
    unittest.main()
