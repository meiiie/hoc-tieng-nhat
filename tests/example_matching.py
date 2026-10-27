"""Exact surface selection must reject partial tokens and wrong readings."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from tatoeba import match_word
class MatchTest(unittest.TestCase):
 def test_exact_and_kana(self):
  self.assertEqual(match_word({'kanji':'学校','kana':'がっこう'},'学校へ行く。'),{'start':0,'end':2,'surface':'学校','kind':'exact'})
  self.assertIsNotNone(match_word({'kanji':'珈琲','kana':'コーヒー'},'コーヒーを飲む。'))
 def test_no_partial_or_inflection(self):
  for word,text in [({'kanji':'校','kana':'こう'},'学校へ行く。'),({'kanji':'愛','kana':'あい'},'愛知に住む。'),({'kanji':'行く','kana':'いく'},'学校へ行った。'),({'kanji':'高い','kana':'たかい'},'高かった。'),({'kanji':'いる','kana':'いる'},'ビールが入る。')]:
   self.assertIsNone(match_word(word,text),(word,text))
 def test_homophone(self):
  self.assertIsNone(match_word({'kanji':'今日','kana':'こんにち'},'今日は暑い。'))
if __name__=='__main__':unittest.main()
