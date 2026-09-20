---
name: forecasting-ch04-smoothing
description: "Use when regular demand, workload or revenue series whose recent level, trend and repeating seasonality may forecast the next periods, or studying forecasting book chapter 4."
---

# Chapter 4: The Smoother

## Scope and intake

Use when regular demand, workload or revenue series whose recent level, trend and repeating seasonality may forecast the next periods. Do not use for a new launch with no comparable history, intermittent demand dominated by zeros, or an intervention-effect question.

Ask only for unresolved material inputs: What is the observation frequency and decision horizon? Is demand censored by stockouts? Which seasonal period is plausible? Is the business changing enough that old cycles are misleading?

## Input contract and additional evidence

CSV: timestamp (unique ISO period), target (finite number in consistent units). Config: frequency, horizon, season, as_of, units and source. At least two complete seasonal cycles are needed even to attempt seasonal estimation; reserve further data for evaluation. The rolling comparison needs 2 seasons + 4 horizons of history (72 monthly points for a 12-month horizon, 48 for six months, 36 for three); with less, the tool returns a provisional persistence baseline and says how many points are missing. Zero sales are observations; absent months are missing.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target
2024-01-01,100
2024-02-01,110
2024-03-01,105
```

## Executable interface

Exact CLI columns: `timestamp,target`. Supported method controls: `as_of, conformal, country, criterion, frequency, future_regressors, horizon, origins, per_horizon_buckets, periods, pool, regressors, season, seed, transform`. `season` may be `"auto"` or omitted: the data profile then supplies it, and the profile (frequency, gaps, demand class, seasonal periods, outliers, break hint, route) is returned under `profile` in every summary.

The adapter runs the companion engine with the `smoothing` pool: naive, seasonal naive, drift, SES, Holt, damped Holt, an AICc-selected ETS form (additive or multiplicative error and seasonality, damped or not), Theta and STL+ETS. A log transform is chosen on training data when positive values and a Box-Cox lambda near zero call for it (`transform: auto|none|log`). Up to five expanding origins (`origins`) select the model on MAE; a final untouched holdout scores it once; the selection is refitted on all history. Output carries the model's nominal 80% interval with its measured validation coverage, plus empirical residual quantiles by horizon step. Optional `pool` overrides the method set. A short but valid regular series returns status=provisional with naive and, when available, seasonal-naive scenario values rather than pretending a model was validated.

## Applied procedure

1. Parse and sort the dates; check the calendar for gaps, duplicates, returns and stockout periods. Plot values and seasonal profiles before choosing additive or multiplicative components.
2. Reserve a final contiguous horizon. Within earlier data choose several expanding origins with the same operational horizon. Fit every transformation and initialization anew on each training slice.
3. At each origin generate naive and seasonal-naive baselines, then SES, Holt, damped Holt and additive Holt-Winters where data support them. Keep Theta as an optional extra. Record skipped models and fit warnings.
4. Compare MAE by origin and lead time, using the same available actuals. Prefer the simpler method when improvements are inconsistent or negligible for the decision. Select settings on these earlier origins, then score the untouched final horizon once.
5. Refit the selected specification through the as-of cutoff. Export dated forecasts; obtain residual-based intervals only with enough earlier origin errors, keeping horizon-specific errors separate.

## Diagnostics, selection and uncertainty

Inspect seasonal residual patterns, residual bias and parameter estimates at boundaries. A low fitted SSE is not selection evidence. Never force multiplicative seasonality onto zeros or negative values. Long trends need a damping sensitivity. Backtested marginal coverage is evidence for the tested horizons, not a guarantee after a break.

## Missing evidence and fallback

With one seasonal cycle, use naive or a defensible seasonal-naive comparison and mark seasonality estimation unsupported. For gaps, report the cause and perform training-only imputation or shorten the usable series; do not turn unknown sales into zeros. Without evaluation history, supply an explicitly provisional forecast and scenarios.

## Applied report contract

`results.csv` columns: `timestamp,forecast,model,empirical_q10,empirical_q50,empirical_q90,lower,upper,interval_level,conformal_lower,conformal_upper,band_lower,band_upper`. `summary.json` keys: `profile,gaps_filled,pool,selected,criterion,baseline,forced_baseline,robustness,unavailable,conformal,conformal_test_coverage,selected_by_bucket,band_method,band_note,conformal_m,conformal_level_effective,transform,specification,origins,horizon,season,leaderboard,validation,validation_predictions,test_mae,test_interval_coverage,skipped,executed,evaluation,intervals` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Report the measured coverage of lower/upper at the selection origins beside the nominal level; never quote the nominal level alone. Also return a per-origin MAE table, skipped-method reasons, seasonal assumptions and whether uncertainty was calibrated or only scenarized.

## Run it

The [notebook](../../companion/notebooks/04-smoothing.ipynb) is the worked lesson; its editable [source](../../companion/lessons/04-smoothing.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. [self-check.md](references/self-check.md) holds the three questions to answer before reporting. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 4 \
  --input companion/data/examples/ch04.csv \
  --config companion/configs/ch04.json \
  --output companion/applied-runs/ch04-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 4`.

Learning prompt: “Teach me chapter 4 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 4 to monthly demand.csv for the next six months. Audit gaps and stockouts, compare supported smoothing methods at earlier six-month origins, retain a final holdout, and return the forecast plus a defensible uncertainty statement.”
