# Cao độ và mora: phương pháp và giới hạn

## Chấm từng mora trên thiết bị (v1.10)

**Mô hình:** `prj-beatrice/japanese-hubert-base-phoneme-ctc-v4` (rinna/japanese-hubert-base fine-tune trên ReazonSpeech, nhãn âm vị OpenJTalk), bản ONNX 4-bit của `air-air/japanese-hubert-base-phoneme-ctc-v4-ONNX`, ghim revision `a36617c5fbf7cfde02caa067716961c03cf4d87e`. Giấy phép Apache-2.0. Tải 63 MB một lần khi người học bấm "Tải mô hình", giữ trong Cache Storage `htn-engine-v1`, chạy bằng onnxruntime-web 1.30 WASM một luồng trong `asr-worker.js`. Âm thanh không rời thiết bị.

**Vì sao chọn:** nhãn của nó là âm vị tiếng Nhật thật (có `cl` cho っ, `N` cho ん, `I`/`U` cho nguyên âm vô thanh), nên chấm được đúng các lỗi người Việt hay gặp. 63 MB là mức iPhone tải được (bản tiếng Anh dùng ZIPA 71 MB). Đã cân nhắc: ZIPA đa ngôn ngữ (nhãn IPA, không riêng tiếng Nhật), `sakasegawa/japanese-wav2vec2-large-hiragana-ctc` (315M tham số, ~630 MB, không có ONNX), Whisper (nhận dạng chữ, tự sửa lỗi người học nên không hợp để chấm âm), `TKU410410103/wav2vec2-base-japanese-asr` (chưa có ONNX). CREPE/pYIN không cần: cao độ dùng bộ đo F0 sẵn có, nay đo trong đúng khoảng thời gian của từng mora.

**Cách chấm (`ja-phone.js`):** kana → chuỗi âm vị theo mora (っ, ん, trường âm う/い/ー, âm ghép, は/へ cuối từ đọc wa/e). Biến thể được chấp nhận: nguyên âm vô thanh (です, した), trường âm đọc o-o hay o-u. Căn chỉnh CTC Viterbi theo mẫu, rồi mỗi âm vị có điểm GOP (phần xác suất của âm đúng so với âm cạnh tranh mạnh nhất). Thêm một lượt so khoảng cách chỉnh sửa với chuỗi máy nghe tự do để bắt mora bị bỏ (forced alignment luôn "nhét" được mora vào). Mỗi mora: tốt / gần đúng / chưa đúng / thiếu / thiếu trường âm, kèm gợi ý. Mỗi mora lỗi trừ thêm 15% tổng điểm.

**Cao độ:** trung vị F0 (bán cung) trong khoảng của từng mora, so tương quan với mọi mẫu accent; heiban và odaka coi như nhau khi đọc riêng một từ. Luôn ghi "ước lượng".

**Đo thực tế (giọng Nanami, không phải người học):**

| Bộ thử | n | Trung vị | ≥ 70 điểm |
|---|---:|---:|---:|
| Đọc đúng từ (mẫu ngẫu nhiên N5–N1) | 300 | 100 | 96% |
| Đọc một từ khác | 300 | 0 | 0% |
| Bỏ trường âm う | 32 | 64 | 3% |
| Bỏ trường âm い | 43 | 57 | 0% |
| Bỏ っ | 10 | 64 | 0% |
| Bỏ ん | 34 | 57 | 3% |

Cao độ: đoán đúng kiểu accent theo từ điển 53% (127/239), tốt nhất với heiban/atamadaka, kém với nakadaka. Một phần sai lệch có thể do chính giọng Nanami không theo accent từ điển. Vì thế cao độ không cộng vào điểm.

Trình duyệt: Chromium với micro giả phát MP3 Nanami: がっこう 100, phát せんせい khi phải đọc がっこう: 0 (`tests/pron_e2e.py`, axe 0 lỗi ở màn kết quả). Engine WebKit: mô hình tải trong ~5,6 s (từ cache), chấm một từ ~3 s, cùng kết quả (`tests/pron_webkit.py`). **Chưa thử trên iPhone thật, chưa thử với giọng người học thật**; độ chính xác với giọng người Việt chưa được đo.

