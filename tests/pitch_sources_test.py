"""Real dictionary regressions: reject guesses, compounds and homophone leakage."""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import fugashi
from pitch_sources import choose_unidic, parse_accents, allowed_lemmas

class PitchSources(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.tagger=fugashi.Tagger('-a')
 def pick(self,form,reading,lemmas):return choose_unidic(self.tagger,form,reading,set(lemmas))
 def test_explicit_variants_keep_preference_order(self):
  self.assertEqual(parse_accents('3,0'),[3,0]);self.assertIsNone(parse_accents('*'));self.assertIsNone(parse_accents('2@1'))
 def test_exact_loanword(self):
  self.assertEqual(self.pick('アパート','あぱーと',{'アパート'})['pitch'],[2])
 def test_homophones_follow_the_selected_jmdict_lemma(self):
  self.assertEqual(self.pick('はし','はし',{'箸'})['pitch'],[1]);self.assertEqual(self.pick('はし','はし',{'橋'})['pitch'],[2])
  self.assertIsNone(self.pick('し','し',{'市'}))
 def test_no_compound_or_unknown_accent_synthesis(self):
  self.assertIsNone(self.pick('勉強する','べんきょうする',{'勉強する'}));self.assertIsNone(self.pick('ネコニャッピ','ねこにゃっぴ',{'ネコニャッピ'}))
 def test_reading_and_inflected_form_must_match(self):
  self.assertIsNone(self.pick('学校','がくこう',{'学校'}));self.assertIsNone(self.pick('食べた','たべた',{'食べる'}))
 def test_reading_does_not_authorize_an_unrelated_name_or_symbol_lemma(self):
  word={'kanji':'総','kana':'そう'}
  entry={'kanji':[{'text':'総'}],'kana':[{'text':'そう','appliesToKanji':['*']}]}
  lemmas=allowed_lemmas(word,entry)
  self.assertNotIn('そう',lemmas)
  self.assertIsNone(self.pick('総','そう',lemmas))
 def test_ambiguous_dictionary_entries_remain_null(self):
  self.assertIsNone(self.pick('あまり','あまり',{'余り'}))

if __name__=='__main__':unittest.main()
