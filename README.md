# Học Tiếng Nhật cùng Neko

PWA tiếng Việt cho người học tiếng Nhật, ưu tiên iPhone. Phiên bản **1.12.1**, ngày 27-10-2026. Chạy bằng các tệp tĩnh; không cần tài khoản, máy chủ ứng dụng hay khóa API.

## Học cùng Neko

- 214 mục hiragana/katakana: âm cơ bản, âm đục, âm ghép, nghe, luyện nhớ và viết nét.
- 2.971 từ N5/N4/N3 có ví dụ Tatoeba ngắn và bản dịch có nhãn/ghi công; bước điền vào câu bật khi có ví dụ.
- 8.344 mục từ N5–N1 có nghĩa Việt, kana, romaji, nghĩa Anh đối chiếu và liên kết JMdict. Furigana bật/tắt trên thanh đầu trang; romaji trong Cài đặt.
- Ôn theo lịch FSRS-6, Thẻ ghi nhớ, Học, Từ khó, Ghép thẻ, Nghe – chép, Kiểm tra, Ôn toàn bộ, Danh sách từ và Thống kê.
- Bắt đầu từ kana hoặc N5; mặc định 5 từ mới/ngày. Cấp tiếp theo mở khi 80% từ đã qua bước học ban đầu, hoặc chọn **Mở sớm**.
- Viết chữ bằng KanjiVG: xem thứ tự nét rồi viết theo từng nét bằng ngón tay.
- Cao độ và mora: nghe mẫu, xem cao/thấp, theo nhịp, ghi và nghe lại giọng mình. Phân tích F0 chạy trên thiết bị; phản hồi luôn là **ước lượng**, không phải điểm phát âm.
- Neko, giao diện sáng/tối, vùng chạm lớn, một cột trên máy tính, bàn phím và thao tác vuốt/hoàn tác.
- IndexedDB riêng, sao lưu tự động, nhập/xuất JSON, khôi phục bản ghi hỏng và cập nhật PWA theo lựa chọn **Tải lại**.

**Phạm vi nội dung:** tất cả 8.344 nghĩa Việt đã được AI rà soát theo JMdict tiếng Anh; chưa được người bản ngữ duyệt. 20 mảnh dữ liệu nguồn không đủ căn cứ được cách ly, không biến thành thẻ giả. Xem [dữ liệu](docs/DATA.md) và [kiểm tra bản dịch](docs/VIETNAMESE.md).

| Cấp | Từ | Nghĩa Việt | Hán Việt | Cao độ | MP3 Nanami |
|---|---:|---:|---:|---:|---:|
| N5 | 684 | 684 | 514 | 638 | 684 |
| N4 | 641 | 641 | 496 | 605 | 641 |
| N3 | 1.768 | 1.768 | 1.546 | 1.712 | 1.768 |
| N2 | 1.826 | 1.826 | 1.508 | 1.749 | 1.826 |
| N1 | 3.425 | 3.425 | 3.152 | 3.328 | 3.425 |

Từ chưa có MP3 dùng `speechSynthesis` tiếng Nhật của thiết bị. Sau lần tải và cài service worker đầu tiên, ứng dụng và toàn bộ từ vựng dùng được ngoại tuyến. MP3 và nét chữ chỉ được lưu khi đã mở; Cài đặt có nút tải toàn bộ âm thanh của bộ đang chọn. Giọng thiết bị có thể cần cài thêm hoặc cần mạng. Ghi âm cần HTTPS hoặc localhost.

## Chạy và triển khai

```sh
python3 -m http.server 8931
# Mở http://localhost:8931/
```

GitHub Pages: sau khi chủ repository tạo remote và đẩy mã, chọn **Deploy from a branch → main → / (root)**. Không có bước build bắt buộc. `.nojekyll`, manifest, URL tương đối và service worker đã hỗ trợ đường dẫn `/hoc-tieng-nhat/`. `sitemap.xml` đang dùng chủ sở hữu dự kiến `meiiie`; đổi URL nếu nơi triển khai khác. Website: https://meiiie.github.io/hoc-tieng-nhat/. Remote `meiiie/hoc-tieng-nhat`, nhánh `main`; chỉ push sau khi các gate được thông qua.

