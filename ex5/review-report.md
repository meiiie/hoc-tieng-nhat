Independent review of Examples v5 — 27 October 2026

Reviewed **all 1,409 items**, not a sample: 684 from [authored.json](authored.json) and 725 from [licensed-candidates.json](licensed-candidates.json). Result: **1,263 pass, 126 fix, 20 reject**. The item-level decisions and complete corrected Japanese/Vietnamese pairs for every fix are in [review.json](review.json). No subagents were used, and neither the repository nor the two inputs was edited.

**Counts and rates by level**

| Level | Items | Pass | Fix | Reject | Fix rate | Rejection rate | Fix + reject rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N5 | 35 | 34 | 1 | 0 | 2.86% | 0.00% | 2.86% |
| N4 | 14 | 11 | 3 | 0 | 21.43% | 0.00% | 21.43% |
| N3 | 50 | 45 | 4 | 1 | 8.00% | 2.00% | 10.00% |
| N2 | 305 | 275 | 20 | 10 | 6.56% | 3.28% | 9.84% |
| N1 | 1005 | 898 | 98 | 9 | 9.75% | 0.90% | 10.65% |
| All | 1409 | 1263 | 126 | 20 | 8.94% | 1.42% | 10.36% |

Each rate uses all items in that row as its denominator. “Fix + reject” is the proportion that should not be used unchanged. Counts refer to word/example associations; the inputs contain 1,392 distinct Japanese strings, so repeated sentences are still reviewed for each target word.

**Counts and rates by input**

| Input | Items | Pass | Fix | Reject | Fix rate | Rejection rate | Fix + reject rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Authored | 684 | 650 | 32 | 2 | 4.68% | 0.29% | 4.97% |
| Licensed | 725 | 613 | 94 | 18 | 12.97% | 2.48% | 15.45% |

**Licensed source breakdown**

| Source | Items | Pass | Fix | Reject |
| --- | --- | --- | --- | --- |
| Tatoeba | 373 | 324 | 46 | 3 |
| KFTT 1.0 | 332 | 275 | 43 | 14 |
| Japanese Wiktionary | 12 | 10 | 2 | 0 |
| KNBC 1.0 (2009-09-25) | 8 | 4 | 3 | 1 |

**Issue categories**

| Category | Affected items | Meaning |
| --- | --- | --- |
| ja_grammar | 3 | Japanese grammatical construction or particle choice |
| ja_naturalness | 10 | Japanese phrasing, collocation or translated-style syntax |
| sense | 8 | Recorded JMdict sense, lexical use or part-of-speech mismatch |
| register_orthography | 6 | Register or inappropriate/opaque spelling for the context |
| level | 13 | Supporting vocabulary or constructions too demanding for the assigned level |
| context | 11 | Missing material needed to understand the example |
| vi_accuracy | 63 | Vietnamese changes, omits or invents meaning/referents |
| vi_naturalness | 45 | Vietnamese phrasing, idiom, localization or punctuation |
| content_precision | 3 | Precision of the instructional explanation (mathematics/grammar) |
| length | 0 | Japanese character-limit violation |
| licence_attribution | 0 | Missing or inconsistent required licence/attribution fields |

Categories overlap: one item may have several issues. These are editorial findings, not automated frequency estimates. A pass means the Japanese grammar, naturalness in its intended register, selected sense, supporting vocabulary, length and Vietnamese were acceptable together; licensed passes also passed the metadata audit.

**Review criteria and checks**

I read every Japanese/Vietnamese pair with its target spelling, reading, level, 1-based JMdict sense, glosses, part of speech and register information. I checked entry IDs and copied sense metadata against [the supplied JMdict snapshot](/workspace/japanese/src/jmdict-eng-3.6.2.json) and the repository’s data/n1.json through data/n5.json. The references and copied gloss/register fields match; matching metadata does not establish that the sentence uses the selected sense. Examples such as 空間, 衆 and とどめる fail that semantic check.

