"""AI example card in both themes, with the same production data and renderer."""
import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from onboard import onboard

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('SCREENSHOT_DIR', ROOT.parent / 'screenshots'))
PREFIX = os.environ.get('REPORT_PREFIX', '')
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8931/'
OUT.mkdir(parents=True, exist_ok=True)
shots = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                             has_touch=True, is_mobile=True, reduced_motion='reduce')
    page = ctx.new_page()
    page.goto(BASE)
    onboard(page)
    page.wait_for_selector('.v-home')
    page.evaluate('JaData.loadLevel(5)')
    for theme in ['light', 'dark']:
        ident = page.evaluate("""theme=>{const w=words.find(w=>w.example?.source==='ai');
          S.set.theme=theme;S.set.autoplay=false;S.set.gtip=true;S.set.furigana='on';S.set.romaji='off';
          S.star={[w.id]:true};S.set.f={cefr:'N5',star:true};S.srs={};S.sess={};S.introductions={};
          S.bury=null;S.studyDay=null;FC=null;applyTheme();return save().then(()=>w.id)}""", theme)
        page.goto(BASE + '#/review')
        page.evaluate('route()')
        page.wait_for_selector('#show')
        page.click('#show')
        page.wait_for_selector('.fc.flip .ja-example-ai')
        page.evaluate('document.fonts.ready')
        page.evaluate("Promise.all(document.getAnimations().filter(a=>a.effect?.getComputedTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{})))")
        page.locator('.face.b .ja-example-source summary').click()
        box = page.locator('.face.b .ja-example-ai')
        assert 'Câu do AI viết, cần kiểm tra' in box.inner_text()
        assert 'Tatoeba' not in box.inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        filename = OUT / (PREFIX + theme + '-ai-sentence-card.png')
        box.screenshot(path=str(filename), animations='disabled')
        shots.append({'file': str(filename), 'word': ident, 'theme': theme})
    ctx.close()
    browser.close()
(OUT / (PREFIX + 'ai-screenshots.json')).write_text(json.dumps({'url': BASE, 'files': shots}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(shots, ensure_ascii=False))
