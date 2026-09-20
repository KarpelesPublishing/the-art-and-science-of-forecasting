# Chapter 7 workshop: from lesson to decision

## Explain the mechanism

Monte Carlo pushes assumptions through a calculation by repeated sampling. Direct simulation samples specified inputs; MCMC approximates a target distribution through dependent states. The number of draws is not a substitute for trustworthy assumptions.

## Work through the arithmetic

If an indicator event occurs in 2,000 of 10,000 independent draws, estimated probability is .2 and approximate Monte Carlo standard error is sqrt(.2×.8/10000)=.004. Four times as many draws reduces that standard error to .002. This is simulation precision, not uncertainty that the assumed risk model is correct.

## Adapt the lesson to reader data

Replace the cost-generation block with named components and a documented joint simulator. Do not pass arithmetic means directly as the mean argument of a lognormal generator. Keep the Metropolis demonstration separate: it targets Beta(9,5), whose analytic mean is 9/14, not a cost model.

For this chapter, settle these questions before fitting: What outcome and units matter? Which input distributions are measured or elicited? Which dependencies matter? What precision is needed for the decision?

## Interpret the actual lesson outputs

The cost histogram reflects independent assumed lognormal components. The sample-size plot illustrates the square-root precision rate under finite variance. The single-chain Beta density comparison and mean assertion do not implement multiple-chain convergence or ESS diagnostics.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `quantile,total`.
- `summary.json`: `mean,mean_mcse,analytic_mean,samples,correlation` plus method, interpretation, assumptions, not_done and status.

Positive arithmetic means and nonnegative SDs define lognormal components. correlation is shared latent-normal correlation in [0,1), not the resulting components’ Pearson correlation. The adapter simulates totals directly; it does not run MCMC or report budget exceedance unless added separately.

## Decide what the evidence supports

More draws reduce Monte Carlo error, not model error. Independent-draw formulas do not apply to correlated MCMC draws without an effective-sample adjustment. Acceptance rate and a plausible trace are insufficient convergence evidence.

With only unweighted scenarios, report scenario outcomes rather than invented percentiles. With unknown dependence, show several defensible dependence scenarios. If serious MCMC diagnostics are absent, report the missing diagnostics and use an analytic/direct sampler when available.

The applied deliverable must make these items inspectable: `results.csv` columns: `quantile,total`; `summary.json` keys: `mean,mean_mcse,analytic_mean,samples,correlation` plus method, interpretation, assumptions, not_done and status. Return input distributions and provenance, dependence assumptions, seed/draw count, outcome quantiles, exceedance probabilities, Monte Carlo precision and separate model-sensitivity results.

## Three exercises with worked solutions

### Exercise 1

Independent simulated mean has SE=.1 at N=1000. Approximate SE at N=4000?

**Worked solution.** SE=.05 under the same finite-variance model.

### Exercise 2

You observe 90% interval coverage across simulator draws. Is empirical business coverage established?

**Worked solution.** No. Simulator draws came from assumed distributions; real later outcomes are required to assess operational coverage.

### Exercise 3

MCMC has 10,000 draws but ESS=100. Which count informs mean precision?

**Worked solution.** Effective sample size, approximately 100, subject to valid diagnostics; raw draw count overstates independent information.

## Business-reader application

Use this request with the skill:

> Apply chapter 7 to cost_components.csv, preserve the stated dependence assumptions, calculate budget-exceedance probabilities and distinguish simulation error from model uncertainty.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
