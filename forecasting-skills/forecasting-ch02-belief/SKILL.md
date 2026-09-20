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

Exact CLI columns: `successes,trials`. Supported method controls: `as_of, frequency, horizon, prior_alpha, prior_beta, season, seed`.

The three rows use .25×, 1× and 4× prior strength, with 95% posterior credible bounds. They hold the prior mean fixed. There is no future-count interval in this output.

## Applied procedure

1. Define the trial population and observation process. Identify exclusions and whether repeating customers or clustered trials violate simple binomial assumptions.
2. Choose and document Beta prior alpha,beta before inspecting the batch. Sum only disjoint exchangeable observations.
3. Update to Beta(alpha+successes,beta+trials-successes). Calculate posterior mean and quantiles; compare alternate defensible priors.
4. Distinguish uncertainty about a probability from predictive uncertainty for future counts. Audit whether selection or dependence invalidates the likelihood before interpreting a narrow posterior.

## Diagnostics, selection and uncertainty

Posterior concentration is conditional on the prior, binomial sampling and representativeness. Regression toward the mean needs noisy repeated measurements; it is not proof that an intervention worked. Survivor-only records can reverse an inference.

## Missing evidence and fallback

If denominators are unknown, do not fit a binomial posterior. If outcomes are selected, describe selection scenarios or obtain the missing cohort. With clustered data, aggregate at a defensible independent unit or use a separately justified hierarchical model.

## Applied report contract

`results.csv` columns: `prior_strength,posterior_mean,lower,upper`. `summary.json` keys: `successes,failures,posterior_alpha,posterior_beta` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return success/trial totals, prior and posterior parameters, posterior mean and credible interval, sensitivity to the prior and a selection-process note. Label future-count predictions separately.

## Run it

The [notebook](../../companion/notebooks/02-belief.ipynb) is the worked lesson; its editable [source](../../companion/lessons/02-belief.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 2 \
  --input companion/data/examples/ch02.csv \
  --config companion/configs/ch02.json \
  --output companion/applied-runs/ch02-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 2`.

Learning prompt: “Teach me chapter 2 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 2 to update the success probability from batches.csv, explain the prior in business terms, and audit whether missing failures invalidate the calculation.”
