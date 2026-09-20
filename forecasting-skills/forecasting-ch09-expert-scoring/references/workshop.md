# Chapter 9 workshop: from lesson to decision

## Explain the mechanism

Proper scores reward honest probabilities over repeated events. Calibration asks whether events given similar probabilities occur at corresponding frequencies. A forecaster can be calibrated yet offer little differentiation among events.

## Work through the arithmetic

For p=[.7,.2] and outcomes [1,0], Brier contributions are .09 and .04, averaging .065. A .5 baseline scores .25 on both. On these two events the difference is -.185, but two events cannot certify skill or calibration.

## Adapt the lesson to reader data

Replace generated p/outcomes with recorded eligible forecasts and resolved outcomes. Retain the fixed event set across comparisons. Do not use the observed full-sample event rate as though it were known when historical baseline forecasts were issued.

For this chapter, settle these questions before fitting: Which events and forecast lead time are shared? Were forecasts recorded before resolution? What baseline was predeclared? Are outcomes missing or selectively reported?

## Interpret the actual lesson outputs

The lesson’s 6,000 events are synthetic and its one-third baseline is known from the generator. The confidence plot annotates counts. A visually diagonal curve does not establish causality, and confidence in the favored outcome differs from probability of the same named event.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `bin_lower,count,mean_probability,frequency,frequency_lower,frequency_upper`.
- `summary.json`: `brier,baseline_brier,events` plus method, interpretation, assumptions, not_done and status.

The scoring adapter requires one resolved outcome per event and uses fixed probability bins. Wilson frequency bounds assume independent events. Preserve unresolved/late forecasts outside this scoring input and report their exclusions in the accompanying analysis.

## Decide what the evidence supports

Lower Brier is better on the same event set. Extreme probabilities are not automatically good resolution. A constant forecast is calibrated only relative to its population event rate. Small or dependent event samples cannot support confident expert rankings.

Without timestamps, report score eligibility as unverified. Without baseline records, use a transparently labeled retrospective comparator, not a claimed predeclared baseline. Missing outcomes stay excluded; investigate whether missingness favors successful predictions.

The applied deliverable must make these items inspectable: `results.csv` columns: `bin_lower,count,mean_probability,frequency,frequency_lower,frequency_upper`; `summary.json` keys: `brier,baseline_brier,events` plus method, interpretation, assumptions, not_done and status. Return per-event and mean Brier, baseline difference, eligibility/exclusion counts, bin means and counts, and limitations of expert comparison.

## Three exercises with worked solutions

### Exercise 1

Forecast .9, outcome 0: Brier?

**Worked solution.** .81, a large penalty for confident error.

### Exercise 2

Every event has true rate .2. Is a constant .5 forecast calibrated?

**Worked solution.** No. In its single forecast bin, observed frequency would approach .2 rather than .5.

### Exercise 3

Expert A scored easy events, B scored difficult ones. Can mean Brier rank skill fairly?

**Worked solution.** Not without adjusting the comparison design; use common events and lead times or explicitly defend a different comparison.

## Business-reader application

Use this request with the skill:

> Use chapter 9 to score probabilities.csv on eligible resolved events, compare the recorded baseline and explain calibration with bin counts rather than unsupported rankings.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
