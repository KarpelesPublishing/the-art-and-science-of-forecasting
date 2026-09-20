# Chapter 3 workshop: from lesson to decision

## Explain the mechanism

Deterministic equations can be sensitive to uncertain starting conditions. Business decomposition asks a related but distinct question: what slowly changing and repeating patterns summarize observations? Neither computation removes uncertainty about whether those patterns persist.

## Work through the arithmetic

If a monthly observation is 120, estimated trend is 100 and seasonal component is 15, the remainder is 5. A spectral frequency 1/12 cycles per month corresponds to a 12-month period. Frequency is reciprocal period, not the number of months itself.

## Adapt the lesson to reader data

Replace seasonal_series in the STL block with the regular user series and update period. Leave Lorenz simulation separate from that business analysis. If using decomposition features in a model, move the STL fit inside the historical-origin loop rather than decomposing once before splitting.

For this chapter, settle these questions before fitting: What interval is sampled? Which seasonal periods are physically or commercially plausible? Is the goal descriptive decomposition or future forecasting? Are current state estimates uncertain?

## Interpret the actual lesson outputs

The Lorenz panels compare initial perturbations against the same reference with shared axes. Their horizontal units are dimensionless. The STL reconstruction assertion checks arithmetic, not forecast quality; the printed dominant frequency describes the controlled series.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,observed,trend,seasonal,remainder`.
- `summary.json`: `max_trend_revision` plus method, interpretation, assumptions, not_done and status.

STL is descriptive. At least three seasonal cycles are required. The adapter refits an earlier vintage and reports the maximum historical trend revision; it does not issue a weather or business forecast.

## Decide what the evidence supports

A spectral peak may reflect trend, aliasing or limited sample length; detrend and inspect calendar plausibility. Estimated components are not observed causes. Lorenz trajectories do not specify a calibrated business prediction interval.

With irregular sampling, first decide whether calendar aggregation is defensible; do not run a regular-grid FFT uncritically. With too few cycles, use plots and a simple baseline and mark seasonal decomposition provisional.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,observed,trend,seasonal,remainder`; `summary.json` keys: `max_trend_revision` plus method, interpretation, assumptions, not_done and status. Return the calendar audit, chosen period and rationale, decomposition table, reconstruction error, and any origin-safe baseline comparison. For dynamics report initial-state and numerical-tolerance assumptions separately.

## Three exercises with worked solutions

### Exercise 1

Frequency is .25 cycles per quarter. What is the period?

**Worked solution.** Four quarters, because 1/.25=4.

### Exercise 2

Can a smoother using next December’s value construct a forecast for this June?

**Worked solution.** No. Full-sample decomposition leaks future observations; refit at June’s cutoff.

### Exercise 3

A changed integration tolerance produces nearly identical short trajectories. Has initial uncertainty vanished?

**Worked solution.** No. That checks numerical stability locally; uncertainty in the true starting state remains.

## Business-reader application

Use this request with the skill:

> Use chapter 3 to audit the seasonality of demand.csv and explain which components are retrospective and which can safely inform future forecasts.

## Observed-data transfer exercise

A bundled [observed series](../../../companion/data/observed/monthly-temperature.csv) and [matching config](../../../companion/configs/ch03-observed.json) provide a second application after the controlled fixture. Read the [data registry](../../../companion/data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 3 \
  --input companion/data/observed/monthly-temperature.csv \
  --config companion/configs/ch03-observed.json \
  --output companion/applied-runs/ch03-observed-reader
```

Inspect max_trend_revision and explain why full-history decomposition cannot supply origin-known features. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
