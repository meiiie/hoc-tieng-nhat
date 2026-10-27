# Startup performance

## Baseline measured before implementation (2026-10-27)

Baseline commit: `b4e0bc07df8d11365df3f264881bc8f17032a2ac` (v1.10.1).
`git pull --rebase origin main` reported up to date. Measurements were made against
https://meiiie.github.io/hoc-tieng-nhat/ and http://localhost:8931/ before changing
application code. Raw reports live outside the repository at
`/workspace/japanese/reports/perf-before-{live,local}-*`:

- `cold.json`: first visit in a fresh Chromium profile, page and worker requests,
  response sizes/encoding, resource timings, observed long tasks and CDP metrics.
- `cold-trace.json`: Chromium performance trace, including V8 profiling.
- `lighthouse-1.report.json` / `.html`: Lighthouse **13.5.0**, mobile simulation,
  home after onboarding, installed SW, `--disable-storage-reset`, same warm-profile
  method as handoff 3. The `*-0.trace.json` and `*-0.devtoolslog.json` retain assets.
- `summary.json`: full `mainthread-work-breakdown`, `bootup-time`,
  `network-requests`, `total-byte-weight`, and `long-tasks` audits.
- `parse.json`: separate diagnostic run, timing native `JSON.parse` after reading
  each Response as text; unthrottled, not substituted for Lighthouse timings.

| Measurement | Live before | Localhost before |
|---|---:|---:|
| Performance (one baseline run) | 74 | 75 |
| TBT, simulated ms | 1,471 | 1,321 |
| Main-thread audit, ms | 4,340.95 | 3,753.76 |
| Script evaluation, ms | 624.78 | 553.77 |
| Script parse/compile, ms | 120.21 | 42.79 |
| Style/layout, ms | 326.49 | 288.66 |
| Rendering, ms | 192.52 | 194.13 |
| Garbage collection, ms | 118.36 | 108.81 |
| HTML/CSS parse, ms | 51.59 | 53.92 |
| Other (not safely attributable to JS parse), ms | 2,907.00 | 2,511.68 |
| Page startup requests (including document) | 25 | 25 |
| Page decoded response bytes | 14,559,738 | 14,559,738 |
| Cold page encoded body bytes (Content-Length) | 2,416,014 | 14,559,738 |
| Additional SW install requests | 43 | 43 |
| SW install encoded body bytes (Content-Length) | 2,504,760 | 14,687,822 |
| Cold page observed long tasks | 6 (510 ms total, max 151 ms) | 5 (402 ms total, max 100 ms) |
| Lighthouse warm `total-byte-weight` | 0 (SW cache) | 0 (SW cache) |

The historical live 73 / 1,780 ms is reproduced within shared-machine run
variation, not used as the new baseline. Warm Lighthouse reports 25 requests and
zero transferred bytes because they are served by the SW. That is **not zero
startup data**: JSON decoding, parsing, allocation and rendering still happen.
Cold Content-Length sums exclude HTTP headers; gzip is used on Pages. Playwright
returns empty bodies for SW-originated requests, so their Content-Length is
reported separately instead of claiming an observed decoded size of zero.

## Verified causes

`LANG.loadData` awaits all five vocabulary arrays plus kana and kanji before
rendering any screen; it copies all 8,344 records into core-compatible objects and
builds indexes. Home and statistics need IDs, levels and saved progress, not
examples, English senses, translation provenance or ruby segments. Those fields
are embedded in the following files (no separate example/ruby request exists):

| File fetched by both page and SW | Decoded bytes | Live gzip body bytes | Diagnostic JSON parse ms, live / local |
|---|---:|---:|---:|
| `data/n5.json` | 1,103,219 | 182,789 | 9.5 / 2.3 |
| `data/n4.json` | 1,121,206 | 188,330 | 5.4 / 12.9 |
| `data/n3.json` | 3,116,789 | 509,376 | 12.9 / 47.3 |
| `data/n2.json` | 3,124,008 | 497,925 | 13.4 / 27.3 |
| `data/n1.json` | 5,230,858 | 848,555 | 27.8 / 59.5 |
| `data/kanji.json` | 490,153 | 72,354 | 3.3 / 1.7 |
| `data/kana.json` | 39,013 | 3,206 | 0.2 / 0.1 |

The five level files alone are **13,696,080 decoded bytes**. Native JSON.parse
in the separate diagnostic totals 72.5 ms live / 151.1 ms local, before copying,
GC and core work. These unthrottled measurements do not explain every millisecond
of Lighthouse's much larger simulated “Other” bucket; the raw traces are retained
rather than relabelling that entire bucket as parse time.

`sw.js` also precaches all six large files in its 42-entry install shell using
`cache: 'reload'`. Cold context request logging confirms these additional fetches
overlap the first visit. That is about 2.30 MB of extra compressed level/kanji
responses on live Pages, and installation/offline readiness depends on them all.

`bootup-time` additionally attributes 799.61 ms total CPU to mascot animation,
429.46 ms to app-core, and 2,409.20 ms to unattributable work on the live warm run.
The first fix will remove unnecessary vocabulary/kanji work and duplicate
precache traffic; further decisions will use fresh measurements, not assumptions
about script size or the pronunciation model. No model or MP3 was requested at
startup.

## Implementation (v1.11.0)

`tools/build-index.py` generates a **134,067-byte** catalogue from the unchanged
level files. It contains IDs in their original order, level membership, missing
audio IDs, byte sizes and content revisions. Home, onboarding, statistics,
filters, unlocking and global/reverse due counts use that catalogue plus saved
progress. The full five JSON files and all of their fields remain byte-identical.

