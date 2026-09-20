# Chapter 18 workshop: from lesson to decision

## Explain the mechanism

Reconciliation projects conflicting forecasts onto the space where totals equal their parts. Bottom-up trusts the detailed forecasts; OLS spreads discrepancies geometrically; MinT weights directions by their forecast-error covariance.

## Work through the arithmetic

For total 210 and stores 90,105, the discrepancy is 15. Bottom-up sets total to 195 and retains stores. Equal-weight OLS adds 5 to each store and subtracts 5 from total, giving [205,95,110]. These values are coherent because 95+110=205; their accuracy still needs actual outcomes.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace S, base and historical error construction. Keep historical covariance data separate from test errors. The original source demonstrates bottom-up and MinT; if OLS is absent in the current lesson, add a W=I comparison in the applied copy rather than claiming the chart already contains it.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: What are the bottom-level quantities and summing relationships? Do nodes overlap? Are base forecasts for the same origin/horizon? Are historical forecast errors available to estimate covariance?

## Interpret the actual lesson outputs

The 210-versus-195 example demonstrates inconsistency. The projection assertions check coherence and identity on already coherent vectors. Independent synthetic test errors assess accuracy under one known covariance process, not a retailer’s real distribution.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `node,timestamp,base,bottom_up,OLS[,MinT][,MinT_q10,MinT_q50,MinT_q90]`.
- `summary.json`: `nodes,leaves,S,selected,shrinkage,error_rows,holdout,leaderboard,coherence_max_abs_residual,pool,horizon` plus method, interpretation, assumptions, not_done and status.

The tool builds S from `edges`, forecasts every node with the companion engine (default `pool: smoothing`; `full` and `arima` are available), takes each node's base-forecast errors from the engine's own validation origins, shrinks their covariance toward the diagonal by `shrinkage` (default 0.2), and reconciles by bottom-up, OLS and MinT. Coherence is asserted for every reconciled column. Every method, including the unreconciled base, is scored per node on the untouched final holdout, so the leaderboard shows whether reconciliation helped this hierarchy rather than assuming it. `coherent_quantiles: true` reconciles 500 joint draws when every node's model has intervals and returns MinT q10/q50/q90. MinT is dropped, and reported under `not_done`, when fewer than n_nodes+2 matched errors exist or the covariance is not positive definite. Nonnegativity is not enforced. When the history is too short to hold the engine's rolling origins twice over (for monthly data with a 12-step horizon, fewer than 84 observations), the tool still reconciles the production forecasts but skips the holdout leaderboard, takes the error covariance from the engine's own rolling origins, returns `status: provisional` and says so under `not_done`. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

The [fixture](../../../companion/data/examples/ch18.csv) and [config](../../../companion/configs/ch18.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Check matrix conditioning, covariance sample size and sensitivity to shrinkage. MinT rests on estimated error structure. Nonnegative operational quantities may require a separately implemented constrained method; clipping node forecasts independently breaks coherence.

Without past errors, use bottom-up or clearly labeled OLS, not fabricated MinT covariance. If hierarchy mapping is ambiguous, return inconsistencies before fitting. If constraints are required but unsupported, report infeasibility rather than hiding negative nodes.

The applied deliverable must make these items inspectable: `results.csv` columns: `node,timestamp,base,bottom_up,OLS[,MinT][,MinT_q10,MinT_q50,MinT_q90]`; `summary.json` keys: `nodes,leaves,S,selected,shrinkage,error_rows,holdout,leaderboard,coherence_max_abs_residual,pool,horizon` plus method, interpretation, assumptions, not_done and status. Quote the holdout leaderboard beside the reconciled forecasts; a coherent forecast that lost accuracy on the holdout is a finding, not a success.

## Three exercises with worked solutions

### Exercise 1

Base [100,40,50]: bottom-up result?

**Worked solution.** [90,40,50].

### Exercise 2

No historical errors are available. Can W=I be called empirically estimated MinT?

**Worked solution.** No. Label it OLS/unweighted reconciliation; empirical covariance was not estimated.

### Exercise 3

A negative bottom node is clipped to zero without changing total. What can fail?

**Worked solution.** Coherence. Enforce nonnegativity jointly or disclose that a constrained reconciliation is needed.

## Business-reader application

Use this request with the skill:

> Use chapter 18 to reconcile hierarchy.csv using the supplied summing matrix, compare eligible methods and verify coherence without claiming accuracy from addition alone.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
