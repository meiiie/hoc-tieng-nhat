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
