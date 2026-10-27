# Nguồn dữ liệu

- [JMdict và KANJIDIC2, EDRDG](https://www.edrdg.org/edrdg/licence.html): CC BY-SA 4.0, bản jmdict-simplified 3.6.2, ngày từ điển 2026-10-26.
- [jmdict-simplified](https://github.com/scriptin/jmdict-simplified): định dạng JSON nguồn, 3.6.2+20261026175559.
- [Tanos, Jonathan Waller](https://www.tanos.co.uk/jlpt/sharing/): danh sách JLPT, CC BY.
- [Bluskyo/JLPT_Vocabulary](https://github.com/Bluskyo/JLPT_Vocabulary): bản chuyển đổi JSON, MIT.
- [KanjiVG](https://kanjivg.tagaini.net/): Ulrich Apel, CC BY-SA 3.0, r20260714.
- [Kanjium](https://github.com/mifunetoshiro/kanjium): Uros O., dữ liệu cao độ CC BY-SA 4.0.
- [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) và [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).

Đầu vào lưu ngoài repository, chỉ đọc tại ../src. SHA-256 nằm trong meta.json. tools/build-data.py là pipeline tái dựng. Nghĩa tiếng Việt do dự án dịch từ tiếng Anh của JMdict; không nhập bộ từ điển Nhật–Việt không rõ giấy phép. Nghĩa tiếng Anh được giữ để đối chiếu. Từng mục ghi phương pháp: "dịch từ JMdict (tiếng Anh), cần người bản ngữ kiểm tra".

- [Helsinki-NLP/opus-mt-en-vi](https://huggingface.co/Helsinki-NLP/opus-mt-en-vi): Marian dịch Anh–Việt, Apache-2.0; chỉ hỗ trợ nháp trong quá trình biên soạn. Thông số, SHA-256 model và phạm vi rà trong sources/translation-method.json. Model không có trong bản phát hành.
- [Lucide](https://github.com/lucide-icons/lucide): ISC, một số icon gốc Feather/MIT; nguyên thông báo trong ../vendor/lucide.LICENSE.
- [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs): MIT, phiên bản 5.4.2, sao chép bản đang dùng của English Neko.
- Bản văn giấy phép đầy đủ lấy từ repository chính thức [Creative Commons](https://github.com/creativecommons/creativecommons.org/tree/main/docroot/legalcode): by-sa_4.0.txt và by-sa_3.0.txt, lưu tại LICENSE-CC-BY-SA-4.0.txt và LICENSE-CC-BY-SA-3.0.txt.

Tệp âm thanh tổng hợp được tạo bằng edge-tts, giọng ja-JP-NanamiNeural; 8.344 MP3. Nhật ký gốc: sources/audio-generation.json; các đợt bổ sung: sources/audio-generation-n*.json. Không gửi bản ghi giọng người học đến dịch vụ tạo giọng. Từ chưa có MP3 dùng speechSynthesis trên thiết bị.

- [Tatoeba downloads](https://tatoeba.org/en/downloads), [quy định sử dụng corpus](https://en.wiki.tatoeba.org/articles/show/using-the-tatoeba-corpus), [CC BY 2.0 FR](https://creativecommons.org/licenses/by/2.0/fr/): câu Nhật và bản dịch Việt/Anh, bản xuất nhận 2026-10-27. Username/ID/URL của từng câu nằm trong dữ liệu; SHA-256 của jpn.tsv, vie.tsv, eng.tsv, links.csv trong sources/tatoeba-method.json. Không có cột licence trong detailed TSV này, dùng giấy phép văn bản của bản xuất. Không dùng audio Tatoeba.
- [fugashi](https://github.com/polm/fugashi) và [unidic-lite](https://github.com/polm/unidic-lite): công cụ phân tích biên từ/cách đọc và tạo furigana bảo thủ lúc biên soạn; không tải trong ứng dụng.

- [UniDic 2.1.2, NINJAL / The UniDic Consortium](https://clrd.ninjal.ac.jp/unidic/en/back_number_en.html), [điều khoản](https://clrd.ninjal.ac.jp/unidic/faq.html): chọn BSD-3-Clause; bản binary qua unidic-lite 1.0.8, đọc bằng fugashi 1.5.2. 935 accent trích trực tiếp, giữ thứ tự biến thể. SHA-256, phiên bản và phương pháp: sources/pitch-method.json; từng bản ghi: sources/pitch-additions.json; còn thiếu: sources/pitch-unresolved.json. Không phân phối binary từ điển.
- Kanjium tại [commit 9ebca4589565c696e7c39e089e2e928ad65f678c](https://github.com/mifunetoshiro/kanjium/tree/9ebca4589565c696e7c39e089e2e928ad65f678c): đã kiểm tra raw/accents.txt và các bảng edict, jukugo, compverbs, yojijukugo; thêm 1 mục khớp acc_pos, giữ nguyên 7.096 mẫu cũ.

### Bộ phân tích furigana — đối chiếu 2026-10-27

- [fugashi 1.5.2](https://github.com/polm/fugashi/tree/v1.5.2): [MIT](https://raw.githubusercontent.com/polm/fugashi/v1.5.2/LICENSE), Paul O’Leary McCann. Bản cài giữ tại [LICENSE-fugashi-MIT.txt](LICENSE-fugashi-MIT.txt). Wheel kèm MeCab của Taku Kudo / Nippon Telegraph and Telephone Corporation, BSD-3-Clause: [LICENSE-MeCab-BSD.txt](LICENSE-MeCab-BSD.txt).
- [unidic-lite 1.0.8](https://github.com/polm/unidic-lite): mã đóng gói MIT (Paul McCann), [bản quyền](LICENSE-unidic-lite-MIT.txt). Dữ liệu UniDic 2.1.2 có giấy phép riêng, **chọn BSD-3-Clause** trong GPL/LGPL/BSD theo [NINJAL FAQ](https://clrd.ninjal.ac.jp/unidic/faq.html); giữ nguyên [BSD](LICENSE-UniDic-BSD.txt), [AUTHORS](AUTHORS-UniDic.txt), [COPYING](COPYING-UniDic.txt). Không nhầm giấy phép MIT của gói với từ điển.
- Binary sys.dic SHA-256 `122c4c91f026bf4b65bbe2dfd8b9f8eeb6ab56d8eb2a7287a68bca75708ba513`; các sửa nhỏ của unidic-lite như phần cao độ. Kết quả trích đọc từ điển giữ BSD-3-Clause; câu Tatoeba giữ CC BY 2.0 FR. Chính sách/các số bị bỏ: [furigana-method.json](sources/furigana-method.json).

- Bản dịch câu máy N2/N1: [Helsinki-NLP/opus-mt-en-vi model card](https://huggingface.co/Helsinki-NLP/opus-mt-en-vi/raw/main/README.md), Apache-2.0 (đối chiếu 2026-10-27). Trọng số gốc Marian, token `>>vie<<`, chạy offline; hash/engine/tham số trong sources/tatoeba-machine-method.json. Bản dịch máy giữ giấy phép phái sinh CC BY 2.0 FR của câu; chỉ mẫu ID công bố được Codex xem/sửa, không kiểm định bản ngữ. Không dùng bản CTranslate2 cache lỗi.


## Ví dụ v5

Nguồn và đầu vào được ghim trong [hồ sơ nguồn v5](../ex5/sources-checked.md) và [manifest](../ex5/input-manifest.json): Tatoeba (CC BY 2.0 FR), KFTT 1.0 (CC BY-SA 3.0), Wiktionary tiếng Nhật (CC BY-SA 4.0, revision cố định), KNBC 1.0 (BSD ba khoản tiếng Nhật). Thông báo nguyên văn KFTT/KNBC ở `../ex5/licences/`; per-item credit và sửa đổi nằm trong `sources/examples-v5.json`. Câu nguồn được sửa vẫn giữ nguồn/giấy phép, có `original_ja` và `changes`; bản dịch người đóng góp bị sửa giữ `translation.original`.

Câu AI dùng `source:"ai"`, nhãn “Câu do AI viết, cần kiểm tra”, ghi công OpenAI Codex và CC BY-SA 4.0; không mang nhãn Tatoeba. [Review](../ex5/review.json) tách khỏi [quyết định cuối](../ex5/final.json): bản viết lại chỉ có `rewrite_selfcheck` của trợ lý tích hợp, không phải review độc lập. Phương pháp, số lượng và giới hạn ở [DATA](../docs/DATA.md).
