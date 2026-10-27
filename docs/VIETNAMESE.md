# Nghĩa tiếng Việt và rà soát

Nguồn cuối cùng là `data/sources/vi-glosses.tsv`, **8.344 mục**, bốn cột `id`, `kanji`, `reading`, `vi`. Mỗi mục từ phát hành ghi đúng phương pháp: **“dịch từ JMdict (tiếng Anh), cần người bản ngữ kiểm tra”**. Câu này có trong dữ liệu, NOTICE, cài đặt và bảng nguồn của từ. Bản dịch là tác phẩm phái sinh JMdict, CC BY-SA 4.0.

## Cách thực hiện

Một Codex làm toàn bộ công việc, không có agent phụ và không có người bản ngữ trong lượt rà này. Đọc cặp Nhật/cách đọc/nghĩa Anh, đặt nghĩa Việt thường dùng trước, giữ ngắn theo phong cách người học; các nghĩa không đủ ngữ cảnh được diễn đạt thận trọng. Không lấy bộ Ja–Vi của bên thứ ba.

**1.325 mục N5/N4** được biên soạn trực tiếp. Để hỗ trợ bản nháp ở phần còn lại, model cục bộ `Helsinki-NLP/opus-mt-en-vi` (Apache-2.0) dịch nghĩa Anh đầu tiên bằng Transformers Marian float32 CPU, beam 4, batch 32. Model không phải agent, không được dùng trong ứng dụng và không được đưa vào repository. `tools/translate-local.py` chỉ tạo TSV ứng viên trong `.cache/`; không ghi đè bản dịch đã rà hoặc nhật ký rà chính thức.

Model ban đầu sinh **7.594 ứng viên**; 575 mục N4 trong số đó sau đó được viết lại trực tiếp. **7.019 mục N3–N1** dùng nháp hỗ trợ rồi được Codex đọc, rà theo nghĩa Anh và sửa từng lô. Bản nháp đã tạo nhiều lỗi nghĩa/đại từ/câu không liên quan; không coi đầu ra model là dữ liệu sẵn phát hành. **3.659 ứng viên khác với bản nháp đầu** sau biên tập, tính cả viết lại N4 và sửa dấu/ký hiệu. Con số này đo số dòng đã thay, không phải số dòng dịch máy đúng hay sai.

Các mốc lô theo thứ tự từ vựng: 750, 950, 1.150, 1.325, 1.625, 2.025, 2.525, 3.093, 3.593, 4.093, 4.593, 5.093, 5.743, 6.393, 7.043, 7.693, 8.344. `tools/translate-batch.py` hỗ trợ xem/áp dụng TSV theo ID; bản nguồn cuối, dấu vết ghép/sửa JMdict và thống kê phương pháp được giữ trong `data/sources/`. SHA-256 model và TSV cuối nằm trong `translation-method.json`.

## Kiểm tra toàn bộ

- Đủ nghĩa cho cả năm cấp; không trống, không nhân bản ID, đúng cặp chữ + cách đọc.
- Bộ lọc tìm từ tiếng Anh hay sót và dòng giống nguyên nghĩa Anh; Codex xem các mục bị đánh dấu. Các nghĩa Việt không dấu như “ao”, “ba”, “than”, “cho” không bị đổi chỉ vì thiếu dấu.
- Rà từ ngoại lai và các đoạn ASCII; giữ thuật ngữ đã dùng trong tiếng Việt như kana, kanji, hiragana, katakana, vitamin, vinyl, compa. Không còn câu/nghĩa Anh chưa dịch được phát hiện trong cột `vi`; trường `en` vẫn cố ý giữ nghĩa Anh để tham khảo.
- Quét emoji trong dữ liệu và nguồn ứng dụng. Không dùng biểu tượng Unicode thay cho icon.
- Kiểm tra nghĩa của các từ đồng âm; ghim lựa chọn từ điển ở `sense-selection.tsv`, không chỉ sửa tiếng Việt trên một JMdict ID sai.

Các bộ lọc trên không thể chứng minh một bản dịch đúng, tự nhiên hoặc đúng nghĩa JLPT trong mọi ngữ cảnh. Tất cả “đã rà” ở đây là **AI tự rà**, không phải kiểm định bởi người Nhật/Việt hay hai biên tập viên độc lập.

## Mẫu ngẫu nhiên 100 mục

Lấy 100 ID không lặp bằng `random.Random(20261027)` từ danh mục đã sắp xếp của pipeline, bao gồm cả năm cấp. Nhật ký đầy đủ: `data/sources/vi-audit-100.tsv`, giữ nghĩa trước/sau, nghĩa Anh, nhận xét và kết quả từng dòng.

Kết quả tự rà: **95 giữ nguyên, 5 sửa**. Năm chỉnh sửa đã được áp dụng lại vào TSV và JSON phát hành:

| Mục | Chỉnh sửa cuối |
|---|---|
| ええと | “ừm; để xem nào” |
| 南極 | Viết đúng tên riêng “Nam Cực” |
| 協議 | “bàn bạc; hiệp nghị” |
| 擦れる | “bị cọ xát; sờn” |
| 益々 | “ngày càng; càng lúc càng” |

Không suy “95% chính xác” từ kết quả này: cùng AI đã dịch và tự kiểm tra, không có đáp án chuẩn độc lập và mẫu nhỏ không đủ đánh giá 8.344 mục. Các dạng hiếm/cũ, đa nghĩa, thuật ngữ và từ đồng âm ở N1 còn cần người am hiểu rà sâu. Trước khi quảng bá là nội dung đã kiểm định, cần người bản ngữ kiểm tra cả cách đọc/nghĩa ưu tiên và nghe mẫu âm thanh.

## Cập nhật nghĩa

Sửa dòng đúng `id` trong `vi-glosses.tsv`, đối chiếu `kanji/reading` và JMdict ID, chạy lại build và test. Không sửa trực tiếp `n*.json`; không đổi ID chỉ để sửa nghĩa. Nếu sửa cặp chữ/cách đọc, ghi ở `entry-fixes.tsv` và chuẩn bị ánh xạ tiến độ cũ trước một lần phát hành dữ liệu mới. Bản 1.0.0 chưa có người dùng cũ cần ánh xạ.
