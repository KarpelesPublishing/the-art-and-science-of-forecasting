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

Exact CLI columns: `component,mean,sd`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `samples,seed,correlation`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

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

With only unweighted scenarios, report scenario outcomes rather than invented percentiles. With unknown dependence, show several defensible dependence scenarios. If serious MCMC diagnostics are absent, report the missing diagnostics and use an analytic/direct sampler when available. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return input distributions and provenance, dependence assumptions, seed/draw count, outcome quantiles, exceedance probabilities, Monte Carlo precision and separate model-sensitivity results. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 7 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 7 to cost_components.csv, preserve the stated dependence assumptions, calculate budget-exceedance probabilities and distinguish simulation error from model uncertainty.”

The [notebook](../../companion/notebooks/07-monte-carlo.ipynb) is a worked lesson; its editable [source](../../companion/lessons/07-monte-carlo.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 7
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch07.csv) and [editable config](../../companion/configs/ch07.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 7 \
  --input companion/data/examples/ch07.csv \
  --config companion/configs/ch07.json \
  --output companion/applied-runs/ch07-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `quantile,total`, `summary.json` containing `mean,mean_mcse,analytic_mean`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
