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

Exact CLI columns: `timestamp,target`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, frequency, horizon, season, seed`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

STL is descriptive. At least three seasonal cycles are required. The adapter refits an earlier vintage and reports the maximum historical trend revision; it does not issue a weather or business forecast.

## Applied procedure

1. Check regular spacing, outliers and whether at least two cycles exist for a proposed seasonal period. Plot the history before interpreting its spectrum.
2. For description, fit STL and verify observed equals trend+seasonal+remainder. Label full-sample components retrospective.
3. For forecasting use, refit decomposition entirely within each training origin and compare a seasonal baseline; never use full-series trend or seasonality as precomputed validation features.
4. For a dynamics lesson, perturb initial conditions and vary integration tolerance separately. Explain divergence in model time, keeping numerical approximation error distinct from state uncertainty.

## Diagnostics, selection and uncertainty

A spectral peak may reflect trend, aliasing or limited sample length; detrend and inspect calendar plausibility. Estimated components are not observed causes. Lorenz trajectories do not specify a calibrated business prediction interval.

## Missing evidence and fallback

With irregular sampling, first decide whether calendar aggregation is defensible; do not run a regular-grid FFT uncritically. With too few cycles, use plots and a simple baseline and mark seasonal decomposition provisional. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return the calendar audit, chosen period and rationale, decomposition table, reconstruction error, and any origin-safe baseline comparison. For dynamics report initial-state and numerical-tolerance assumptions separately. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 3 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 3 to audit the seasonality of demand.csv and explain which components are retrospective and which can safely inform future forecasts.”

The [notebook](../../companion/notebooks/03-weather.ipynb) is a worked lesson; its editable [source](../../companion/lessons/03-weather.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 3
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch03.csv) and [editable config](../../companion/configs/ch03.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 3 \
  --input companion/data/examples/ch03.csv \
  --config companion/configs/ch03.json \
  --output companion/applied-runs/ch03-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,observed,trend,seasonal,remainder`, `summary.json` containing `max_trend_revision`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
