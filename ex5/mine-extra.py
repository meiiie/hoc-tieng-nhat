#!/usr/bin/env python3
"""Conservative extraction of original Wiktionary usage lines and KNBC."""
import html
import json
import re
import tarfile
import urllib.parse
from collections import Counter, defaultdict
from mine import CACHE, ROOT, matches, eligible, BY_ID

result = defaultdict(list)
counts = Counter()
seen = set()
for path in sorted((CACHE / 'wiktionary').glob('*.json')):
    for page in json.loads(path.read_text())['query']['pages'].values():
        if 'revisions' not in page or page['pageid'] in seen:
            continue
        seen.add(page['pageid'])
        counts['wiktionary_pages'] += 1
        rev = page['revisions'][0]
        in_ja = False
        for line_no, raw in enumerate(rev['slots']['main']['*'].splitlines(), 1):
            if re.match(r'^==[^=].*[^=]==$', raw):
                in_ja = bool(re.search(r'\{\{(?:L|ja)\|?ja?\}\}|日本語', raw)) or raw == '=={{L|ja}}=='
            if not in_ja or not re.match(r'^#[:*][^:*#]', raw):
                continue
            counts['wiktionary_usage_lines'] += 1
            text = re.sub(r'^#[:*]\s*', '', raw)
            # Exclude citations, literary quotations, templates and source-bearing lines.
            if re.search(r'\{\{|<|https?://|『|』|（|\(|\[\[w:|—|--|―', text):
                counts['wiktionary_complex_or_quoted'] += 1
                continue
            text = re.sub(r'\[\[([^\[\]]+)\]\]', lambda m: m[1].split('|')[-1], text)
            text = html.unescape(text.replace("'''", '').replace("''", '')).strip()
            if not eligible(text):
                counts['wiktionary_length_or_fragment'] += 1
                continue
            for ident, match in matches(text):
                result[ident].append({'id': ident, 'level': BY_ID[ident]['level'], 'ja': text,
                    'source': 'Japanese Wiktionary', 'source_id': f'{page["pageid"]}:{rev["revid"]}:L{line_no}',
                    'url': f'https://ja.wiktionary.org/w/index.php?oldid={rev["revid"]}',
                    'history_url': 'https://ja.wiktionary.org/w/index.php?title=' + urllib.parse.quote(page['title']) + '&action=history',
                    'author': f'Japanese Wiktionary contributors to {page["title"]}',
                    'licence': 'CC BY-SA 4.0', 'licence_url': 'https://creativecommons.org/licenses/by-sa/4.0/',
                    'page_title': page['title'], 'page_id': page['pageid'], 'revision': rev['revid'],
                    'revision_timestamp': rev['timestamp'], 'line': line_no, 'source_wikitext': raw,
                    'changes': 'Removed list/bold/link markup only; Japanese wording unchanged.', 'match': match})
                counts['wiktionary_matched_pairs'] += 1

archive = tarfile.open(CACHE / 'KNBC_v1.0_090925.tar.bz2')
licence_dir = ROOT / 'ex5/licences'
licence_dir.mkdir(exist_ok=True)
readme = archive.extractfile('KNBC_v1.0_090925/README.txt').read().decode('euc_jp')
(licence_dir / 'KNBC-README.txt').write_text(readme)
for member in archive:
    if '/corpus1/' not in member.name or not member.isfile() or member.name.endswith('fileinfos'):
        continue
    raw = archive.extractfile(member).read().decode('euc_jp')
    lines = raw.splitlines()
    # Parenthetical child sentences have separate files. Skip parents whose
    # annotations refer to removed parentheses rather than silently dropping text.
    if '括弧' in raw:
        counts['knbc_parenthesis_skipped'] += 1
        continue
    surfaces = [line.split(' ', 1)[0] for line in lines if line and line[0] not in '#*+@' and line != 'EOS']
    text = ''.join(surfaces)
    counts['knbc_sentences'] += 1
    if not eligible(text):
        continue
    counts['knbc_eligible'] += 1
    for ident, match in matches(text):
        sid = re.search(r'S-ID:(\S+)', lines[0])[1]
        result[ident].append({'id': ident, 'level': BY_ID[ident]['level'], 'ja': text,
            'source': 'KNBC 1.0 (2009-09-25)', 'source_id': sid,
            'url': 'https://nlp.ist.i.kyoto-u.ac.jp/kuntt/',
            'archive_url': 'https://nlp.ist.i.kyoto-u.ac.jp/kuntt/KNBC_v1.0_090925.tar.bz2',
            'archive_path': member.name, 'author': 'Kurohashi Laboratory, Graduate School of Informatics, Kyoto University; KNBC student contributors',
            'licence': 'BSD-3-Clause (Japanese text)', 'licence_url': 'https://nlp.ist.i.kyoto-u.ac.jp/kuntt/KNBC_v1.0_090925.tar.bz2',
            'licence_file': 'licences/KNBC-README.txt', 'changes': 'Reconstructed by concatenating annotated surface tokens; wording unchanged.',
            'match': match})
        counts['knbc_matched_pairs'] += 1
(CACHE / 'extra-pool.json').write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
counts['covered'] = len(result)
(CACHE / 'extra-counts.json').write_text(json.dumps(counts, indent=2) + '\n')
print(json.dumps(counts))