Level judgments concern the surrounding vocabulary and construction, not just the difficulty of the target itself. N1 literary, historical and technical examples are acceptable when the intended use is coherent. A single unfamiliar proper name, ordinary Japanese subject omission, a short complete utterance or a legitimate spelling variant is not automatically an error. I rejected examples whose essential content is missing, whose supporting jargon overwhelms the target, or whose central usage cannot be repaired locally while retaining the recorded sense. A fix supplies a usable revised pair; a reject calls for reselection or a fresh example. These are independent assistant editorial judgments, not native-speaker certification.

Length was assessed against the project’s documented targets: at most 25 Japanese Unicode characters for authored examples and 35 for licensed examples, including punctuation. Authored lengths are 9–21; licensed lengths are 5–35. **All 1,409 comply**; 207 licensed items exceed 25 but remain within 35. Every proposed Japanese fix also remains within its corresponding limit. No separate Vietnamese character limit was specified.

**Licence and provenance findings**

No missing required licence/attribution fields were found in the 725 licensed items. Every row identifies its source, source ID, URL, author/contributor credit, licence, licence URL, changes and attribution. Vietnamese has separate text, translator/author and licence information. The 27 reused human translations retain their own sentence IDs, credited usernames and links; the other 698 identify the machine translator. Human Vietnamese credit is often nested in `translation`, so the top-level Japanese `attribution` string alone is not the complete bilingual credit.

I independently compared all 373 Tatoeba Japanese texts and their author names with the local export, all 332 KFTT Japanese/English pairs with their archive member and line, all 12 Wiktionary examples with their pinned revision/wikitext, and all eight KNBC examples with reconstructed archive tokens and S-IDs. All matched. The 27 human Vietnamese texts/owners and all 36 recorded translation-link edges also matched. The supplied full KNBC licence notice matches the archive README.

