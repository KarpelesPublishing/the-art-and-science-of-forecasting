---
name: forecasting-ch09-expert-scoring
description: "Use when probability forecasters need fair scoring and calibration diagnostics on common resolved events, or studying forecasting book chapter 9."
---

# Chapter 9: The Oracle Problem

## Scope and intake

Use when probability forecasters need fair scoring and calibration diagnostics on common resolved events. Do not use for ranking experts by reputation, one success or noncomparable question sets.

Ask only for unresolved material inputs: Which events and forecast lead time are shared? Were forecasts recorded before resolution? What baseline was predeclared? Are outcomes missing or selectively reported?

## Input contract and additional evidence

CSV event_id,probability,outcome,baseline; probabilities and baseline in [0,1], outcome 0/1 for CLI scoring; retain unresolved cases in the journal, not this scoring file. Each row is one eligible event forecast. Multiple experts require separate aligned forecast columns/files or an explicitly adapted expert_id panel; revisions must be reduced by the predeclared cutoff rule.

Minimal **format illustration**, not sufficient training data:

```csv
event_id,probability,outcome,baseline
E1,0.7,1,0.5
E2,0.2,0,0.5
```

## Executable interface

Exact CLI columns: `event_id,probability,outcome,baseline`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `No chapter-specific configuration keys`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

The scoring adapter requires one resolved outcome per event and uses fixed probability bins. Wilson frequency bounds assume independent events. Preserve unresolved/late forecasts outside this scoring input and report their exclusions in the accompanying analysis.

## Applied procedure

1. Fix event eligibility and lead time, exclude unresolved or late forecasts with reasons, and align comparison forecasters on common events.
2. Compute per-event Brier (p-y)² and mean score. Compare against a baseline available before outcomes.
3. Group probabilities into predeclared bins and report forecast mean, outcome frequency and count, retaining sparse-bin uncertainty.
4. Separate calibration from discrimination/resolution and sharpness. Inspect performance by event type and time period before promoting a forecaster.

## Diagnostics, selection and uncertainty

Lower Brier is better on the same event set. Extreme probabilities are not automatically good resolution. A constant forecast is calibrated only relative to its population event rate. Small or dependent event samples cannot support confident expert rankings.

## Missing evidence and fallback

Without timestamps, report score eligibility as unverified. Without baseline records, use a transparently labeled retrospective comparator, not a claimed predeclared baseline. Missing outcomes stay excluded; investigate whether missingness favors successful predictions. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return per-event and mean Brier, baseline difference, eligibility/exclusion counts, bin means and counts, and limitations of expert comparison. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 9 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 9 to score probabilities.csv on eligible resolved events, compare the recorded baseline and explain calibration with bin counts rather than unsupported rankings.”

The [notebook](../../companion/notebooks/09-expert-scoring.ipynb) is a worked lesson; its editable [source](../../companion/lessons/09-expert-scoring.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 9
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch09.csv) and [editable config](../../companion/configs/ch09.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 9 \
  --input companion/data/examples/ch09.csv \
  --config companion/configs/ch09.json \
  --output companion/applied-runs/ch09-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `bin_lower,count,mean_probability,frequency,frequency_lower,frequency_upper`, `summary.json` containing `brier,baseline_brier`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
