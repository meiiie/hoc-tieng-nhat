# Kết quả kiểm thử — 27-10-2026

Môi trường: Node 20.19.2, Python 3.13.5, Playwright 1.64.0; Chromium revision 1248 (Chrome for Testing 156.0.8078.4), WebKit revision 2370. HTTP server: `python3 -m http.server 8931`. Kiểm thử chính dùng viewport 390 × 844, touch/mobile. Đây là engine trên Linux, không phải Safari trên iPhone thật.

## Kết quả bản 1.0.0 (lịch sử)

| Suite | Đạt | Trượt |
|---|---:|---:|
| `srs.test.js` — giữ nguyên English | 23 | 0 |
| `learning-plan.test.js` — một fixture danh mục đổi sang Nhật | 26 | 0 |
| `lang-ja.test.js` | 10 | 0 |
| `data.test.js` | 9 | 0 |
| `pitch.test.js` | 7 | 0 |
| `storage.test.js` | 4 | 0 |
| Tổng `npm test` | **79** | **0** |
| E2E Chromium — nhóm kiểm tra | 27 | 0 |
| E2E WebKit — nhóm kiểm tra | 26 | 0 |
| PWA Chromium — 5 kiểm tra tại mỗi đường dẫn | 10 | 0 |
| PWA WebKit — 5 kiểm tra tại mỗi đường dẫn | 10 | 0 |
| Ranh giới câu trả lời, Chromium | 3 | 0 |
| Ranh giới câu trả lời, WebKit | 3 | 0 |

E2E kiểm tra onboarding, hai bảng kana/nhóm âm, luyện nhớ, mở cấp sớm/80%, rating/undo/persistence, cuộn/vuốt, modal/focus, route cài đặt, export/import/snapshot/tệp sai, các chế độ luyện tập, ngoại lệ English kéo hạn, tracing bằng pointer touch, cao độ/mora, không micro, furigana/romaji, offline, migration 7, dữ liệu hỏng localStorage/IDB và schema tương lai 99 thiếu cài đặt. Chỉ Chromium chạy thu âm bằng micro giả; WebKit không có kiểm tra này nên ít hơn một nhóm.

Axe 4.10.3: **0 vi phạm**, **34 trạng thái route/theme mỗi engine**, gồm onboarding sáng/tối, 14 route sáng/tối, mặt sau review và cài đặt. Kiểm tra tràn ngang ở viewport iPhone trên các route. Không có `pageerror` hoặc console error trong E2E cuối. Axe không tương đương kiểm tra VoiceOver thủ công.

PWA kiểm tra `/` và `/hoc-tieng-nhat/`: manifest/scope tương đối, update shell lỗi vẫn giữ bản đang dùng, update hoàn chỉnh chờ **Tải lại**, giữ tiến độ/cache ứng dụng khác, offline 5 cấp/worker/icon, MP3 và nét đã cache. Chromium có thêm xác minh installability qua CDP; không tuyên bố đã cài trên màn hình chính iOS.

Kiểm tra ranh giới bổ sung sau lần rà romaji cuối: `axtsu` nhận đúng あっ, `a` không bị nhận thay, và しんよう khác しにょう. Tất cả **8.344 romaji** có khóa âm/mora tương ứng với kana trong test dữ liệu. Dạng gõ `xtsu` được dùng khi っ đứng cuối để không làm mất mora.

## Lighthouse

| Bản Lighthouse | Hạng mục | Điểm |
|---|---|---:|
| 13.5.0 | Accessibility | 100 |
| 13.5.0 | Performance | 98 |
| 13.5.0 | Best Practices | 100 |
| 11.7.1 | PWA (danh mục cũ) | 100 |
| 11.7.1 | Accessibility | 100 |

Không có cảnh báo trong hai lượt đo cuối. Bản 13.5.0 không còn PWA; lệnh yêu cầu danh mục đó bị công cụ từ chối, nên dùng 11.7.1 để đo đúng danh mục cũ, không tự tạo điểm. Report JSON/HTML giữ tên và phiên bản riêng. `CHROME_PATH` trỏ Chromium Playwright. Đo trang chủ mobile sau onboarding/cài service worker, có cache, tại localhost; không đại diện cho tải lạnh qua mạng di động hoặc website công khai. Sau lượt đo chỉ bổ sung sửa romaji của あっ và kiểm tra ranh giới; không thay cấu trúc/giao diện trang chủ.

## Dữ liệu, build và ảnh

