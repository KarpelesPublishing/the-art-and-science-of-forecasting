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

Exact CLI columns: `question,expert,round,estimate,actual`. Supported method controls: `as_of, frequency, horizon, season, seed`.

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

Without actuals, report agreement and unresolved status but no accuracy score. With one expert, report an expert judgment rather than a Delphi panel. Without independent evidence, explain common-source dependence and seek external information.

## Applied report contract

`results.csv` columns: `question,round,n,median,iqr,absolute_error`. `summary.json` keys: `forecast_value_added,questions,rounds` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return anonymized round tables, medians/spreads, rationale changes, dissenting evidence, stopping reason and resolved-question first-versus-final losses where available.

## Run it

The [notebook](../../companion/notebooks/08-delphi.ipynb) is the worked lesson; its editable [source](../../companion/lessons/08-delphi.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. [self-check.md](references/self-check.md) holds the three questions to answer before reporting. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 8 \
  --input companion/data/examples/ch08.csv \
  --config companion/configs/ch08.json \
  --output companion/applied-runs/ch08-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 8`.

Learning prompt: “Teach me chapter 8 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 8 to analyze expert_rounds.csv, distinguish consensus from accuracy, retain dissent and evaluate whether later rounds improved resolved forecasts.”
