# Dữ liệu

Đầu vào được cung cấp tại `../src`, chỉ đọc. Ngày từ điển 2026-10-26, jmdict-simplified `3.6.2+20261026175559`. SHA-256 từng JSON/text gốc nằm trong `data/meta.json`. Không nhập từ điển Nhật–Việt không rõ giấy phép.

## Số lượng thực tế

| Cấp | Từ phân biệt | Có nghĩa Việt | Có Hán Việt | Có cao độ | Có MP3 |
|---|---:|---:|---:|---:|---:|
| N5 | 684 | 684 | 514 | 506 | 684 |
| N4 | 641 | 641 | 496 | 488 | 641 |
| N3 | 1.768 | 1.768 | 1.546 | 1.536 | 0 |
| N2 | 1.826 | 1.826 | 1.508 | 1.494 | 0 |
| N1 | 3.425 | 3.425 | 3.152 | 3.072 | 0 |
| Tổng | 8.344 | 8.344 | 7.216 | 7.096 | 1.325 |

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
| `pitch` | Danh sách số accent từ Kanjium, hoặc `null` khi thiếu |
| `example` | Câu Tatoeba, bản dịch, tác giả/ID/URL/giấy phép và vị trí khớp chính xác; thiếu thì `null` |
| `audio` | Đường dẫn MP3 thực sự tồn tại, hoặc `null` |

Hán Việt trình bày **theo từng chữ**, không tự chọn một cách đọc chuẩn cho cả từ; thí dụ 校 có nhiều âm trong KANJIDIC2. Từ thuần kana không tự suy diễn Hán Việt. `kanji.json` giữ toàn bộ âm on/kun, Hán Việt, cấp từ danh mục kanji (có thể `null` nếu chữ chỉ có trong từ vựng), số nét và đường dẫn SVG. Không suy cấp của chữ từ cấp của từ chứa nó.

Cao độ ghép đúng dạng chữ + cách đọc, chỉ chuẩn hóa katakana/hiragana cho khóa cách đọc. Giữ nhiều biến thể; không đoán từ khi dữ liệu thiếu. **1.248 mục chưa có cao độ**. Số accent phải nằm trong số mora của từ; test xác minh toàn bộ.

## Câu ví dụ Tatoeba

<!-- example-counts:start -->
| Cấp | Có ví dụ | Việt trực tiếp | Việt qua Anh (pivot) | Dịch máy |
|---|---:|---:|---:|---:|
| N5 | 648 | 518 | 44 | 86 |
| N4 | 611 | 387 | 70 | 154 |
| N3 | 0 | 0 | 0 | 0 |
| N2 | 0 | 0 | 0 | 0 |
| N1 | 0 | 0 | 0 | 0 |
<!-- example-counts:end -->

Mỗi từ được chọn tối đa một câu thật, dài 4–25 ký tự, có dấu kết câu và tác giả được nêu tên. Tệp chi tiết thực tế có sáu cột `id, lang, text, username, created, modified`, **không có cột giấy phép**; văn bản được tái sử dụng theo CC BY 2.0 FR của bản xuất Tatoeba. Bỏ câu không có chủ sở hữu. SHA-256 và phương pháp nằm trong `data/sources/tatoeba-method.json`; nguyên câu, tên người đóng góp và liên kết `https://tatoeba.org/sentences/show/<id>` giữ cho cả Nhật, Việt và Anh được dùng.

Chọn bản dịch Việt có liên kết trực tiếp trước; nếu thiếu, chọn Việt nối qua một câu Anh và ghi `pivot:true`, nhãn **dịch qua câu tiếng Anh**. Nếu chỉ có câu Anh liên kết trực tiếp, Codex dịch sang Việt, đối chiếu câu Nhật và giữ `machine:true`, nhãn **bản dịch máy, cần kiểm tra**. Không gọi các bản dịch AI là bản dịch do người đóng góp Tatoeba viết. Cột Việt trực tiếp/pivot chỉ cho biết nguồn văn bản do người đóng góp đăng; chưa có biên tập viên bản ngữ kiểm định chúng hay xác minh cách tác giả tạo ra chúng.

