# Dữ liệu

Đầu vào được cung cấp tại `../src`, chỉ đọc. Ngày từ điển 2026-10-26, jmdict-simplified `3.6.2+20261026175559`. SHA-256 từng JSON/text gốc nằm trong `data/meta.json`. Không nhập từ điển Nhật–Việt không rõ giấy phép.

## Số lượng thực tế

| Cấp | Từ phân biệt | Có nghĩa Việt | Có Hán Việt | Có cao độ | Có MP3 |
|---|---:|---:|---:|---:|---:|
| N5 | 684 | 684 | 514 | 638 | 684 |
| N4 | 641 | 641 | 496 | 605 | 641 |
| N3 | 1.768 | 1.768 | 1.546 | 1.712 | 1.768 |
| N2 | 1.826 | 1.826 | 1.508 | 1.749 | 1.826 |
| N1 | 3.425 | 3.425 | 3.152 | 3.328 | 3.425 |
| Tổng | 8.344 | 8.344 | 7.216 | 8.032 | 8.344 |

`data/kanji.json` có **2.535 kanji**, tất cả có âm Hán Việt trong KANJIDIC2 và SVG KanjiVG. `data/kana.json` có **214 mục**: mỗi bảng có 46 âm cơ bản, 25 âm đục/bán đục, 36 âm ghép. **2.683 SVG** là hợp của các chữ trong danh mục kanji JLPT, chữ xuất hiện trong từ vựng và kana dùng trong bảng; không sao chép toàn bộ KanjiVG hoặc các biến thể không dùng. SVG nguồn giữ nguyên byte.

## Ghép Tanos với JMdict

JSON Tanos có **8.138 khóa dạng chữ**, chứa **8.505 dòng dạng chữ + cách đọc**. Chỉ số `5` là N5 và `1` là N1. Nhiều khóa có hơn một cách đọc; vì vậy 8.138 không phải số thẻ cuối.

- Ghép nguyên bản bằng kanji + kana, tuân thủ ràng buộc cách đọc JMdict: **8.349/8.505 = 98,1658%**. Mục chỉ có kana được ghép bằng cách đọc, với lựa chọn từ đồng âm riêng khi cần.
- **156 dòng** không ghép chính xác lúc đầu được ghi trong `data/sources/unmatched.tsv`, kể cả những dòng sau đó sửa được.
- Sau sửa lỗi có nguồn: **8.471 dòng ghép chính xác**, **14 dòng có liên kết JMdict được rà riêng**, **20 dòng cách ly**. Tỷ lệ chính xác sau sửa là **8.471/8.485 = 99,8350%**, không tính 20 dòng cách ly. Đây là tỷ lệ ghép dữ liệu, không phải độ chính xác nghĩa Việt.
- Hợp nhất **141 dòng trùng** theo cặp chữ + cách đọc tạo **8.344 mục** cuối. Cặp xuất hiện ở nhiều cấp lấy cấp dễ nhất, tức số N lớn nhất.

`entry-fixes.tsv` giữ cặp gốc, cặp sửa, lý do, JMdict ID khi liên kết thủ công và cờ cách ly. Sửa các lỗi cột/ký tự như `賛成 / Uӣ[い`, phần “（する）” lọt vào cách đọc và đuôi bị mất. Không âm thầm sửa JSON gốc. `sense-selection.tsv` ghim 28 lựa chọn từ đồng âm (chẳng hạn はし, そば, 虹); pipeline assert lựa chọn có trong tập ghép. `quarantined.tsv` công bố 20 âm Hán đơn tự không tìm thấy mục từ phù hợp để dạy, đều thuộc nguồn N1. Chúng không có thẻ hoặc nghĩa bịa.

Tanos là danh mục cộng đồng, có các dạng hiếm/cũ và không đủ ngữ cảnh cho mọi từ đồng âm. Ghép được một JMdict ID không chứng minh đó là nghĩa được người soạn Tanos định chọn. Các sửa/ghim đã được AI xem xét, cần kiểm tra song ngữ độc lập, nhất là N1. Không tuyên bố đây là danh sách từ chính thức của kỳ thi.

