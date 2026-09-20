---
name: forecasting-ch12-benchmarking
description: "Use when forecast methods need a fair chronological benchmark across series, origins and horizons, or studying forecasting book chapter 12."
---

# Chapter 12: The Competition

## Scope and intake

Use when forecast methods need a fair chronological benchmark across series, origins and horizons. Do not use for claiming a global method ranking from one convenient synthetic panel.

Ask only for unresolved material inputs: What horizon and loss match the decision? Which series and origins define deployment? Are weights business volume weights or equal-series weights? Is there an untouched final test?

## Input contract and additional evidence

CSV timestamp,target and optional series_id; unique timestamp per series with regular frequency. Config horizon,season,origins and aggregation weights. Every compared method must face the same eligible targets. The rolling comparison needs 2 seasons + 4 horizons of history (72 monthly points for a 12-month horizon, 48 for six months, 36 for three); with less, the tool returns a provisional persistence baseline and says how many points are missing.

Minimal **format illustration**, not sufficient training data:

```csv
series_id,timestamp,target
A,2025-01-01,100
A,2025-02-01,104
B,2025-01-01,20
```

## Executable interface

Exact CLI columns: `timestamp,target`. Supported method controls: `as_of, frequency, horizon, origins, pool, season, seed, transform`.

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

If histories differ, report the common eligible evaluation subset and separately report deployment coverage. If MASE scale is zero, flag it and use an unscaled metric rather than adding an arbitrary epsilon. With few origins, report descriptive results without broad superiority claims.

## Applied report contract

`results.csv` columns: `timestamp,forecast,model,empirical_q10,empirical_q50,empirical_q90`. `summary.json` keys: `pool,selected,transform,specification,origins,horizon,season,leaderboard,validation,validation_predictions,test_mae,test_interval_coverage,skipped,executed,evaluation,intervals` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return prediction-level records, per-series/per-origin/per-horizon losses, weighting rules, coverage and failed-fit counts, baseline comparisons and final-selection separation.

## Run it

The [notebook](../../companion/notebooks/12-benchmarking.ipynb) is the worked lesson; its editable [source](../../companion/lessons/12-benchmarking.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 12 \
  --input companion/data/examples/ch12.csv \
  --config companion/configs/ch12.json \
  --output companion/applied-runs/ch12-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 12`.

Learning prompt: “Teach me chapter 12 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 12 to build a common rolling-origin benchmark for panel.csv, retain prediction-level records and compare methods under explicit business weights.”
