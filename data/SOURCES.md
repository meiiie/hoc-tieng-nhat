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

Tệp âm thanh tổng hợp được tạo bằng edge-tts, giọng ja-JP-NanamiNeural; 3.093 MP3. Nhật ký gốc: sources/audio-generation.json; các đợt bổ sung: sources/audio-generation-n*.json. Không gửi bản ghi giọng người học đến dịch vụ tạo giọng. Từ chưa có MP3 dùng speechSynthesis trên thiết bị.

- [Tatoeba downloads](https://tatoeba.org/en/downloads), [quy định sử dụng corpus](https://en.wiki.tatoeba.org/articles/show/using-the-tatoeba-corpus), [CC BY 2.0 FR](https://creativecommons.org/licenses/by/2.0/fr/): câu Nhật và bản dịch Việt/Anh, bản xuất nhận 2026-10-27. Username/ID/URL của từng câu nằm trong dữ liệu; SHA-256 của jpn.tsv, vie.tsv, eng.tsv, links.csv trong sources/tatoeba-method.json. Không có cột licence trong detailed TSV này, dùng giấy phép văn bản của bản xuất. Không dùng audio Tatoeba.
- [fugashi](https://github.com/polm/fugashi) và [unidic-lite](https://github.com/polm/unidic-lite): công cụ kiểm tra biên từ/cách đọc lúc biên soạn, không tạo furigana, không tải trong ứng dụng.
