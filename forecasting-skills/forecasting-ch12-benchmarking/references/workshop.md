# Chapter 12 workshop: from lesson to decision

## Explain the mechanism

A benchmark is an experimental design. Common target dates, equal information and frozen selection rules matter as much as the error formula. An ensemble is a candidate; averaging is not a guarantee of improvement.

## Work through the arithmetic

Actuals [10,20] with forecasts [12,16] give errors [2,4], MAE=3 and RMSE=sqrt(10)=3.162. If the training seasonal-naive scale is 2, MASE=1.5. That 1.5 does not compare directly with a held-out naive forecast unless its actual held-out loss is separately calculated.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace the generated panel with sorted grouped series. Recompute each scale inside its training window. Keep the lesson’s per-horizon error array structure or an equivalent long table; averaging too early hides cases and makes fair alignment hard to audit.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: What horizon and loss match the decision? Which series and origins define deployment? Are weights business volume weights or equal-series weights? Is there an untouched final test?

## Interpret the actual lesson outputs

The relative-error chart uses 100×(method MAE/seasonal-naive MAE-1), so negative is better and zero ties that origin’s baseline. The boxplot shows per-series heterogeneity. These synthetic seasonal series are not an M-competition reproduction.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,forecast,model (plus series_id for a panel)`.
- `summary.json`: inspect `selected,validation,validation_predictions,test_mae,intervals; per-series summaries for a panel`.

Each series independently runs the companion engine with the `full` pool: the chapter 4 smoothing family with an AICc-selected ETS form, Theta, STL+ETS, the chapter 6 ARIMA family with diagnostic differencing, LightGBM on lags when history allows, a median of the top three, an equal ensemble, and the naive, seasonal-naive and drift benchmarks. Validation includes MAE, RMSE and training-scaled MASE at up to five origins plus a final untouched holdout; interval coverage is measured for every model that produces intervals. No pooled business-weight ranking or formal significance test is produced. Short valid histories return a provisional naive baseline and optional seasonal-naive scenario; these are not validated model comparisons.

The [fixture](../../../companion/data/examples/ch12.csv) and [config](../../../companion/configs/ch12.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

MAE is unit-dependent; RMSE emphasizes large misses. Seasonal MASE divides by training seasonal-naive absolute differences, not held-out naive error. Zero scale makes MASE undefined. Overlapping origins and related series weaken naive significance calculations.

If histories differ, report the common eligible evaluation subset and separately report deployment coverage. If MASE scale is zero, flag it and use an unscaled metric rather than adding an arbitrary epsilon. With few origins, report descriptive results without broad superiority claims.

The applied deliverable must make these items inspectable: Return prediction-level records, per-series/per-origin/per-horizon losses, weighting rules, coverage and failed-fit counts, baseline comparisons and final-selection separation.

## Three exercises with worked solutions

### Exercise 1

Method MAE=8, baseline MAE=10: relative gap?

**Worked solution.** 100×(8/10-1)=-20%, a 20% lower MAE on those matched cases.

### Exercise 2

Training seasonal-naive error scale is zero. What is MASE?

**Worked solution.** Undefined, not zero. Flag it and report an appropriate unscaled metric.

### Exercise 3

Weights are tuned using the final test. Is it still a final test?

**Worked solution.** No. It became selection data; evaluate the frozen combination on later untouched cases.

## Business-reader application

Use this request with the skill:

> Use chapter 12 to build a common rolling-origin benchmark for panel.csv, retain prediction-level records and compare methods under explicit business weights.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Observed-data transfer exercise

A bundled [observed series](../../../companion/data/observed/monthly-temperature.csv) and [matching config](../../../companion/configs/ch12-observed.json) provide a second application after the controlled fixture. Read the [data registry](../../../companion/data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 12 \
  --input companion/data/observed/monthly-temperature.csv \
  --config companion/configs/ch12-observed.json \
  --output companion/applied-runs/ch12-observed-reader
```

Explain why a ranking on this one observed series does not establish an across-industry ranking. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.
