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

Exact CLI columns: `event_id,probability,outcome`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, false_alarm_cost, frequency, horizon, miss_cost, season, seed`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

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

Without credible costs, present the threshold/cost tradeoff and ask for the material missing preference rather than declare an optimal action. With unresolved outcomes, log expected decisions but do not compute realized loss. Uncertain probabilities warrant sensitivity around the decision boundary. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return loss table, threshold and assumptions, event-level probabilities/actions, realized costs and proper scores where resolved, benchmark policies, unresolved counts and revision plan. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 26 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 26 to translate probabilities.csv into an explicit action policy under our costs, preserve unresolved cases and evaluate both probability quality and realized decision loss.”

The [notebook](../../companion/notebooks/26-decision-readiness.ipynb) is a worked lesson; its editable [source](../../companion/lessons/26-decision-readiness.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 26
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch26.csv) and [editable config](../../companion/configs/ch26.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 26 \
  --input companion/data/examples/ch26.csv \
  --config companion/configs/ch26.json \
  --output companion/applied-runs/ch26-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `event_id,probability,outcome,action,loss,cumulative_loss`, `summary.json` containing `threshold,brier,mean_loss,best_constant_policy_hindsight_cost`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
