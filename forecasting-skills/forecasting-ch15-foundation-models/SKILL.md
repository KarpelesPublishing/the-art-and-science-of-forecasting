---
name: forecasting-ch15-foundation-models
description: "Use when a pretrained time-series model is being evaluated on a new series under a fixed model revision, or studying forecasting book chapter 15."
---

# Chapter 15: The Foundation

## Scope and intake

Use when a pretrained time-series model is being evaluated on a new series under a fixed model revision. Do not use for assuming a foundation model is automatically superior or diagnosing training contamination from pattern similarity alone.

Ask only for unresolved material inputs: Which checkpoint and revision will be fixed? When did the data become public? Are private later data available? What context, horizon and baseline are appropriate? Can the environment run the actual dependency?

## Input contract and additional evidence

A regular series with at least three seasons of history and 30 observations beyond the horizon. `checkpoint` is `tiny` (cached, pinned revision) by default; `mini` (about 80 MB), `small` (about 185 MB) and `base` (about 800 MB) download weights on first use, so state the size and get the reader's agreement before choosing one.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target
2010-01-01,41.3
2010-02-01,41.8
2010-03-01,44.9
```

## Executable interface

Exact CLI columns: `timestamp,target`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, checkpoint, frequency, horizon, origins, quantiles, samples, season, seed`. Unknown config keys are rejected.

The tool runs Chronos-T5 zero-shot in a separate worker process (so it can share a session with LightGBM), sampling `samples` paths and reporting the requested `quantiles` at `origins` expanding origins plus the untouched final holdout: median MAE, coverage of the outer quantile band and latency per call. It runs the engine's baseline pool (naive, seasonal naive, drift, equal ensemble) at exactly the same origins and reports both leaderboards side by side, then issues the future forecast from full history. No fine-tuning, no covariates, and no certification that the series was absent from pretraining.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Freeze dataset vintage, evaluation origins and checkpoint revision before final evaluation. Document what is unknown about pretraining overlap.
2. Create context-only input windows at each origin and run the real pinned inference pipeline. Record package/model versions and any device or sampling settings.
3. Generate forecast samples/quantiles and compare with naive or seasonal-naive on identical horizons and contexts.
4. Assess MAE and interval scores/coverage on later cases. Compare latency and resource requirements when they affect use.
5. Keep checkpoint selection or fine-tuning outside the final evaluation; mark unimplemented covariate or adaptation capabilities explicitly.

## Diagnostics, selection and uncertainty

A frozen model avoids local fitting leakage but may still have unknown pretraining exposure. A contamination toy is not evidence of contamination in a particular checkpoint. Sample quantiles have Monte Carlo error; few cases cannot establish a broad ranking.

## Missing evidence and fallback

If downloads or the dependency are unavailable, return baseline forecasts and an explicit not-run status for the foundation model. Never substitute a generic smoother and call it Chronos. If overlap is unknown, preserve the uncertainty and prioritize later private data. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

`results.csv` columns: `timestamp,forecast,q10,q50,q90 (one column per requested quantile)`. `summary.json` keys: `checkpoint,model_id,revision,download_warning,origins,per_origin,engine_baselines,test_mae,test_coverage,mean_latency_s,quantiles,samples` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`. Report the pretrained model beside the seasonal naive at the same origins; a model that does not beat the seasonal naive on this series has not earned the download. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 15 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 15 to benchmark the pinned foundation model on demand.csv with frozen origins, honest dependency status and matched baseline and interval scores.”

The [notebook](../../companion/notebooks/15-foundation-models.ipynb) is a worked lesson; its editable [source](../../companion/lessons/15-foundation-models.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 15
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch15.csv) and [editable config](../../companion/configs/ch15.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 15 \
  --input companion/data/examples/ch15.csv \
  --config companion/configs/ch15.json \
  --output companion/applied-runs/ch15-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,lower,forecast,upper`, `summary.json` containing `revision,test_mae,baseline_mae,test_coverage`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
