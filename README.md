# The Art and Science of Forecasting: Companion

**Free companion to *The Art and Science of Forecasting: Prediction Methods for Time Series, Predictive Analytics, Probability, AI, Machine Learning, and Making Better Decisions in the Age of AI* by Jason Karpeles.**

Every chapter of the book has a runnable lesson and an AI skill behind it. This repository holds all of them: 27 executed Jupyter notebooks, a forecasting engine and 27 chapter tools with rolling-origin validation, 27 chapter skills plus one integrated skill for guiding an AI assistant, a batch forecaster for thousands of series, and the desk model from chapters 20 and 27 that forecasts a new product before it has sold a unit.

- Book website, errata and updates: <https://karpeles.com/publishing/the-art-and-science-of-forecasting>
- New reader: start with [companion/START-HERE.md](companion/START-HERE.md)
- Technical setup and reproduction: [companion/README.md](companion/README.md)
- Using the skills with an AI assistant: [forecasting-skills/all-chapters-forecasting/SKILL.md](forecasting-skills/all-chapters-forecasting/SKILL.md)

This repository does not contain the book text. It contains the code, data, figures and instructions the book refers to.

---

## Contents

1. [What is here](#what-is-here)
2. [Quick start](#quick-start)
3. [The three ways to use the companion](#the-three-ways-to-use-the-companion)
4. [Chapter by chapter](#chapter-by-chapter)
5. [The forecasting engine](#the-forecasting-engine)
6. [The chapter tools](#the-chapter-tools)
7. [The skills](#the-skills)
8. [The launch desk model: reconcile-tdbu](#the-launch-desk-model-reconcile-tdbu)
9. [Forecasting many series at once](#forecasting-many-series-at-once)
10. [Data and provenance](#data-and-provenance)
11. [Repository layout](#repository-layout)
12. [Requirements](#requirements)
13. [Tests and verification](#tests-and-verification)
14. [Design principles](#design-principles)
15. [Contributing and support](#contributing-and-support)
16. [License and citation](#license-and-citation)

---

## What is here

| Piece | What it is | Where |
|---|---|---|
| 27 notebooks | One executed lesson per chapter: explanation, editable inputs, code, charts, results. Each ends with an applied workshop that runs the chapter's tool on an example file. | `companion/notebooks/` (sources in `companion/lessons/`) |
| 92 figures | Every figure printed in the book, as PNG, PDF and SVG, with the code that drew it. | `companion/figures/` |
| Forecasting engine | Rolling-origin model selection over smoothing, ARIMA, Theta, STL, LightGBM and combinations, with intervals and measured coverage. | `companion/src/forecasting_companion/engine.py` |
| 27 chapter tools | One executable per chapter behind a single command line, each validating its inputs, scoring itself at rolling origins where a forecast is produced, and recording what it did not do. | `companion/src/forecasting_companion/applied/` |
| Batch forecaster | Forecasts a CSV of many series in parallel with resume, per-series metrics and quantile bands. | `companion/src/forecasting_companion/batch.py` |
| 27 chapter skills | Instructions an AI assistant follows to apply one chapter's method properly: intake questions, method rules, the exact input contract of the chapter tool, and evaluation scenarios. | `forecasting-skills/forecasting-chNN-*/` |
| Complete Forecasting Skill | The integrated entry point that frames a forecasting question and routes it to the chapters it needs. | `forecasting-skills/all-chapters-forecasting/` |
| reconcile-tdbu | The launch desk model: interviews for six inputs, runs a trial-and-repeat engine and a market-share engine, reports the gap between them and reconciles it. Also packaged as `reconcile-tdbu.skill`. | `forecasting-skills/reconcile-tdbu/` |
| Example data and configs | A synthetic example and a JSON configuration for every chapter, plus seven public-domain observed series. | `companion/data/`, `companion/configs/` |
| Tests | 137 tests covering the engine, every tool, the batch runner, the practitioner workflows and every chapter's example. | `companion/tests/` |

## Quick start

Python 3.12 is the tested target.

```bash
git clone https://github.com/KarpelesPublishing/the-art-and-science-of-forecasting.git
cd the-art-and-science-of-forecasting/companion
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.lock        # pinned; includes the model extras
.venv/bin/python scripts/run.py chapters --chapter 4   # execute one lesson end to end
.venv/bin/python -m pytest tests -q                   # about two minutes
```

Open any notebook in `companion/notebooks/` with Jupyter, or read them rendered on GitHub. To run every lesson and regenerate every figure:

```bash
.venv/bin/python scripts/run.py chapters --all --profile complete
```

The `complete` profile includes the LightGBM, Prophet, neural and Chronos chapters (13 to 16); `core` skips them. The Chronos chapter uses the tiny checkpoint, pinned to a specific revision and cached on first run.

## The three ways to use the companion

**1. Read and run a lesson.** Each notebook follows its chapter: the idea, a worked example on synthetic data whose generating process is stated, the failure mode the chapter warns about, and an applied workshop that runs the chapter's tool on a bundled example. Every number in the book's figures comes from these notebooks; the execution record for each is in `companion/results/`.

**2. Apply a chapter to your own data.** One command line serves all 27 chapters:

```bash
.venv/bin/python scripts/run.py apply --chapter 18 \
    --input my-hierarchy.csv --config my-config.json --output applied-runs/my-hierarchy
```

It writes `results.csv`, `summary.json`, `diagnostic.png` and `run.json` (a provenance record of code, data and environment). The input columns each chapter expects and the configuration keys it accepts are listed in that chapter's skill under *Executable interface*; unknown configuration keys are rejected rather than ignored. Every `summary.json` carries the same five keys: `method`, `interpretation`, `assumptions`, `not_done` (what the chapter discusses that this run did not do) and `status` (`passed`, `provisional` or `needs_evidence`).

**3. Direct an AI assistant.** Point an assistant that supports skills (Claude Code, Codex and others read `SKILL.md` files) at this repository and ask, for example:

> Use $all-chapters-forecasting to forecast my sales data for the next 12 months, compare suitable methods, and report uncertainty and validation results.

The skill frames the target (units, horizon, as-of date, decision costs, what is known in advance), routes to the chapters that fit, runs the chapter tools only when you agree the method fits, and reports assumptions, validation and what was not done. `scripts/install_skills.py` links the 29 skill folders into `.agents/skills/` for runtimes that discover skills there. The skills never run anything on their own; they tell the assistant how.

## Chapter by chapter

Titles are the book's. The tool column is what `run.py apply --chapter N` executes; every tool validates at rolling origins where a forecast is produced and names its own limits.

| Ch | Chapter | Notebook | What the tool does |
|---|---|---|---|
| 1 | The Market Discovers the Future | `01-markets` | OHLC audit; predeclared persistence, momentum and mean-reversion rules at expanding origins; directional hit rates with a binomial test against a coin; Benford first-digit check. Price error only, never a trading return. |
| 2 | The Mathematics of Belief | `02-belief` | Beta-binomial updating with prior-strength sensitivity. |
| 3 | The Weather That Could Be Computed | `03-weather` | STL decomposition and component revision across data vintages. |
| 4 | The Smoother | `04-smoothing` | The engine's smoothing pool: SES, Holt, damped Holt, AICc-selected ETS, seasonal naive; rolling comparison, final holdout, refit. |
| 5 | The Filter | `05-state-space` | Unobserved-components state space (local level, linear or smooth trend, optional seasonal and cycle) with missing observations; filtered versus smoothed states; interval forecasts; rolling check against the last value. |
| 6 | The Unexpected Route | `06-arima` | The engine's ARIMA pool: KPSS and seasonal-strength differencing, AICc grid, the airline model, diagnostics on training residuals. |
| 7 | The Casino at Los Alamos | `07-monte-carlo` | Dependent cost simulation; Metropolis chain with four-chain posterior diagnostics. |
| 8 | The Delphi Room | `08-delphi` | Round-level medians, spread and forecast value added across Delphi rounds. |
| 9 | The Oracle Problem | `09-expert-scoring` | Brier scores on common events, reliability bins with counts, calibration versus resolution. |
| 10 | The Superforecaster | `10-superforecasting` | Forecast journal: revision eligibility, pending events, one eligible pre-resolution forecast per event, scoring against a recorded baseline. |
| 11 | The Crowd and the Ox | `11-crowds` | Mean, median and trimmed-mean aggregation; learned weights evaluated on later events; logit extremization scored by Brier for probability pools. |
| 12 | The Competition | `12-benchmarking` | The full engine: every candidate at common origins, MAE, RMSE and MASE leaderboard, per-horizon records, combinations as candidates. |
| 13 | The Walmart War Room | `13-retail-ml` | LightGBM direct or recursive multi-step on lags, rolling means, calendar and declared covariates at expanding origins; seasonal-naive baseline; feature-group ablation; SHAP with an additivity check. |
| 14 | The Globalizer | `14-global-neural` | Global Gaussian MLP trained across entities, held-out entities, sampled predictive paths, coverage by horizon. |
| 15 | The Foundation | `15-foundation-models` | Chronos-T5 zero-shot at a chosen checkpoint, scored at the engine's own origins beside the baseline pool; sampled quantiles, coverage, latency. Larger checkpoints download only on request. |
| 16 | The Prophet | `16-prophet` | Prophet with a declared event table and future regressors; changepoint prior grid at earlier origins; ablation without events and without regressors; holdout MAE and coverage. |
| 17 | Living with Probability | `17-probabilistic` | Split and adaptive conformal intervals around the engine's selection; interval score and pinball loss on a test block; comparison with the model's own band. |
| 18 | The Hierarchy | `18-hierarchy` | Summing matrix from child-parent edges; per-node engine forecasts; bottom-up, OLS and shrunk-covariance MinT reconciliation with a holdout leaderboard; optional coherent quantiles. |
| 19 | Frank Bass and the Television | `19-diffusion` | Bass fits per market ceiling with optional fixed q; adoption converted to unit sales under Bass and gamma launch timing with a repeat kernel; Parfitt-Collins share. |
| 20 | The Marketing Mix | `20-marketing-mix` | Adstock and saturation per channel selected on earlier origins; closed-form ridge with controls; holdout against seasonal naive; response curves, marginal response, refit stability, optional Gaussian posterior, budget reallocation scenario. |
| 21 | The Bullwhip | `21-supply-chain` | Croston, SBA and TSB for intermittent demand; bootstrapped order-up-to policy simulation (cycle service, fill rate, on-hand, cost); N-echelon bullwhip with local versus shared demand signal. |
| 22 | The Causal Forecaster | `22-causal` | Difference-in-differences, multi-control OLS counterfactual, synthetic control on a simplex, placebo-in-space and placebo-in-time p-values, event study with pre-trend test. |
| 23 | The Epidemiologist's Dilemma | `23-epidemics` | Reporting-triangle nowcast with a delay law estimated from mature cohorts and negative-binomial bounds; archived evaluation by age; SEIR fitted at rolling origins against persistence. |
| 24 | The Anomaly | `24-structural-breaks` | Binary-segmentation changepoint dating, strongest single split, two-sided calibrated CUSUM, drift metrics, four adaptation policies scored after the calibration window. |
| 25 | Forecasting Your Own Life | `25-reference-classes` | Reference-class ratios with Kaplan-Meier handling of unfinished cases. |
| 26 | How to Be Ready Without Being Certain | `26-decision-readiness` | Cost-sensitive action thresholds and realized costs on a forecast journal. |
| 27 | Giving the Oracle Direction | `27-directed-forecasting` | Routing: the full engine for series with history, a refusal with a persistence baseline for sparse history, and the launch transfer (calibrate on mature products, re-base for the new one, spread trial with the gamma curve, add repeat). |

Chapters 3, 4, 6, 12, 15 and 16 also run on an observed public-domain temperature series and chapters 5 and 24 on the Nile annual flow, with matching `chNN-observed.json` configurations.

## The forecasting engine

`companion/src/forecasting_companion/engine.py` is what the smoothing, ARIMA, benchmarking and directed-forecasting chapters and the batch runner share. For one regular series it:

1. chooses the working scale on training data only (a Box-Cox lambda near zero on positive data selects a log transform);
2. fits a pool of candidates anew at up to five expanding origins before an untouched final holdout: naive, seasonal naive, drift, SES, Holt, damped Holt, AICc-selected ETS, Theta, STL+ETS, an AICc-selected seasonal ARIMA with KPSS and seasonal-strength differencing, the airline model, LightGBM on lags when history allows, a median of the top three, and an equal-weight ensemble;
3. scores every candidate at every origin on MAE, RMSE and training-scaled MASE, and measures the coverage of each model's nominal 80 percent interval;
4. selects on earlier-origin error, scores the selection once on the final holdout, refits on all history and returns point forecasts, the model's own intervals with measured coverage, and empirical residual quantiles by horizon step.

Specifications are frozen on the first training slice, so later actuals cannot influence the choice. The tests prove it by corrupting the holdout and checking that the leaderboard does not move. Pools: `full`, `smoothing` (chapter 4), `arima` (chapter 6), `baseline`.

## The chapter tools

All 27 tools live in `companion/src/forecasting_companion/applied/` and are reached through `methods.analyze(chapter, data, config)` or the `run.py apply` command. They share one contract:

- **Explicit schema.** `core.SCHEMAS` declares each chapter's input columns; `methods.options` declares its configuration keys. Anything else raises before any data is touched.
- **No leakage.** Where a forecast is produced, selection happens at expanding origins and the final holdout is scored once. Origins come from one shared rule (`core.expanding_origins`), so a Chronos run and a baseline run compare at identical dates.
- **Honest summaries.** `core.finish()` guarantees `method`, `interpretation`, `assumptions`, `not_done` and `status`. Tables never contain NaN.
- **Deterministic.** Seeds are fixed; simulated intervals are seeded.
- **Only when asked.** The tools run when a reader or an assistant invokes them. The skills tell the assistant to decide, with the reader, whether the method fits first.

Chapter 15 runs Chronos in a separate worker process so it can share a session with LightGBM (both ship an OpenMP runtime).

## The skills

A skill is a folder with a `SKILL.md` and `references/`. Each chapter skill contains:

- **Applicability and intake questions:** when the method fits and what to ask before running anything.
- **Method rules and safeguards:** the chapter's discipline in checklist form, including what the method cannot establish.
- **Input contract and executable interface:** the exact CSV columns, the accepted configuration keys, what the tool does, what it reports under `not_done`, and the `results.csv` and `summary.json` layout.
- **`references/workshop.md`:** the applied workshop text that also appears in the notebook.
- **`references/evaluation.md`:** scenarios for judging whether the skill was applied well.

`all-chapters-forecasting` is the integrated entry point. It records target, units, horizon, frequency, as-of date, decision costs and which covariates are known in advance, then routes: ordinary series to the engine; gaps and hidden states to chapter 5; covariates to 13; calendars to 16; intervals with guarantees to 17; hierarchies to 18; launches to 19, 20, 25, 27 and `reconcile-tdbu`; attribution to 20; causal questions to 22; inventory to 21; reporting delays to 23; regime change to 24; judgment and probability work to 2, 8 to 11 and 26. Its safeguards survive deadline pressure: baselines before claims, validation before selection, intervals with measured coverage, and a written record of what was not done.

`SKILL-LIBRARY.md` explains the philosophy behind the library: model what has data, estimate what does not, never let an assistant judge a number the data can produce, and always build a second method.

## The launch desk model: reconcile-tdbu

Chapters 20 and 27 describe a way to forecast a packaged-goods launch with no sales history: judged inputs instead of a test market. `forecasting-skills/reconcile-tdbu/` is that model as a skill, with `scripts/reconcile_model.py` as the engine. It:

- interviews for six typed inputs (population, category penetration, purchase frequency, units per purchase, market size, price) and a handful of settings, with defaults and valid ranges in `references/interview-guide.md`;
- derives what a test market would have measured: trial from seven judged attribute scores, awareness from the media plan, share of choice, repeat dynamics and the build curve;
- runs two engines on the same derived quantities: bottom-up (penetration given, market size solved) and top-down (market size given, penetration solved);
- reports the gap between them and what each typed input would have to be for the others to hold, then reconciles by feeding the implied values back until nothing moves;
- sweeps any input for a tornado table.

Every coefficient in it is an illustrative starting value chosen by judgment so that an ordinary launch lands in the right ballpark. None comes from a published study or a client dataset, and all are meant to be tuned to launches you know. `references/model-map.md` lists every formula. The same model is packaged as `reconcile-tdbu.skill` for runtimes that install skills from a single file.

## Forecasting many series at once

```bash
.venv/bin/python scripts/run.py forecast --input data/sales.csv --horizon 12 --frequency MS \
    --workers 4 --resume --engine full --output applied-runs/sales
```

Input columns: `series_id,timestamp,target`. `--engine baseline` (the default) runs the transparent baselines and is right for thousands of series or a first pass; `--engine full`, `smoothing` or `arima` runs the engine pool on every series. Output: `forecast.csv` (quantile rows per horizon step, plus model intervals with the full engine), `metrics.csv` (selected model, transform, validation and holdout MAE, interval coverage, skipped candidates) and `failures.json`. Failures are per series; resume keys cover data, settings, code and library versions.

## Data and provenance

- **Synthetic examples** (`companion/data/examples/`) are generated by `scripts/build_workshop_data.py` from fixed seeds. Their generating processes are stated in the notebooks, so a method's success on them shows the method works when its assumptions hold, and nothing more.
- **Observed series** (`companion/data/observed/`) are public-domain datasets bundled with statsmodels: the Nile annual flow, monthly temperature, El Niño, Grunfeld, macrodata and strikes. `companion/data/registry.json` records source and transformations. These are historical revised snapshots, not archived real-time vintages.
- **Execution records** (`companion/results/`) hold each notebook's run status and content hashes of the code, data and environment it ran with, so a figure can be traced to the exact inputs that produced it.
- **Applied runs** write `run.json` with the same hashes, and `run()` refuses to write into the publication folders.

## Repository layout

```
companion/
  START-HERE.md          reader's guide: what a notebook is, what a skill is, which to use
  README.md              technical setup and reproduction guide
  notebooks/             27 executed notebooks (generated from lessons/)
  lessons/               editable notebook sources, one .py per chapter (# %% cells)
  src/forecasting_companion/
    engine.py            the forecasting engine
    batch.py             many-series runner
    practitioner.py      launch workflows: calibrate_scale, launch_trials, cohort_units, adstock, ...
    reconcile_sim.py     the desk model behind chapters 20 and 27
    applied/             core.py (schemas, contract), methods.py (dispatch), tools_*.py (27 chapter tools)
  scripts/               run.py (chapters | apply | forecast), catalog.py, build_workshop_data.py,
                         expand_workshops.py, install_skills.py, export_public.py
  data/                  examples/ (synthetic), observed/ (public domain), registry.json
  configs/               one JSON configuration per chapter example
  figures/               92 figures as PNG, PDF and SVG
  results/               execution records and figure journals
  tests/                 pytest suite
forecasting-skills/
  all-chapters-forecasting/    the Complete Forecasting Skill and the chapter map
  forecasting-ch01-markets/ ... forecasting-ch27-directed-forecasting/
  reconcile-tdbu/              the launch desk model
SKILL-LIBRARY.md         the philosophy and routing of the skill library
reconcile-tdbu.skill     the desk model packaged as a single skill file
```

## Requirements

- Python 3.12 (`requires-python = ">=3.12,<3.13"`).
- Core: numpy, pandas, scipy, matplotlib, statsmodels, nbformat, nbclient, ipykernel, pymupdf.
- Model extras (chapters 13 to 16): lightgbm, prophet, torch, transformers, chronos-forecasting.
- `requirements.lock` pins the exact versions the notebooks were executed with. Everything runs on CPU; the Chronos tiny checkpoint is about 30 MB and is cached on first use.
- No R, no GPU, no licensed data.

## Tests and verification

```bash
.venv/bin/python -m pytest tests -q
```

The suite covers the engine (selection is frozen before the holdout; pools are distinct; the airline series selects a seasonal model with a log transform and beats seasonal naive), every chapter tool on a synthetic case with a known answer, the batch runner (resume, schema, bands), the practitioner workflows, and every chapter's bundled example through the same `analyze` path the CLI uses. A separate guard asserts that unknown configuration keys are rejected by every chapter.

What the checks establish: that the notebooks ran, that the figures came from that code, and that each tool does what its skill says on data whose truth is known. What they do not establish: that any method fits your data. That judgment is the subject of the book.

## Design principles

1. **Model what has data; estimate what does not.** The launch model and the reference-class chapter are estimation; the engine and the panel tools are modelling. The Complete Forecasting Skill routes between them.
2. **Baselines first.** Nothing is reported as an improvement without a seasonal naive or persistence comparison at the same origins.
3. **Validation before selection.** Rolling origins, one untouched holdout, specifications frozen on the training slice.
4. **Intervals that are measured, not asserted.** Coverage is reported beside every nominal band.
5. **Say what was not done.** Every summary lists it, and the skills require the assistant to repeat it.
6. **Synthetic data is labelled synthetic.** Every figure caption and every example file says so.

## Contributing and support

Issues and pull requests are welcome for bugs, clearer explanations, and additional worked examples. Please keep the contract: new tools go through `core.finish()`, declare their schema and options, validate at rolling origins, and come with a test that has a known answer. Book errata go to the website, not to this repository.

## License and citation

Code, notebooks, skills, data generators and documentation in this repository are released under the [MIT License](LICENSE). The book itself is copyright 2026 Jason Karpeles and is not part of this repository.

If you use the companion in published work, cite the book:

> Karpeles, J. (2026). *The Art and Science of Forecasting: Prediction Methods for Time Series, Predictive Analytics, Probability, AI, Machine Learning, and Making Better Decisions in the Age of AI.* Karpeles Publishing. Companion: https://github.com/KarpelesPublishing/the-art-and-science-of-forecasting
