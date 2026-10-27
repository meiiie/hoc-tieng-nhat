# Japanese content expansion implementation plan

> Execute inline with superpowers:executing-plans. The user explicitly forbids all subagents and questions and authorizes gated commits and pushes to main.

**Goal:** Add attributed Tatoeba examples, Nanami audio for the remaining levels, licensed pitch data where defensible, and verify the public PWA.

**Architecture:** Preserve word IDs and schema 11. Keep authored source overlays under data/sources and apply them in tools/build-data.py. Reuse the language adapter and generated core hooks; keep large assets lazy.

**Tech stack:** Static JavaScript, Python data scripts, Node tests, Python Playwright Chromium/WebKit, FFmpeg, edge-tts.

**Spec:** User request in this session, with the v1.0.0 handoff at /workspace/japanese/codex-report.md.

## Global constraints

- Work personally in the existing main checkout; no agents, force push, history rewriting or destructive storage changes.
- Every release push requires npm test and all browser gates documented in docs/TESTING.md. Local checkpoints may precede release verification.
- Bump version.json, sw.js and CHANGELOG for each release; preserve stored IDs/progress.
- Attributed CC BY 2.0 FR Japanese sentences, at most 25 characters; exact surface matches checked against token boundaries/readings. No speculative furigana or accents.
- One example per eligible word initially. Direct vie > eng-pivot vie > machine translation of directly linked eng. Each reused sentence keeps its own attribution; pivot and machine are visibly labelled.
- Audio stays outside the SW shell, mono 24 kHz / 32 kbit/s Nanami. No LFS.

## Review focus

- Substring false matches and homophones: matching fixtures plus corpus provenance validation.
- Inflected cloze answers: exact-only examples initially, so dictionary answers fit the blank; skip unsupported matches.
- Rebuild erasing enrichment: overlays applied on every build, verify deterministic rebuild and stable IDs.
- SW update across releases and subpaths: make PWA test derive current version, exercise failed and successful updates.
- Live report false positives from local URLs/caches: fresh browser contexts, explicit base URL and live report prefix, record actual URLs/versions.

### Task 1: N5/N4 examples and cloze

- [x] Add failing matching/data and cloze regression tests.
- [x] Build deterministic attributed Tatoeba extraction/selection and translation overlay; retain checksums/link evidence.
- [x] Render Vietnamese, translation labels and attribution; enable core cloze with real blank/answer.
- [x] Update notices, data counts and version; run unit, E2E/axe, PWA and answer-boundary gates, checkpoint and push green release.

### Task 2: N3 examples

- [x] Reuse pipeline, review machine translations, record coverage; run all gates, bump, commit and push.

### Task 3: Audio per N3, N2, N1

- [ ] Add resumable chunk/backoff options to tools/gen-audio.py with retry behavior checks.
- [ ] Generate in background chunks, verify all MP3 decode/format, rebuild bindings, document actual counts and hosting size/limits.
- [ ] Gate, bump, commit and push each level separately.

### Task 4: Licensed pitch completion

- [ ] Inspect local Kanjium and licensed online alternatives, retain exact source provenance and licence terms.
- [ ] Add only directly supported form/reading accents; test mora bounds and source matches; document remaining nulls and before/after counts.
- [ ] Gate, bump, commit and push release.

### Task 5: Live verification and report

- [ ] Test scripts accept base URL/prefix. Wait for Pages build matching final pushed commit.
- [ ] Run full live Chromium/WebKit E2E/axe, live-safe PWA checks, answer boundaries, Lighthouse 13.x and 11.7.1 PWA.
- [ ] Save live-* reports and review-example screenshots; inspect screenshots.
- [ ] Write /workspace/japanese/codex-report-2.md with full commit hashes/push status, counts, sizes, gate results, scores and honest untested list.
