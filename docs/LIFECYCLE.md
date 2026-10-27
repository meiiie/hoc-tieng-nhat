# Vòng đời từ và lịch ôn

Một từ có thẻ chính `S.srs[id]` (Nhật sang Việt) và thẻ ngược `id~r` khi bật hai chiều. Chỉ **Ôn theo lịch** ghi mức nhớ vào FSRS. `srs.js`, ts-fsrs 5.4.2 và learning-plan được giữ nguyên byte so với English `89eedfc6`.

## Trạng thái

| Nhãn | Điều kiện |
|---|---|
| Tạm ngưng | Một trong hai thẻ có `susp` |
| Hay quên | Leech ở lần quên thứ 8; nhắc lại mỗi 4 lần, tự tạm ngưng và gắn sao |
| Tạm ẩn hôm nay | Bury cho tới ranh giới ngày học 04:00 |
| Mới | Chưa có thẻ hoặc `state=new` |
| Đang học | Bước học 1 phút, 10 phút |
| Học lại | Sau Lại ở Review; bước 10 phút |
| Đang ôn | Đã tốt nghiệp bước học, độ bền dưới 21 ngày |
| Ôn ổn định | Review, độ bền từ 21 ngày; SM-2 dùng khoảng ôn từ 21 ngày |

“Ôn ổn định” là mốc của lịch, không xác nhận thành thạo tiếng Nhật. Quên từ đưa thẻ về Học lại. FSRS mặc định retention 90%, cho chỉnh 80–95%; fuzz và cân bằng lịch theo English. SM-2 cũ vẫn được đọc và chuyển đổi không mất dữ liệu.

## Hàng đợi và thao tác

Hàng đợi ưu tiên learning đến hạn, rồi review đến hạn, rồi chiều mới/thẻ mới theo `LearningPlan.next`; learning sắp đến trong 20 phút được dùng khi không còn việc ưu tiên khác. Review và learning luôn xét toàn thư viện. Từ mới lấy trong bộ đang chọn, ưu tiên từ gắn sao và đã gặp trong luyện tập, rồi thứ tự kana cố định của dữ liệu.

Ngày học bắt đầu 04:00 theo giờ thiết bị. Mặc định 5 từ mới/ngày, tính bằng ID từ phân biệt; đổi cấp không cấp thêm quota. Chiều ngược của từ đã gặp có hạn mức riêng bằng quota. Hai chiều không đưa ra cùng ngày. Luyện tập không tiêu quota giới thiệu từ theo lịch.

Mở đáp án trước khi tự đánh giá Lại/Khó/Được/Dễ. Vuốt trái/phải sau khi lật là Lại/Được; trước khi lật chỉ hiện đáp án. Chạm lật, kéo dọc cuộn, chữ trên desktop có thể chọn. Space hiện đáp án rồi chọn Được; 1–4 chấm khi đã hiện; Z hoàn tác. Hoàn tác khôi phục card, bury, quota, giới thiệu từ, nhật ký và trạng thái phiên, kể cả sau câu cuối. Không nhận xét lại dựa trên kết quả cao độ.

Mở N4 sau 80% thẻ chính N5 có `state=review`, tương tự đến N1; đó là tốt nghiệp bước học, không phải 80% đạt độ bền 21 ngày. **Mở sớm** không sửa thẻ hay bằng chứng. Mở rồi không khóa lại.

## Bằng chứng ngoài lịch ôn

| Chế độ | Thành công | Chưa nhớ |
|---|---|---|
| Thẻ ghi nhớ, Học, Từ khó, Nghe – chép, Kiểm tra | Ghi `ev` và mức quen; không tăng khoảng ôn | Ghi bằng chứng/lỗi; với thẻ Review có hạn xa hơn ngày mai, kéo `due` về ngày mai tối đa một lần/ngày |
| Ghép thẻ | Ghi lần tiếp xúc | Không thay lịch |
| Ôn toàn bộ (`cram`) | Luyện trong phiên, không ghi FSRS | Chỉ lặp lại trong phiên |
| Kana | `kanaPractice` | Không có card từ vựng |
| Viết chữ | `writing`, bằng chứng luyện viết | Hướng dẫn thử lại từng nét |
| Cao độ/mora | `pron`: thời điểm, thời lượng, biến thể, loại phản hồi | Nghe và đối chiếu; không ghi điểm nhớ nghĩa |

Ngoại lệ kéo ngày ôn là hành vi có thật của English, khác Chinese. Chỉ `due` và dấu `fwd` đổi; stability, difficulty, interval, reps và lapses giữ nguyên. Thành công ngoài lịch không tăng khoảng ôn vì các hoạt động này thường cung cấp gợi ý hoặc lặp ngay. Test byte-identical áp dụng cho các tình huống không có ngoại lệ; một test riêng xác minh ngoại lệ, không che giấu bằng cách tắt nó.

Undo của **Thẻ ghi nhớ** chỉ lùi vị trí/lượt trong buổi lướt, theo English; nó không xóa bằng chứng đã ghi hay đảo ngoại lệ kéo ngày ôn. Undo của **Ôn theo lịch** mới khôi phục toàn bộ lần chấm FSRS.

Danh sách từ dùng cùng lifecycle, tìm theo từ/kana/romaji/Hán Việt/nghĩa, gắn sao, ghi chú, xem lịch sử, tạm ngưng/ẩn và học lại có xác nhận. Các snapshot và migration được mô tả trong [ECOSYSTEM](ECOSYSTEM.md).
