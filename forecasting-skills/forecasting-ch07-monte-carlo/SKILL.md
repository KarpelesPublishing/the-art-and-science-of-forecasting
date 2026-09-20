---
name: forecasting-ch07-monte-carlo
description: "Use when uncertain inputs must be propagated through a calculation or simulation precision needs auditing, or studying forecasting book chapter 7."
---

# Chapter 7: The Casino at Los Alamos

## Scope and intake

Use when uncertain inputs must be propagated through a calculation or simulation precision needs auditing. Do not use for creating probabilities by assigning arbitrary distributions to unsupported low/base/high scenarios.

Ask only for unresolved material inputs: What outcome and units matter? Which input distributions are measured or elicited? Which dependencies matter? What precision is needed for the decision?

## Input contract and additional evidence

CSV component,mean,sd for positive lognormal components, with mean > 0 and sd >= 0 in common additive units. Config samples,seed and correlation assumption. Arithmetic-scale mean/sd are not log-scale normal parameters. Other distributions require an explicitly adapted model.

Minimal **format illustration**, not sufficient training data:

```csv
component,mean,sd
Labor,100,20
Materials,50,15
```

## Executable interface

Exact CLI columns: `component,mean,sd`. Supported method controls: `as_of, correlation, frequency, horizon, samples, season, seed`.

Positive arithmetic means and nonnegative SDs define lognormal components. correlation is shared latent-normal correlation in [0,1), not the resulting components’ Pearson correlation. The adapter simulates totals directly; it does not run MCMC or report budget exceedance unless added separately.

## Applied procedure

1. Define the simulation function and input provenance. Specify marginal distributions and dependence before sampling.
2. Translate arithmetic lognormal moments: sigma_log²=log(1+sd²/mean²), mu_log=log(mean)-sigma_log²/2. Validate support and any dependence matrix.
3. Draw joint inputs, compute the outcome for each draw, and summarize decision-relevant quantiles and exceedance probabilities. Compare an analytic special case where available.
4. Repeat with independent seeds or batches to estimate Monte Carlo variability; increase draws until simulation error is small relative to the decision. Stress uncertain distribution/dependence assumptions separately.
5. For posterior MCMC, inspect multiple chains, autocorrelation, effective sample size and convergence diagnostics before inference. If only a one-chain toy ran, label it an illustration rather than certified inference.

## Diagnostics, selection and uncertainty

More draws reduce Monte Carlo error, not model error. Independent-draw formulas do not apply to correlated MCMC draws without an effective-sample adjustment. Acceptance rate and a plausible trace are insufficient convergence evidence.

## Missing evidence and fallback

With only unweighted scenarios, report scenario outcomes rather than invented percentiles. With unknown dependence, show several defensible dependence scenarios. If serious MCMC diagnostics are absent, report the missing diagnostics and use an analytic/direct sampler when available.

## Applied report contract

`results.csv` columns: `quantile,total`. `summary.json` keys: `mean,mean_mcse,analytic_mean,samples,correlation` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return input distributions and provenance, dependence assumptions, seed/draw count, outcome quantiles, exceedance probabilities, Monte Carlo precision and separate model-sensitivity results.

## Run it

The [notebook](../../companion/notebooks/07-monte-carlo.ipynb) is the worked lesson; its editable [source](../../companion/lessons/07-monte-carlo.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 7 \
  --input companion/data/examples/ch07.csv \
  --config companion/configs/ch07.json \
  --output companion/applied-runs/ch07-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 7`.

Learning prompt: “Teach me chapter 7 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 7 to cost_components.csv, preserve the stated dependence assumptions, calculate budget-exceedance probabilities and distinguish simulation error from model uncertainty.”
