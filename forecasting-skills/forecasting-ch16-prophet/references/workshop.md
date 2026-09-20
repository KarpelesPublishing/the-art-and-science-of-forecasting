# Chapter 16 workshop: from lesson to decision

## Explain the mechanism

Prophet makes analyst-supplied structure explicit: trend changes, seasonal cycles and calendar events. The analyst is responsible for whether that structure will remain true. Flexible trend can absorb patterns that should have another explanation.

## Work through the arithmetic

In additive mode, trend 100 plus weekly effect -5 and event effect +20 gives yhat=115. If the event moves but the calendar does not, the model may predict 115 on the wrong day. A perfect component-sum identity checks implementation, not timing accuracy.

## Adapt the lesson to reader data

Replace the data DataFrame with ds,y mapped from reader columns. Replace the synthetic recurring campaign calendar with actual known-at-origin events, not an outcome-selected list of high-sales dates. Keep validation and final-test boundaries intact.

For this chapter, settle these questions before fitting: Which calendar events were known at the origin? Is their effect repeated in history? What trend flexibility is plausible? Which future regressors are actually supplied?

## Interpret the actual lesson outputs

The source runs actual Prophet, chooses flexibility at two earlier origins, and evaluates the final 45 days after selection. Its calendar ablation holds the selected prior fixed, so it isolates calendar omission at that setting rather than separately optimizing both architectures.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,lower,forecast,upper`.
- `summary.json`: `mode,mode_note,prior,validation,ablation,test_mae,test_coverage,nominal,table_scope,events,regressors` plus method, interpretation, assumptions, not_done and status.

Prophet with the event calendar as holidays and the declared regressors. `mode: auto` chooses multiplicative seasonality when a Box-Cox check on training data calls for a log scale, else additive. The changepoint prior is chosen from `priors` on `origins` earlier blocks; the calendar and the regressors are each ablated on the same blocks so their contribution is measured, not assumed. The untouched holdout is scored once with MAE and the coverage of the nominal 80 percent band. The forecast table is the future when no regressors are needed or exactly `horizon` future regressor rows were supplied, otherwise the holdout, and the summary says which under `table_scope`. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Decide what the evidence supports

Model components are fitted explanations, not independently observed causal effects. A good additive synthetic result favors that generator. MAP intervals omit some parameter uncertainty and can fail under breaks. Do not select flexibility using the final test.

Without repeated event history, use a stated event scenario or omit unsupported event estimation. If future regressors are unknown, provide conditional forecasts. If Prophet is unavailable, name the missing dependency and use a labeled baseline.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,lower,forecast,upper`; `summary.json` keys: `mode,mode_note,prior,validation,ablation,test_mae,test_coverage,nominal,table_scope,events,regressors` plus method, interpretation, assumptions, not_done and status. Quote the ablation: if removing the calendar barely changes validation MAE, the calendar is decoration and the report should say so.

## Three exercises with worked solutions

### Exercise 1

Trend 80, weekly +4, holiday -10 in additive mode: prediction?

**Worked solution.** 74.

### Exercise 2

The last campaign shifts seven days after a forecast is issued. Was the original calendar necessarily leaked?

**Worked solution.** No; it may simply have become stale. Record the schedule vintage and assess the resulting forecast error.

### Exercise 3

May a future event date be included in Prophet fitting?

**Worked solution.** Yes if genuinely known at the origin; its future outcome value must not enter fitting.

## Business-reader application

Use this request with the skill:

> Use chapter 16 to forecast activity.csv with the actual known event calendar, select trend flexibility on earlier origins and explain components and held-out uncertainty.

## Observed-data transfer exercise

A bundled [observed series](../../../companion/data/observed/monthly-temperature.csv) and [matching config](../../../companion/configs/ch16-observed.json) provide a second application after the controlled fixture. Read the [data registry](../../../companion/data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 16 \
  --input companion/data/observed/monthly-temperature.csv \
  --config companion/configs/ch16-observed.json \
  --output companion/applied-runs/ch16-observed-reader
```

Explain whether fitted seasonality transfers to the last year; this temperature example does not validate business-event effects. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