## Pipeline và định dạng

```sh
python3 tools/build-data.py --source ../src
```

Python chuẩn và Node (dùng cùng bộ chuyển kana/romaji với ứng dụng), không mạng, không model dịch. Sắp xếp cố định theo cấp, kana chuẩn hóa và chữ. ID là `j` + 12 ký tự đầu SHA-256 của `kanji + NUL + reading`; nghĩa Việt thay đổi không làm đổi ID. TSV bản dịch là đầu vào đã rà, không phải kết quả được tự ghi đè mỗi lần build. Chế độ phát hành từ chối nghĩa trống trước khi ghi dữ liệu; `--draft` chỉ dùng trong biên soạn. Các bản dịch nháp nằm ngoài bản phát hành.

| Trường từ | Nội dung |
|---|---|
| `id`, `kanji`, `kana`, `romaji`, `level` | ID ổn định, dạng chữ, cách đọc, romaji, cấp 5–1 |
| `pos` | Nhãn từ loại tiếng Việt, tối đa hai nhóm khác nhau |
| `en`, `jmdict`, `match`, `sourceForm` | Các nghĩa Anh đúng ràng buộc kana/kanji, ID từ điển, cách ghép, cặp Tanos gốc |
| `v`, `viMethod` | Nghĩa Việt ngắn và phương pháp cho từng mục |
| `hv` | Ghép âm `vietnam` của từng kanji, viết thường; `/` phân cách biến thể, `·` phân cách chữ |
| `pitch`, `pitchSource` | Số accent gốc và nguồn `kanjium`/`unidic-2.1.2`; cả hai `null` khi thiếu |
| `example` | Câu Tatoeba, bản dịch, tác giả/ID/URL/giấy phép và vị trí khớp chính xác; thiếu thì `null` |
| `audio` | Đường dẫn MP3 thực sự tồn tại, hoặc `null` |

Hán Việt trình bày **theo từng chữ**, không tự chọn một cách đọc chuẩn cho cả từ; thí dụ 校 có nhiều âm trong KANJIDIC2. Từ thuần kana không tự suy diễn Hán Việt. `kanji.json` giữ toàn bộ âm on/kun, Hán Việt, cấp từ danh mục kanji (có thể `null` nếu chữ chỉ có trong từ vựng), số nét và đường dẫn SVG. Không suy cấp của chữ từ cấp của từ chứa nó.

Cao độ có nguồn tăng từ **7.096 lên 8.032**: thêm **936** (935 UniDic, 1 Kanjium). Còn **312 mục `null`**, không đoán khi thiếu hoặc mơ hồ. Giữ thứ tự biến thể trong nguồn; số accent phải nằm trong số mora của từ. ID và 7.096 giá trị cũ không thay đổi.

## Bổ sung cao độ có nguồn

`data/sources/pitch-method.json` ghi số trước/sau từng cấp, phiên bản, SHA-256 và URL nguồn; `pitch-additions.json` giữ từng giá trị gốc và khóa ghép. `pitch-unresolved.json` công bố các mục còn `null`. Không thay các giá trị Kanjium đã có.

Đã đối chiếu `../src/accents.txt` với Kanjium tại commit `9ebca4589565c696e7c39e089e2e928ad65f678c`: cùng byte. Kiểm tra thêm các bảng `edict`, `jukugo`, `compverbs`, `yojijukugo` và mô tả cột; một mục có giá trị `acc_pos` khớp chính xác dạng chữ/cách đọc. Giữ dòng nguồn, số dòng, ID bảng và giấy phép CC BY-SA 4.0 của Uros O.

