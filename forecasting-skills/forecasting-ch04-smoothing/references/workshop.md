# Chapter 4 workshop: from lesson to decision

## Explain the mechanism

SES carries one level forward. Holt carries level and slope; damping reduces future slope increments. Holt-Winters adds a repeating seasonal component. These are alternative assumptions about what persists. Choose the memory length by future forecast loss, not by how closely the fitted line hugs history.

## Work through the arithmetic

With previous level 100, observation 120 and alpha=.25, the updated level is .25×120+.75×100=105. That is the next one-step SES forecast, not the forecast that existed before observing 120. With Holt level 105 and slope 4, a three-step forecast is 117. With damping phi=.8 it is 105+4(.8+.64+.512)=112.808.

## Adapt the lesson to reader data

Replace the lesson’s generated y in the level experiment or final seasonal experiment with one regularly indexed observed timestamp,target series, keeping the experiments separate. The small CSV above illustrates syntax only: it is not enough to fit annual seasonality. Set period=12 for monthly annual seasonality only when the calendar and history justify it. The applied adapter now performs the common expanding-origin comparison. Inspect summary.json validation rows and test_mae separately; no additional loop is needed for that supplied comparison.

For this chapter, settle these questions before fitting: What is the observation frequency and decision horizon? Is demand censored by stockouts? Which seasonal period is plausible? Is the business changing enough that old cycles are misleading?

## Interpret the actual lesson outputs

The level-shift curves are updated levels after observing each point. They demonstrate responsiveness, not pre-observation accuracy. The final holdout MAE chart compares only its named methods and uses a favorable seasonal generator. A lower bar supports that method on that holdout. It does not establish a universal ranking. The applied adapter adds a common rolling comparison; inspect its separate validation table rather than attributing that work to the original holdout chart.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,forecast,model,empirical_q10,empirical_q50,empirical_q90,lower,upper,interval_level,conformal_lower,conformal_upper`.
- `summary.json`: `profile,gaps_filled,pool,selected,criterion,baseline,forced_baseline,robustness,unavailable,conformal,conformal_test_coverage,transform,specification,origins,horizon,season,leaderboard,validation,validation_predictions,test_mae,test_interval_coverage,skipped,executed,evaluation,intervals` plus method, interpretation, assumptions, not_done and status.

The adapter runs the companion engine with the `smoothing` pool: naive, seasonal naive, drift, SES, Holt, damped Holt, an AICc-selected ETS form (additive or multiplicative error and seasonality, damped or not), Theta and STL+ETS. A log transform is chosen on training data when positive values and a Box-Cox lambda near zero call for it (`transform: auto|none|log`). Up to five expanding origins (`origins`) select the model on MAE; a final untouched holdout scores it once; the selection is refitted on all history. Output carries the model's nominal 80% interval with its measured validation coverage, plus empirical residual quantiles by horizon step. Optional `pool` overrides the method set. A short but valid regular series returns status=provisional with naive and, when available, seasonal-naive scenario values rather than pretending a model was validated.

## Decide what the evidence supports

Inspect seasonal residual patterns, residual bias and parameter estimates at boundaries. A low fitted SSE is not selection evidence. Never force multiplicative seasonality onto zeros or negative values. Long trends need a damping sensitivity. Backtested marginal coverage is evidence for the tested horizons, not a guarantee after a break.

With one seasonal cycle, use naive or a defensible seasonal-naive comparison and mark seasonality estimation unsupported. For gaps, report the cause and perform training-only imputation or shorten the usable series; do not turn unknown sales into zeros. Without evaluation history, supply an explicitly provisional forecast and scenarios.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,forecast,model,empirical_q10,empirical_q50,empirical_q90,lower,upper,interval_level,conformal_lower,conformal_upper`; `summary.json` keys: `profile,gaps_filled,pool,selected,criterion,baseline,forced_baseline,robustness,unavailable,conformal,conformal_test_coverage,transform,specification,origins,horizon,season,leaderboard,validation,validation_predictions,test_mae,test_interval_coverage,skipped,executed,evaluation,intervals` plus method, interpretation, assumptions, not_done and status. Report the measured coverage of lower/upper at the selection origins beside the nominal level; never quote the nominal level alone. Also return a per-origin MAE table, skipped-method reasons, seasonal assumptions and whether uncertainty was calibrated or only scenarized.

## Three exercises with worked solutions

### Exercise 1

Recalculate the SES update with alpha=.8. What changes?

**Worked solution.** The level is 116. It reacts more quickly to the shock, but this calculation alone says nothing about future accuracy.

### Exercise 2

Actuals are 100,120 and forecasts A=110,110, B=100,100. Compare MAE.

**Worked solution.** A has MAE (10+10)/2=10; B has (0+20)/2=10. Prefer neither on this score alone; examine the decision costs and further origins.

### Exercise 3

You receive eighteen monthly observations with three unknown months. May you report annual Holt-Winters as validated?

**Worked solution.** No. There are not two complete annual cycles, much less a separate evaluation period. Audit missingness, use an eligible simple baseline and disclose the unsupported seasonal fit.

## Business-reader application

Use this request with the skill:

> Apply chapter 4 to monthly demand.csv for the next six months. Audit gaps and stockouts, compare supported smoothing methods at earlier six-month origins, retain a final holdout, and return the forecast plus a defensible uncertainty statement.

## Observed-data transfer exercise

A bundled [observed series](../../../companion/data/observed/monthly-temperature.csv) and [matching config](../../../companion/configs/ch04-observed.json) provide a second application after the controlled fixture. Read the [data registry](../../../companion/data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 4 \
  --input companion/data/observed/monthly-temperature.csv \
  --config companion/configs/ch04-observed.json \
  --output companion/applied-runs/ch04-observed-reader
```

Compare the two validation origins with final-test MAE. Does the selected smoothing method still beat seasonal-naive on the last twelve months? Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
