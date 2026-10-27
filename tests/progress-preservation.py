"""Compare the performance release to the deployed v1.10.1, not a regenerated fixture."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'b4e0bc07df8d11365df3f264881bc8f17032a2ac'
UPSTREAM = '8e70f86a8903e7389a2b6bfccd26a4b02d28a64b'


def before(name):
    return subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=ROOT)


files = ['srs.js', 'learning-plan.js', 'storage.js', 'content.js',
         'vendor/ts-fsrs.min.js', 'core/mascot.js', 'data/kanji.json', 'data/kana.json']
files += [f'data/n{n}.json' for n in [5, 4, 3, 2, 1]]
hashes = {}
for name in files:
    raw = (ROOT / name).read_bytes()
    assert raw == before(name), name
    hashes[name] = hashlib.sha256(raw).hexdigest()
old, new = before('core/app-core.js').decode(), (ROOT / 'core/app-core.js').read_text()
sections = [('/* ---------- state ---------- */', '/* ---------- data ---------- */'),
            ('/* ---------- SRS review', 'function resumeBanner()'),
            ('/* ---------- backup ---------- */', '/* ---------- router & boot ---------- */')]
for start, end in sections:
    assert old[old.index(start):old.index(end)] == new[new.index(start):new.index(end)], start
assert 'const SCHEMA=11;' in new
result = {'baseline': BASE, 'schema': 11, 'unchangedFilesSHA256': hashes,
          'unchangedCoreSections': [s for s, _ in sections],
          'words': sum(len(json.loads((ROOT / f'data/n{n}.json').read_text())) for n in range(1, 6)),
          'allWordFieldsAndIDsByteIdentical': True}
# PR #3 landed while this task was running. Preserve every incoming audio/data/
# tooling change, plus its selective audio-cache invalidation list.
merged = {'CHANGELOG.md', 'lang-ja.js', 'sw.js', 'package.json', 'package-lock.json', 'version.json'}
incoming = subprocess.check_output(['git', 'diff', '--name-only', BASE, UPSTREAM], cwd=ROOT, text=True).splitlines()
for name in incoming:
    if name not in merged:
        assert (ROOT / name).read_bytes() == subprocess.check_output(['git', 'show', f'{UPSTREAM}:{name}'], cwd=ROOT), name
upstream_sw = subprocess.check_output(['git', 'show', f'{UPSTREAM}:sw.js'], cwd=ROOT, text=True)
audio_list = lambda s: json.loads(re.search(r'const REPLACED_AUDIO=(\[.*?\]);', s)[1])
assert audio_list(upstream_sw) == audio_list((ROOT / 'sw.js').read_text())
result['incomingRelease'] = {'head': UPSTREAM, 'filesPreservedExactly': len(set(incoming)-merged),
                             'replacedAudioPreserved': len(audio_list(upstream_sw))}
out = Path(os.environ.get('REPORT_DIR', ROOT.parent / 'reports'))
out.mkdir(parents=True, exist_ok=True)
(out / (os.environ.get('REPORT_PREFIX', '') + 'progress-preservation.json')).write_text(json.dumps(result, indent=2) + '\n')
print('Schema 11; all 8344 word records and scheduling/storage/backup code unchanged')
