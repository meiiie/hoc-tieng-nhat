# Thông báo giấy phép dữ liệu

JMdict và KANJIDIC2: Electronic Dictionary Research and Development Group (EDRDG), CC BY-SA 4.0. Dữ liệu tiếng Nhật, nghĩa tiếng Anh, âm Hán Việt và bản dịch nghĩa tiếng Việt trong dự án được ghi công EDRDG. Từng mục có trường viMethod: "dịch từ JMdict (tiếng Anh), cần người bản ngữ kiểm tra". Bản dịch do AI biên soạn trong dự án, là tác phẩm phái sinh của JMdict, CC BY-SA 4.0; chưa được người bản ngữ duyệt. N5/N4 có 1.325 mục biên soạn trực tiếp; 7.019 mục N3–N1 dùng nháp hỗ trợ từ Helsinki-NLP/opus-mt-en-vi (Apache-2.0) rồi được cùng AI rà soát. Model chỉ chạy lúc biên soạn, không được phân phối. Không coi việc tự rà là kiểm định độc lập.

Danh sách JLPT: Jonathan Waller, Tanos (CC BY), bản chuyển đổi Bluskyo/JLPT_Vocabulary (MIT). Đây là danh sách cộng đồng, không phải danh mục chính thức của JLPT. Các lỗi nguồn, sửa chữa và mục chưa ghép được được công bố trong sources/.

Kanjium: Uros O. / mifunetoshiro, CC BY-SA 4.0, dựa trên dữ liệu EDRDG. Đường cao độ là dữ liệu tham khảo, không phải bản ghi giọng mẫu.

KanjiVG: Ulrich Apel, CC BY-SA 3.0. Các SVG được sao chép nguyên bản; giấy phép và ghi công giữ trong từng tệp. Giấy phép 3.0 của các SVG này vẫn áp dụng riêng, không bị thay bằng giấy phép 4.0 của bộ từ.

Audio: giọng tổng hợp Microsoft ja-JP-NanamiNeural; chưa được nghe duyệt từng tệp. Giọng thiết bị là phương án dự phòng.

Mã chương trình: MIT. Biểu tượng Lucide: ISC. ts-fsrs: MIT. Linh vật Neko và mã nền từ các ứng dụng Neko của meiiie.

Bản phát hành 1.0.0 (2026-10-27) có các thay đổi so với nguồn: sửa lỗi cặp chữ/cách đọc có ghi TSV, lựa chọn từ đồng âm có JMdict ID, ghép Hán Việt/cao độ, thêm romaji, dịch nghĩa Việt và tạo audio tổng hợp. 20 mảnh nguồn không đủ căn cứ được cách ly. Giữ nghĩa Anh để đối chiếu. Các nguồn không bảo đảm nội dung hoàn toàn đúng hoặc phù hợp với mọi mục đích học tập.

Bộ từ và phần biên soạn phái sinh được phát hành theo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); không áp dụng MIT của mã cho dữ liệu. SVG KanjiVG giữ giấy phép riêng [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). Bản đầy đủ: LICENSE-CC-BY-SA-4.0.txt, LICENSE-CC-BY-SA-3.0.txt. Audio được tạo qua dịch vụ Microsoft; không có model giọng Microsoft được phân phối trong dự án.

Biểu tượng Lucide giữ thông báo ISC và ghi công các icon kế thừa Feather/MIT trong vendor/lucide.LICENSE. ts-fsrs giữ nguyên vendor/ts-fsrs.LICENSE.

Câu ví dụ từ Tatoeba và người đóng góp, [CC BY 2.0 FR](https://creativecommons.org/licenses/by/2.0/fr/). Mỗi câu Nhật, bản dịch Việt của người đóng góp và câu Anh trung gian giữ ID, username, URL và giấy phép trong `tatoeba-examples.json` và dữ liệu từng cấp; ghi công hiển thị ở từng câu trong ứng dụng. Câu gốc không sửa. Bản dịch Việt do Codex tạo từ câu Anh liên kết là phần phái sinh, ghi `machine:true`, cũng cung cấp theo CC BY 2.0 FR; nhãn “bản dịch máy, cần kiểm tra”. Bản dịch qua liên kết Anh ghi `pivot:true`, nhãn “dịch qua câu tiếng Anh”. Giấy phép Tatoeba này áp dụng riêng cho câu, không bị thay bởi MIT của mã hoặc CC BY-SA của từ điển. Không phân phối âm thanh Tatoeba. Phương pháp và dấu vết nguồn nằm trong sources/tatoeba-method.json.

Biên soạn ví dụ dùng fugashi (MIT) và UniDic 2.1.2 qua unidic-lite (BSD cho dữ liệu từ điển); chúng chỉ chạy ngoài website, không có model/từ điển phân tích được phân phối trong bản này.

Cao độ bổ sung từ UniDic 2.1.2 (unidic-lite 1.0.8): Copyright (c) 2011–2013, The UniDic Consortium. Chọn BSD-3-Clause theo giấy phép phân phối; giữ nguyên [BSD](LICENSE-UniDic-BSD.txt), [AUTHORS](AUTHORS-UniDic.txt), [COPYING](COPYING-UniDic.txt). Phần giá trị/bản ghi trích UniDic giữ giấy phép này; không thay bằng MIT của mã hay giấy phép dữ liệu khác. 935 mục trích giá trị aType có sẵn, không tạo accent từ quy tắc nối từ hoặc biến cách. Kanjium bổ sung một mục từ bảng có acc_pos; ghi công/CC BY-SA 4.0 như trên. Đường tham khảo cho biết nguồn tương ứng trong ứng dụng.

Furigana câu ví dụ (1.8.0): phân tích offline bằng fugashi 1.5.2 (MIT, Paul O’Leary McCann; [nguyên giấy phép](LICENSE-fugashi-MIT.txt)), MeCab đi kèm (BSD-3-Clause, Taku Kudo / NTT; [giấy phép](LICENSE-MeCab-BSD.txt)), unidic-lite 1.0.8 (mã đóng gói MIT, Paul McCann; [giấy phép](LICENSE-unidic-lite-MIT.txt)) và UniDic 2.1.2 (The UniDic Consortium, chọn BSD-3-Clause như trên). Dữ liệu đọc và bằng chứng trích từ UniDic giữ BSD-3-Clause. Câu gốc Tatoeba giữ nguyên và giữ CC BY 2.0 FR; chỉ thêm các đoạn ruby khi đủ căn cứ. Không phát hành binary analyzer/dictionary. Nguồn chính thức, ngày đối chiếu và hash trong SOURCES.md và sources/furigana-method.json.
