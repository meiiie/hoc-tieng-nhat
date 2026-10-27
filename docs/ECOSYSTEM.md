# Core Neko và adapter tiếng Nhật

## Nguồn được ghim

English `/workspace/english/hoc-tu-vung` tại `89eedfc6` là chuẩn cho lịch ôn và vòng đời. Chinese `/workspace/chinese/hoc-tieng-trung` tại `0744f1ee` là mẫu cấu trúc. Cả hai chỉ được đọc. SHA-256 từng tệp đầu vào nằm trong [core-provenance.json](core-provenance.json).

`tools/make-core.py` đọc `app.js` tiếng Anh, dùng thay thế chuỗi có assert số lần khớp và thay đoạn có assert hai mốc duy nhất. Nếu đầu vào thay đổi, generator dừng để người bảo trì rà lại. `core/app-core.js` không được chỉnh bằng tay.

| Thành phần | Nguồn / trách nhiệm |
|---|---|
| `core/app-core.js` | Sinh từ English app hiện tại; UI chung, bằng chứng, queue, phiên học, lịch ôn, nhập/xuất |
| `core/style.css`, `core/mascot.js` | Sao chép nguyên byte từ English |
| `srs.js`, `learning-plan.js`, `content.js`, `vendor/ts-fsrs.*` | Sao chép nguyên byte từ English; FSRS-6/ts-fsrs 5.4.2 |
| `core/speech.js`, `core/mic-meter.js`, `core/mic-worklet.js` | Sao chép nguyên byte từ Chinese; thu âm, hủy ghi, tín hiệu micro |
| `storage.js` | Adapter lưu trữ Nhật, schema logic do core xử lý |
| `lang-ja.js`, `lang-ja.css` | Mọi nội dung/hiển thị/đường đi và lựa chọn riêng tiếng Nhật |
| `ja-kana.js` | Kana, romaji, ruby an toàn, kiểm tra câu trả lời, đếm mora |
| `ja-pitch.js`, `ja-pitch-worker.js`, `ja-engine.js` | Ước lượng F0, so mẫu và worker có thể dừng |
| `ja-writing.js` | Xem/viết nét KanjiVG, chỉ ghi lịch sử luyện tập |

Không dùng bundler, framework hay CDN lúc chạy. Các hook `LANG` cho dữ liệu, bộ từ, câu trả lời, phát âm, mặt thẻ, lọc, cài đặt, routes, boot và chip đầu trang giữ cách tổ chức của Chinese. Các hàm tiếng Anh bị hook thay thế không được gọi cho tiếng Nhật; model ASR tiếng Anh không được tải.

## Các quyết định khác biệt

**Bằng chứng luyện tập theo English.** Chinese tắt `bringForward`; English hiện tại kéo ngày ôn về ngày mai khi thất bại trong luyện nhớ một thẻ Review chưa đến hạn. Nhật giữ hành vi English. Do đó yêu cầu “mọi luyện tập giữ SRS byte-identical” và “giữ nguyên evidence policy English” không đồng thời đúng với trường hợp này. Bộ test kiểm tra byte-identical cho thẻ mới, học ban đầu, luyện thành công, ghép thẻ và ôn toàn bộ; kiểm tra riêng đúng ngoại lệ thất bại Review. Ngoại lệ chỉ thay `due/fwd`, không thay độ bền, độ khó, khoảng ôn hoặc số lần lặp. [LIFECYCLE](LIFECYCLE.md) mô tả chính xác.

**Quota và cấp độ.** English dùng nhóm học 25 từ. Nhật không tạo các nhóm Ngày; 5 từ mới/ngày là mặc định chung cho các cấp đã mở, đổi cấp không làm mới quota. Queue/learning steps/cap chiều ngược/undo vẫn dùng cùng `learning-plan.js`. Mở cấp theo 80% thẻ chính có `state=review`, hoặc mở sớm theo lựa chọn người học. Cấp đã mở không khóa lại sau một lần quên. Thẻ đến hạn vẫn được ôn trên toàn thư viện.