**Không có mô hình:** người học chọn "Chỉ đo cao độ" thì dùng lại đường ước lượng cao độ cũ.

Ứng dụng cho nghe mẫu, xem đường cao/thấp, theo nhịp mora, ghi âm rồi nghe lại. Khi có đủ tín hiệu, nó so hình dạng cao độ với mẫu từ điển có nguồn và luôn ghi **ước lượng**. Từ v1.10 có thêm chấm điểm từng mora trên thiết bị (phần dưới). Kết quả luyện nói không đưa vào FSRS.

## Mẫu tiếng Nhật

Ghép dạng chữ + cách đọc từ Kanjium và mục từ UniDic 2.1.2 đã kiểm tra lemma; 8.032/8.344 mục có mẫu, 312 mục không có. Màn hình ghi nguồn Kanjium hoặc UniDic cho từ đang xem. 936 mẫu bổ sung có bằng chứng/giấy phép trong data/sources/pitch-additions.json; không nối hoặc suy accent cho từ ghép. Giữ các biến thể accent để chọn. Số 0 là không hạ trong từ (heiban); số dương là vị trí hạ sau mora đó. `JaPitch.pattern` tạo các mức cao/thấp, kể cả hình minh họa trợ từ sau từ. Trợ từ này không nằm trong âm cần ghi hoặc so sánh.

Mora khác số chữ/âm tiết: âm ghép きゃ tính một; っ, ん và dấu kéo dài ー mỗi phần tính một; きょう có hai, がっこう và コーヒー có bốn. Các ô sáng lần lượt mỗi 500 ms chỉ là nhịp luyện do ứng dụng đặt, không phải tốc độ nói tự nhiên hoặc đo thời gian mora của người học. Furigana áp dụng ruby cho cả từ, không tự tách/đoán cách đọc của từng kanji.

Giọng Nanami và giọng thiết bị đọc kana có thể chọn biến thể cao độ khác mẫu từ điển. Đường tham khảo không được trích từ MP3 này, và MP3 không phải bản ghi người bản ngữ đã kiểm duyệt.

## Thu âm trên thiết bị

Tái sử dụng nguyên `core/speech.js`, `mic-meter.js`, `mic-worklet.js` từ Chinese. Xin quyền micro trên HTTPS/localhost, hiển thị tín hiệu/thời gian, kết thúc theo khoảng yên lặng hoặc tối đa 7 giây. Người học có thể dừng. Hủy luồng khi rời màn hình, mở cài đặt hoặc đưa trang xuống nền; không giữ micro chạy ngầm. Khi thiếu micro/quyền/thiết bị, cho nghe và đối chiếu bằng mắt.

Cắt vùng yên lặng theo Speech, đưa về PCM 16 kHz. Từ chối đầu vào quá ngắn (dưới 0,2 giây), không nhận tiếng nói hoặc biên độ thấp; cảnh báo khi tỷ lệ mẫu clipping trên 2%. Bản ghi ở RAM/Blob trong phiên, URL được thu hồi khi đổi từ/rời màn hình. Không upload PCM, không lưu âm thanh vào IndexedDB. `S.pron` chỉ lưu tối đa 20 bản tóm tắt mỗi từ: thời điểm, thời lượng, accent, `similar/compare/unclear`.

## Phân tích thực sự

`ja-pitch.js` dùng tự tương quan chuẩn hóa, theo hướng tiếp cận F0 của Chinese `tones.js`, chạy trong Web Worker có timeout/hủy:

