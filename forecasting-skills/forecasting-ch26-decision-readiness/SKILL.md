---
name: forecasting-ch26-decision-readiness
description: "Use when a probability forecast must guide a concrete action under explicit costs and ongoing evaluation, or studying forecasting book chapter 26."
---

# Chapter 26: How to Be Ready Without Being Certain

## Scope and intake

Use when a probability forecast must guide a concrete action under explicit costs and ongoing evaluation. Do not use for requiring certainty before acting or choosing thresholds solely to maximize classification accuracy.

Ask only for unresolved material inputs: What actions are available? What is the cost of a false alarm and a miss? Are costs constant and probabilities relevant/calibrated? What capacity or feasibility constraints apply?

## Input contract and additional evidence

CSV event_id,probability,outcome with p in [0,1], outcome 0/1 for CLI scoring; retain unresolved cases in the journal, not this scoring file. Config false_alarm_cost and miss_cost are strictly positive and finite for the supplied adapter. Record forecast timestamps, event definition and action constraints separately; predictions must predate outcomes.

Minimal **format illustration**, not sufficient training data:

```csv
event_id,probability,outcome
E1,0.3,1
E2,0.1,0
```

## Executable interface

Exact CLI columns: `event_id,probability,outcome`. Supported method controls: `as_of, false_alarm_cost, frequency, horizon, miss_cost, season, seed`.

The adapter requires resolved events and strictly positive finite costs. It acts at p>=threshold. The reported best constant policy is a hindsight diagnostic, not a pre-recorded baseline. It reports Brier alongside decision loss; chapter 9 adds a fuller calibration diagnosis.

## Applied procedure

1. Define action consequences before selecting a threshold. Under the simple binary loss table, compute threshold false_alarm_cost/(false_alarm_cost+miss_cost).
2. For each forecast compare expected action costs using only information available then; record the action and any capacity constraint or override.
3. After resolution compute Brier and realized decision cost on the same events, comparing predeclared simple policies.
4. If combining forecasts, use fixed weights or learn weights on earlier resolved events and evaluate later. Preserve the journal and unresolved events.
5. Review calibration drift, realized costs and whether the loss table remains appropriate; change future policy prospectively rather than rewriting past actions.

## Diagnostics, selection and uncertainty

The threshold formula assumes zero cost for correct actions and fixed misclassification costs. Capacity limits, intervention effectiveness and heterogeneous costs can require a different optimization. A good score does not automatically imply useful decisions, and one outcome cannot establish calibration.

## Missing evidence and fallback

Without credible costs, present the threshold/cost tradeoff and ask for the material missing preference rather than declare an optimal action. With unresolved outcomes, log expected decisions but do not compute realized loss. Uncertain probabilities warrant sensitivity around the decision boundary.

## Applied report contract

`results.csv` columns: `event_id,probability,outcome,action,loss,cumulative_loss`. `summary.json` keys: `threshold,brier,mean_loss,best_constant_policy_hindsight_cost` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return loss table, threshold and assumptions, event-level probabilities/actions, realized costs and proper scores where resolved, benchmark policies, unresolved counts and revision plan.

## Run it

The [notebook](../../companion/notebooks/26-decision-readiness.ipynb) is the worked lesson; its editable [source](../../companion/lessons/26-decision-readiness.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. [self-check.md](references/self-check.md) holds the three questions to answer before reporting. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 26 \
  --input companion/data/examples/ch26.csv \
  --config companion/configs/ch26.json \
  --output companion/applied-runs/ch26-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 26`.

Learning prompt: “Teach me chapter 26 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 26 to translate probabilities.csv into an explicit action policy under our costs, preserve unresolved cases and evaluate both probability quality and realized decision loss.”
