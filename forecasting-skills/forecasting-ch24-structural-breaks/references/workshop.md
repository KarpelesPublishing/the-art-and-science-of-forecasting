# Chapter 24 workshop: from lesson to decision

## Explain the mechanism

A detector accumulates evidence that the existing model no longer fits. It does not identify the cause. Operational value depends on what happens after an alarm and on the costs of both needless changes and delayed adaptation.

## Work through the arithmetic

For k=.5, threshold h=3 and standardized residuals [1,2,2], CUSUM values before reset are [.5,2,3.5]. The third observation triggers an alarm; the next update starts from zero under a resetting policy. Drawing a continuous line from 3.5 without showing the reset can misrepresent the detector.

## Adapt the lesson to reader data

Replace the generated series while preserving the initial training and subsequent monitoring split. Plot alarm markers and reset-aware paths. The original lesson used an illustrative threshold and no alarm-triggered override; the applied interface must explicitly report which calibration and policies it actually runs.

For this chapter, settle these questions before fitting: What stable period can calibrate the detector? What false-alarm burden is tolerable? Which errors are available online? What action follows the first alarm? Could the anomaly be bad data?

## Interpret the actual lesson outputs

The original controlled level shift occurs at period 100. Its frozen/rolling/expanding curves use past observations. A resetting detector can produce many later alarms, so the first post-break delay and the action after that alarm matter more than raw alarm count alone.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,actual,frozen,rolling,expanding,adaptive,cusum_before_reset,alarm,rolling_mean,rolling_var,mean_shift_sd,variance_ratio,segment_id`.
- `summary.json`: `threshold,alarm_count,alarms,changepoints,changepoint_positions,best_split,detection,drift,mae,best_policy,calibration_size` plus method, interpretation, assumptions, not_done and status.

The tool dates mean shifts by binary segmentation with a Gaussian cost and a penalty of three times log(n) times a robust noise variance (about a one percent false split rate on white noise), reports the strongest single split with its Welch t statistic, runs a two-sided CUSUM alarm calibrated by simulation to a five percent false-alarm probability over the monitored span, tracks rolling mean and variance against the calibration window as standardised drift metrics, and scores four adaptation policies after the calibration window: frozen calibration mean, rolling mean over `rolling_window`, expanding mean, and an alarm-adaptive mean that restarts at each alarm. Detection delay is the gap between the first dated changepoint and the first alarm after it. Variance-only changes appear in the drift metrics but are not dated. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Decide what the evidence supports

Repeated alarms after resets are not independent discoveries. An iid-normal calibration is conditional on that null model; serial correlation changes false-alarm behavior. Fast adaptation can overreact to temporary outliers. Threshold performance and forecast-policy performance are different outcomes.

Without a plausible stable calibration period, report exploratory alarms with no controlled false-alarm claim. If no response policy was implemented, state that monitoring alone was evaluated. Missing observations require an explicit skip/elapsed-time treatment.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,actual,frozen,rolling,expanding,adaptive,cusum_before_reset,alarm,rolling_mean,rolling_var,mean_shift_sd,variance_ratio,segment_id`; `summary.json` keys: `threshold,alarm_count,alarms,changepoints,changepoint_positions,best_split,detection,drift,mae,best_policy,calibration_size` plus method, interpretation, assumptions, not_done and status. Quote the detection delay with the alarm count; a monitor that fires eleven times after one break has not found eleven breaks, it has kept a stale reference mean.

## Three exercises with worked solutions

### Exercise 1

S=1,z=-2,k=.5: next S?

**Worked solution.** max(0,1-2-.5)=0.

### Exercise 2

An alarm at period 50 leads to refitting including y50. When can the revised forecast first be available?

**Worked solution.** After observing period 50, for period 51 or later; never retroactively for period 50.

### Exercise 3

A threshold was simulated under iid normal noise. Is its false-alarm rate guaranteed under autocorrelated demand?

**Worked solution.** No. Validate under an appropriate dependent null or disclose the calibration mismatch.

## Business-reader application

Use this request with the skill:

> Apply chapter 24 to monitored_series.csv, predeclare threshold calibration and post-alarm action, and compare false alarms, delay and forecasting costs honestly.

## Observed-data transfer exercise

A bundled [observed series](../../../companion/data/observed/annual-nile.csv) and [matching config](../../../companion/configs/ch24-observed.json) provide a second application after the controlled fixture. Read the [data registry](../../../companion/data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 24 \
  --input companion/data/observed/annual-nile.csv \
  --config companion/configs/ch24-observed.json \
  --output companion/applied-runs/ch24-observed-reader
```

Inspect first and repeated alarms, and distinguish a historical regime-change signal from evidence of its cause. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
