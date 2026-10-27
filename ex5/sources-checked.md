# Examples v5 — sources checked

Checked on **2026-10-27**, for Phase A only. The sentence-level decisions and
attribution are in [licensed-candidates.json](licensed-candidates.json).
Exact input bytes, URLs and SHA-256 hashes are recorded in
[input-manifest.json](input-manifest.json). No app data has been changed.

| Source | Decision | Licence used | Selected word/example rows |
|---|---|---|---:|
| Named Tatoeba text, including longer sentences | Include after individual review | CC BY 2.0 FR | 373 |
| JMdict example edition / Tanaka | Cross-reference Tatoeba; not an independent corpus | Sentence: CC BY 2.0 FR; dictionary metadata: CC BY-SA 4.0 | 33 selected rows also have JMdict example references |
| Japanese Wiktionary original usage examples | Include simple, revision-pinned usage lines | CC BY-SA 4.0 | 12 |
| Japanese Wikipedia dump | Available; no direct bulk extraction selected | Current text: CC BY-SA 4.0, subject to source exceptions | 0 directly |
| KFTT 1.0, Wikipedia-derived | Include reviewed original Japanese lines | CC BY-SA 3.0 | 332 |
| Kyoto–NTT Blog Corpus, KNBC 1.0 | Include reviewed complete sentences | BSD three-clause terms in Japanese | 8 |
| JParaCrawl | Exclude | Research/information-analysis restrictions | 0 |
| Kyoto University Text Corpus / Mainichi | Exclude original newspaper text | No general sentence redistribution grant established | 0 |
| Kyoto University Web Document Leads Corpus | Exclude | No underlying web-text permissions or original URLs supplied | 0 |

Counts are word/example associations, not necessarily unique Japanese strings.
All 725 selected licensed rows have a source, source ID, URL, author/contributors,
licence and licence URL. Each Japanese sentence is copied without rewriting;
Wiktionary markup removal and KNBC token reconstruction are explicitly recorded.

## Tatoeba, Tanaka and JMdict examples

