---
name: forecasting-ch25-reference-classes
description: "Use when project duration or cost needs an outside-view reference class and a risk-based commitment, or studying forecasting book chapter 25."
---

# Chapter 25: Forecasting Your Own Life

## Scope and intake

Use when project duration or cost needs an outside-view reference class and a risk-based commitment. Do not use for excluding unfinished or abandoned cases merely to make the reference class convenient.

Ask only for unresolved material inputs: What outcome and decision percentile matter? Which projects were comparable before their outcomes were known? Are unfinished cases censored or failed? Do plans and actuals share units?

## Input contract and additional evidence

CSV case_id,planned,actual,completed; planned > 0, actual >= 0, completed true/false. For incomplete projects actual is elapsed follow-up at extraction, not a completed duration. Record extraction date, class-selection criteria and abandonment status separately when relevant.

Minimal **format illustration**, not sufficient training data:

```csv
case_id,planned,actual,completed
A,12,15,true
B,12,18,false
```

## Executable interface

Exact CLI columns: `case_id,planned,actual,completed`. Supported method controls: `as_of, frequency, horizon, season, seed`.

Kaplan–Meier estimates the ratio survival curve under independent right-censoring. P50/P80/P90 are the first steps crossing their cumulative probabilities, not interpolated empirical quantiles. Unsupported upper quantiles remain null. Abandonment needs a separate outcome interpretation.

## Applied procedure

1. Define the reference class by size, complexity, technology and operating context without conditioning on desirable outcomes. Document excluded and unfinished cases.
2. Align time/cost definitions and compute completed-case duration or actual/planned ratios. Distinguish right-censoring from abandonment or competing outcomes.
3. Estimate empirical quantiles for complete data; use a supported survival estimate such as Kaplan–Meier when independent right-censoring is defensible. Do not invent an unobserved tail quantile.
4. Choose a commitment percentile from consequences of late delivery versus excess contingency. Show sensitivity to alternative defensible classes.
5. Preserve the original plan, forecast date and eventual outcome; update the class as new cases complete without rewriting prior predictions.

## Diagnostics, selection and uncertainty

Completion-only data can underestimate durations. Independent censoring is an assumption, not guaranteed by a completed flag. Abandoned projects are not simply completed at their stop date. Small classes and changing execution conditions make high quantiles unstable.

## Missing evidence and fallback

If no comparable class exists, broaden it transparently and show sensitivity rather than asserting precision. If a survival curve never reaches the requested quantile, report that quantile not estimable. Without censoring metadata, show limitations of completed-case estimates.

## Applied report contract

`results.csv` columns: `duration_ratio,at_risk,completed,survival`. `summary.json` keys: `quantiles,cases,completed` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return class definition/inclusions, completion and censoring counts, empirical or survival quantiles, uplift factors, chosen commitment and its decision rationale, plus unidentifiable tail risks.

## Run it

The [notebook](../../companion/notebooks/25-reference-classes.ipynb) is the worked lesson; its editable [source](../../companion/lessons/25-reference-classes.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. [self-check.md](references/self-check.md) holds the three questions to answer before reporting. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 25 \
  --input companion/data/examples/ch25.csv \
  --config companion/configs/ch25.json \
  --output companion/applied-runs/ch25-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 25`.

Learning prompt: “Teach me chapter 25 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 25 to projects.csv, retain censored cases, defend the reference class and translate supported quantiles into a commitment aligned with delay costs.”
