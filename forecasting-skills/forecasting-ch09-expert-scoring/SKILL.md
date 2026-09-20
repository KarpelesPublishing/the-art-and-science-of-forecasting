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

Exact CLI columns: `event_id,probability,outcome,baseline`. Supported method controls: `as_of, frequency, horizon, season, seed`.

The scoring adapter requires one resolved outcome per event and uses fixed probability bins. Wilson frequency bounds assume independent events. Preserve unresolved/late forecasts outside this scoring input and report their exclusions in the accompanying analysis.

## Applied procedure

1. Fix event eligibility and lead time, exclude unresolved or late forecasts with reasons, and align comparison forecasters on common events.
2. Compute per-event Brier (p-y)² and mean score. Compare against a baseline available before outcomes.
3. Group probabilities into predeclared bins and report forecast mean, outcome frequency and count, retaining sparse-bin uncertainty.
4. Separate calibration from discrimination/resolution and sharpness. Inspect performance by event type and time period before promoting a forecaster.

## Diagnostics, selection and uncertainty

Lower Brier is better on the same event set. Extreme probabilities are not automatically good resolution. A constant forecast is calibrated only relative to its population event rate. Small or dependent event samples cannot support confident expert rankings.

## Missing evidence and fallback

Without timestamps, report score eligibility as unverified. Without baseline records, use a transparently labeled retrospective comparator, not a claimed predeclared baseline. Missing outcomes stay excluded; investigate whether missingness favors successful predictions.

## Applied report contract

`results.csv` columns: `bin_lower,count,mean_probability,frequency,frequency_lower,frequency_upper`. `summary.json` keys: `brier,baseline_brier,events` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return per-event and mean Brier, baseline difference, eligibility/exclusion counts, bin means and counts, and limitations of expert comparison.

## Run it

The [notebook](../../companion/notebooks/09-expert-scoring.ipynb) is the worked lesson; its editable [source](../../companion/lessons/09-expert-scoring.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 9 \
  --input companion/data/examples/ch09.csv \
  --config companion/configs/ch09.json \
  --output companion/applied-runs/ch09-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 9`.

Learning prompt: “Teach me chapter 9 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 9 to score probabilities.csv on eligible resolved events, compare the recorded baseline and explain calibration with bin counts rather than unsupported rankings.”