Nguồn bổ sung chính: [UniDic 2.1.2](https://clrd.ninjal.ac.jp/unidic/en/back_number_en.html), The UniDic Consortium, qua `unidic-lite==1.0.8`. [NINJAL cho chọn BSD trong bộ ba giấy phép](https://clrd.ninjal.ac.jp/unidic/faq.html); dự án chọn BSD-3-Clause và giữ nguyên `data/LICENSE-UniDic-BSD.txt`, `data/AUTHORS-UniDic.txt`, `data/COPYING-UniDic.txt`. Không phân phối toàn bộ từ điển. Gói unidic-lite có thay đổi nhỏ so với bản gốc (thêm 令和, bỏ mục số/chữ Latin đơn, sửa mục chưa biết); ghim hash đúng binary đã dùng, không gọi đây là bản UniDic gốc chưa sửa.

[UniDic mô tả `aType`](https://clrd.ninjal.ac.jp/unidic/UNIDIC_manual.pdf#page=27) là vị trí accent tính theo mora; 0 là heiban, danh sách phân cách bằng dấu phẩy giữ thứ tự ưu tiên. Công cụ đọc mọi nút từ điển thật của fugashi `-a`, đòi nguyên từ bằng `surface`, `orth`, `orthBase`; cả `kana` và `kanaBase` phải đúng cách đọc. Lemma phải thuộc dạng chữ của mục JMdict đã chọn (chỉ bỏ hậu tố nguồn gốc từ mượn như `-apartment`); không dùng riêng cách đọc để cho phép lemma khác. Chỉ nhận `aType` số, không sửa accent, không nút chưa biết, không quy tắc chia động từ hay nối từ. Mọi nút phù hợp phải đồng ý cả giá trị lẫn thứ tự biến thể. Nếu còn mơ hồ, giữ `null`.

Tái trích: `.cache/content-venv/bin/python tools/pitch_sources.py --download` (tải Kanjium đã ghim vào `.cache`); sau đó `python3 tools/build-data.py`. Build thông thường chỉ đọc overlay, không chạy bộ phân tích. `tests/pitch_sources_test.py` kiểm tra từ đồng âm, từ ghép, nút chưa biết và bẫy tên riêng/ký hiệu; `tests/pitch_provenance.py` đối chiếu từng bản ghi với binary/dòng nguồn và bảo toàn toàn bộ accent/ID cũ. Không dùng Wiktionary hoặc nguồn không rõ giấy phép trong đợt này. Chưa có kiểm định accent bởi người bản ngữ; đây là dữ liệu từ điển, không phải kết quả suy từ âm thanh Nanami.

## Câu ví dụ Tatoeba

<!-- example-counts:start -->
| Cấp | Có ví dụ | Việt trực tiếp | Việt qua Anh (pivot) | Dịch máy |
|---|---|---|---|---|
| N5 | 649 | 541 | 37 | 71 |
| N4 | 627 | 450 | 59 | 118 |
| N3 | 1718 | 1044 | 169 | 505 |
| N2 | 1521 | 294 | 134 | 1093 |
| N1 | 2420 | 632 | 195 | 1593 |
<!-- example-counts:end -->

Mỗi từ được chọn tối đa một câu thật, dài 4–25 ký tự, có dấu kết câu và tác giả được nêu tên. Tệp chi tiết thực tế có sáu cột `id, lang, text, username, created, modified`, **không có cột giấy phép**; văn bản được tái sử dụng theo CC BY 2.0 FR của bản xuất Tatoeba. Bỏ câu không có chủ sở hữu. SHA-256 và phương pháp nằm trong `data/sources/tatoeba-method.json`; nguyên câu, tên người đóng góp và liên kết `https://tatoeba.org/sentences/show/<id>` giữ cho cả Nhật, Việt và Anh được dùng.

Chọn bản dịch Việt có liên kết trực tiếp trước; nếu thiếu, chọn Việt nối qua một câu Anh và ghi `pivot:true`, nhãn **dịch qua câu tiếng Anh**. Nếu chỉ có câu Anh liên kết trực tiếp, bản dịch AI sang Việt giữ `machine:true`, nhãn **bản dịch máy, cần kiểm tra**. Không gọi các bản dịch AI là bản dịch do người đóng góp Tatoeba viết. Cột Việt trực tiếp/pivot chỉ cho biết nguồn văn bản do người đóng góp đăng; chưa có biên tập viên bản ngữ kiểm định chúng hay xác minh cách tác giả tạo ra chúng.

`match` ghi `start`, `end`, `surface`, `kind:exact` hoặc `kind:lemma`. Biên từ và cách đọc được kiểm tra bằng fugashi 1.5.2 + UniDic 2.1.2 (unidic-lite 1.0.8). Chỉ lấy dạng chữ hoặc kana nguyên vẹn, không ghép một phần kanji/từ đồng âm khác cách đọc. Bản 1.9.0 dùng lemma + POS và kiểm tra dạng chữ/cách đọc JMdict cho động từ/tính từ đã chia; không tìm chuỗi thân từ bằng cách cắt đuôi. Bộ phân tích vẫn có thể sai nghĩa/cách tách; không bảo đảm mọi ví dụ đúng sense JLPT. Furigana được biên soạn offline theo chính sách bảo thủ bên dưới. Cloze che đúng đoạn khớp; chỉ bật khi có ví dụ hợp lệ.

Đầu vào biên soạn bền vững: `tatoeba-examples.json`, `tatoeba-vi-machine.tsv`, `tatoeba-exclusions.json`. Tệp loại trừ ghi lý do cho câu/link lỗi phát hiện khi rà. `tools/build-data.py` luôn ghép overlay, giữ ID từ và tiến độ cũ. Tái chọn bằng `tools/tatoeba.py --levels 5 4` rồi `tools/apply-examples.py .cache/examples-5-4.json`; bước apply từ chối bản dịch máy còn trống. Dùng venv biên soạn `.cache/content-venv`, không phân phối bộ tách từ/từ điển trong website.

`tests/tatoeba_provenance.py` đối chiếu tất cả câu/ID/tác giả với TSV gốc và mọi cạnh liên kết với links.csv. `tests/example_matching.py` kiểm tra khớp từ và các trường hợp âm/biên sai; Node kiểm tra thuộc tính ghi công, câu ngắn và vị trí từ; E2E kiểm tra nhãn, nguồn và bước cloze. Nhật ký tự rà: `data/sources/tatoeba-review.json`. Ở đợt ví dụ lịch sử 1.0–1.7, Codex đã dịch/đối chiếu các trường hợp máy, xem mẫu 35 bản dịch của người đóng góp N5/N4 và 60 N3; lỗi phát hiện được loại bằng danh sách có lý do. Không suy ra tỷ lệ chính xác; chưa có người bản ngữ rà toàn bộ câu/bản dịch. Không dùng `sentences_with_audio.csv`: phát âm câu vẫn dùng giọng thiết bị; không tải audio Tatoeba khi chưa kiểm tra giấy phép riêng từng bản ghi.

### Ghép dạng biến cách (1.9.0)

`tools/example_lemmas.py` dùng UniDic `lemma`, `orthBase`, `kanaBase`, POS và dạng chữ JMdict đúng ràng buộc cách đọc. Không chấp nhận chỉ vì đồng âm. Nếu UniDic gộp lemma của hai cách viết (như 閉める/締める), kanji xuất hiện vẫn phải thuộc từ đích. Cách đọc kana thay cho kanji cũng phải chỉ đúng lexeme; chuỗi trợ từ như と + お không được khớp 十/とお. Cách đọc mơ hồ, từ không phân tích chắc hoặc sai POS bị bỏ.

Từ viết kana cũng giữ phân biệt lemma từ mượn khi từ điển có nút nguyên token cho kanji của từ đích: アイ-eye không được khớp 藍/アイ (cây chàm). Đây không phải kiểm định sense toàn bộ câu. Trường hợp tên người マーク mà UniDic vẫn chọn danh từ thường được loại bằng ngoại lệ nguồn có lý do. Provenance từ chối mọi ID câu đã có trong danh sách loại, gồm lỗi nguồn １５年間前; các mục loại sau lựa chọn được ghi ở `postSelectionRejected`.

Vị trí cloze bao gồm dạng thực và trợ động từ liên tiếp: 食べました → 食べる, 高かった → 高い, 勉強しませんでした → 勉強する; bao gồm ない ở dạng phủ định. `match` lưu `lemma`, `dictionaryForm`, `targetReading`, `surfaceReading`, `pos`, `lexicalEnd`. Bước điền câu nhận dạng thực bằng kanji/kana/romaji, không nhận dạng từ điển thay cho phần biến cách; phản hồi hiện đúng phần đã che. Lịch SRS không đổi.

Tái chọn bằng `.cache/content-venv/bin/python tools/tatoeba.py --levels 5 4 3`, `python3 tools/apply-examples.py .cache/examples-5-4-3.json`, rồi annotate/build. Giữ ví dụ cũ còn hợp lệ, chỉ thay khi chất lượng bản dịch cao hơn (Việt trực tiếp > Việt qua Anh > máy), hoặc bản dịch người đóng góp cùng loại có câu ngắn hơn. Giữ câu máy cũ nếu chỉ có máy mới ngắn hơn. Loại các ví dụ cũ sai biên/POS/lexeme; từng thay đổi nằm trong `tatoeba-selection-5-4-3.json`. Không thể bảo đảm cùng sense trong mọi thành ngữ hoặc ngữ cảnh.

## Furigana câu ví dụ (1.8.0)

Chạy `.cache/content-venv/bin/python tools/annotate-examples.py` rồi `python3 tools/build-data.py`. Ghim fugashi 1.5.2, unidic-lite 1.0.8 / UniDic 2.1.2 và SHA-256 binary; không cần mạng. Build thường chỉ đọc overlay đã biên soạn. Không tải bộ phân tích hoặc từ điển vào trình duyệt.

`example.furigana` là danh sách `{base, ruby?}` nối lại đúng nguyên câu. Chỉ nhóm kanji nhận ruby, kana/okurigana luôn giữ riêng. Mọi nút từ điển nguyên token phải thống nhất một cách đọc, hoặc cách đọc phải đồng ý với từ đích JMdict. Từ chưa biết, tên riêng, số/đơn vị đếm, 今日/一日/人, cách đọc khác nhau và phép tách kana không duy nhất giữ nguyên chữ. `furiganaEvidence` trong overlay nguồn lưu cách đọc và nguồn tin cậy; `furiganaSkipped` lưu vị trí/lý do từng token kanji bị bỏ. JSON dùng trong trình duyệt chỉ chứa các đoạn `furigana`, không tải những bản ghi kiểm toán từ điển lặp lại này. Đây là bộ lọc bảo thủ, không phải xác suất thống kê hay kiểm định bản ngữ.

Nút furigana hiện có điều khiển cả từ và câu. Các bộ đếm theo từng ví dụ của từng từ (có thể lặp ID câu) ở `data/sources/furigana-method.json`; token bỏ chỉ đếm token chứa kanji. Câu chỉ có kana được đếm riêng. `tests/furigana.py` tái tạo toàn bộ annotation bằng dictionary thật và kiểm tra cách đọc từ đích; Node kiểm tra phép nối base, không ruby kana và bằng chứng. Chưa bảo đảm đọc đúng mọi ngữ cảnh.

<!-- furigana-counts:start -->
| Cấp | Ruby đầy đủ | Ruby một phần | Chưa ruby | Chỉ kana | Token bỏ | Khớp lemma |
|---|---|---|---|---|---|---|
| N5 | 222 | 322 | 77 | 28 | 632 | 99 |
| N4 | 210 | 347 | 48 | 22 | 604 | 132 |
| N3 | 515 | 1080 | 90 | 33 | 1965 | 165 |
| N2 | 478 | 895 | 93 | 55 | 1543 | 320 |
| N1 | 781 | 1411 | 163 | 65 | 2482 | 342 |
<!-- furigana-counts:end -->

### Mở rộng N2/N1 và bản dịch máy (1.10.1)

N2/N1 dùng cùng bộ chọn câu 4–25 ký tự, kiểm tra exact/lemma, ưu tiên Việt trực tiếp rồi Việt qua Anh, cùng ghi công Tatoeba/CC BY 2.0 FR và bộ lọc ruby. Quy trình: `tools/tatoeba.py --levels 2 1`, apply, annotate, build. `tatoeba-selection-2-1.json` ghi các từ có câu.

Các bản dịch máy đã có từ trước được giữ. Phần Anh liên kết còn thiếu dùng model [Helsinki-NLP/opus-mt-en-vi](https://huggingface.co/Helsinki-NLP/opus-mt-en-vi) (Apache-2.0) chạy offline bằng Transformers/PyTorch từ trọng số gốc. Model không được phân phối. Bản chuyển đổi CTranslate2 cũ cho kết quả lỗi trong smoke test nên **không dùng để tạo bản dịch phát hành**. Bản gốc được thử với câu đơn giản trước khi chạy; smoke test không chứng minh chất lượng toàn bộ dữ liệu.

`tools/translate-example-drafts.py` tạo nháp trong `.cache`; `tools/import-example-drafts.py` nhập nháp với thông tin kiểm tra tách biệt. `tatoeba-machine-method.json` ghim engine, tham số, hash, số đã xem/sửa; `tatoeba-machine-methods.json` ghi `aiSpotChecked`, `aiCorrected`, `nativeReviewed:false` và ID câu Anh cho từng câu mới. Chỉ các ID đã ghi mới được Codex xem/sửa; **phần còn lại chưa được đối chiếu từng câu với tiếng Nhật**. Mọi bản dịch này vẫn `machine:true`, nhãn **bản dịch máy, cần kiểm tra**, kể cả đã được cùng AI xem lại. `translation.translator` ghi đúng model và phần sửa của Codex; không gán nhãn người đóng góp Tatoeba cho bản dịch máy.

Mẫu rà nguồn Việt và bản dịch máy, các lỗi đã sửa/loại và giới hạn nằm trong `tatoeba-review.json`. Không có tỷ lệ chính xác hoặc đánh giá bản ngữ. Các bản dịch máy chưa rà có thể sai nghĩa từ đa nghĩa, thành ngữ và thuật ngữ chuyên ngành; đây là dữ liệu cần kiểm tra tiếp.

## Âm thanh

`tools/gen-audio.py` dùng cùng pipeline N5/N4: edge-tts 7.3.1, `ja-JP-NanamiNeural`, đầu vào kana, FFmpeg MP3 mono 24 kHz / 32 kbit/s. Đường dẫn `audio/n<level>/w/<id>.mp3`. Tệp chỉ được đưa vào vị trí phát hành sau khi giải mã thành công, sau đó `tools/build-data.py` gắn đường dẫn thực sự tồn tại. Không đổi ID từ hoặc schema tiến độ.

Có **8.344 MP3**, tổng **65.934.464 byte**. Bảng phía trên là số thực tế từng cấp. Mọi tệp của các cấp hoàn tất được kiểm tra lại bằng FFmpeg và ffprobe (`tests/audio_decode.py`): phải giải mã được, đúng mono/24 kHz/32 kbit/s, không thiếu/thừa ID. Chưa nghe duyệt từng tệp; giọng TTS có thể chọn accent khác từ điển. Không dùng MP3 làm nhãn chuẩn để chấm phát âm.

Chạy nền theo lô 100, bốn yêu cầu đồng thời, tiếp tục được từ tệp đã có: `python3 tools/gen-audio.py --levels n3 --chunk-size 100 --workers 4`. Mỗi lỗi được thử tối đa 5 lần, chờ 3/6/12/24 giây; dừng lấy việc mới sau 3 từ lỗi liên tiếp đã hết lượt thử. Có `--offset`/`--limit` để chạy một đoạn. Nhật ký riêng cho từng cấp tại `data/sources/audio-generation-n*.json`, giữ số thật, lỗi và retry; kết thúc thiếu không báo complete. `tests/audio_generation.py` kiểm tra retry/backoff, hết lượt và hủy.

MP3 và nét chữ tải lười, không nằm trong SW shell. Cài đặt tải bộ đang chọn (chọn cấp ở trang chủ); từ chưa có MP3 dùng speechSynthesis ja-JP của thiết bị, khả năng offline tùy máy. [Git LFS không được Pages hỗ trợ](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage); dự án không dùng LFS.

Giới hạn đã đối chiếu ngày 2026-10-27: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) cho site tối đa 1 GB, băng thông mềm 100 GB/tháng; [GitHub files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) chặn tệp trên 100 MiB. `tools/site-size.py` kiểm kê toàn bộ tệp Git phát hành, áp ngưỡng mỗi tệp dưới 100 MB nghiêm hơn và site dưới 1 GB; không tính .git/node_modules/.cache vào site. Kích thước đối tượng Git được báo riêng trong report. Không có số liệu băng thông sử dụng thực tế.

## Kiểm soát và giấy phép

Node kiểm tra đủ cấp/trường, ID duy nhất, kana hợp lệ, bản dịch không trống/không còn mẫu tiếng Anh rõ ràng/không emoji, Hán Việt đối chiếu từng âm KANJIDIC2, giới hạn cao độ, audio tồn tại và mọi kanji N5 có SVG. Một lượt giải mã riêng kiểm tra toàn bộ MP3; nó không đo chất lượng nói. So sánh SHA-256 trước/sau build xác minh tái dựng không đổi các tệp đã tạo.

JMdict, KANJIDIC2 và bản dịch phái sinh giữ CC BY-SA 4.0. Tanos/Waller CC BY, bản chuyển đổi Bluskyo MIT; Kanjium CC BY-SA 4.0; phần trích UniDic BSD-3-Clause; SVG KanjiVG giữ CC BY-SA 3.0. [NOTICE](../data/NOTICE.md) và [SOURCES](../data/SOURCES.md) có ghi công, liên kết giấy phép và mô tả phần sửa.

## Kiểm tra tự động thay cho người duyệt bản ngữ (1.10.2)

**Âm thanh: nghe lại bằng máy.** `tools/audio_roundtrip_logits.py` + `tools/audio-roundtrip-score.js` cho mô hình japanese-hubert-base-phoneme-ctc-v4 (cũng là mô hình chấm phát âm trong app) nghe từng MP3 và chấm so với kana của từ. Kết quả cuối (`data/sources/audio-roundtrip.json`): 7.864 tệp ≥ 85 điểm (94,2%), 380 tệp 60–84, 100 tệp < 60. Lần đầu có 252 tệp < 60; `tools/audio_regen_flagged.py` thu lại bằng Nanami với `kana。`, `「kana」` hoặc `chữ Hán。` và chỉ thay khi bản mới ≥ 85 và hơn bản cũ ≥ 20 điểm: 152 tệp được thay (`data/sources/audio-regenerated.json`, danh sách `audio-replaced-1.10.2.json`). Nhiều lỗi là từ một mora (ぶ, げ, き) mà Nanami đọc thành âm khác.

Giới hạn: người chấm và người chọn bản thay là cùng một mô hình, nên đây không phải bằng chứng độc lập. Mô hình hay nhầm phụ âm đầu từ ngắn (k/g, t/d, n/m, h/f/w); nhiều tệp trong 100 tệp còn lại có thể đúng. Chưa có người nghe lại.

**Nghĩa Việt: dịch ngược.** `tools/meaning_crosscheck.py` dịch nghĩa Việt sang Anh bằng Helsinki-NLP/opus-mt-vi-en và so từ nội dung với chú giải JMdict. 5.636 khớp rõ, 86 khớp một phần, 2.622 không chung từ nào. Đọc thử ngẫu nhiên 15 mục "không khớp" thì cả 15 đều là nghĩa Việt chấp nhận được; lệch là do dịch ngược hoặc từ đồng nghĩa (chất lên → "load" so với "pile up"). Vì vậy nhãn này chỉ dùng để ưu tiên rà soát, không hiển thị như cảnh báo trong app. Một lượt đánh giá bằng mô hình ngôn ngữ lớn chưa chạy.
