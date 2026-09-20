---
name: forecasting-ch11-crowds
description: "Use when several independent quantity estimates need aggregation with attention to common bias and outliers, or studying forecasting book chapter 11."
---

# Chapter 11: The Crowd and the Ox

## Scope and intake

Use when several independent quantity estimates need aggregation with attention to common bias and outliers. Do not use for assuming more respondents or more AI-generated opinions automatically create more independent evidence.

Ask only for unresolved material inputs: Do estimates share a target, horizon and units? Who saw whose answer? Which sources are common? Are there past resolved questions for testing weights?

## Input contract and additional evidence

CSV question,expert,estimate,actual; one independent initial estimate per expert/question, actual finite for CLI scoring; keep unresolved estimates separately. Document units and any elicitation order. Do not mix probability and quantity estimates.

Minimal **format illustration**, not sufficient training data:

```csv
question,expert,estimate,actual
Q1,E1,90,100
Q1,E2,110,100
Q1,E3,1000,100
```

## Executable interface

Exact CLI columns: `question,expert,estimate,actual`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, extremize_a, frequency, horizon, season, seed`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

The adapter requires resolved question actuals and compares fixed mean, median and 20%-each-tail trimmed mean. When the estimates are event probabilities with binary actuals, `extremize_a` (a positive number, 2.5 is the usual starting value) adds a logit-extremized pool and scores every rule by Brier as well as MAE; extremization helps only when experts share information and the plain pool is too timid, and the tool refuses it on non-probability data. It does not learn weights or turn disagreement into calibrated outcome intervals.

## Applied procedure

1. Audit duplicate respondents, units and shared source exposure. Preserve independent estimates before discussion.
2. Compute equal-weight mean, median and a predeclared trimmed mean, recording sample size and trimming convention.
3. If resolved questions exist, compare aggregators on matched questions with settings chosen on earlier events. Avoid fitting precision weights to the same outcomes used for evaluation.
4. Examine sensitivity to extreme values and common bias separately. Report an aggregate and disagreement range without pretending respondent spread is a calibrated outcome interval.

## Diagnostics, selection and uncertainty

Mean aggregation cancels idiosyncratic error but not common bias. Median robustness to extremes does not correct shared moderate error. With equal individual variance sigma² and correlation rho, mean variance is sigma²[rho+(1-rho)/n].

## Missing evidence and fallback

With few estimates, report each judgment and simple aggregates rather than unstable learned weights. Without resolved outcomes, compare robustness and assumptions only. If everyone shares one source, state that the aggregate contains little independent information. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return respondent count, mean/median/trimmed estimates, source-dependence notes, outlier sensitivity and held-out aggregation losses if available. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 11 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 11 to estimates.csv, compare transparent aggregators and explain whether apparent agreement comes from independent information or shared evidence.”

The [notebook](../../companion/notebooks/11-crowds.ipynb) is a worked lesson; its editable [source](../../companion/lessons/11-crowds.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 11
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch11.csv) and [editable config](../../companion/configs/ch11.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 11 \
  --input companion/data/examples/ch11.csv \
  --config companion/configs/ch11.json \
  --output companion/applied-runs/ch11-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `question,actual,mean,median,trimmed`, `summary.json` containing `mae`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
