# Chapter 2 workshop: from lesson to decision

## Explain the mechanism

Bayesian updating combines prior and likelihood rather than replacing uncertainty with an observed percentage. Selection bias concerns which observations enter the calculation; more selected data can make a wrong inference more precise.

## Work through the arithmetic

Beta(2,2) plus seven successes in ten trials gives Beta(9,5), with mean 9/14=.642857. The observed success rate is .7 and the prior mean .5, so the posterior is between them. The predictive success probability for one exchangeable next trial is also 9/14; a credible interval describes the latent probability, not a binary outcome.

## Adapt the lesson to reader data

Replace the successes/failures and prior inputs in the first lesson block. Keep survivor diagrams conceptual unless historical observations are actually supplied. If source data list individual cases, deduplicate them and derive disjoint success/trial counts without dropping failures.

For this chapter, settle these questions before fitting: What counts as a trial and success? Are trials independent and comparable? Why this prior? Which failures or nonrespondents are missing?

## Interpret the actual lesson outputs

The posterior density is normalized. The paired-measurement cloud shares latent ability with independent new noise. The aircraft illustration is conceptual; the subsequent controlled simulation supplies a known selection mechanism, not evidence about historical aircraft.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `prior_strength,posterior_mean,lower,upper`.
- `summary.json`: `successes,failures,posterior_alpha,posterior_beta` plus method, interpretation, assumptions, not_done and status.

The three rows use .25×, 1× and 4× prior strength, with 95% posterior credible bounds. They hold the prior mean fixed. There is no future-count interval in this output.

## Decide what the evidence supports

Posterior concentration is conditional on the prior, binomial sampling and representativeness. Regression toward the mean needs noisy repeated measurements; it is not proof that an intervention worked. Survivor-only records can reverse an inference.

If denominators are unknown, do not fit a binomial posterior. If outcomes are selected, describe selection scenarios or obtain the missing cohort. With clustered data, aggregate at a defensible independent unit or use a separately justified hierarchical model.

The applied deliverable must make these items inspectable: `results.csv` columns: `prior_strength,posterior_mean,lower,upper`; `summary.json` keys: `successes,failures,posterior_alpha,posterior_beta` plus method, interpretation, assumptions, not_done and status. Return success/trial totals, prior and posterior parameters, posterior mean and credible interval, sensitivity to the prior and a selection-process note. Label future-count predictions separately.

## Three exercises with worked solutions

### Exercise 1

Beta(1,1), three successes in four trials: posterior?

**Worked solution.** Beta(4,2), mean 4/6=2/3.

### Exercise 2

A database contains 90 successes but no count of attempts. What can be updated?

**Worked solution.** Not a binomial probability. Obtain the attempts denominator or report counts without a probability estimate.

### Exercise 3

Low performers improved on retesting after coaching. Is coaching identified?

**Worked solution.** No. Measurement noise and selection can produce regression toward the mean. A credible comparator or experiment is needed.

## Business-reader application

Use this request with the skill:

> Use chapter 2 to update the success probability from batches.csv, explain the prior in business terms, and audit whether missing failures invalidate the calculation.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
