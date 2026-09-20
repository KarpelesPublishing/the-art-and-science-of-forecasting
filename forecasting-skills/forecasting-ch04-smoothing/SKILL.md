---
name: forecasting-ch04-smoothing
description: "Use when regular demand, workload or revenue series whose recent level, trend and repeating seasonality may forecast the next periods, or studying forecasting book chapter 4."
---

# Chapter 4: The Smoother

## Scope and intake

Use when regular demand, workload or revenue series whose recent level, trend and repeating seasonality may forecast the next periods. Do not use for a new launch with no comparable history, intermittent demand dominated by zeros, or an intervention-effect question.

Ask only for unresolved material inputs: What is the observation frequency and decision horizon? Is demand censored by stockouts? Which seasonal period is plausible? Is the business changing enough that old cycles are misleading?

## Input contract and additional evidence

CSV: timestamp (unique ISO period), target (finite number in consistent units). Config: frequency, horizon, season, as_of, units and source. At least two complete seasonal cycles are needed even to attempt seasonal estimation; reserve further data for evaluation. Zero sales are observations; absent months are missing.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target
2024-01-01,100
2024-02-01,110
2024-03-01,105
```

## Executable interface

Exact CLI columns: `timestamp,target`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `horizon,season,frequency,as_of`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

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

With one seasonal cycle, use naive or a defensible seasonal-naive comparison and mark seasonality estimation unsupported. For gaps, report the cause and perform training-only imputation or shorten the usable series; do not turn unknown sales into zeros. Without evaluation history, supply an explicitly provisional forecast and scenarios. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Forecast table: timestamp,forecast,model,lower,upper,interval_level,empirical_q10,empirical_q50,empirical_q90. Report the measured coverage of lower/upper at the selection origins beside the nominal level; never quote the nominal level alone. Also return a per-origin MAE table, skipped-method reasons, seasonal assumptions and whether uncertainty was calibrated or only scenarized. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 4 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 4 to monthly demand.csv for the next six months. Audit gaps and stockouts, compare supported smoothing methods at earlier six-month origins, retain a final holdout, and return the forecast plus a defensible uncertainty statement.”

The [notebook](../../companion/notebooks/04-smoothing.ipynb) is a worked lesson; its editable [source](../../companion/lessons/04-smoothing.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 4
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch04.csv) and [editable config](../../companion/configs/ch04.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 4 \
  --input companion/data/examples/ch04.csv \
  --config companion/configs/ch04.json \
  --output companion/applied-runs/ch04-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,forecast,model`, `summary.json` containing `selected,validation,validation_predictions,test_mae,intervals`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
