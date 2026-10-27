# Examples v5 — Phase A work plan

Spec: the user's Phase A1/A2 request, 2026-10-27. Work alone; no agents,
no push, no app-data integration. Baseline: v1.11.0,
`cceba8b696feb5dce1fb7caa233653aa05775b48`, after
`git pull --rebase origin main`; local branch `examples-v5`.

- [x] Read handoffs 3/4 and DATA/TESTING; snapshot the 1,409 missing words
  and applicable JMdict senses in `missing-words.json`.
- [x] A1: verify primary-source licences; mine attributed, unmodified
  sentences up to 35 Unicode characters; review sense, completeness and
  Vietnamese; write `licensed-candidates.json` and `sources-checked.md`.
- [x] A2: personally compose Japanese and Vietnamese for remaining IDs,
  with explicit 1-based JMdict sense index/gloss, actual target surface and
  specific rationale; prefer <=25 characters. Write `authored.json`.
- [x] Run the pinned fugashi/UniDic analyzer and conservative ruby routine;
  record matches, ambiguity and exceptions without modifying runtime tools.
- [x] Validate coverage, source text/IDs, senses, translations, ruby and
  preservation; self-review all rows, write `phaseA-report.md`, mirror
  deliverables to `/workspace/japanese/ex5`, and commit only `ex5/` locally.

Canonical versioned artifacts live in repository `ex5/`; the requested
absolute handoff directory receives identical copies. Large downloaded
corpora and extraction scratch stay under `.cache/ex5/` and are not committed.

Review focus: homographs/senses; sentence fragments; quoted literary text
with separate rights; implicit machine translation; uncertain compound
readings. Analyzer agreement does not constitute native editorial review.

Execution decisions: the detailed user specification and autonomous-work
instruction replace additional design approval. The explicit no-agent rule
also applies to final review. No release/browser gates are needed because
runtime and published data remain byte-identical; run the relevant offline
checks and the existing unit suite.
