# 1.10.2 — 2026-10-27

- Kiểm tra tự động toàn bộ 8.344 MP3: cho mô hình nhận dạng âm vị nghe lại từng tệp và chấm so với kana. 252 tệp dưới 60 điểm được thu lại bằng cùng giọng Nanami (thêm dấu câu hoặc ngữ cảnh chữ Hán); 152 tệp được thay vì bản mới khớp rõ hơn (≥ 85 điểm và hơn bản cũ ≥ 20). Còn 100 tệp dưới 60 được liệt kê để nghe lại.
- Sau cập nhật, chỉ 152 tệp đã thay bị xoá khỏi bộ nhớ âm thanh offline; các tệp đã tải khác giữ nguyên.
- Đối chiếu nghĩa Việt với JMdict bằng dịch ngược (opus-mt-vi-en); kết quả lưu trong data/sources/meaning-check.json để rà soát, chưa hiển thị trong app vì độ tin cậy của phép kiểm tra còn thấp.
- Cache htn-v1.10.2.

# 1.10.1 — 2026-10-27

- Thêm ví dụ Tatoeba cho N2/N1, cùng kiểm tra lemma/POS/dạng chữ/cách đọc, nguồn và nhãn dịch trực tiếp/qua Anh/dịch máy.
- Furigana câu chạy offline; trình duyệt chỉ nhận các đoạn ruby, bằng chứng từ điển giữ ở overlay nguồn để giảm dữ liệu tải lúc mở app.
- Bản dịch máy mới có model/hash và cờ xem/sửa riêng từng ID; phần chưa đối chiếu được ghi rõ, tất cả giữ nhãn cần kiểm tra.
- Loại khớp sai アイ (cây chàm) với từ mượn “eye” và マーク với tên người; giữ phân biệt lemma của UniDic và ghi ngoại lệ nguồn đã rà.
- Kiểm tra N2/N1 trên hai engine và ảnh review ruby sáng/tối. Cache htn-v1.10.1 chờ Tải lại; ID/schema 11/tiến độ giữ nguyên.

# 1.10.0 — 2026-10-27

- Luyện nói chấm từng mora ngay trên máy: mô hình âm vị tiếng Nhật japanese-hubert-base-phoneme-ctc-v4 (Apache-2.0, ONNX 4-bit, 63 MB, chỉ tải khi người học bấm "Tải mô hình", lưu offline). Phát hiện sai âm, bỏ trường âm, bỏ っ, bỏ ん; chấp nhận nguyên âm vô thanh. Giao diện điểm, chip từng mora, gợi ý, so sánh giọng mẫu và giọng mình giống app tiếng Anh.
- Cao độ đo trong đúng khoảng thời gian của từng mora rồi so với mẫu từ điển, vẫn ghi là ước lượng và không cộng vào điểm.
- "Chỉ đo cao độ" giữ đường cũ cho máy không muốn tải mô hình.
- Đo trên giọng Nanami: đọc đúng từ trung vị 100 (96% đạt ≥ 70), đọc sai từ trung vị 0, bỏ trường âm/っ/ん phần lớn dưới 70. Chưa đo với giọng người học thật.
- Cache htn-v1.10.0 chờ Tải lại; schema không đổi.

# 1.9.0 — 2026-10-27

- Chọn câu bằng lemma/POS, dạng chữ và cách đọc JMdict; hỗ trợ động từ, tính từ, する và phủ định. Sửa ghép kana nhầm từ đồng âm/trợ từ; giữ câu cũ trừ khi sai khớp hoặc có câu người đóng góp tốt hơn/ngắn hơn.
- Chọn lại N5–N3, bổ sung chỗ trống; mọi câu giữ nguồn, nhãn dịch và furigana bảo thủ.
- Cloze che toàn bộ dạng thực, nhận cách đọc của dạng đó và hiển thị đúng đáp án. Không đổi ID, schema 11 hoặc lịch SRS. Cache htn-v1.9.0 chờ Tải lại.

# 1.8.0 — 2026-10-27

- Thêm furigana câu ví dụ N5–N3, biên soạn offline bằng fugashi/UniDic có phiên bản/hash và giấy phép đầy đủ. Chỉ ruby kanji khi đủ căn cứ; giữ chữ mơ hồ và ghi lý do bỏ.
- Nút furigana điều khiển cả từ và câu. Không đổi câu gốc, bản dịch, ID hoặc schema 11.
- Kiểm tra dữ liệu ruby/cách đọc, toggle trên hai engine và gate onboarding 5 bước độc lập. Cache htn-v1.8.0 chờ Tải lại.

# 1.7.0 — 2026-10-27

- Màn hình mở đầu theo đúng mẫu app tiếng Anh: 5 bước có thanh tiến trình và nút quay lại (tên, điểm bắt đầu, số từ mới mỗi nhóm, kiểu học, kế hoạch). Bước riêng cho tiếng Nhật: bắt đầu từ kana, N5, N4 hoặc N3; chọn N4/N3 mở sẵn các cấp tương ứng.
- Nút "Chọn bộ từ" có nhãn chữ như app tiếng Anh.
- Tiến độ cũ giữ nguyên: người đã hoàn tất onboarding không phải làm lại; schema không đổi. Cache htn-v1.7.0 chờ Tải lại.

