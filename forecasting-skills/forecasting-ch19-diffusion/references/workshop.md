# Chapter 19 workshop: from lesson to decision

## Explain the mechanism

Bass separates external adoption pressure p from imitation pressure q times existing penetration. Remaining nonadopters limit growth. Its familiar S-shape is a model of first adoption, not a universal sales law.

## Work through the arithmetic

With m=10,000, existing adopters N=2,000, p=.02/year and q=.3/year, instantaneous adoption rate is (.02+.3×.2)×8,000=640 adopters/year. If q>p, peak time is log(q/p)/(p+q); here log(15)/.32≈8.463 years under a launch at zero adoption.

## Adapt the lesson to reader data

Replace early/observed in the sparse-fit block with elapsed time and cumulative unique adopters. Select ceiling scenarios from external market definitions, not simply from whichever fit pleases the sponsor. Keep repeat-volume arithmetic separate.

For this chapter, settle these questions before fitting: Does the series count cumulative unique adopters? What is the market ceiling’s evidence? Are time units consistent? Has the inflection or peak been observed? What repeat behavior lies outside adoption?

## Interpret the actual lesson outputs

The lesson contrasts cumulative adoption with its derivative and fits the first five synthetic years under different ceilings. Similar early fits expose weak identification; they do not assign probabilities to ceilings. Trial/repeat figures use separately assumed purchase factors.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `time,ceiling,bass_trials,gamma_trials,bass_units,gamma_units`.
- `summary.json`: `fits,ceilings,sales_horizon,peak,kernel,timing_comparison,parfitt_collins,bass_table_rows` plus method, interpretation, assumptions, not_done and status.

The tool fits the Bass model for each declared ceiling (with early-fit holdout, Jacobian condition and peak time), optionally refits with `fix_q` held, then converts adoption into sales over `sales_horizon` periods (24 or more) under two timing curves that share the same trial total: Bass incidence and the author's gamma-shaped launch curve with its `peak` month. Each timing is spread with the repeat kernel into unit sales, and the tool compares peak period, twelve-period units and total units between them. With `parfitt_collins` inputs it reports the steady-state share and a plus or minus 20 percent band on repeat. Price, distribution and advertising are not in the curve; the kernel is assumed, not estimated. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Decide what the evidence supports

Early adoption often weakly identifies m and can trade off with p,q. An interior incidence peak formula requires q>p. Saturation is a structural assumption, not proof that the market cannot expand. Scenario curves are not a calibrated interval.

With no adoption history use defended analogue parameters and explicit scenarios. With only sales units, obtain unique-adopter/cohort information or change the target; do not treat cumulative repeat sales as cumulative adoption.

The applied deliverable must make these items inspectable: `results.csv` columns: `time,ceiling,bass_trials,gamma_trials,bass_units,gamma_units`; `summary.json` keys: `fits,ceilings,sales_horizon,peak,kernel,timing_comparison,parfitt_collins,bass_table_rows` plus method, interpretation, assumptions, not_done and status. Show both timing curves; the same eventual total can put half the first year in a different quarter.

## Three exercises with worked solutions

### Exercise 1

p=.01,q=.2,m=1000,N=100: incidence?

**Worked solution.** (.01+.2×.1)×900=27 adopters per time unit.

### Exercise 2

If q<=p, should a negative interior peak time be forecast?

**Worked solution.** No. The interior formula does not describe a future peak; incidence is highest at or near launch under the basic model.

### Exercise 3

Cumulative sales are 10,000 but include three purchases per buyer. Are there 10,000 adopters?

**Worked solution.** No. Unique adopter counts require separate evidence; repeat units cannot be silently equated with adoption.

## Business-reader application

Use this request with the skill:

> Apply chapter 19 to adoption.csv, defend several market ceilings and show which long-run differences are unsupported by the early history.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
