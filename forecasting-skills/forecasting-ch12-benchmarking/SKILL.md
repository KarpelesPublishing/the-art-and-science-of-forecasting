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

Exact CLI columns: `timestamp,target`. Supported method controls: `as_of, conformal, country, criterion, frequency, future_regressors, horizon, origins, per_horizon_buckets, periods, pool, regressors, season, seed, transform`. `season` may be `"auto"` or omitted: the data profile then supplies it, and the profile (frequency, gaps, demand class, seasonal periods, outliers, break hint, route) is returned under `profile` in every summary.

Each series runs the companion engine with the pool the data profile recommends when none is declared: `full` for an ordinary series (the chapter 4 smoothing family with an AICc-selected ETS form, Theta, STL+ETS, the chapter 6 ARIMA family with diagnostic differencing, LightGBM on lags when history allows, a median of the top three, an equal ensemble, an inverse-error weighted ensemble, and the naive, seasonal-naive and drift benchmarks); `intermittent` when demand is mostly zeros (Zero, Mean, Croston, SBA, TSB, ADIDA, IMAPA, scored on RMSSE and cumulative error, never MAE on zeros); `multiseasonal` when the profile finds two cycles (MSTL with ETS or ARIMA, Fourier-term ARIMA, Prophet, TBATS when statsforecast is installed); `regressors` when driver columns are declared (`regressors: [...]` plus `future_regressors`, a path or rows giving the drivers for exactly the next horizon periods: regression with ARIMA errors, LightGBM with the drivers at the target date and calendar terms, Prophet with regressors); `foundation` on request (Chronos tiny cached; Chronos-Bolt small, about 190 MB, and TimesFM 2.5, about 800 MB, download only with FORECAST_ALLOW_DOWNLOADS=1; Moirai is not offered because its package pins an older torch than the rest of the environment). `per_horizon_buckets: true` selects one model for the near steps (1 to ceil(h/2)) and another for the far steps and names the model per row; `criterion` selects on `mae` (default), `mase`, `rmsse` or `pinball`; a candidate that loses to the baseline at more than half the origins can never be selected, and if all do, the baseline is selected and the interpretation says so. Validation includes MAE, RMSE, MASE, RMSSE, cumulative error and pinball at up to five origins plus a final untouched holdout; interval coverage is measured for every model that produces intervals, and split-conformal bands from the selected model's origin residuals are added as `conformal_lower/upper`. Gaps the profile judges small are filled for fitting (interpolated, or zero for intermittent demand) and never scored; larger gaps are refused with the reason. Candidates whose optional package is missing are listed under `unavailable` with the install hint; `requirements-best.lock` (a second environment, `.venv-best`) holds the tested set with statsforecast, mlforecast, hierarchicalforecast, neuralforecast and timesfm, at pandas 2 because statsforecast and mlforecast do not yet support pandas 3. Conformal bands pool the selected model's origin residuals with its final-holdout residuals (never used for selection) and raise the rank level for the finite sample; the summary reports the pool size, the effective level, and the origin-only band's measured coverage on the holdout. No pooled business-weight ranking or formal significance test is produced. Short valid histories (fewer than 2 seasons + 4 horizons) return a provisional persistence baseline and say how many points are missing.

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

`results.csv` columns: `timestamp,forecast,model,empirical_q10,empirical_q50,empirical_q90,conformal_lower,conformal_upper,band_lower,band_upper`. `summary.json` keys: `profile,gaps_filled,pool,selected,criterion,baseline,forced_baseline,robustness,unavailable,conformal,conformal_test_coverage,selected_by_bucket,band_method,band_note,conformal_m,conformal_level_effective,transform,specification,origins,horizon,season,leaderboard,validation,validation_predictions,test_mae,test_interval_coverage,skipped,executed,evaluation,intervals` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return prediction-level records, per-series/per-origin/per-horizon losses, weighting rules, coverage and failed-fit counts, baseline comparisons and final-selection separation.

## Run it

The [notebook](../../companion/notebooks/12-benchmarking.ipynb) is the worked lesson; its editable [source](../../companion/lessons/12-benchmarking.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. [self-check.md](references/self-check.md) holds the three questions to answer before reporting. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

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
