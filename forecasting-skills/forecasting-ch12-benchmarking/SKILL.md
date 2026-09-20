---
name: forecasting-ch12-benchmarking
description: "Use when forecast methods need a fair chronological benchmark across series, origins and horizons, or studying forecasting book chapter 12."
---

# Chapter 12: The Competition

## Scope and intake

Use when forecast methods need a fair chronological benchmark across series, origins and horizons. Do not use for claiming a global method ranking from one convenient synthetic panel.

Ask only for unresolved material inputs: What horizon and loss match the decision? Which series and origins define deployment? Are weights business volume weights or equal-series weights? Is there an untouched final test?

## Input contract and additional evidence

CSV timestamp,target and optional series_id; unique timestamp per series with regular frequency. Config horizon,season,origins and aggregation weights. Every compared method must face the same eligible targets.

Minimal **format illustration**, not sufficient training data:

```csv
series_id,timestamp,target
A,2025-01-01,100
A,2025-02-01,104
B,2025-01-01,20
```

## Executable interface

Exact CLI columns: `timestamp,target`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, frequency, horizon, origins, pool, season, seed, transform`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

Each series independently runs the companion engine with the `full` pool: the chapter 4 smoothing family with an AICc-selected ETS form, Theta, STL+ETS, the chapter 6 ARIMA family with diagnostic differencing, LightGBM on lags when history allows, a median of the top three, an equal ensemble, and the naive, seasonal-naive and drift benchmarks. Validation includes MAE, RMSE and training-scaled MASE at up to five origins plus a final untouched holdout; interval coverage is measured for every model that produces intervals. No pooled business-weight ranking or formal significance test is produced. Short valid histories return a provisional naive baseline and optional seasonal-naive scenario; these are not validated model comparisons.

## Applied procedure

1. Define the evaluation population, horizons, losses and series weights before inspecting model results. Freeze final evaluation dates.
2. Construct expanding or rolling training windows; fit each method and transformation only before its origin. Include naive, seasonal-naive and a fixed equal-weight combination when eligible.
3. Save predictions at series×origin×horizon granularity, with actuals attached only for scoring. Record failures rather than silently dropping a difficult method’s cases.
4. Compute MAE, RMSE and MASE using training-only scales. Compare both aggregate losses and distributions across series and origins.
5. Choose methods or weights on earlier validation data, then evaluate the frozen policy on later data. Explain sensitivity to weighting and dependence rather than treating every overlapping error as independent.

## Diagnostics, selection and uncertainty

MAE is unit-dependent; RMSE emphasizes large misses. Seasonal MASE divides by training seasonal-naive absolute differences, not held-out naive error. Zero scale makes MASE undefined. Overlapping origins and related series weaken naive significance calculations.

## Missing evidence and fallback

If histories differ, report the common eligible evaluation subset and separately report deployment coverage. If MASE scale is zero, flag it and use an unscaled metric rather than adding an arbitrary epsilon. With few origins, report descriptive results without broad superiority claims. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return prediction-level records, per-series/per-origin/per-horizon losses, weighting rules, coverage and failed-fit counts, baseline comparisons and final-selection separation. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 12 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 12 to build a common rolling-origin benchmark for panel.csv, retain prediction-level records and compare methods under explicit business weights.”

The [notebook](../../companion/notebooks/12-benchmarking.ipynb) is a worked lesson; its editable [source](../../companion/lessons/12-benchmarking.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 12
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch12.csv) and [editable config](../../companion/configs/ch12.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 12 \
  --input companion/data/examples/ch12.csv \
  --config companion/configs/ch12.json \
  --output companion/applied-runs/ch12-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,forecast,model (plus series_id for a panel)`, `summary.json` containing `selected,validation,validation_predictions,test_mae,intervals; per-series summaries for a panel`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