**Kana là luyện tập.** Ghi `kanaPractice`, không giả định nhận ra âm kana là nhớ nghĩa từ vựng. Không sinh các card `S.srs` riêng, không tiêu quota. Viết chữ ghi `writing` và một bằng chứng luyện tập; luyện cao độ chỉ ghi `pron`. Không đưa kết quả cao độ vào FSRS.

**Các sửa UI trong generator.** Mặt trước chỉ mở đáp án khi vuốt, sau đó vuốt trái/phải tương ứng Lại/Được. Chặn click dư sau vuốt nhưng không chặn lần chạm đầu. Modal có nút đóng Lucide, đặt focus, giữ focus trong modal, làm nền inert, trả focus khi đóng và đóng khi đổi route. Những điểm này không thay thuật toán FSRS; đều được kiểm tra trong hai engine. CSS Nhật sửa tương phản nhãn thẻ và chỉ chứa phần bổ sung, không chỉnh stylesheet chung.

**Giọng nói.** Giữ pipeline thu âm và meter của Chinese; ước lượng F0 tự tương quan theo hướng tiếp cận của `tones.js`. Không dùng ASR để tạo điểm giả. `Speech.record` hủy khi rời màn hình, mở modal hoặc đưa ứng dụng xuống nền. PCM ở RAM; chỉ lịch sử tóm tắt được lưu.

## Dữ liệu và bộ nhớ

Namespace độc lập: `htn-core`, `htn-core-bak`; IndexedDB `hoc-tieng-nhat`, object store `progress`. Không đọc/chuyển hay xóa `htv2`, `htt-core` hoặc cơ sở dữ liệu ứng dụng khác. Schema hiện tại 11, theo English; các trường Nhật chỉ được thêm. `set.dark` cũ được giữ sau chuyển đổi; bộ lọc cũ được chụp trong migration snapshot. `learning-plan` có thể chuyển cấu trúc chỉ mục/quota theo logic English, không làm mất `srs`, `ev`, `revlog` hay ghi chú.

Trước migration có `<key>-pre-v<n>`. LocalStorage chứa JSON hỏng được giữ dưới `<key>-corrupt-<time>`; IndexedDB hỏng được giữ dưới `corrupt-<time>`. Khôi phục từ bản dự phòng, không âm thầm xóa. Snapshot trước import là `<key>-before-import-<time>` và bản tương ứng trong IDB. Hàng đợi ghi bảo đảm các lần lưu bất đồng bộ không đảo thứ tự. Thiếu IndexedDB thì dùng localStorage với thông báo; không ghi được thì báo xuất sao lưu.

Schema lớn hơn 11 chỉ đọc: bổ sung mặc định trong RAM để hiển thị thông báo, vô hiệu hóa nút cài đặt/đổi furigana và từ chối `save()`. Bản trên đĩa giữ nguyên. Import từ app khác hoặc schema tương lai bị từ chối; import hợp lệ cần xác nhận thao tác thay thế của người học và chụp snapshot trước.

## PWA và phát hành

Cache shell `htn-v1.12.1`; nét chữ/model `htn-data-v1`; MP3 `htn-audio-v1`. `SHELL` liệt kê tất cả JS/CSS/vendor dùng lúc chạy, 5 cấp từ, metadata, kana, kanji, manifest, version, credits và icon. SVG nét, âm thanh và model tải lười; không tải sẵn 2.683 SVG hoặc 8.344 MP3 khi cài ứng dụng.

Install dùng `cache:'reload'` và `addAll` nguyên khối. Không `skipWaiting` tự động. Khi bản mới đã cài đầy đủ, core mời **Tải lại**; activate chỉ xóa cache cũ có prefix Nhật. Service worker không chạm tiến độ. Các kiểm tra update thất bại/thành công và offline chạy ở cả `/` lẫn `/hoc-tieng-nhat/` trên Chromium/WebKit. GitHub Pages đã được triển khai tại https://meiiie.github.io/hoc-tieng-nhat/; chưa thử iPhone thật.
