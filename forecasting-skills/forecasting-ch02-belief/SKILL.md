---
name: forecasting-ch02-belief
description: "Use when binary success evidence must update a base rate or a selected sample needs a survivorship audit, or studying forecasting book chapter 2."
---

# Chapter 2: The Mathematics of Belief

## Scope and intake

Use when binary success evidence must update a base rate or a selected sample needs a survivorship audit. Do not use for a causal claim from regression toward the mean or exchangeability that cannot be defended.

Ask only for unresolved material inputs: What counts as a trial and success? Are trials independent and comparable? Why this prior? Which failures or nonrespondents are missing?

## Input contract and additional evidence

CSV successes,trials with integer 0 <= successes <= trials and trials > 0; rows must represent disjoint comparable batches. Config prior_alpha and prior_beta are positive. Record population, sampling window and observation/selection rules.

Minimal **format illustration**, not sufficient training data:

```csv
successes,trials
7,10
```

## Executable interface

Exact CLI columns: `successes,trials`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, frequency, horizon, prior_alpha, prior_beta, season, seed`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

The three rows use .25×, 1× and 4× prior strength, with 95% posterior credible bounds. They hold the prior mean fixed. There is no future-count interval in this output.

## Applied procedure

1. Define the trial population and observation process. Identify exclusions and whether repeating customers or clustered trials violate simple binomial assumptions.
2. Choose and document Beta prior alpha,beta before inspecting the batch. Sum only disjoint exchangeable observations.
3. Update to Beta(alpha+successes,beta+trials-successes). Calculate posterior mean and quantiles; compare alternate defensible priors.
4. Distinguish uncertainty about a probability from predictive uncertainty for future counts. Audit whether selection or dependence invalidates the likelihood before interpreting a narrow posterior.

## Diagnostics, selection and uncertainty

Posterior concentration is conditional on the prior, binomial sampling and representativeness. Regression toward the mean needs noisy repeated measurements; it is not proof that an intervention worked. Survivor-only records can reverse an inference.

## Missing evidence and fallback

If denominators are unknown, do not fit a binomial posterior. If outcomes are selected, describe selection scenarios or obtain the missing cohort. With clustered data, aggregate at a defensible independent unit or use a separately justified hierarchical model. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return success/trial totals, prior and posterior parameters, posterior mean and credible interval, sensitivity to the prior and a selection-process note. Label future-count predictions separately. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 2 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 2 to update the success probability from batches.csv, explain the prior in business terms, and audit whether missing failures invalidate the calculation.”

The [notebook](../../companion/notebooks/02-belief.ipynb) is a worked lesson; its editable [source](../../companion/lessons/02-belief.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 2
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch02.csv) and [editable config](../../companion/configs/ch02.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 2 \
  --input companion/data/examples/ch02.csv \
  --config companion/configs/ch02.json \
  --output companion/applied-runs/ch02-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `prior_strength,posterior_mean,lower,upper`, `summary.json` containing `interpretation`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
