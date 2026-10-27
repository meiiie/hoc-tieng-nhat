"""Three warm-home Lighthouse 13.x runs (median), plus legacy 11.7.1 PWA.
Use performance.py for a cold page/SW network budget. This reproduces the warm
installed-home methodology of handoff 3; it is not a cold mobile-network score.
"""
import json
import os
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from onboard import onboard

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('REPORT_DIR', ROOT.parent / 'reports'))
PREFIX = os.environ.get('REPORT_PREFIX', '')
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8931/'
RUNS = int(os.environ.get('LIGHTHOUSE_RUNS', '3'))
OUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='neko-lighthouse-') as profile, sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(profile, headless=True,
        args=['--remote-debugging-port=9225', '--no-sandbox'],
        viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    page = ctx.pages[0]
    page.goto(BASE)
    page.wait_for_selector('.view')
    if page.locator('#nm').count():
        onboard(page)
    page.wait_for_selector('.v-home .ja-levels')
    page.evaluate("S.set.theme='light';S.set.autoplay=false;save()")
    page.evaluate('navigator.serviceWorker.ready')
    page.wait_for_function('!!navigator.serviceWorker.controller')
    cases = [('lighthouse', f'lighthouse-current-{i}', 'performance,accessibility,best-practices')
             for i in range(1, RUNS + 1)]
    cases.append((str(ROOT / '.cache/lighthouse11/node_modules/.bin/lighthouse'),
                  'lighthouse-pwa-legacy', 'pwa,accessibility'))
    env = {**os.environ, 'CHROME_PATH': p.chromium.executable_path}
    summary = {'url': BASE, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'method': 'mobile simulation, onboarded light home, installed SW, warm persistent profile, disable-storage-reset',
               'runs': []}
    for cmd, label, categories in cases:
        name = PREFIX + label
        with (OUT / (name + '.log')).open('w') as log:
            run = subprocess.run([cmd, BASE, '--port=9225', '--disable-storage-reset',
                '--only-categories=' + categories, '--save-assets', '--output=json', '--output=html',
                '--output-path=' + str(OUT / name), '--quiet'], stdout=log, stderr=subprocess.STDOUT,
                timeout=240, env=env)
        path = OUT / (name + '.report.json')
        if run.returncode or not path.exists():
            raise RuntimeError((name, run.returncode, (OUT / (name + '.log')).read_text()[-2500:]))
        r = json.loads(path.read_text())
        a = r['audits']
        item = {'name': name, 'version': r['lighthouseVersion'], 'chromePath': env['CHROME_PATH'],
                'scores': {k: round(v['score'] * 100) for k, v in r['categories'].items()},
                'warnings': r.get('runWarnings', [])}
        if 'performance' in r['categories']:
            assert r['lighthouseVersion'].startswith('13.'), r['lighthouseVersion']
            item.update(tbtMs=a['total-blocking-time']['numericValue'],
                        mainThreadMs=a['mainthread-work-breakdown']['numericValue'],
                        totalByteWeight=a['total-byte-weight']['numericValue'],
                        requests=len(a['network-requests']['details']['items']))
            summary['runs'].append(item)
        else:
            assert r['lighthouseVersion'] == '11.7.1'
            summary['legacy'] = item
        print(json.dumps(item), flush=True)
    summary['median'] = {k: statistics.median([r[k] for r in summary['runs']])
                         for k in ['tbtMs', 'mainThreadMs', 'totalByteWeight', 'requests']}
    summary['median']['scores'] = {k: statistics.median([r['scores'][k] for r in summary['runs']])
                                   for k in summary['runs'][0]['scores']}
    (OUT / (PREFIX + 'lighthouse-summary.json')).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print('Median:', json.dumps(summary['median']), flush=True)
    ctx.close()
