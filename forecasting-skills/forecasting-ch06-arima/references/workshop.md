# Chapter 6 workshop: from lesson to decision

## Explain the mechanism

AR terms use past values; MA terms use past innovations. Integration describes accumulated change requiring differencing. Seasonal versions add dependence at calendar lags. Order selection and forecast validation are separate tasks.

## Work through the arithmetic

For levels [100,103,105], differences are [3,2]. If the last difference is 2 and its AR(1) coefficient is .6 with zero drift, next expected difference is 1.2 and next expected level is 106.2. The second future difference is .72, making the two-step level 106.92.

## Adapt the lesson to reader data

Replace generated y before train/test splitting. For the separate seasonal experiment replace seasonal_y and choose a justified seasonal period. Orders in the teaching source are prespecified from its generator; do not claim they were automatically discovered for user data.

For this chapter, settle these questions before fitting: What is the target frequency and forecast horizon? Are trends deterministic or accumulated shocks? What seasonality exists? Will any future regressors actually be known?

## Interpret the actual lesson outputs

ADF and ACF/PACF use training differences. The forecast chart’s band is nominal model uncertainty. The separate seasonal comparison reports three origins at a twelve-step horizon and does not implement VAR, cointegration or GARCH.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,forecast,model,empirical_q10,empirical_q50,empirical_q90,lower,upper,interval_level,conformal_lower,conformal_upper,band_lower,band_upper`.
- `summary.json`: `profile,gaps_filled,pool,selected,criterion,baseline,forced_baseline,robustness,unavailable,conformal,conformal_test_coverage,selected_by_bucket,band_method,band_note,conformal_m,conformal_level_effective,transform,specification,origins,horizon,season,leaderboard,validation,validation_predictions,test_mae,test_interval_coverage,skipped,executed,evaluation,intervals` plus method, interpretation, assumptions, not_done and status.

The adapter runs the companion engine with the `arima` pool: naive, seasonal naive, drift, ARIMA(0,1,1), ARIMA(1,1,0), the airline model ARIMA(0,1,1)(0,1,1)s, and an AICc-selected seasonal ARIMA whose regular differencing comes from repeated KPSS tests and whose seasonal differencing comes from STL seasonal strength, searched over p,q in 0–2 and P,Q in 0–1 on the first training slice. A log transform is chosen on training data when the series asks for it. Up to five expanding origins select the model; a final untouched holdout scores it once; model intervals are produced and their validation coverage is measured. Short valid histories return a provisional naive baseline and optional seasonal-naive scenario, with no claimed validation.

## Decide what the evidence supports

White residuals do not rule out nonlinear predictability. Differencing can remove useful structure or induce noise when excessive. Intervals depend on parameter/model assumptions and should be assessed by horizon on held-out origins.

With a short series use naive or low-order candidates and mark seasonal fitting unsupported. For calendar gaps, audit the measurement process before imputation. If regressors are unknown, show conditional forecasts or omit the regressor model.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,forecast,model,empirical_q10,empirical_q50,empirical_q90,lower,upper,interval_level,conformal_lower,conformal_upper,band_lower,band_upper`; `summary.json` keys: `profile,gaps_filled,pool,selected,criterion,baseline,forced_baseline,robustness,unavailable,conformal,conformal_test_coverage,selected_by_bucket,band_method,band_note,conformal_m,conformal_level_effective,transform,specification,origins,horizon,season,leaderboard,validation,validation_predictions,test_mae,test_interval_coverage,skipped,executed,evaluation,intervals` plus method, interpretation, assumptions, not_done and status. Return differencing/order rationale, fit warnings, origin-by-horizon benchmark losses, residual diagnostics, dated forecasts and model-interval assumptions.

## Three exercises with worked solutions

### Exercise 1

Levels 10,13,12: first differences?

**Worked solution.** 3 and -1.

### Exercise 2

Residual Ljung–Box does not reject. Is the chosen model proven optimal?

**Worked solution.** No. The test concerns a particular residual dependence diagnostic and has limited power; compare future losses.

### Exercise 3

A future promotion variable becomes known only after the forecast date. May its realized value be used?

**Worked solution.** No. Use the schedule actually known at the origin or label a conditional scenario.

## Business-reader application

Use this request with the skill:

> Apply chapter 6 to sales.csv with a twelve-period horizon, compare supported ARIMA and seasonal-naive candidates at earlier origins, and explain selection and residual limitations.

## Observed-data transfer exercise

A bundled [observed series](../../../companion/data/observed/monthly-temperature.csv) and [matching config](../../../companion/configs/ch06-observed.json) provide a second application after the controlled fixture. Read the [data registry](../../../companion/data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 6 \
  --input companion/data/observed/monthly-temperature.csv \
  --config companion/configs/ch06-observed.json \
  --output companion/applied-runs/ch06-observed-reader
```

Compare seasonal and nonseasonal candidates without changing their orders after viewing the final test. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
