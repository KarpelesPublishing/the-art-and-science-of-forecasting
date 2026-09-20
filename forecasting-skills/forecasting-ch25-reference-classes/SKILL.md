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

Exact CLI columns: `case_id,planned,actual,completed`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `No chapter-specific configuration keys`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

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

If no comparable class exists, broaden it transparently and show sensitivity rather than asserting precision. If a survival curve never reaches the requested quantile, report that quantile not estimable. Without censoring metadata, show limitations of completed-case estimates. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return class definition/inclusions, completion and censoring counts, empirical or survival quantiles, uplift factors, chosen commitment and its decision rationale, plus unidentifiable tail risks. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 25 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 25 to projects.csv, retain censored cases, defend the reference class and translate supported quantiles into a commitment aligned with delay costs.”

The [notebook](../../companion/notebooks/25-reference-classes.ipynb) is a worked lesson; its editable [source](../../companion/lessons/25-reference-classes.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 25
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch25.csv) and [editable config](../../companion/configs/ch25.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 25 \
  --input companion/data/examples/ch25.csv \
  --config companion/configs/ch25.json \
  --output companion/applied-runs/ch25-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `duration_ratio,at_risk,completed,survival`, `summary.json` containing `quantiles`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
