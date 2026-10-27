#!/usr/bin/env python3
"""Fetch pinned Wiktionary revisions for the missing headwords, sequentially."""
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/ex5/wiktionary'
CACHE.mkdir(exist_ok=True)
words = json.loads((ROOT / 'ex5/missing-words.json').read_text())
titles = sorted({f for w in words for f in [w['kanji'], w['kana']]})
for start in range(0, len(titles), 40):
    out = CACHE / f'{start:04}.json'
    if out.exists():
        continue
    params = {'action': 'query', 'format': 'json', 'titles': '|'.join(titles[start:start+40]),
              'prop': 'revisions', 'rvprop': 'ids|timestamp|content', 'rvslots': 'main',
              'redirects': '1', 'maxlag': '5'}
    url = 'https://ja.wiktionary.org/w/api.php?' + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={'User-Agent': 'NekoJapaneseExampleResearch/1.0 (local corpus licence audit)'})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = json.load(response)
    assert 'query' in data, data
    out.write_text(json.dumps(data, ensure_ascii=False) + '\n')
    print(start, len(data['query']['pages']), flush=True)
