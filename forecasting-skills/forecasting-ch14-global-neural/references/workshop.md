# Chapter 14 workshop: from lesson to decision

## Explain the mechanism

A global model shares parameters across series. A probabilistic autoregressive model predicts a distribution for the next value; recursive sampling carries future uncertainty forward. Cross-entity transfer requires relevant common structure, not simply more rows.

## Work through the arithmetic

If context mean absolute level is 50 and the network predicts normalized mean .1 with normalized SD .2, the original-scale mean is 50×(1+.1)=55 and SD=10. Using a scale computed from future actuals would leak information even if the network weights were frozen.

## Adapt the lesson to reader data

Replace ys and entity splits with aligned observed panels; keep a separate mask for incomplete context. Preserve context-only scaling. Do not let unseen-entity observations contribute training examples; only their pre-origin context can enter prediction.

For this chapter, settle these questions before fitting: Which entities are related and which will be unseen at deployment? How much recent context exists? Is the outcome continuous, count or nonnegative? What horizon and distributional loss matter?

## Interpret the actual lesson outputs

The lesson trains an actual small PyTorch Gaussian MLP, not a recurrent DeepAR implementation. Eight entities are held out from training but provide fourteen observed values. The reported coverage comes from related series and overlapping origins; it is a limited controlled evaluation.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `series_id,timestamp,actual,baseline,lower,median,upper`.
- `summary.json`: `training_entities,held_out_entities,coverage,interval_score,mae,baseline_mae` plus method, interpretation, assumptions, not_done and status.

At least four aligned related series are required. The last quarter of sorted entity groups is held out, not a user-configurable split. The actual Gaussian MLP uses 100 recursive paths for nominal 80% bands. It does not implement DeepAR or tune hyperparameters on held-out entities.

## Decide what the evidence supports

Lower training loss does not establish generalization. Gaussian likelihood can assign impossible negative demand. Coverage from many dependent horizon rows is not equivalent to the same count of independent forecast cases. Test entity exclusion and time cutoff explicitly.

With one or a few unrelated series, use a local baseline rather than assuming pooling helps. With no context for a new entity, the demonstrated model is unsupported. If the required neural dependency is missing, report the skipped method honestly.

The applied deliverable must make these items inspectable: `results.csv` columns: `series_id,timestamp,actual,baseline,lower,median,upper`; `summary.json` keys: `training_entities,held_out_entities,coverage,interval_score,mae,baseline_mae` plus method, interpretation, assumptions, not_done and status. Return entity/time split, context and scaling rules, model/training record, sampled forecast quantiles, local-baseline comparison and coverage/width by entity and horizon.

## Three exercises with worked solutions

### Exercise 1

Normalized output mean=-.2, SD=.1, scale=100. Original mean and SD?

**Worked solution.** Mean 80 and SD 10 under the lesson’s centering convention.

### Exercise 2

Test entity history appears in training but future dates do not. Is this unseen-entity evaluation?

**Worked solution.** No. It is temporal generalization for a seen entity; label it accordingly.

### Exercise 3

Why must sampled paths feed back their own values?

**Worked solution.** To propagate uncertainty through autoregressive dependence without importing future actuals.

## Business-reader application

Use this request with the skill:

> Apply chapter 14 to panel.csv with an explicit unseen-entity holdout, compare the actual global Gaussian MLP with local baselines and report uncertainty limitations.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
