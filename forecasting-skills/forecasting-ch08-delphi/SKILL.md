---
name: forecasting-ch08-delphi
description: "Use when structured anonymous expert rounds are needed for sparse-evidence quantity forecasts, or studying forecasting book chapter 8."
---

# Chapter 8: The Delphi Room

## Scope and intake

Use when structured anonymous expert rounds are needed for sparse-evidence quantity forecasts. Do not use for using convergence of opinions as evidence of accuracy or treating AI personas as independent experts.

Ask only for unresolved material inputs: What question and common units will every expert answer? What independent evidence does each have? How many rounds are justified? When will actual outcomes resolve?

## Input contract and additional evidence

CSV question,expert,round,estimate,actual; one estimate per question/expert/round. round is a positive integer, estimates share units, actual is finite for CLI scoring and identical across rows for the same question; retain unresolved blank actuals separately. Keep rationale and evidence in a linked qualitative record.

Minimal **format illustration**, not sufficient training data:

```csv
question,expert,round,estimate,actual
Q1,E1,1,100,110
Q1,E2,1,120,110
```

## Executable interface

Exact CLI columns: `question,expert,round,estimate,actual`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, frequency, horizon, season, seed`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

The adapter requires complete resolved actuals and compares round medians. Keep unresolved elicitation records in a separate journal until resolution. It does not solicit experts, authenticate independence or estimate a full opinion distribution.

## Applied procedure

1. Write one unambiguous question and recruit experts with distinct relevant evidence. Record independent first-round estimates before feedback.
2. Summarize anonymous estimates with median, quartiles and reasons; include contradictory evidence rather than only the central number.
3. Collect revisions with reasons linked to new information or corrected assumptions. Retain all rounds; stop when additional evidence or decision value is exhausted.
4. Compare spread across rounds. When outcomes resolve, compare first and final estimates on the same questions with the same loss; calculate forecast value added.
5. Inspect shared sources, persistent bias and attrition. Preserve a dissenting scenario where its evidence is credible even if a majority converges.

## Diagnostics, selection and uncertainty

Falling interquartile range measures agreement. It does not measure calibration or accuracy. Attrition can make later consensus appear stronger. Elicited quartiles alone do not determine a full probability distribution.

## Missing evidence and fallback

Without actuals, report agreement and unresolved status but no accuracy score. With one expert, report an expert judgment rather than a Delphi panel. Without independent evidence, explain common-source dependence and seek external information. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return anonymized round tables, medians/spreads, rationale changes, dissenting evidence, stopping reason and resolved-question first-versus-final losses where available. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 8 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 8 to analyze expert_rounds.csv, distinguish consensus from accuracy, retain dissent and evaluate whether later rounds improved resolved forecasts.”

The [notebook](../../companion/notebooks/08-delphi.ipynb) is a worked lesson; its editable [source](../../companion/lessons/08-delphi.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 8
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch08.csv) and [editable config](../../companion/configs/ch08.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 8 \
  --input companion/data/examples/ch08.csv \
  --config companion/configs/ch08.json \
  --output companion/applied-runs/ch08-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `question,round,n,median,iqr,absolute_error`, `summary.json` containing `forecast_value_added`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