# 1.6.0 — 2026-10-27

- Thêm 936 cao độ có nguồn: 935 UniDic 2.1.2 (BSD-3-Clause), 1 Kanjium (CC BY-SA 4.0); tổng 8.032/8.344, còn 312 null.
- Giữ từng bản ghi gốc, phiên bản/hash, giấy phép, thứ tự biến thể; không đoán hoặc nối accent. 7.096 giá trị cũ và mọi ID không đổi.
- Hiển thị nguồn cao độ của từ và trạng thái thiếu; kiểm tra đồng âm/tên riêng, nguồn dữ liệu và trình duyệt.
- Cache htn-v1.6.0 chờ Tải lại; không đổi schema tiến độ.

# 1.5.0 — 2026-10-27

- Đủ 3.425 MP3 N1 Nanami; toàn bộ 8.344 từ N5–N1 có tệp mono 24 kHz / 32 kbit/s.
- Kiểm tra giải mã từng tệp và tải trong Cài đặt ở cả năm cấp; audio vẫn tải lười, không thuộc SW shell.
- Công bố dung lượng thực tế và retry; cache htn-v1.5.0 chờ Tải lại, giữ nguyên tiến độ.

# 1.4.0 — 2026-10-27

- Đủ 1.826 MP3 N2 Nanami; tổng 4.919 MP3 N5–N2, mono 24 kHz / 32 kbit/s.
- Kiểm tra giải mã toàn bộ N2; tiếp tục tải theo yêu cầu hoặc qua Cài đặt, không đưa MP3 vào SW shell.
- Cache htn-v1.4.0 chờ Tải lại; giữ nguyên ID và tiến độ.

# 1.3.0 — 2026-10-27

- Đủ 1.768 MP3 N3 Nanami; tổng 3.093 MP3 N5–N3, giữ mono 24 kHz / 32 kbit/s.
- Tạo theo lô có tiếp tục, retry/backoff và kiểm tra giải mã trước khi xuất tệp; không đưa audio vào SW shell.
- Kiểm tra thao tác tải âm thanh từ Cài đặt ở từng cấp có MP3, cache và giữ tiến độ; axe thêm nguồn ví dụ mở rộng.
- Công bố kiểm kê giới hạn GitHub Pages; cache htn-v1.3.0 chờ Tải lại.

# 1.2.0 — 2026-10-27

- Thêm 1.712 ví dụ N3: 992 Việt trực tiếp, 161 qua tiếng Anh, 559 dịch máy có nhãn; tổng 2.971 từ N5–N3 có câu.
- Giữ ghi công và liên kết từng câu; công bố mẫu tự rà và lý do loại câu/link không phù hợp.
- Ghi rõ giấy phép và tác giả AI cho bản dịch máy; không thêm furigana suy đoán, không đổi ID hoặc schema tiến độ.
- Cache shell htn-v1.2.0, cập nhật theo nút Tải lại.

# 1.1.0 — 2026-10-27

- 648 ví dụ N5 và 611 ví dụ N4 từ Tatoeba, ghi công từng câu; phân biệt Việt trực tiếp, qua Anh và dịch máy.
- Bật bước điền vào câu cho từ có ví dụ khớp chính xác; không suy furigana câu hoặc thay ID/tiến độ.
- Pipeline nguồn tái dựng, kiểm tra liên kết/tác giả, bộ kiểm tra chấp nhận URL triển khai và tiền tố report.
- Cache shell htn-v1.1.0; bản PWA cũ chờ Tải lại sau khi tải đủ bản mới.

# Thay đổi

## 1.0.0 — 2026-10-27

- Phát hành đầu tiên của Học Tiếng Nhật cùng Neko, tiếng Việt, iPhone/PWA.
- Core sinh từ English Neko `89eedfc6`, cấu trúc adapter theo Chinese Neko `0744f1ee`. FSRS, learning-plan và mascot giữ nguyên bản gốc.
- Kana, 5 cấp JLPT, furigana, romaji, chấp nhận kana/romaji/kanji, luyện viết và phản hồi cao độ trên thiết bị.
- 8.344 mục từ đã có nghĩa Việt được AI rà soát; 2.535 kanji có Hán Việt và nét chữ; 7.096 mục có cao độ Kanjium; 1.325 tệp MP3 N5/N4.
- 20 mảnh dữ liệu không đủ căn cứ được cách ly và công bố. Mọi nghĩa Việt vẫn cần người bản ngữ kiểm tra.
- Bảo vệ bản ghi lỗi, snapshot trước nhập/migration, schema mới hơn không bị ghi đè, IndexedDB riêng và xuất JSON.
- Chỉnh các điểm giao tiếp core bằng generator: quota 5 từ/ngày, lớp tiếng Nhật, modal có nút đóng/focus trap, vuốt mặt trước mở đáp án, và sửa độ tương phản nhãn thẻ bằng CSS adapter.
- Đo bằng Node, Chromium/WebKit, axe hai giao diện, cập nhật/offline dưới đường dẫn Pages và Lighthouse. Chi tiết kết quả thật ở báo cáo bàn giao; chưa kiểm định bằng người học hoặc iPhone thật.
