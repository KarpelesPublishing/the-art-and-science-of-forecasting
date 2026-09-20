# Chapter 26 workshop: from lesson to decision

## Explain the mechanism

Readiness converts uncertain beliefs into contingent actions. A threshold expresses relative consequences, not how confident one should feel. A forecast and the policy using it need separate evaluation because either can fail.

## Work through the arithmetic

With false-alarm cost 2 and miss cost 8, act when p>=2/(2+8)=.2 under the adapter’s tie rule. At p=.3, acting costs 2×.7=1.4 in expectation; not acting costs 8×.3=2.4. A rare event can therefore justify action well below a .5 threshold.

## Adapt the lesson to reader data

Replace the synthetic journal with timestamped event probabilities and outcomes; retain baseline predictions made on the same events. Change costs before recomputing policy decisions. If historical decisions were different, do not represent newly optimized retrospective decisions as actions actually taken.

For this chapter, settle these questions before fitting: What actions are available? What is the cost of a false alarm and a miss? Are costs constant and probabilities relevant/calibrated? What capacity or feasibility constraints apply?

## Interpret the actual lesson outputs

The lesson’s events and journal are synthetic, with fixed equal ensemble weights. The cost curve applies alternate thresholds to the same outcomes; choosing its minimum and reporting that same minimum as future performance would overfit policy selection.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `event_id,probability,outcome,action,loss,cumulative_loss`.
- `summary.json`: `threshold,brier,mean_loss,best_constant_policy_hindsight_cost` plus method, interpretation, assumptions, not_done and status.

The adapter requires resolved events and strictly positive finite costs. It acts at p>=threshold. The reported best constant policy is a hindsight diagnostic, not a pre-recorded baseline. It reports Brier alongside decision loss; chapter 9 adds a fuller calibration diagnosis.

## Decide what the evidence supports

The threshold formula assumes zero cost for correct actions and fixed misclassification costs. Capacity limits, intervention effectiveness and heterogeneous costs can require a different optimization. A good score does not automatically imply useful decisions, and one outcome cannot establish calibration.

Without credible costs, present the threshold/cost tradeoff and ask for the material missing preference rather than declare an optimal action. With unresolved outcomes, log expected decisions but do not compute realized loss. Uncertain probabilities warrant sensitivity around the decision boundary.

The applied deliverable must make these items inspectable: `results.csv` columns: `event_id,probability,outcome,action,loss,cumulative_loss`; `summary.json` keys: `threshold,brier,mean_loss,best_constant_policy_hindsight_cost` plus method, interpretation, assumptions, not_done and status. Return loss table, threshold and assumptions, event-level probabilities/actions, realized costs and proper scores where resolved, benchmark policies, unresolved counts and revision plan.

## Three exercises with worked solutions

### Exercise 1

False alarm 9, miss 1: optimal simple threshold?

**Worked solution.** 9/(9+1)=.9.

### Exercise 2

p=.4, false alarm 2, miss 8: expected costs?

**Worked solution.** Act: 2×.6=1.2; do not act: 8×.4=3.2. Act under the simple loss table.

### Exercise 3

A threshold tuned to all outcomes has lower realized cost. Is deployment improvement established?

**Worked solution.** No. Freeze it and evaluate later events; retrospective optimization is not untouched policy evidence.

## Business-reader application

Use this request with the skill:

> Use chapter 26 to translate probabilities.csv into an explicit action policy under our costs, preserve unresolved cases and evaluate both probability quality and realized decision loss.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
