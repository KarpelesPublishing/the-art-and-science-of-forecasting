# Companion depth upgrade: completed 2026-09-18

The 27 chapter companions now support learning and applying the chapter: a worked
problem, explicit input contract, executable application, interpretation, failure
cases, and three exercises with worked answers. The 27 chapter skills and master
routing skill explain when to use the method, what evidence to request, how to
check it, and what the implemented adapter does and does not automate.

## Delivered

- 27 expanded and freshly executed notebooks, with 81 worked exercises.
- 27 expanded chapter skills, each with workshop and evaluation references.
- A shared `apply` command with chapter-specific CSV/JSON schemas, editable example
  inputs/configurations, diagnostics, explicit assumptions and hashed run records.
- Eight observed-data applications using documented historical temperature and Nile
  datasets; controlled synthetic examples elsewhere. Bundled dataset provenance,
  licensing notes and checksums are recorded in the data registry.
- Improved temporal validation, sparse-data handling, pending-event scoring,
  hierarchy checks, launch assumptions, neural holdouts and output isolation.
- Corrected equal-variance Delphi comparison, CUSUM alarm/reset display and separately
  tuned Prophet calendar comparison. Chapter 27 now also demonstrates historical-data
  routing, sparse-data refusal and an independent capacity bound.
- Rebuilt PDF and EPUB review editions plus a portable companion ZIP.

## Verification

- Automated tests: **105 passed**; five dependency deprecation warnings.
- All **27 notebooks executed successfully** against current source/data/configuration
  hashes, including actual LightGBM, neural, Chronos and Prophet examples.
- Artifact validation: **passed, zero errors**, 27 chapters, 89 figures/captions,
  640 PDF pages. Original chapter source hashes match the manifest.
- EPUBCheck: **zero errors and zero warnings**.
- All 89 figures inspected on eight current grayscale contact sheets. Revised PDF
  pages for figures 8.3, 16.3 and 24.2 inspected at readable size. Automated layout
  scan returned 31 boundary flags, all page-number footers extending 0.286 points
  beyond the conservative scan boundary; no body-text overflow flags.
- Extracted ZIP validated from a new temporary directory. Chapters 4, 10 and 27
  applied workflows passed there, and chapter 4 notebook executed successfully.
  Publication assets were unchanged by applied runs. This uses the existing tested
  interpreter, not a fresh dependency installation on a different operating system.
- Independent code and skill/spec reviews completed; identified issues corrected.
  Selected behavioral skill evaluations were exercised; the 81 reusable evaluation
  scenarios are not claimed as 81 separate agent sessions or human-reader tests.

## Evidence and practical limits

See [chapter coverage](coverage.md), [skill evaluation](skill-evaluation.md),
[content inventory](content-inventory.json), [portability checks](portability.json),
[current validation](../validation.json) and [build provenance](../build.json).

The numerical adapters cover the documented worked workflows, not every professional
technique discussed in each chapter. Synthetic outcomes are teaching evidence, not
business performance claims. Historical observed data are revised snapshots, not
real-time vintages. Forecast intervals and scenario ranges retain their stated limits.

The PDF is a review edition, not a physical-print proof or a certification of every
book statement. The index builder reports 16 entries with omitted targets requiring
editorial review; see [index review](../index-review.json). The visual review above
covers chart sheets and selected changed PDF pages, not a fresh line-by-line proof of
all 640 pages. Earlier audit reports describe earlier builds; this report records the
completed depth upgrade.

Start with [the reader guide](../../START-HERE.md), then choose a chapter or the
[complete forecasting skill](../../../forecasting-skills/all-chapters-forecasting/SKILL.md).