Tatoeba's [corpus reuse policy](https://en.wiki.tatoeba.org/articles/show/using-the-tatoeba-corpus)
specifies the default **CC BY 2.0 FR** text licence and requires naming the author.
The [licence](https://creativecommons.org/licenses/by/2.0/fr/) permits copying,
adaptation and redistribution with attribution. Audio has different terms and
was not used. The supplied detailed exports have no per-row licence column;
this phase retains the documented default text licence, as the existing repo
does, and rejects ownerless rows rather than inventing authors.

The existing local `jpn.tsv`, `vie.tsv`, `eng.tsv` and `links.csv` were read only.
The miner inspected 148,831 named Japanese sentences; 141,737 met the lexical
scan's 4–35-character/punctuation and exclusion rules. It found 3,016 matching
word/sentence pairs covering 506 missing IDs before editorial review. The old
pipeline's 25-character ceiling was raised to **35**, without truncation.
Among the 373 selected Tatoeba rows, **116** exceed 25 characters; **65** pass
the reconstructed old eligibility rules except for length. The other longer
rows also needed a spelling alias or removal of the linked-translation gate.
These reasons remain in `original_rejection_reasons`, not just a length flag.

The [EDRDG Tanaka documentation](https://www.edrdg.org/wiki/Tanaka_Corpus.html)
explains that Tanaka entered Tatoeba in 2006 and that a linked subset has been
included in the JMdict example edition since 2021. It also describes known
quality problems. The original historical collection was therefore not treated
as a fresh, independently vetted pool.

Downloaded and parsed the official
[JMdict example XML](https://www.edrdg.org/pub/Nihongo/JMdict_e_examp.gz):
32,364 example associations overall, including 962 associations for the missing
words' JMdict entries. The supplied `jmdict-eng-3.6.2.json` has **no example field**;
its absence does not mean these sentences were never used. The app already has
6,935 Tatoeba examples using 5,793 distinct sentence IDs. Fourteen IDs in the
962-association subset already occur in app examples for other words. Of this
phase's selected Tatoeba rows, 28 reuse IDs already serving another app word;
33 rows, representing 31 distinct IDs, also have exact-text JMdict example
references. Every target ID in this phase was previously empty.

Sentence ownership is taken from the named Tatoeba export, not attributed to
JMdict as if it authored the Japanese. Selected senses use the original 1-based
index in the **2026-10-26 JMdict snapshot**, independently of the example XML's
sense associations. The JMdict-derived spellings, readings and sense glosses
are copyright James William Breen and EDRDG, under
[CC BY-SA 4.0 and the EDRDG attribution conditions](https://www.edrdg.org/edrdg/licence.html).

Existing human Vietnamese is preserved exactly when available: **27 rows**,
with its own sentence ID, username, URL and links. Five have optional
`vi_refinement` suggestions marked machine; these do not replace `vi`.
The other **698 licensed rows** have Vietnamese translated directly from
Japanese by this assistant, explicitly marked `machine: true`. Adapted
translations retain the source licence; share-alike translations are not
relabelled as unrestricted original text.

## Japanese Wiktionary and Wikipedia

The current [Japanese Wiktionary copyright policy](https://ja.wiktionary.org/wiki/Wiktionary:著作権)
offers its own text under **CC BY-SA 4.0**, also GFDL where applicable. This is
not a blanket licence for quoted books or other separately copyrighted material.
This phase uses the CC route and excludes cited literary quotations, templates,
external links and complex usage lines.

Both official dump directories are available:
[jawiktionary](https://dumps.wikimedia.org/jawiktionary/latest/) and
[jawiki](https://dumps.wikimedia.org/jawiki/latest/). The checked listings show
2026-10-01 `pages-articles.xml.bz2` files of 94,439,126 bytes and 4,757,398,424
bytes respectively, as well as multistream files and checksum manifests.
Direct shell access returned HTTP 403 during research; this was an access
failure in this session, **not evidence that the dumps do not exist**. No full
dump is claimed as downloaded or processed.

Instead, the [Wiktionary API](https://ja.wiktionary.org/w/api.php) supplied fixed
revisions for relevant kanji/kana titles. Inspected 2,216 existing pages and
1,139 Japanese usage lines. The extractor rejected 521 complex/quoted lines
and 243 length/fragment cases before matching; 57 matching associations were
then available for manual selection. The 12 selected rows retain title, page
ID, revision ID/timestamp, source line, original wikitext, permanent revision
URL and history link. Contributors are credited through those links.

Extraction is reliable only for this narrow subset: remove list/bold/link
markup, retain the Japanese wording, then inspect the sentence and selected
sense. A naive dump-wide regular expression cannot reliably resolve templates,
citations, language sections, infoboxes or sentence boundaries. Direct
Wikipedia extraction was not selected; Wikipedia-derived KFTT provides a
smaller, sentence-aligned corpus with explicit release terms. This is not a
claim that all usable Wikipedia examples have been exhausted. Wikimedia's
[reuse terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use)
govern attribution, changes and share-alike requirements for current text.

## KFTT 1.0

Downloaded the official [KFTT archive](https://www.phontron.com/kftt/download/kftt-data-1.0.tar.gz)
from the [task site](https://www.phontron.com/kftt/). Its README explicitly
licenses all data under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).
A verbatim copy is retained in [licences/KFTT-README.txt](licences/KFTT-README.txt).
The archive contains Japanese Wikipedia-derived text and NICT translations,
prepared for the task by Graham Neubig.

Scanned **443,849 original Japanese lines** across train/dev/test/tune;
159,396 passed the short-sentence filter, yielding 22,465 matching associations.
Only `data/orig/*.ja` was used, never tokenized text. Each selected row preserves
the archive URL, exact member path, 1-based line number, corresponding original
English, contributor/task attribution and CC BY-SA 3.0 licence. The English is
reference material; the new Vietnamese was composed from Japanese.

The distributed files do not give a per-line original Wikipedia article title
or revision. Attribution therefore identifies the **released KFTT corpus and
exact archive line**, with Japanese Wikipedia contributors, NICT and the task
creator; it does not fabricate an article URL or claim a reconstructed edit
history. This is a limitation of the source metadata to preserve in any later
integration. Historical subjects and implicit antecedents make this corpus
most useful at N1/N2; names, incomplete lists and wrong senses were rejected.

## Kyoto University corpora

**KNBC included.** The [Kyoto–NTT project page](https://nlp.ist.i.kyoto-u.ac.jp/kuntt/)
describes 249 blog articles with 4,186 sentences. The downloaded
[2009-09-25 archive](https://nlp.ist.i.kyoto-u.ac.jp/kuntt/KNBC_v1.0_090925.tar.bz2)
contains the commissioned student texts and a copyright notice for Kyoto
University Graduate School of Informatics, Kurohashi Laboratory. Its Japanese
three-clause BSD terms permit redistribution and modification, requiring the
notice, conditions and disclaimer and prohibiting implied endorsement.
The **complete original README**, including those terms, is preserved in
[licences/KNBC-README.txt](licences/KNBC-README.txt); no invented English licence
text substitutes for it.

Reconstructed sentences from annotated surface tokens, preserving wording.
Files referring to split parenthetical material were skipped to avoid silently
omitting clauses: 725 skipped files, 3,462 inspected sentence files, 2,068
length-eligible, 94 matching associations, **8 selected**. These file counts
include corpus segmentation details and should not be equated with the headline
4,186 count. Each selected sentence retains its S-ID and exact archive member.
The released material does not name individual student authors, so attribution
uses the named copyright holder and KNBC contributors rather than guessed names.

**Kyoto University Text Corpus excluded.** The official
[KyotoCorpus README](https://github.com/ku-nlp/KyotoCorpus)
says the repository contains annotations, not original sentences; reconstructing
them requires the Mainichi 1995 CD-ROM. Annotation availability is not permission
to redistribute the underlying news prose.

**KWDLC excluded.** The official
[KWDLC README](https://github.com/ku-nlp/KWDLC)
says the underlying web-document permissions were not obtained and original
URLs are not provided. This fails the requested redistributable-sentence and
per-sentence attribution requirements, regardless of public download access.

## JParaCrawl excluded

The [official NTT terms, Article 1](https://www.kecl.ntt.co.jp/icl/lirg/jparacrawl/)
restrict use to research involving information analysis, apply the same
restriction to derived data, and require separate contact for commercial use.
They allow replication/distribution **within that restricted purpose**; it
would be inaccurate to say redistribution is categorically forbidden.
General learner-facing example redistribution is not established by that
grant. No JParaCrawl text was downloaded into or selected for this deliverable.

## Selection result and scope

The combined candidate pool covered 1,025 missing IDs. After individual source,
sense and readability review, licensed sentences were selected for **725**.
The remaining **684** received authored examples: 300 had mined matches that
were not selected, and 384 had no pooled match. This is a documented finite
search, not a claim that no other redistributable example exists online.

The assistant reviewed all final Japanese/Vietnamese pairs. Neither corpus
availability nor analyzer agreement is native-speaker certification. Detailed
analysis exceptions, validation and the stop point are in
[phaseA-report.md](phaseA-report.md). Sentence licences, JMdict metadata terms
and UniDic-derived analysis terms remain separate; no blanket licence replaces
the individual source grants.

The frozen missing-word inventory also retains existing project metadata;
its original attributions remain documented in [data/SOURCES.md](../data/SOURCES.md).
UniDic-derived reading evidence retains the BSD terms documented there. This
phase does not relicense the repository's existing vocabulary, pitch or audio.
