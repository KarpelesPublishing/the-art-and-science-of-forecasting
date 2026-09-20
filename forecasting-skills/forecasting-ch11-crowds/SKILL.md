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

Exact CLI columns: `question,expert,estimate,actual`. Supported method controls: `as_of, extremize_a, frequency, horizon, season, seed`.

The adapter requires resolved question actuals and compares fixed mean, median and 20%-each-tail trimmed mean. When the estimates are event probabilities with binary actuals, `extremize_a` (a positive number, 2.5 is the usual starting value) adds a logit-extremized pool and scores every rule by Brier as well as MAE; extremization helps only when experts share information and the plain pool is too timid, and the tool refuses it on non-probability data. It does not learn weights or turn disagreement into calibrated outcome intervals.

## Applied procedure

1. Audit duplicate respondents, units and shared source exposure. Preserve independent estimates before discussion.
2. Compute equal-weight mean, median and a predeclared trimmed mean, recording sample size and trimming convention.
3. If resolved questions exist, compare aggregators on matched questions with settings chosen on earlier events. Avoid fitting precision weights to the same outcomes used for evaluation.
4. Examine sensitivity to extreme values and common bias separately. Report an aggregate and disagreement range without pretending respondent spread is a calibrated outcome interval.

## Diagnostics, selection and uncertainty

Mean aggregation cancels idiosyncratic error but not common bias. Median robustness to extremes does not correct shared moderate error. With equal individual variance sigma² and correlation rho, mean variance is sigma²[rho+(1-rho)/n].

## Missing evidence and fallback

With few estimates, report each judgment and simple aggregates rather than unstable learned weights. Without resolved outcomes, compare robustness and assumptions only. If everyone shares one source, state that the aggregate contains little independent information.

## Applied report contract

`results.csv` columns: `question,actual,mean,median,trimmed`. `summary.json` keys: `mae,brier,extremize_a` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return respondent count, mean/median/trimmed estimates, source-dependence notes, outlier sensitivity and held-out aggregation losses if available.

## Run it

The [notebook](../../companion/notebooks/11-crowds.ipynb) is the worked lesson; its editable [source](../../companion/lessons/11-crowds.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 11 \
  --input companion/data/examples/ch11.csv \
  --config companion/configs/ch11.json \
  --output companion/applied-runs/ch11-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 11`.

Learning prompt: “Teach me chapter 11 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 11 to estimates.csv, compare transparent aggregators and explain whether apparent agreement comes from independent information or shared evidence.”
