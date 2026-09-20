# Chapter 13 workshop: from lesson to decision

## Explain the mechanism

Pooled trees learn shared nonlinear relationships across related item-store series. Their advantage comes from useful predictors available at the decision time. Excellent retrospective results can disappear when supposedly predictive columns were only known after the outcome.

## Work through the arithmetic

For demand values 10,12,14 on days 1–3, the day-4 three-day rolling feature is 12. A rolling mean that includes day-4 actual 20 would use [12,14,20], or 15.333, and leak the target. If base prediction 20 and SHAP contributions 3,-1,5 sum to 7, the model output is 27.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace panel construction with series_id mapped to the lesson’s entity key and a consistent time index. Preserve groupby boundaries for all lags. Include store/item fields only if actual metadata supports them; series_id alone does not magically recover that hierarchy. Keep observed-lag updating consistent with the one-step task.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: Is the decision daily one-step replenishment or a fixed-origin horizon? Were promotions and prices known then? Are sales censored by stockouts? What defines a series?

## Interpret the actual lesson outputs

The source runs actual LightGBM and native TreeSHAP on synthetic retail data. Its 28-day folds contain successive one-day forecasts with lag updates, not a 28-day forecast issued once. It does not reproduce M5 hierarchy, WRMSSE or Walmart data.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `series_id,timestamp,horizon,actual,seasonal_naive,prediction`.
- `summary.json`: `strategy,features,feature_groups,covariates,known_in_advance,validation,ablation,test_mae,baseline_mae,first_explanation,origins` plus method, interpretation, assumptions, not_done and status.

LightGBM on leakage-safe grouped features: lags (`lags`), shifted rolling means (`rolling`), a calendar term (day of week for daily data, month otherwise), an entity code, and the declared covariates. `strategy: direct` (default) fits one booster per horizon step, each mapping the origin's lag features plus the target date's known covariates and calendar to that step's target; `recursive` fits a one-step model and feeds its own predictions back as lags. Evaluation uses expanding origins (`origins`) against seasonal naive computed from pre-origin history, then scores the untouched final holdout once. `ablation: true` drops each feature group (calendar, lags, rolling, covariates) in turn at every origin and reports the change in MAE. Additive contributions are returned for `shap_rows` rows with an additivity check. No hyperparameter search, no quantile objective. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

The [fixture](../../../companion/data/examples/ch13.csv) and [config](../../../companion/configs/ch13.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Removing promotion while retaining discount price may leave the same information. Ablate dependent feature groups. Check negative predictions, lag availability and error concentration in sparse series. TreeSHAP allocations among correlated features depend on the model and are not identified marketing effects.

If LightGBM is unavailable, name the skipped model and run an eligible baseline; do not relabel a substitute. If future prices are unknown, use a known schedule or scenarios. If demand is censored, separate observed sales prediction from latent demand estimation.

The applied deliverable must make these items inspectable: `results.csv` columns: `series_id,timestamp,horizon,actual,seasonal_naive,prediction`; `summary.json` keys: `strategy,features,feature_groups,covariates,known_in_advance,validation,ablation,test_mae,baseline_mae,first_explanation,origins` plus method, interpretation, assumptions, not_done and status. State which covariates were treated as known in advance; a forecast that assumes next month's price is known must say so.

## Three exercises with worked solutions

### Exercise 1

At a Monday origin, may Wednesday’s observed sales be a lag for Friday’s fixed-origin forecast?

**Worked solution.** No. They are unknown Monday. Use recursive predictions or horizon-safe direct features.

### Exercise 2

Ablation removes promo but leaves promo-discount price. What is the problem?

**Worked solution.** Price still encodes much of the promotion; the ablation does not isolate that information group.

### Exercise 3

SHAP assigns +10 to promotion. Is causal lift 10 units?

**Worked solution.** No. It explains a fitted prediction under model assumptions, not an intervention effect.

## Business-reader application

Use this request with the skill:

> Use chapter 13 to forecast retail_panel.csv one day ahead, audit every feature’s availability and compare LightGBM with seasonal-naive and a promotion/price ablation.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
