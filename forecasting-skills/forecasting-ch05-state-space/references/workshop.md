# Chapter 5 workshop: from lesson to decision

## Explain the mechanism

The Kalman gain is a precision tradeoff. A noisy sensor gets less weight; a volatile state makes the previous estimate less reliable. The filter uses information through now; a smoother uses later observations to reconstruct the past.

## Work through the arithmetic

Prior m=10,P=4, process Q=1 and measurement R=5 give predicted variance 5 and gain .5. Seeing z=14 updates m to 12 and P to 2.5. One-step future state variance is 3.5; future observation variance is 8.5. Using 3.5 for a measurement interval would omit sensor noise.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace observed in the filter block; retain truth only for controlled simulation. Record missing measurements explicitly and skip their update. The supplied source uses fixed Q,R; changing them requires documenting how they were estimated or specifying sensitivity scenarios.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: What latent state is being measured? What are measurement units and timing? How were process variance Q and measurement variance R estimated? Are missing observations or changing sensor quality expected?

## Interpret the actual lesson outputs

The latent truth line exists because the example is simulated. Its filter and smoother RMSE comparison is not available from ordinary sensor readings alone. The 95% shaded band belongs to the online filter, not the smoother. Noise-sensitivity coverage uses one dependent path and does not certify deployment calibration.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,kind,estimate,lower,upper (kind is filtered, smoothed or forecast)`.
- `summary.json`: `model,seasonal,cycle,params,llf,missing_count,missing_timestamps,ljung_box_p,validation,test_mae,horizon` plus method, interpretation, assumptions, not_done and status.

The tool fits a statsmodels unobserved-components model with the chosen level dynamics, optional seasonal and cycle components, and missing observations handled by the Kalman filter; it returns the filtered level (past data only), the smoothed level (all data, retrospective) with 80 percent bands, and an `horizon`-step forecast with its interval, plus the estimated variances, log likelihood, the timestamps that were missing, a Ljung-Box test on second-half standardised innovations, and a rolling check at `origins` expanding origins against the last observed value. Regression effects and non-Gaussian filters are not attempted. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

The [fixture](../../../companion/data/examples/ch05.csv) and [config](../../../companion/configs/ch05.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Check innovation bias, correlation and variance against assumptions. Large residuals do not automatically increase the gain when Q,R are fixed. State intervals and observation intervals answer different questions; real latent-state coverage cannot be measured without independent truth.

At a missing measurement perform prediction only and let uncertainty grow. Without known Q,R use sensitivity cases or train-only estimation, not the generator’s hidden truth. If linear/Gaussian assumptions fail, route to a separately implemented richer state model.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,kind,estimate,lower,upper (kind is filtered, smoothed or forecast)`; `summary.json` keys: `model,seasonal,cycle,params,llf,missing_count,missing_timestamps,ljung_box_p,validation,test_mae,horizon` plus method, interpretation, assumptions, not_done and status. Never present the smoothed path as what could have been known at the time; the filtered path is the real-time estimate.

## Three exercises with worked solutions

### Exercise 1

Predicted variance 9 and R=3: gain?

**Worked solution.** 9/(9+3)=.75, so three quarters of the innovation updates the state.

### Exercise 2

What happens to uncertainty during two missing readings with Q=2?

**Worked solution.** Without updates, state variance increases by 4.

### Exercise 3

Can lower smoothed RMSE justify replacing recorded online predictions?

**Worked solution.** No. Smoothing uses later measurements; preserve the forecasts actually available at each origin.

## Business-reader application

Use this request with the skill:

> Use chapter 5 to track the latent level in readings.csv, explain Q and R, retain online predictions and distinguish state uncertainty from observation uncertainty.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Observed-data transfer exercise

A bundled [observed series](../../../companion/data/observed/annual-nile.csv) and [matching config](../../../companion/configs/ch05-observed.json) provide a second application after the controlled fixture. Read the [data registry](../../../companion/data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 5 \
  --input companion/data/observed/annual-nile.csv \
  --config companion/configs/ch05-observed.json \
  --output companion/applied-runs/ch05-observed-reader
```

Inspect the standardized-innovation diagnostic and explain whether the local-level model leaves persistent structure. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.
