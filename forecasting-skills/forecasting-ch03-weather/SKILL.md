---
name: forecasting-ch03-weather
description: "Use when seasonal structure or sensitivity to initial conditions needs to be understood before choosing a forecast, or studying forecasting book chapter 3."
---

# Chapter 3: The Weather That Could Be Computed

## Scope and intake

Use when seasonal structure or sensitivity to initial conditions needs to be understood before choosing a forecast. Do not use for operational weather prediction from the Lorenz teaching system.

Ask only for unresolved material inputs: What interval is sampled? Which seasonal periods are physically or commercially plausible? Is the goal descriptive decomposition or future forecasting? Are current state estimates uncertain?

## Input contract and additional evidence

CSV timestamp,target on a regular unique calendar; metadata frequency, season,units and cutoff. For a dynamics experiment separately specify the equations, initial states and integration tolerance; those are not columns in the business-series CSV.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target
2024-01-01,100
2024-02-01,110
```

## Executable interface

Exact CLI columns: `timestamp,target`. Supported method controls: `as_of, frequency, horizon, season, seed`.

STL is descriptive. At least three seasonal cycles are required. The adapter refits an earlier vintage and reports the maximum historical trend revision; it does not issue a weather or business forecast.

## Applied procedure

1. Check regular spacing, outliers and whether at least two cycles exist for a proposed seasonal period. Plot the history before interpreting its spectrum.
2. For description, fit STL and verify observed equals trend+seasonal+remainder. Label full-sample components retrospective.
3. For forecasting use, refit decomposition entirely within each training origin and compare a seasonal baseline; never use full-series trend or seasonality as precomputed validation features.
4. For a dynamics lesson, perturb initial conditions and vary integration tolerance separately. Explain divergence in model time, keeping numerical approximation error distinct from state uncertainty.

## Diagnostics, selection and uncertainty

A spectral peak may reflect trend, aliasing or limited sample length; detrend and inspect calendar plausibility. Estimated components are not observed causes. Lorenz trajectories do not specify a calibrated business prediction interval.

## Missing evidence and fallback

With irregular sampling, first decide whether calendar aggregation is defensible; do not run a regular-grid FFT uncritically. With too few cycles, use plots and a simple baseline and mark seasonal decomposition provisional.

## Applied report contract

`results.csv` columns: `timestamp,observed,trend,seasonal,remainder`. `summary.json` keys: `max_trend_revision` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return the calendar audit, chosen period and rationale, decomposition table, reconstruction error, and any origin-safe baseline comparison. For dynamics report initial-state and numerical-tolerance assumptions separately.

## Run it

The [notebook](../../companion/notebooks/03-weather.ipynb) is the worked lesson; its editable [source](../../companion/lessons/03-weather.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 3 \
  --input companion/data/examples/ch03.csv \
  --config companion/configs/ch03.json \
  --output companion/applied-runs/ch03-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 3`.

Learning prompt: “Teach me chapter 3 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 3 to audit the seasonality of demand.csv and explain which components are retrospective and which can safely inform future forecasts.”
