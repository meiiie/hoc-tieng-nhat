"""Cold startup budgets and real lazy/offline navigation, Chromium and WebKit.
The budget includes service-worker installation; a warm SW's zero wire bytes is
not evidence of a small startup. No Lighthouse timing thresholds in this gate.
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from onboard import onboard

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('REPORT_DIR', ROOT.parent / 'reports'))
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8931/'
PREFIX = os.environ.get('REPORT_PREFIX', '')
BIG = re.compile(r'/data/(n[1-5]|kanji)\.json$')
results = {}
with sync_playwright() as p:
    for engine in ['chromium', 'webkit']:
        browser = getattr(p, engine).launch()
        ctx = browser.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
        requests, responses, errors, checks = [], [], [], []
        ctx.on('request', lambda r: requests.append(r.url))
        ctx.on('response', lambda r: responses.append(r))
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: errors.append(str(e)))
        pg.goto(BASE)
        onboard(pg)
        pg.wait_for_selector('.v-home .ja-levels')
        pg.evaluate('navigator.serviceWorker.ready')
        pg.wait_for_function('!!navigator.serviceWorker.controller')
        pg.wait_for_timeout(350)
        assert not [u for u in requests if BIG.search(urlsplit(u).path)], requests
        bodies = [{'url': r.url, 'bytes': int(r.headers.get('content-length', 0)),
                   'encoding': r.headers.get('content-encoding')} for r in responses]
        startup_bytes = sum(r['bytes'] for r in bodies)
        decoded = pg.evaluate('performance.getEntriesByType("navigation").concat(performance.getEntriesByType("resource")).reduce((n,r)=>n+r.decodedBodySize,0)')
        assert startup_bytes < 1_300_000, startup_bytes  # Both page + worker; uncompressed localhost.
        assert 100_000 < decoded < 600_000, decoded
        assert pg.evaluate('words.length===8344&&!words.some(w=>w.example)')
        checks.append('cold page <600 KB decoded; page + SW <1.3 MB; no level/kanji requests')

        # Home/statistics must count scheduled cards outside the selected level
        # without hydrating any vocabulary, including the reverse direction.
        due_id = next(w['id'] for w in json.loads((ROOT / 'data/n2.json').read_text()) if w['example'])
        pg.evaluate("id=>{const w=byId(id);S.set.autoplay=false;S.set.f={cefr:'N5'};S.jaUnlocked[2]=true;S.notes[w.id]='giữ nguyên';S.srs[w.id+'~r']={...SRS.fresh(),state:'review',s:31,d:4,int:30,due:Date.now()-86400000,reps:4};S.introductions[w.id]=Date.now()-86400000;save();route()}", due_id)
        assert pg.locator('.kpis div').nth(1).locator('b').inner_text() == '1'
        pg.evaluate("S.set.f={cefr:'N2'};location.hash='#/stats'")
        pg.wait_for_selector('.v-stats .stat')
        assert pg.locator('.stat div').nth(2).locator('b').inner_text() == '1'
        assert not [u for u in requests if BIG.search(urlsplit(u).path)]
        pg.evaluate("S.set.f={cefr:'N5'};location.hash='#/'")
        pg.wait_for_selector('.v-home .ja-levels')
        snapshot = pg.evaluate('save().then(()=>JSON.stringify([S.srs,S.notes,S.ev,S.introductions,S.revlog]))')
        checks.append('home and selected-level stats count global/reverse progress without level fetches')

        pg.evaluate("location.hash='#/review'")
        pg.wait_for_selector('.fc')
        assert pg.evaluate('id=>document.querySelector(".face.f .vi").textContent===byId(id).v', due_id)
        assert pg.evaluate('JaData.isLoaded(5)&&JaData.isLoaded(2)&&!JaData.isLoaded(1)&&!JaData.isLoaded(3)&&!JaData.isLoaded(4)')
        for n in [5, 2]:
            rows = json.loads((ROOT / f'data/n{n}.json').read_text())
            for expected in [rows[0], next(w for w in rows if w['example'])]:
                actual = pg.evaluate('x=>Object.fromEntries(x.keys.map(k=>[k,byId(x.id)[k]]))',
                                     {'id': expected['id'], 'keys': list(expected)})
                assert actual == expected
        assert pg.evaluate('JSON.stringify([S.srs,S.notes,S.ev,S.introductions,S.revlog])') == snapshot
        checks.append('review hydrates selected + scheduled levels; full fields/ruby and reverse due card preserved')

        ctx.set_offline(True)
        pg.reload()
        pg.wait_for_selector('.fc')
        assert pg.evaluate('id=>!!byId(id).example', due_id)
        pg.evaluate("S.set.f={cefr:'N1'};S.jaUnlocked[1]=true;location.hash='#/list'")
        pg.wait_for_selector('#retry-data')
        assert pg.evaluate('JSON.stringify([S.srs,S.notes,S.ev,S.introductions,S.revlog])') == snapshot
        ctx.set_offline(False)
        pg.click('#retry-data')
        pg.wait_for_selector('.v-list #sq')
        assert pg.evaluate('JaData.isLoaded(1)')
        checks.append('used levels survive offline reload; uncached level offers retry without changing progress')

        pg.evaluate("location.hash='#/settings'")
        pg.wait_for_selector('#data-dl')
        pg.click('#data-dl')
        pg.wait_for_function("document.querySelector('#data-dlst').textContent.startsWith('Đã lưu N5–N1')&&!document.querySelector('#data-dl').disabled", timeout=60000)
        assert pg.evaluate('!JaData.isLoaded(3)&&!JaData.isLoaded(4)')
        pg.click('.sheet-close')
        pg.wait_for_selector('.v-home .ja-levels')
        ctx.set_offline(True)
        pg.reload()
        pg.wait_for_selector('.v-home .ja-levels')
        for n in [5, 4, 3, 2, 1]:
            pg.evaluate("n=>{S.jaUnlocked[n]=true;S.set.f={cefr:'N'+n};location.hash='#/list'}", n)
            pg.evaluate('route()')
            pg.wait_for_selector('.v-list #sq')
            assert pg.evaluate('n=>words.some(w=>w.level===n&&w.example?.furigana)', n)
        pg.evaluate('JaData.loadKanji()')
        assert pg.evaluate('!!LANG.kanji["学"].strokes')
        assert pg.evaluate('JSON.stringify([S.srs,S.notes,S.ev,S.introductions,S.revlog])') == snapshot
        assert not errors, errors
        checks.append('Settings downloads all levels without parsing unused levels; every level and kanji work offline')
        ctx.close()

        # A delayed load finishing after navigation must not replace the current
        # view. Repeated navigation requests share one in-flight level fetch.
        isolated = browser.new_context(service_workers='block', reduced_motion='reduce')
        page = isolated.new_page()
        held = []
        page.route('**/data/n4.json*', lambda route: held.append(route))
        page.goto(BASE)
        onboard(page)
        page.wait_for_selector('.v-home .ja-levels')
        page.evaluate("S.jaUnlocked[4]=true;S.set.f={cefr:'N4'};location.hash='#/list'")
        page.wait_for_function("document.querySelector('#title').textContent==='Đang tải bộ từ'")
        page.evaluate('void route();void route()')
        page.wait_for_timeout(100)
        assert len(held) == 1
        page.evaluate("location.hash='#/'")
        page.wait_for_selector('.v-home .ja-levels')
        held[0].fulfill(status=200, content_type='application/json', body=(ROOT / 'data/n4.json').read_text())
        page.wait_for_function('JaData.isLoaded(4)')
        assert page.locator('.v-home .ja-levels').count() == 1
        checks.append('one fetch per concurrent level load; late completion never replaces a newer route')
        isolated.close()
        browser.close()
        results[engine] = {'url': BASE, 'passed': len(checks), 'startupRequests': len(bodies),
                           'startupEncodedBodyBytesIncludingSW': startup_bytes,
                           'pageDecodedBytes': decoded, 'startupFiles': bodies, 'checks': checks}
        print(engine, len(checks), 'performance/offline checks passed', flush=True)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / (PREFIX + 'performance.json')).write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
