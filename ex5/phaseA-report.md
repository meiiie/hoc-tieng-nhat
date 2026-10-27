# Examples v5 — Phase A report

**1,409 previously empty word IDs now have a candidate: 725 licensed and 684
authored.** The two files are disjoint and cover the requested inventory exactly.
These are review artifacts; **no examples have been integrated into app data**.

**Analyzer limitation:** 1,349 targets have machine confirmation of the selected
lexeme through the strict matcher or explicit UniDic alternatives. The remaining
**60 authored examples do not have that confirmation** and remain flagged for
reading/lemma review. Candidate coverage is complete; automatic confirmation is
not. No native-speaker review is claimed.

| Level | Initially empty | A1 licensed | A2 authored | No candidate |
|---|---:|---:|---:|---:|
| N5 | 35 | 7 | 28 | 0 |
| N4 | 14 | 8 | 6 | 0 |
| N3 | 50 | 12 | 38 | 0 |
| N2 | 305 | 186 | 119 | 0 |
| N1 | 1,005 | 512 | 493 | 0 |
| **Total** | **1,409** | **725** | **684** | **0** |

## Deliverables

- [licensed-candidates.json](licensed-candidates.json): sentence text, target
  ID/level, source/ID/URL, author, licence, translation provenance, selected
  JMdict sense, analyzer evidence and conservative ruby.
- [authored.json](authored.json): all requested `id`, `level`, `ja`,
  `target_surface`, `sense`, `vi`, `rationale` fields, plus machine-authoring
  labels and the same analysis/ruby evidence.
- [sources-checked.md](sources-checked.md): primary-source licence research,
  dump availability, extraction limits, source counts and exclusions.
- [analyzer-review.json](analyzer-review.json): all 277 strict-matcher
  exceptions, including the 217 alternatives that could be confirmed and
  the 60 that could not.
- [validation.json](validation.json): counts, candidate hashes, unresolved
  IDs and structural/provenance validation result.
- [input-manifest.json](input-manifest.json): 82 pinned input hashes,
  including external corpora, revision API responses and unchanged analyzer
  code. Large raw corpora remain outside the committed deliverables.
- [editorial-decisions.tsv](editorial-decisions.tsv): individually written
  selection/authoring decisions. This is not a generated sentence-template list.
- [licences](licences): complete KFTT and KNBC release notices.
- [checks](checks): logs of the existing unit, matching and ruby tests.

The versioned files live in this repository's `ex5/`. Identical handoff copies
are placed at **`/workspace/japanese/ex5/`**, including the explicitly requested
absolute path `/workspace/japanese/ex5/sources-checked.md`.

## A1 results

| Selected source | Rows | Sentence licence |
|---|---:|---|
| Tatoeba | 373 | CC BY 2.0 FR |
| KFTT 1.0 | 332 | CC BY-SA 3.0 |
| Japanese Wiktionary | 12 | CC BY-SA 4.0 |
| KNBC 1.0 | 8 | BSD three-clause Japanese terms |

The finite mining pool covered 1,025 missing IDs. Individual review retained
licensed examples for 725. Another 300 had mined matches that were unsuitable
for the selected word/sense or not selected after readability review; 384 had
no pooled match. All 684 received authored examples. Common rejection reasons
were proper names, fragments, a different homograph, a verb stem mistaken for
a noun, or an unsuitable context. No licensed Japanese was shortened to fit.

Licensed examples are at most **35 Unicode characters**; 207 exceed 25.
Of the selected Tatoeba rows, 116 exceed 25 and 65 were eligible under the
reconstructed old rules except for the length limit. JMdict examples overlap
Tatoeba rather than providing an independent corpus: 33 selected rows have
matching JMdict example references. Twenty-eight selected Tatoeba IDs already
serve other app words, but none of this phase's target IDs had an example.

There are **27 existing human Vietnamese translations**, retained verbatim
with their own attribution and corpus links. Five optional machine refinements
are stored separately. The remaining **698 licensed translations** were written
directly from Japanese by this assistant and marked machine. Source-specific
share-alike terms and attribution remain attached to their translations.

JParaCrawl, Mainichi/KyotoCorpus text and KWDLC were excluded for the documented
licensing/attribution reasons. Wikipedia dumps were checked for availability;
no full dump was processed. Wiktionary uses fixed API revisions. KFTT has exact
archive-line identifiers but lacks per-line original Wikipedia revision URLs;
the output preserves that limitation instead of inventing links.

## A2 and linguistic review

All **684 authored sentences are 9–21 characters**, including punctuation,
so none exceeds the requested approximate 25-character preference. Japanese
and Vietnamese were composed individually. The selected sense stores the
original **1-based JMdict entry sense index**, full English gloss list,
part of speech, usage markers and spelling/reading restrictions. Every index
and gloss was checked against the supplied dictionary snapshot.

