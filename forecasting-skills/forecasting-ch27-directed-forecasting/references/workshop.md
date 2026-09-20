# Chapter 27 workshop: from lesson to decision

## Explain the mechanism

Directed forecasting begins with the business question, not the most impressive model. Historical time series, analogues and bottom-up builds have different evidence requirements. A decomposition is useful because its assumptions can be challenged individually. Multiplying uncertain or correlated inputs does not create new evidence.

## Work through the arithmetic

For 100,000 eligible buyers, awareness .5, availability conditional on awareness .6, interest .2 and four units per buyer, raw mature volume is 24,000 units. A shared scale .85 gives 20,400. Transferring .85 to trial conversion is a separate assumption: the implied trial total would be 5,100. Under the standard 24-month convention, year-one trials are .8×5,100=4,080 and year two 1,020; total sales still require repeat cohorts.

## Adapt the lesson to reader data

Replace the references DataFrame in the lesson with observed products and retain an explicit product-level calibration/validation split. Replace new and kernel separately. A single sample row only illustrates format, not adequate calibration. For established-product time series, use the appropriate time-series chapter rather than forcing every problem through launch gamma. Save intake and routing reasoning alongside, not inside, the numerical fit.

For this chapter, settle these questions before fitting: What decision changes with the answer? What target, population, unit, horizon and cutoff apply? Is usable history present? Are analogues comparable and current? Does stated volume mean unique trials or total units? Which genuinely distinct cross-check and eventual scoring outcome are available?

## Interpret the actual lesson outputs

The reference scatter shows synthetic mature-product calibration; validation points test products excluded from fitting. The leave-one-out range measures sensitivity to product selection, not full uncertainty. Gamma scenarios conserve declared trials but move year-one shares. Earlier trials generate more within-horizon repeats, so identical trial totals need not produce identical 24-month sales. The explicit progress example matches gamma by construction and is not independent validation.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `month,peak,trials,units`.
- `summary.json`: `scale,trial_total,held_out_mae,year_one_units` plus method, interpretation, assumptions, not_done and status.

Launch requires at least three calibration and two validation products and runs peaks 3,4,5. Explicitly defend scale transfer or supply declared_trial_total; trials may not exceed jointly reached eligible buyers. Supply a constant repeat_rate (one unit at trial) or an explicit repeat_kernel with one nonnegative units-per-trier entry per horizon month. No default repeat assumption is invented; custom timing peaks are not accepted. Standard horizon=24; larger horizons are explicitly different scenarios. mode=estimate and insufficient history return needs_evidence, not a fabricated numeric forecast.

## Decide what the evidence supports

Check product-level residuals and scale instability, out-of-population analogues, double timing, probability denominator errors, unit reconciliation and conservation of the trial total. A mature-product fit validates only the fitted relationship on comparable products, not causal marketing effects or an unmeasured trial-transfer assumption.

If history is sparse, do not fabricate backtests; use explicit analogue/scenario estimates. If repeat data are absent, report trials separately and show repeat assumptions as scenarios. If no distinct cross-check exists, record that absence and the shared-input dependence rather than presenting two formulas as triangulation.

The applied deliverable must make these items inspectable: `results.csv` columns: `month,peak,trials,units`; `summary.json` keys: `scale,trial_total,held_out_mae,year_one_units` plus method, interpretation, assumptions, not_done and status. Return an intake/routing record, proxy/source register, reference-product calibration and held-out errors, monthly trial and total-unit tables, Y1/Y2/tail reconciliation, sensitivity table, missing-evidence priorities and dated scoring plan. State which methods were executed and which remain proposed.

## Three exercises with worked solutions

### Exercise 1

A declared trial total is 4,000. Under standard timing, how many occur in each year?

**Worked solution.** 3,200 in year one and 800 in year two. A slower timing scenario lowers year-one trials while retaining the 4,000 total.

### Exercise 2

Trial cohorts are [100,50], and expected unit kernel is [1,.2]. What are first two months’ sales?

**Worked solution.** Month one is 100. Month two is 50+100×.2=70. The remaining 50×.2=10 repeat units fall after this two-month reporting window.

### Exercise 3

The sales top-down and bottom-up checks both use the same market-size estimate and survey interest. Is their agreement independent validation?

**Worked solution.** No. Record shared evidence and seek a distinct comparison such as observed cohort conversion or comparable launches. Without it, disclose a dependent cross-check.

## Business-reader application

Use this request with the skill:

> Apply chapter 27 to our new product: first determine whether available history supports a model or only an estimate, defend proxy inputs, calibrate across comparable mature products, separate trials from repeat units, preserve 24-month trial totals, and save a forecast/scoring record.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