The named release terms are consistent with the [Tatoeba reuse policy](https://en.wiki.tatoeba.org/articles/show/using-the-tatoeba-corpus), the [KFTT release README](licences/KFTT-README.txt) and [CC BY-SA 3.0 terms](https://creativecommons.org/licenses/by-sa/3.0/), the [Japanese Wiktionary copyright policy](https://ja.wiktionary.org/wiki/Wiktionary:%E8%91%97%E4%BD%9C%E6%A8%A9), and the complete [KNBC notice](licences/KNBC-README.txt). KFTT attribution is at the released-corpus level: collective contributor credit plus an exact archive line. Its release does not supply original Wikipedia article/revision identities. This audit confirms the supplied corpus-level fields and traceability; it does not reconstruct those absent article histories or certify every upstream rights chain.

Corrections are proposals, not edits to the source records. If a Japanese correction is adopted, retain the source and mark the adaptation rather than leaving “copied verbatim” in `changes`/`attribution`. A revised human Vietnamese translation must retain the original credit and identify the assistant’s adaptation. Update the corresponding translation text, target spans and reading annotations when integrating a fix. The review JSON’s `source` is `authored` for authored entries, otherwise the original licensed corpus label.

**20 examples of problems found**

1. **N4 · j7c23332ecdd6 · authored · fix** — 二階建て (にかいだて)

   Original Japanese: 駅の近くの二階建てに住んでいます。

   Original Vietnamese: Tôi sống trong căn nhà hai tầng gần ga.

   Problem: 二階建て is an awkward isolated housing referent here; 二階建ての家 gives the natural complete noun phrase.

   Corrected Japanese: 駅の近くの二階建ての家に住んでいます。

   Corrected Vietnamese: Tôi sống trong căn nhà hai tầng gần ga.

2. **N2 · jaf7b06668b45 · authored · reject** — 佚 (いつ)

   Original Japanese: 佚をむさぼり、務めを忘れてはならぬ。

   Original Vietnamese: Đừng mải hưởng nhàn mà quên bổn phận.

   Problem: The rare literary noun 佚 is surrounded by むさぼる, literary 務め and the archaic prohibition ならぬ. This creates an unsuitable isolated N2 teaching sentence. The entire admonition is literary/archaizing; it needs explicit literary context rather than presentation as an ordinary model sentence.

   Action: replace/reselect this example; it is not approved for use unchanged.

3. **N2 · j8185799b99fe · authored · reject** — ディア (ディア)

   Original Japanese: この革はディアと呼ばれる鹿革だ。

   Original Vietnamese: Loại da này là da hươu, được gọi là deer.

   Problem: The recorded sense of ディア is the animal 'deer'; this sentence instead presents ディア as the name of a kind of leather. この革はディアと呼ばれる鹿革だ is a contrived product-label explanation, not a clear natural example of the recorded animal sense.

   Action: replace/reselect this example; it is not approved for use unchanged.

4. **N1 · j6a94066bbbb5 · authored · fix** — 空間 (あきま)

   Original Japanese: 箪笥と壁の空間に箱を置いた。

   Original Vietnamese: Tôi đặt chiếc hộp vào khoảng trống giữa tủ và tường.

   Problem: A gap between furniture and a wall is sense 2 (dated 'gap/space'), not the recorded sense 1 ('vacancy/room for rent'). The unmarked 空間 also invites the different reading くうかん.

   Corrected Japanese: この宿には、まだ空き間がある。

   Corrected Vietnamese: Nhà trọ này vẫn còn phòng trống.

5. **N1 · j7e44ca1b4487 · authored · fix** — ウェートレス (ウェートレス)

   Original Japanese: ウェートレスが注文を取りに来た。

   Original Vietnamese: Cô phục vụ đến nhận gọi món.

   Problem: 'nhận gọi món' is not a natural collocation for taking an order.

   Corrected Japanese: ウェートレスが注文を取りに来た。

   Corrected Vietnamese: Cô phục vụ đến ghi món khách gọi.

6. **N1 · jc5460fd7800e · authored · fix** — 助 (じょ)

   Original Japanese: この資料が研究の助となれば幸いです。

   Original Vietnamese: Mong rằng tài liệu này sẽ giúp ích cho việc nghiên cứu.

   Problem: The recorded JMdict entry is the prefix 助 (assistant/helping); 研究の助 uses 助 as an independent noun instead. Demonstrate the prefix in 助監督.

   Corrected Japanese: 彼女は助監督として撮影に参加した。

   Corrected Vietnamese: Cô ấy tham gia quay phim với vai trò trợ lý đạo diễn.

7. **N1 · j622459b2fa56 · authored · fix** — 尉 (じょう)

   Original Japanese: 彼は国司の尉に任じられた。

   Original Vietnamese: Ông được bổ nhiệm làm viên quan cấp ba trong bộ máy cai quản tỉnh thời xưa.

   Problem: 国司の尉 is the wrong historical office/rank combination: the provincial third-rank officer is 掾, while 尉 is used in guard offices such as 衛門府. See [Sanseido's historical office table](https://tbqr.sanseido-publ.co.jp/05-seisenkoten/contents/40_2.pdf). The Vietnamese repeats the incorrect provincial-administration assignment.

   Corrected Japanese: 彼は衛門府の尉に任じられた。

   Corrected Vietnamese: Ông được bổ nhiệm làm quan úy trong Vệ môn phủ, cơ quan bảo vệ cung thành.

8. **N1 · jbba2ef0085dd · authored · fix** — 優 (やさ)

   Original Japanese: 優な姿で舞う人に見とれた。

   Original Vietnamese: Tôi mải ngắm người đang múa với dáng vẻ dịu dàng.

   Problem: 優 (やさ) is recorded as a prefix; 優な treats it as a productive na-adjective and is not a natural modern model. Use the prefix in 優男.

   Corrected Japanese: 彼は優男だが、芯は強い。

   Corrected Vietnamese: Anh ấy trông hiền lành nhưng rất cứng cỏi.

9. **N2 · j65d767b97593 · Tatoeba · fix** — 御手洗 (おてあらい)

   Original Japanese: お手洗いはどこですか？

   Original Vietnamese: Phòng tắm ở đâu

   Problem: お手洗い asks for the toilet/restroom, not a bathing room (phòng tắm). The question is missing its final question mark.

   Corrected Japanese: お手洗いはどこですか？

   Corrected Vietnamese: Nhà vệ sinh ở đâu ạ?

10. **N2 · j88ac7a31ac8f · KFTT 1.0 · reject** — 過半数 (かはんすう)

   Original Japanese: また箏曲でも、古典曲の場合過半数が手事物である。

   Original Vietnamese: Trong nhạc koto cổ điển, hơn một nửa số bản là thể loại tegotomono.

   Problem: 箏曲 and the unexplained genre 手事物 are specialist music terms that overwhelm this N2 example of 過半数. Leaving tegotomono unexplained does not make the musical classification accessible to a Vietnamese learner.

   Action: replace/reselect this example; it is not approved for use unchanged.

11. **N2 · j77a1ab44bdd3 · KFTT 1.0 · fix** — 助教授 (じょきょうじゅ)

   Original Japanese: その後、助教授となる。

   Original Vietnamese: Sau đó, ông trở thành phó giáo sư.

   Problem: The surrounding source identifies a woman (later a prima donna and married to Miura); Ông is the wrong gender.

   Corrected Japanese: その後、助教授となる。

   Corrected Vietnamese: Sau đó, bà trở thành phó giáo sư.

12. **N2 · j2ef7eb1f88fc · KNBC 1.0 (2009-09-25) · reject** — それなのに (それなのに)

   Original Japanese: それなのに、なぜ現在ジョグダイヤルが廃れてしまったのか。

   Original Vietnamese: Vậy mà vì sao nút xoay jog dial giờ lại không còn được dùng nữa?

   Problem: The sentence begins それなのに but omits the preceding proposition it contradicts; a standalone example of this conjunction does not demonstrate the relationship. ジョグダイヤル and 廃れる add avoidable product-specific and advanced vocabulary to the N2 target.

   Action: replace/reselect this example; it is not approved for use unchanged.

13. **N1 · jaed351c71996 · KFTT 1.0 · fix** — 抗争 (こうそう)

   Original Japanese: そうして院と延暦寺の抗争が再燃することになった。

   Original Vietnamese: Như vậy, cuộc xung đột giữa viện và chùa Enryaku lại bùng lên.

   Problem: 院 in this historical passage refers to the retired emperor's government, confirmed by the surrounding Goshirakawa context; the literal 'viện' is misleading.

   Corrected Japanese: そうして院と延暦寺の抗争が再燃することになった。

   Corrected Vietnamese: Như vậy, cuộc xung đột giữa chính quyền Thượng hoàng và chùa Enryaku lại bùng lên.

14. **N1 · j76ac6e27448b · Tatoeba · reject** — 授ける (さずける)

   Original Japanese: 言論の自由は社会に多くの利益を授ける。

   Original Vietnamese: Tự do ngôn luận mang lại nhiều lợi ích cho xã hội.

   Problem: 言論の自由が利益を授ける is an English-like collocation; benefits are normally もたらす, whereas 授ける naturally involves an agent bestowing something. Repairing the sentence with もたらす would remove the target.

   Action: replace/reselect this example; it is not approved for use unchanged.

15. **N1 · j250269b2d36c · Tatoeba · reject** — 衆 (しゅう)

   Original Japanese: トムの講演は人を魅了し、衆を率いることができるほどの力を持っている。

   Original Vietnamese: Bài diễn thuyết của Tom cuốn hút và có sức mạnh dẫn dắt đám đông.

   Problem: 衆を率いる uses the neutral/literary 'masses, great numbers of people' sense 1, not recorded sense 2 with honorific/familiar force (as in 若い衆). The sentence does not demonstrate the hon/fam register explicitly attached to the selected sense.

   Action: replace/reselect this example; it is not approved for use unchanged.

16. **N1 · j9ebb3678a436 · Tatoeba · fix** — 終始 (しゅうし)

   Original Japanese: 何を聞かれても具体策のない返答に終始した。

   Original Vietnamese: Dù được hỏi điều gì, ông ấy cũng chỉ trả lời mà không đưa ra biện pháp cụ thể.

   Problem: 終始した is the verbal construction in JMdict sense 2; the recorded sense 3 is adverbial. Rewrite with adverbial 終始 to retain the selected sense.

   Corrected Japanese: 何を聞かれても、終始具体策のない返答だった。

   Corrected Vietnamese: Suốt buổi, dù được hỏi gì, ông ấy cũng không đưa ra biện pháp cụ thể nào trong câu trả lời.

17. **N1 · j26c79ac3b0e6 · KFTT 1.0 · fix** — 代弁 (だいべん)

   Original Japanese: イギリスの立場を代弁していた様子がある。

   Original Vietnamese: Có vẻ ông đã lên tiếng đại diện cho lập trường của Anh.

   Problem: The surrounding source identifies Japan as the party representing Britain's position; the Vietnamese invents a male individual (ông).

   Corrected Japanese: イギリスの立場を代弁していた様子がある。

   Corrected Vietnamese: Có vẻ Nhật Bản đã lên tiếng thay cho phía Anh.

18. **N1 · j80c6dbb628c7 · KFTT 1.0 · reject** — 止める (とどめる)

   Original Japanese: 旧規定の装束については簡単に説明するにとどめる。

   Original Vietnamese: Về trang phục theo quy định cũ, ở đây chỉ xin giải thích ngắn gọn.

   Problem: 説明するにとどめる means limiting oneself to an explanation, JMdict sense 4 ('to limit'), not the recorded sense 1 ('to stop/halt/hold back'). The Vietnamese correctly reflects limiting, which confirms the mismatch.

   Action: replace/reselect this example; it is not approved for use unchanged.

19. **N1 · jebb917b53ea2 · KFTT 1.0 · fix** — 延いては (ひいては)

   Original Japanese: これがひいては落語家内部の対立の原因となっている。

   Original Vietnamese: Điều này, về lâu dài, trở thành nguyên nhân gây mâu thuẫn trong nội bộ giới nghệ sĩ rakugo.

   Problem: ひいては means by extension/as a further consequence, not 'về lâu dài' (in the long term).

   Corrected Japanese: これがひいては落語家内部の対立の原因となっている。

   Corrected Vietnamese: Điều này còn kéo theo mâu thuẫn trong nội bộ giới nghệ sĩ rakugo.

20. **N1 · jcf0acf7a2a71 · Tatoeba · fix** — 飽和 (ほうわ)

   Original Japanese: ゲーム機の国内市場は飽和状態で、大きなヒットは期待できない。

   Original Vietnamese: Thị trường máy chơi game trong nước đã bão hòa, khó kỳ vọng vào một cú hích lớn.

   Problem: A 大きなヒット is a major commercial hit, not a stimulus/boost (cú hích).

   Corrected Japanese: ゲーム機の国内市場は飽和状態で、大きなヒットは期待できない。

   Corrected Vietnamese: Thị trường máy chơi game trong nước đã bão hòa, khó kỳ vọng có sản phẩm nào thành công vang dội.

**Reproducibility**

| Input | SHA-256 |
| --- | --- |
| authored.json | `fd5f87346e4f4b8d143368e2adc4ae6d2a6022118e9553cf05a3930a7dafb4be` |
| licensed-candidates.json | `4d02e6bd9087b1b35315ea3311c5ac22652d06983153c28267f1e84ea2c691a7` |

The JSON contains exactly one verdict for each of the 1,409 unique input IDs. All fix entries contain both `suggested_ja` and `suggested_vi`; pass entries have empty `issues`. Input hashes were checked again after the review, and the repository worktree remained clean.