`match` ghi `start`, `end`, `surface`, `kind:exact`. Biên từ và cách đọc được kiểm tra bằng fugashi 1.5.2 + UniDic 2.1.2 (unidic-lite 1.0.8). Chỉ lấy dạng chữ hoặc kana nguyên vẹn, không ghép một phần kanji/từ đồng âm khác cách đọc. **Không dùng khớp thân biến cách** trong bản này; các câu chỉ chứa dạng đã chia có thể bị bỏ. Bộ phân tích vẫn có thể sai nghĩa/cách tách; không bảo đảm mọi ví dụ đúng sense JLPT. Không suy furigana từ bộ tách từ: `furigana:null`, hiển thị nguyên câu. Cloze che đúng đoạn khớp; chỉ bật khi có ví dụ hợp lệ.

Đầu vào biên soạn bền vững: `tatoeba-examples.json`, `tatoeba-vi-machine.tsv`, `tatoeba-exclusions.json`. Tệp loại trừ ghi lý do cho câu/link lỗi phát hiện khi rà. `tools/build-data.py` luôn ghép overlay, giữ ID từ và tiến độ cũ. Tái chọn bằng `tools/tatoeba.py --levels 5 4` rồi `tools/apply-examples.py .cache/examples-5-4.json`; bước apply từ chối bản dịch máy còn trống. Dùng venv biên soạn `.cache/content-venv`, không phân phối bộ tách từ/từ điển trong website.

`tests/tatoeba_provenance.py` đối chiếu tất cả câu/ID/tác giả với TSV gốc và mọi cạnh liên kết với links.csv. `tests/example_matching.py` kiểm tra khớp từ và các trường hợp âm/biên sai; Node kiểm tra thuộc tính ghi công, câu ngắn và vị trí từ; E2E kiểm tra nhãn, nguồn và bước cloze. Chưa có người bản ngữ rà toàn bộ câu/bản dịch. Không dùng `sentences_with_audio.csv`: phát âm câu vẫn dùng giọng thiết bị; không tải audio Tatoeba khi chưa kiểm tra giấy phép riêng từng bản ghi.

## Âm thanh

`tools/gen-audio.py` dùng `edge-tts`, giọng `ja-JP-NanamiNeural`, đầu vào là kana đã ghép. FFmpeg chuyển MP3 mono 24 kHz, 32 kbit/s. Đường dẫn `audio/n<level>/w/<id>.mp3`. Có thể chạy lại; chỉ tái tạo mục thiếu. Dừng sau ba lỗi liên tiếp và ghi thật vào `audio-generation.json`; pipeline chỉ gắn đường dẫn nếu tệp tồn tại.

Đã có đủ 684 N5 và 641 N4; tổng 10.463.644 byte MP3. Lần hoàn tất gần nhất dùng lại 1.309 tệp và tạo 16 tệp sau chỉnh danh mục, không có lỗi. Các timeout ở lần đầu được chạy lại; tệp của mục đã bỏ được loại khỏi bản phát hành. Toàn bộ 1.325 tệp được giải mã bằng FFmpeg không lỗi, nhưng **chưa nghe duyệt từng tệp**. Kana làm đầu vào giúp tránh đọc nhầm từ đồng tự, đồng thời giọng TTS có thể chọn cao độ khác Kanjium. Không dùng MP3 làm nhãn chuẩn để chấm phát âm.

N3–N1 chưa có MP3; ứng dụng gọi giọng `ja-JP` của thiết bị. Bộ từ/schema/UI hoạt động offline sau cài service worker; giọng thiết bị không được bảo đảm có sẵn hay offline. Nét và MP3 được cache khi truy cập; có nút tải âm thanh của bộ đang chọn trong Cài đặt.

## Kiểm soát và giấy phép

Node kiểm tra đủ cấp/trường, ID duy nhất, kana hợp lệ, bản dịch không trống/không còn mẫu tiếng Anh rõ ràng/không emoji, Hán Việt đối chiếu từng âm KANJIDIC2, giới hạn cao độ, audio tồn tại và mọi kanji N5 có SVG. Một lượt giải mã riêng kiểm tra toàn bộ MP3; nó không đo chất lượng nói. So sánh SHA-256 trước/sau build xác minh tái dựng không đổi các tệp đã tạo.

JMdict, KANJIDIC2 và bản dịch phái sinh giữ CC BY-SA 4.0. Tanos/Waller CC BY, bản chuyển đổi Bluskyo MIT; Kanjium CC BY-SA 4.0; SVG KanjiVG giữ CC BY-SA 3.0. [NOTICE](../data/NOTICE.md) và [SOURCES](../data/SOURCES.md) có ghi công, liên kết giấy phép và mô tả phần sửa.
