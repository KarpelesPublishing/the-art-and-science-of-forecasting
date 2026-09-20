---
name: forecasting-ch24-structural-breaks
description: "Use when forecast residuals may signal a structural break and adaptation policies need explicit evaluation, or studying forecasting book chapter 24."
---

# Chapter 24: The Anomaly

## Scope and intake

Use when forecast residuals may signal a structural break and adaptation policies need explicit evaluation. Do not use for tuning an alarm threshold on the very break used to claim detection success.

Ask only for unresolved material inputs: What stable period can calibrate the detector? What false-alarm burden is tolerable? Which errors are available online? What action follows the first alarm? Could the anomaly be bad data?

## Input contract and additional evidence

A regular series with at least 80 observations. `calibration_size` names the opening window believed to be a stable regime; the CUSUM mean and standard deviation come from it, so choose it before looking at the later data. Seasonal series should be deseasonalised first, or the seasonal swings will be dated as breaks.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target
1871-01-01,1120
1872-01-01,1160
1873-01-01,963
```

## Executable interface

Exact CLI columns: `timestamp,target`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, calibration_size, drift_window, frequency, horizon, max_breaks, min_segment, rolling_window, season, seed`. Unknown config keys are rejected.

The tool dates mean shifts by binary segmentation with a Gaussian cost and a penalty of three times log(n) times a robust noise variance (about a one percent false split rate on white noise), reports the strongest single split with its Welch t statistic, runs a two-sided CUSUM alarm calibrated by simulation to a five percent false-alarm probability over the monitored span, tracks rolling mean and variance against the calibration window as standardised drift metrics, and scores four adaptation policies after the calibration window: frozen calibration mean, rolling mean over `rolling_window`, expanding mean, and an alarm-adaptive mean that restarts at each alarm. Detection delay is the gap between the first dated changepoint and the first alarm after it. Variance-only changes appear in the drift metrics but are not dated.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Define a frozen baseline from earlier stable observations and record one-step predictions before seeing actuals. Check data-quality explanations for unusual errors.
2. Standardize residuals using training estimates. Set the detector threshold on separate stable data or a disclosed simulation law, targeting a stated false-alarm measure.
3. Update a one-sided CUSUM S=max(0,S+z-k); alarm when it crosses the threshold and apply the declared reset. Store pre-reset and post-reset values clearly.
4. Define the operational response: investigate, monitor, retrain or temporarily switch. Do not use the current observation in a prediction purportedly issued before it.
5. Compare frozen, rolling, expanding and implemented alarm-triggered policies on untouched streams, scoring stable-period costs, detection delay and post-break losses.

## Diagnostics, selection and uncertainty

Repeated alarms after resets are not independent discoveries. An iid-normal calibration is conditional on that null model; serial correlation changes false-alarm behavior. Fast adaptation can overreact to temporary outliers. Threshold performance and forecast-policy performance are different outcomes.

## Missing evidence and fallback

Without a plausible stable calibration period, report exploratory alarms with no controlled false-alarm claim. If no response policy was implemented, state that monitoring alone was evaluated. Missing observations require an explicit skip/elapsed-time treatment. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

`results.csv` columns: `timestamp,actual,frozen,rolling,expanding,adaptive,cusum_before_reset,alarm,rolling_mean,rolling_var,mean_shift_sd,variance_ratio,segment_id`. `summary.json` keys: `changepoints,changepoint_positions,best_split,threshold,alarm_count,alarms,detection,drift,mae,best_policy,calibration_size` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`. Quote the detection delay with the alarm count; a monitor that fires eleven times after one break has not found eleven breaks, it has kept a stale reference mean. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 24 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 24 to monitored_series.csv, predeclare threshold calibration and post-alarm action, and compare false alarms, delay and forecasting costs honestly.”

The [notebook](../../companion/notebooks/24-structural-breaks.ipynb) is a worked lesson; its editable [source](../../companion/lessons/24-structural-breaks.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 24
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch24.csv) and [editable config](../../companion/configs/ch24.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 24 \
  --input companion/data/examples/ch24.csv \
  --config companion/configs/ch24.json \
  --output companion/applied-runs/ch24-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,actual,frozen,rolling,adaptive,cusum_before_reset,alarm`, `summary.json` containing `threshold,alarm_count,mae`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