- Rebuild core và dữ liệu: **2.715 tệp không đổi SHA-256**. Scheduler/vendor, test SRS và mascot giữ nguyên byte English. **2.683 SVG giữ nguyên byte nguồn KanjiVG**.
- **1.325/1.325 MP3** giải mã không lỗi bằng FFmpeg; đây là kiểm tra tệp, không phải nghe duyệt nội dung.
- Kiểm kê: 38 mục shell, không thiếu script/CSS/icon, không có audio/stroke thừa và không phát hiện emoji trong tệp văn bản phát hành.
- Desktop 1440 × 1000: nội dung trang chủ rộng 720 px, danh sách rộng 600 px, một cột, không bảng phụ.
- 16 PNG cuối cho 8 màn hình × sáng/tối, viewport 390 × 844, scale 2 (780 × 1.688 pixel). Đã xem trực quan các ảnh đại diện. `tests/screenshots.py` tái tạo chúng.

## Chạy lại và artifact

```sh
npm test
python3 tests/e2e.py http://localhost:8931/ all
python3 tests/pwa.py
python3 tests/answer-boundaries.py
python3 tests/screenshots.py http://localhost:8931/
python3 tests/lighthouse.py
```

Artifact ngoài repository theo yêu cầu bàn giao: `/workspace/japanese/reports/` (`unit.log`, `e2e.json`, `axe-*.json`, `pwa.json`, `answer-boundaries.json`, `reproducibility.json`, `assets.json`, `desktop.json`, `audio-decode.json`, `lighthouse-*.report.{json,html}`), `/workspace/japanese/screenshots/`, `/workspace/japanese/codex-report.md`.

Các vấn đề phát hiện đã sửa gồm tương phản nhãn thẻ tối, modal/focus, bảo vệ schema tương lai, ranh giới mora và っ cuối từ. Harness cũng được sửa để chờ một modal ẩn bằng trạng thái DOM phù hợp, và tải lại khi mở lại cùng hash trên Chromium. Kết quả trong bảng là lần chạy thành công cuối, không dùng các lần timeout trước làm kết quả đạt.

## Chưa kiểm định

Chưa có kiểm thử trên iPhone thật/VoiceOver, Safari cũ, Bluetooth, thu âm thật có nhãn, kiểm định từ vựng/bản dịch bởi người bản ngữ, nghe duyệt toàn bộ TTS, stress quota bộ nhớ hoặc đồng bộ nhiều tab cùng sửa một thẻ. Bulk download toàn bộ audio trong UI chưa được thao tác hết; từng tệp đã kiểm tra và cache playback đã được thử. Chưa deploy/push hoặc đo URL GitHub Pages công khai. F0 chỉ được kiểm tra bằng contour/PCM tổng hợp và đường thu micro giả; không có số accuracy trên người học. [PRONUNCIATION-JA](PRONUNCIATION-JA.md) mô tả đầy đủ.

## Các gate sau 1.0.0 và URL triển khai

Mỗi release chạy `npm test`, `python3 tests/e2e.py http://localhost:8931/ all`, `python3 tests/pwa.py`, `python3 tests/answer-boundaries.py`. E2E chạy cả Chromium/WebKit và axe; thêm kiểm tra ba loại bản dịch/ghi công và cloze không thay SRS. PWA suy phiên bản hiện hành từ sw.js, kiểm tra failed/successful update ở root và subpath.

Các script e2e, pwa, answer-boundaries, screenshots, lighthouse nhận base URL qua đối số đầu. `REPORT_PREFIX=live-` đặt tên artifact riêng, ví dụ `REPORT_PREFIX=live- python3 tests/e2e.py https://meiiie.github.io/hoc-tieng-nhat/ all`. PWA khi có URL chỉ chạy manifest/scope/installability và offline tài nguyên thực; thử cập nhật lỗi/thành công cần HTTP server kiểm soát được nên chạy ở gate localhost, không giả lập sửa server Pages.

Kiểm tra nguồn ví dụ: `.cache/content-venv/bin/python tests/example_matching.py` và `.cache/content-venv/bin/python tests/tatoeba_provenance.py`; venv cài `fugashi==1.5.2 unidic-lite==1.0.8`. Kết quả từng release lưu `reports/v<version>-*` ngoài repo. Các kết quả 1.0.0 phía trên là lịch sử, không phải kết quả URL công khai.

Audio bổ sung: `python3 tests/audio_generation.py`; `python3 tests/audio_decode.py --levels n3 --report ../reports/audio-n3-decode.json`. E2E xác minh shell không yêu cầu MP3 và thao tác tải thật trong Cài đặt cho một từ ở mỗi cấp đã có MP3, sau đó kiểm tra cache và tiến độ; không gọi đây là thử tải hết hàng nghìn tệp qua UI. `tools/site-size.py` kiểm tra giới hạn dung lượng trước mỗi push.
