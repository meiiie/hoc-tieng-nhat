#!/usr/bin/env python3
"""Refresh content counts and audio documentation from the built release data."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];meta=json.loads((ROOT/'data/meta.json').read_text())
fmt=lambda n:f'{n:,}'.replace(',','.')
for filename in ['README.md','docs/DATA.md']:
 p=ROOT/filename;s=p.read_text();start=s.index('| Cấp |');end=s.index('\n\n',start);old=s[start:end].splitlines();lines=old[:2]
 for level,x in meta['levels'].items():lines.append('| '+level+' | '+' | '.join(fmt(x[k]) for k in ['words','vi','hanViet','pitch','audio'])+' |')
 if filename=='docs/DATA.md':lines.append('| Tổng | '+' | '.join(fmt(sum(x[k] for x in meta['levels'].values())) for k in ['words','vi','hanViet','pitch','audio'])+' |')
 s=s[:start]+'\n'.join(lines)+s[end:];p.write_text(s)
paths=[p for p in (ROOT/'audio').glob('n*/w/*.mp3')];size=sum(p.stat().st_size for p in paths)
p=ROOT/'docs/DATA.md';s=p.read_text();a=s.index('## Âm thanh');b=s.index('## Kiểm soát',a)
s=s[:a]+f'''## Âm thanh

`tools/gen-audio.py` dùng cùng pipeline N5/N4: edge-tts 7.3.1, `ja-JP-NanamiNeural`, đầu vào kana, FFmpeg MP3 mono 24 kHz / 32 kbit/s. Đường dẫn `audio/n<level>/w/<id>.mp3`. Tệp chỉ được đưa vào vị trí phát hành sau khi giải mã thành công, sau đó `tools/build-data.py` gắn đường dẫn thực sự tồn tại. Không đổi ID từ hoặc schema tiến độ.

Có **{fmt(len(paths))} MP3**, tổng **{fmt(size)} byte**. Bảng phía trên là số thực tế từng cấp. Mọi tệp của các cấp hoàn tất được kiểm tra lại bằng FFmpeg và ffprobe (`tests/audio_decode.py`): phải giải mã được, đúng mono/24 kHz/32 kbit/s, không thiếu/thừa ID. Chưa nghe duyệt từng tệp; giọng TTS có thể chọn accent khác từ điển. Không dùng MP3 làm nhãn chuẩn để chấm phát âm.

Chạy nền theo lô 100, bốn yêu cầu đồng thời, tiếp tục được từ tệp đã có: `python3 tools/gen-audio.py --levels n3 --chunk-size 100 --workers 4`. Mỗi lỗi được thử tối đa 5 lần, chờ 3/6/12/24 giây; dừng lấy việc mới sau 3 từ lỗi liên tiếp đã hết lượt thử. Có `--offset`/`--limit` để chạy một đoạn. Nhật ký riêng cho từng cấp tại `data/sources/audio-generation-n*.json`, giữ số thật, lỗi và retry; kết thúc thiếu không báo complete. `tests/audio_generation.py` kiểm tra retry/backoff, hết lượt và hủy.

MP3 và nét chữ tải lười, không nằm trong SW shell. Cài đặt tải bộ đang chọn (chọn cấp ở trang chủ); từ chưa có MP3 dùng speechSynthesis ja-JP của thiết bị, khả năng offline tùy máy. [Git LFS không được Pages hỗ trợ](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage); dự án không dùng LFS.

Giới hạn đã đối chiếu ngày 2026-10-27: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) cho site tối đa 1 GB, băng thông mềm 100 GB/tháng; [GitHub files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) chặn tệp trên 100 MiB. `tools/site-size.py` kiểm kê toàn bộ tệp Git phát hành, áp ngưỡng mỗi tệp dưới 100 MB nghiêm hơn và site dưới 1 GB; không tính .git/node_modules/.cache vào site. Kích thước đối tượng Git được báo riêng trong report. Không có số liệu băng thông sử dụng thực tế.

'''+s[b:];p.write_text(s)
p=ROOT/'README.md';s=p.read_text();s=re.sub(r'N3–N1 dùng `speechSynthesis` tiếng Nhật của thiết bị\.', 'Từ chưa có MP3 dùng `speechSynthesis` tiếng Nhật của thiết bị.',s);p.write_text(s)
p=ROOT/'data/SOURCES.md';s=p.read_text();s=re.sub(r'Tệp âm thanh tổng hợp được tạo bằng edge-tts[^\n]*',f'Tệp âm thanh tổng hợp được tạo bằng edge-tts, giọng ja-JP-NanamiNeural; {fmt(len(paths))} MP3. Nhật ký gốc: sources/audio-generation.json; các đợt bổ sung: sources/audio-generation-n*.json. Không gửi bản ghi giọng người học đến dịch vụ tạo giọng. Từ chưa có MP3 dùng speechSynthesis trên thiết bị.',s);p.write_text(s)
p=ROOT/'docs/ECOSYSTEM.md';s=p.read_text();s=re.sub(r'[0-9][0-9.]* MP3',fmt(len(paths))+' MP3',s).replace('Lần triển khai công khai và iPhone thật chưa được thực hiện.','GitHub Pages đã được triển khai tại https://meiiie.github.io/hoc-tieng-nhat/; chưa thử iPhone thật.');p.write_text(s)
p=ROOT/'docs/PRONUNCIATION-JA.md';s=p.read_text().replace('Giọng Nanami N5/N4','Giọng Nanami');p.write_text(s)
