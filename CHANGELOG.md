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