`ja-data.js` hydrates a level's records in place only when a study route needs
it. That preserves core map/queue references and study order. Review also loads
levels with active scheduled cards, including reverse directions and saved
sessions, so global scheduling still works. Practice distractors use fully loaded
words. Kanji metadata loads on the writing route. Concurrent requests share a
promise; late completion cannot replace a newer route, and failures offer Retry.

The install shell contains the index and small kana table, not vocabulary or
kanji. `htn-content-v1` caches content on use independently of the versioned
shell; revision URLs allow content updates without invalidating unchanged levels.
An offline fallback can use an already-cached prior revision. Activation copies
old eager-shell vocabulary before deleting old shell caches. Cache identity and
content metadata are separate from learner storage: schema stays **11**.

While this task was running, main advanced to v1.10.2 / PR #3
(`8e70f86a8903e7389a2b6bfccd26a4b02d28a64b`). The local commits were rebased;
its 152 corrected MP3s, source audits, tools and selective audio-cache invalidation
were retained. Vocabulary JSON did not change in that release. All final gates
must run on the combined v1.11.0 tree; earlier gate runs are not the final release
verification. The original before measurements remain the v1.10.1 baseline.

Settings offers **Tải để dùng offline** for all five levels, their complete
examples/ruby, and kanji metadata. Downloads are sequential and don't parse
unused levels. It only reports success after the requested content is cached;
partial downloads can be retried. Audio and individual stroke SVGs remain on-use
(or the existing audio download button). Home alone does not make unseen levels
available offline; an uncached level explains this and offers Retry/home.

## First implementation measurement

After the loading change, using the same unmodified capture harness, the first
localhost warm Lighthouse 13.5.0 run scored **100**, TBT **52.5 ms**, main-thread
work **1,499.40 ms**, versus **75 / 1,321 ms / 3,753.76 ms** before. This is one
intermediate local run, not the final live median. Artifacts:
`/workspace/japanese/reports/perf-after-local-*`.

Cold page startup fell from **14,559,738 to 512,535 decoded bytes** and from
**25 to 21 requests**. The page requested only `data/index.json` and
`data/kana.json` as data. Observed worker traffic in that local capture fell from **43 to 38 requests**; combined
page + worker uncompressed response bodies fell from **29,247,560 to 1,150,873
bytes**. The cold page had one 58 ms long task instead of five totaling 402 ms.
This confirms that the unnecessary full-data boot path was the dominant removable
cause. Mascot bytes and animation remain unchanged; optimizing them was not needed
for this measured improvement.

Final deployed verification uses **three** Lighthouse 13.x runs and reports the
median, plus Lighthouse **11.7.1** for its legacy PWA category, after Pages matches
the pushed HEAD. The results and limits belong in
`/workspace/japanese/codex-report-4.md` and `reports/live4-lighthouse-summary.json`;
the localhost result above must not be presented as a live score.

## Initial deployed result (v1.11.0, 2026-10-27)

Pages built `e5cc5877bd5695d02a67312c64db60217d62204a`; 24 release files matched
SHA-256 before live measurement. Lighthouse 13.5.0 scored **100, 100, 95**;
median **100**, TBT **69.5 ms** (69.5 / 10 / 250), main-thread **1,821.79 ms**
(1,821.79 / 1,520.90 / 2,066.79). Accessibility and Best Practices were 100 in
all runs; Lighthouse 11.7.1 PWA and Accessibility were both 100, without warnings.
These are warm installed-home mobile simulations, not cold phone benchmarks.

Fresh live startup: **21 page requests / 512,604 decoded bytes / 186,982 gzip
body bytes**; worker registration + install added **39 requests / 277,735 gzip
body bytes**. Combined traffic: **60 requests / 464,717 encoded body bytes**,
versus 68 / 4,920,774 before. The actual install manifests have **42 → 38 entries**;
observed worker-request counts also include `sw.js` when the browser emits it.
The cold trace observed one 58 ms long task versus six totaling 510 ms before.
The separate native JSON.parse diagnostic fell from **72.5 to 0.3 ms**; only the
index and kana were parsed. Warm Lighthouse still reports zero wire-byte weight
because those 21 requests are served by the installed SW.

The initial deployed Lighthouse reports are archived outside the repository as
`reports/initial-live4-lighthouse-*`; the final deployment's three-run median,
all gate/live results, incoming-release details and untested items are in
`/workspace/japanese/codex-report-4.md` and `reports/live4-*`. Changes since this
measurement only document results; final verification must use the final Pages
HEAD, without substituting this initial score.

## Regression and preservation gates

- `npm test`: index IDs/order/levels/audio/revision integrity in addition to the
  unchanged scheduler, storage, content and pronunciation tests.
- `python3 tests/performance.py [URL]`: cold page <600,000 decoded bytes; page +
  worker response bodies <1,300,000 bytes on uncompressed localhost; no level or
  kanji request on home/stats, including installation. Both Chromium and WebKit
  test global reverse-card counts, hydration, used-level offline reload,
  missing-level retry, full offline download, and stale navigation cancellation.
- `python3 tests/progress-preservation.py`: byte comparison to deployed v1.10.1
  of all 8,344 full records/fields/IDs, kana/kanji, scheduler, storage, vendor and
  mascot; unchanged core state/migration, SRS review and backup sections.
- Existing E2E/axe, PWA root/subpath failed and successful updates,
  answer-boundaries and standalone onboarding remain required. PWA also verifies
  retaining vocabulary from an old eager shell.

Generate core only via `tools/make-core.py` (asserted replacements). Full data
builds also regenerate the index. No Lighthouse timing threshold is used as a
flaky unit test: deterministic network/content boundaries guard the root cause,
while deployed Lighthouse measures the actual outcome. Warm `total-byte-weight`
can still be zero with the SW, so cold request/body inventories are reported too.