The rationale explains the intended meaning, context and register. Rare
readings, classical expressions, bound forms and historical terms use literary,
technical or historical contexts where appropriate; they are not presented as
uniformly common conversational vocabulary. Vietnamese aims at the intended
meaning in natural Vietnamese rather than matching Japanese word order.
All authored rows are marked machine and `native_reviewed: false`.

The assistant reviewed all 1,409 final pairs. **Human/native editorial reviews:
0.** Licence review and morphological evidence do not certify linguistic
perfection, and the 60 unresolved analyzer cases are not ready to be treated as
automatically validated examples in a later import.

## Analyzer and ruby

Ran the repository's existing `analyze`, `match_word`, lemma/spelling guards and
`annotate` functions using **fugashi 1.5.2 / UniDic 2.1.2 via unidic-lite 1.0.8**.
The dictionary binary SHA-256 is
`122c4c91f026bf4b65bbe2dfd8b9f8eeb6ab56d8eb2a7287a68bca75708ba513`.
The existing files under `tools/` were not edited.

| Result | Licensed | Authored | Total |
|---|---:|---:|---:|
| Existing strict matcher confirms target | 725 | 407 | 1,132 |
| Full-surface UniDic alternative confirms spelling + selected reading | 0 | 217 | 217 |
| Same default lemma, requested reading unconfirmed | 0 | 47 | 47 |
| Only assistant/JMdict review; analyzer insufficient | 0 | 13 | 13 |

The phase-only helper examines full-surface alternate dictionary nodes with an
exact JMdict spelling/reading guard; it does not relabel these as strict matches.
The 60 remaining cases are N3 **3**, N2 **4**, N1 **53**. Examples include
greetings parsed as verb sequences, `再来月` split as `再` + `来月`, bound forms
inside compounds, and uncommon readings such as `寄贈／きそう` or
`三日月／みかずき`. Original tokens, lemmas and readings remain visible.
No unknown target tokens were hidden: **0 unknown target tokens** were reported.

Computed **4,014 ruby spans across 1,349 sentences**. Sixty sentences have no
ruby; that is not necessarily the same set as the 60 unresolved targets.
The existing conservative policy omits ambiguous readings, proper names,
numbers/counters and uncertain alignment. In addition, all tokens overlapping
a non-strict target are kept plain, even if another reading looks plausible.
Non-target confident ruby is retained. Every base sequence reconstructs the
exact Japanese sentence, every ruby base contains only kanji, and every ruby
span has retained dictionary evidence. These records are not runtime-ready
imports, and no ruby was added to app data.

## Verification and stop point

| Check | Result |
|---|---|
| `ex5/validate.py` | Passed: 82 input hashes; exact 1,409-ID inventory; disjoint coverage; sense indices/glosses/restrictions; 725 source-text/attribution checks; existing VI text/links; analyzer/ruby reproduction; no changes outside `ex5/` |
| `npm test` | **93 passed**, 0 failed: SRS 23 + plan 26 + Node suites 44 |
| `tests/example_matching.py` | **8 passed**, 0 failed |
| `tests/furigana.py` | **3 passed**, 0 failed, including regeneration of existing app ruby |
| Candidate rebuild | Both JSON files regenerate byte-identically to the validated SHA-256 values |

There are 1,392 distinct Japanese strings across the 1,409 associations; some
spelling variants or separate words share an appropriate source sentence.
Browser, deployment and release-performance gates were not run because this
phase changes no runtime or released data. Their omission is not a claim that
those gates passed for a new release.

Started from v1.11.0, ran `git pull --rebase origin main`, then worked on
**`examples-v5`**. Baseline commit:
`cceba8b696feb5dce1fb7caa233653aa05775b48`.
All tracked content outside `ex5/` remains byte-identical to that baseline.
No subagents, child agents or parallel agents were used. The deliverable is
committed locally on `examples-v5`; **no push, merge, release or app-data
integration** is part of this phase. Stop here.

## Reproduction

From `/workspace/japanese/hoc-tieng-nhat`:

```sh
.cache/content-venv/bin/python ex5/validate.py
.cache/content-venv/bin/python ex5/build-candidates.py
```

Validation uses the raw inputs at the paths in `input-manifest.json`, verifies
their hashes, and regenerates `validation.json`. Building additionally uses the
pinned `.cache/ex5/review-pool.json` and the committed editorial decisions.
It writes only the two candidate files and `analyzer-review.json` in `ex5/`.
Do not run the app's data builder to consume these files during Phase A.

The mining scripts document how the pool was assembled. Re-fetching current
Wiktionary pages is new research, not reproduction of a fixed snapshot; the
recorded revisions/hashes must be retained. `record-inputs.py` records inputs
for a new research run and must not be used to silently accept changed inputs
when verifying this handoff.