Trên iPhone, mở trang bằng Safari rồi chọn **Chia sẻ → Thêm vào Màn hình chính**. Hãy mở trực tuyến ít nhất một lần và xuất bản sao lưu định kỳ. Bản cập nhật hoàn chỉnh chờ nút **Tải lại**; nâng `V` trong `sw.js` và `version.json` khi phát hành tiếp theo. Khi thay nội dung dùng lại cùng URL của stroke/audio, nâng cache dữ liệu/âm thanh tương ứng.

## Tái dựng

```sh
npm ci
python3 tools/make-core.py
python3 tools/build-data.py --source ../src
# Chỉ cần khi tạo thêm hoặc thay âm thanh:
python3 tools/gen-audio.py --levels n5 n4
python3 tools/build-data.py --source ../src
```

`make-core.py` mặc định đọc hai repository tham chiếu tại `/workspace/english/hoc-tu-vung` và `/workspace/chinese/hoc-tieng-trung`; có cờ `--english` và `--chinese`. Nó dùng thay thế có kiểm tra số lần xuất hiện. Không sửa trực tiếp `core/`, `srs.js` hoặc bản vendor FSRS. Pipeline dữ liệu chỉ đọc `../src`, dùng bản dịch đã rà trong `data/sources/vi-glosses.tsv`, và từ chối bản phát hành còn nghĩa trống. Model dịch nháp không cần cho tái dựng bản phát hành.

`gen-audio.py` cần `edge-tts` tại `/home/box/.local/bin/edge-tts` và `ffmpeg`; bỏ qua tệp đã có, dừng sau ba lỗi liên tiếp. `build-icons.py` cần Pillow và CairoSVG. Cách tái dựng không thay đổi repository nguồn.

## Kiểm thử

```sh
npm test
# Giữ http.server ở terminal riêng:
python3 tests/e2e.py http://localhost:8931/ all
python3 tests/pwa.py
python3 tests/screenshots.py http://localhost:8931/
python3 tests/lighthouse.py
```

Kiểm thử trình duyệt cần Python Playwright, Chromium/WebKit và thư viện hệ thống tương ứng; axe nằm trong devDependencies. Bộ kiểm tra Hán Việt đọc KANJIDIC2 ở `../src`; kiểm tra sao chép core đối chiếu repository tiếng Anh. `tests/pwa.py` tự mở HTTP server tạm. Lighthouse hiện tại đã bỏ danh mục PWA; script chạy bản hiện tại cho khả năng tiếp cận/hiệu năng và bản **11.7.1** trong `.cache/lighthouse11` cho PWA cũ. Cài bản này khi cần: `npm install --prefix .cache/lighthouse11 lighthouse@11.7.1`.

Kết quả thực tế và ảnh chụp của lượt bàn giao nằm ở `../reports/`, `../screenshots/` và `../codex-report.md`. Kiểm thử tự động không thay thế kiểm tra VoiceOver, micro, TTS và cài PWA trên iPhone thật.

## Tài liệu và giấy phép

- [Kiến trúc và khác biệt giữa các ứng dụng](docs/ECOSYSTEM.md)
- [Vòng đời từ, lịch ôn và bằng chứng luyện tập](docs/LIFECYCLE.md)
- [Pipeline, tỷ lệ ghép từ và nguồn](docs/DATA.md)
- [Phương pháp dịch và mẫu 100 mục](docs/VIETNAMESE.md)
- [Phát âm: phương pháp, phép đo và giới hạn](docs/PRONUNCIATION-JA.md)
- [Kết quả kiểm thử và Lighthouse](docs/TESTING.md)
- [Thay đổi phiên bản](CHANGELOG.md)

Mã ứng dụng: [MIT](LICENSE). Bộ từ và bản dịch phái sinh: CC BY-SA 4.0; SVG KanjiVG giữ CC BY-SA 3.0. [NOTICE](data/NOTICE.md) và [SOURCES](data/SOURCES.md) ghi riêng từng nguồn, thay đổi và ghi công. ts-fsrs giữ MIT; sprite Lucide giữ ISC.
