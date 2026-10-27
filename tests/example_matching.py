"""Actual dictionary fixtures for exact/lemma matches, POS and homograph guards."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from tatoeba import match_word, better
class MatchTest(unittest.TestCase):
 def test_exact_and_kana(self):
  self.assertEqual(match_word({'kanji':'学校','kana':'がっこう'},'学校へ行く。'),{'start':0,'end':2,'surface':'学校','kind':'exact'})
  self.assertIsNotNone(match_word({'kanji':'珈琲','kana':'コーヒー'},'コーヒーを飲む。'))
  self.assertIsNotNone(match_word({'kanji':'おめでとう','kana':'おめでとう','pos':'thán từ'},'おめでとうございます。'))
  self.assertIsNotNone(match_word({'kanji':'等','kana':'など','pos':'trợ từ'},'私は英雄などではない。'))
 def test_no_partial_or_wrong_reading(self):
  for word,text in [({'kanji':'校','kana':'こう'},'学校へ行く。'),({'kanji':'愛','kana':'あい'},'愛知に住む。'),({'kanji':'行く','kana':'ゆく','pos':'động từ'},'学校へ行った。'),({'kanji':'いる','kana':'いる','pos':'động từ'},'ビールが入る。')]:
   self.assertIsNone(match_word(word,text),(word,text))
 def test_homophone(self):
  self.assertIsNone(match_word({'kanji':'今日','kana':'こんにち'},'今日は暑い。'))
 def test_inflections_hide_the_entire_surface(self):
  for form,reading,pos,text,surface in [
   ('食べる','たべる','động từ','昨日食べました。','食べました'),
   ('高い','たかい','tính từ đuôi i','前は高かった。','高かった'),
   ('勉強する','べんきょうする','động từ','勉強しました。','勉強しました'),
   ('する','する','động từ','しなかった。','しなかった'),
   ('食べる','たべる','động từ','食べない。','食べない'),
   ('勉強する','べんきょうする','động từ','勉強しませんでした。','勉強しませんでした'),
   ('高い','たかい','tính từ đuôi i','高くない。','高くない'),
   ('泳ぐ','およぐ','động từ','泳いだ。','泳いだ')]:
   m=match_word({'kanji':form,'kana':reading,'pos':pos},text)
   self.assertIsNotNone(m,(form,text));self.assertEqual(m['kind'],'lemma')
   self.assertEqual(m['surface'],surface);self.assertEqual(text[m['start']:m['end']],surface)
   self.assertEqual(m['targetReading'],reading)
 def test_lemma_pos_and_kanji_guard(self):
  for word,text in [({'kanji':'会う','kana':'あう','pos':'động từ'},'服が合った。'),
   ({'kanji':'切る','kana':'きる','pos':'động từ'},'服を着た。'),
   ({'kanji':'締める','kana':'しめる','pos':'động từ'},'窓を閉めた。'),
   ({'kanji':'高い','kana':'たかい','pos':'danh từ'},'高かった。'),
   ({'kanji':'居る','kana':'いる','pos':'động từ'},'要らない。')]:
   self.assertIsNone(match_word(word,text),(word,text))
 def test_kana_alias_is_not_a_neighboring_particle_or_homograph(self):
  for word,text in [({'kanji':'十','kana':'とお','pos':'danh từ'},'ゆっくりとお話願います。'),
   ({'kanji':'芽','kana':'め','pos':'danh từ'},'あけおめ！'),
   ({'kanji':'嫌','kana':'いや','pos':'tính từ đuôi na'},'いや、全然。')]:
   self.assertIsNone(match_word(word,text),(word,text))
 def test_existing_selection_is_stable_unless_better(self):
  def e(text,machine=False,pivot=False):return {'text':text,'translation':{'machine':machine,'pivot':pivot}}
  self.assertFalse(better(e('同じ長さ。'),e('同じ長さ。')))
  self.assertFalse(better(e('短い。',True),e('長い人の翻訳です。')))
  self.assertTrue(better(e('短い。'),e('長い人の翻訳です。')))
  self.assertTrue(better(e('人の翻訳です。'),e('短い。',True)))
  self.assertFalse(better(e('短い。',True),e('既にある長い機械翻訳。',True)))
if __name__=='__main__':unittest.main()
