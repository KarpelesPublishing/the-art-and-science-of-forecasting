---
name: forecasting-ch05-state-space
description: "Use when a noisy measurement must track a latent changing level online, or studying forecasting book chapter 5."
---

# Chapter 5: The Filter

## Scope and intake

Use when a noisy measurement must track a latent changing level online. Do not use for using a retrospective smoother as if available in real time, or calling a scalar filter a full structural Bayesian model.

Ask only for unresolved material inputs: What latent state is being measured? What are measurement units and timing? How were process variance Q and measurement variance R estimated? Are missing observations or changing sensor quality expected?

## Input contract and additional evidence

A regular series of at least 30 observed values; the target cell may be empty where an observation is missing, and the filter carries the state across the gap. `model` is `local level`, `local linear trend`, `smooth trend` or `local_level_manual` (the hand-rolled filter with fixed `Q` and `R`, complete data only). Set `seasonal` true to add a seasonal component with period `season`, and `cycle` for a stochastic cycle.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target
2010-01-01,41.3
2010-02-01,
2010-03-01,44.9
```

## Executable interface

Exact CLI columns: `timestamp,target (empty target allowed)`. Supported method controls: `Q, R, as_of, cycle, frequency, horizon, model, origins, season, seasonal, seed, stochastic_cycle`.

The tool fits a statsmodels unobserved-components model with the chosen level dynamics, optional seasonal and cycle components, and missing observations handled by the Kalman filter; it returns the filtered level (past data only), the smoothed level (all data, retrospective) with 80 percent bands, and an `horizon`-step forecast with its interval, plus the estimated variances, log likelihood, the timestamps that were missing, a Ljung-Box test on second-half standardised innovations, and a rolling check at `origins` expanding origins against the last observed value. Regression effects and non-Gaussian filters are not attempted.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Write the state and measurement equations: x[t]=x[t-1]+noise(Q), z[t]=x[t]+noise(R). Set initial state uncertainty from earlier evidence.
2. Before each measurement, predict mean and variance P+Q. Compute innovation z-m and its variance P+Q+R.
3. Update with K=(P+Q)/(P+Q+R), m=m+K(z-m), P=(1-K)(P+Q). Log predictions before updates.
4. Inspect standardized innovations and compare noise assumptions using earlier validation data. Forecast latent states with variance P+hQ; add R when forecasting a future measurement.
5. Run backward smoothing only as a retrospective analysis and label its access to later observations.

## Diagnostics, selection and uncertainty

Check innovation bias, correlation and variance against assumptions. Large residuals do not automatically increase the gain when Q,R are fixed. State intervals and observation intervals answer different questions; real latent-state coverage cannot be measured without independent truth.

## Missing evidence and fallback

At a missing measurement perform prediction only and let uncertainty grow. Without known Q,R use sensitivity cases or train-only estimation, not the generator’s hidden truth. If linear/Gaussian assumptions fail, route to a separately implemented richer state model.

## Applied report contract

`results.csv` columns: `timestamp,kind,estimate,lower,upper`. `summary.json` keys: `model,seasonal,cycle,params,llf,missing_count,missing_timestamps,ljung_box_p,validation,test_mae,horizon` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Never present the smoothed path as what could have been known at the time; the filtered path is the real-time estimate.

## Run it

The [notebook](../../companion/notebooks/05-state-space.ipynb) is the worked lesson; its editable [source](../../companion/lessons/05-state-space.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 5 \
  --input companion/data/examples/ch05.csv \
  --config companion/configs/ch05.json \
  --output companion/applied-runs/ch05-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 5`.

Learning prompt: “Teach me chapter 5 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 5 to track the latent level in readings.csv, explain Q and R, retain online predictions and distinguish state uncertainty from observation uncertainty.”
