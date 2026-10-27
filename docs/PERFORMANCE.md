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

`sw.js` also precaches all six large files in its 43-entry install shell using
`cache: 'reload'`. Cold context request logging confirms these additional fetches
overlap the first visit. That is about 2.30 MB of extra compressed level/kanji
responses on live Pages, and installation/offline readiness depends on them all.

`bootup-time` additionally attributes 799.61 ms total CPU to mascot animation,
429.46 ms to app-core, and 2,409.20 ms to unattributable work on the live warm run.
The first fix will remove unnecessary vocabulary/kanji work and duplicate
precache traffic; further decisions will use fresh measurements, not assumptions
about script size or the pronunciation model. No model or MP3 was requested at
startup.

## Implementation and after measurements

Pending. Storage schema must remain 11, runtime vocabulary files/IDs/semantics
must remain unchanged, and used levels must survive offline reloads and updates.
The regression gate must cover fresh home traffic including SW installation;
zero transferred bytes in a warmed Lighthouse run cannot enforce that budget.