1. Cửa sổ 40 ms, bước 10 ms; tìm chu kỳ tương ứng 70–500 Hz. Loại vùng năng lượng thấp và tương quan thấp hơn 0,65. Chọn đỉnh đủ mạnh sớm nhất, nội suy parabol quanh đỉnh để giảm sai số lấy mẫu.
2. Lấy phần từ frame hữu thanh đầu đến cuối. Cần ít nhất 12 frame, ít nhất 4 frame/mora và tỷ lệ hữu thanh 35%; nếu không thì không so sánh.
3. Chuyển F0 sang bán âm tương đối với trung vị của người nói. Nhờ vậy không yêu cầu giọng cao/thấp tuyệt đối giống mẫu.
4. Chia phần thời gian đó thành các khoảng **bằng nhau** theo số mora tham khảo. Mỗi khoảng cần đủ frame hợp lệ; lấy trung vị. Không có forced alignment hoặc ranh giới mora đo được.
5. So dấu chuyển giữa hai khoảng: chuyển lên/xuống cần hơn 0,8 bán âm đúng hướng; đoạn bằng chấp nhận chênh dưới 2,5 bán âm. Cần đo được ít nhất nửa số chuyển. Nếu mọi chuyển đo được phù hợp thì hiển thị gần mẫu; nếu không thì gợi ý nghe và đối chiếu thêm.

Ngưỡng do dự án chọn để tạo phản hồi thận trọng, **chưa hiệu chỉnh trên người học thật**. Từ một mora, thiếu accent hoặc thiếu đoạn hữu thanh được từ chối so sánh. Một từ heiban và một từ odaka có thể có cùng đường trong từ khi đứng riêng; ứng dụng không tuyên bố phân biệt được nếu chưa nói phần ngữ cảnh theo sau.

## Đã kiểm tra và chưa đo

Đã kiểm thử đơn vị trên đường cao độ và PCM sin tổng hợp: đúng lên/xuống, đổi nền cao độ người nói, im lặng, phần vô thanh, thiếu mẫu, một mora và giới hạn heiban/odaka. Kiểm thử trình duyệt Chromium dùng micro giả để chạy thu/đóng luồng, meter, worker và phản hồi hoặc từ chối; WebKit kiểm tra hiển thị/luồng nghe và mora. Không gán “đúng phát âm” cho micro giả.

**Chưa đo:** độ chính xác F0/âm vị/mora trên người Việt học tiếng Nhật, đồng thuận giáo viên, false acceptance/rejection, khả năng chống nhiễu, micro Safari iPhone thật, Bluetooth, điện thoại yếu và khác biệt giọng/vùng miền. Không có tỷ lệ accuracy hay điểm MOS để công bố. Sóng tổng hợp không đại diện cho tiếng nói tự nhiên. Âm vô thanh (っ, phụ âm, nguyên âm bị vô thanh hóa), khoảng dừng, giọng khàn, lỗi quãng tám, ngữ điệu câu và tiếng ồn có thể làm kết quả sai; chia đều thời gian đặc biệt hạn chế ở từ nhiều mora.

Mora trong bản ghi **chưa được nhận dạng hoặc đếm**. Màn hình chỉ đếm mora từ chữ và hướng dẫn nhịp. Phép so F0 không phát hiện chắc chắn nói sai âm, thiếu âm hoặc nói một từ khác có cùng đường cao độ. Cần nghe lại và nhờ giáo viên góp ý.

## TODO có chủ đích: model âm vị

Chưa tích hợp hoặc tải `air-air/japanese-hubert-base-phoneme-ctc-v4-ONNX` (nguồn được cung cấp, Apache-2.0). Chưa chứng minh độ tin cậy/độ trễ/bộ nhớ trên iPhone nên không thêm nút chấm bằng model. Đây là tính năng tùy chọn chưa làm, không có stub trả kết quả giả.

Trước khi tích hợp: kiểm tra tokenizer/CTC và giấy phép của artifact chính xác, parity Python/ONNX, tập bản ghi có nhãn từ người học, lỗi false acceptance/rejection, ngân sách RAM/độ trễ Safari và cơ chế hủy/tải lại. Khi đủ bằng chứng mới tải model theo yêu cầu, cache riêng và luôn giữ đường nghe-so sánh hiện tại. Không dùng nhận dạng của trình duyệt/đám mây như một phép đo âm vị thay thế chưa kiểm chứng.
