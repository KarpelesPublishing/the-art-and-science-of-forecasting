# Chapter 20 workshop: from lesson to decision

## Explain the mechanism

Carryover changes when spend can matter; saturation changes marginal response. Neither transformation resolves why spend was high when demand was high. Attribution is a decomposition conditional on a model, whereas incrementality asks what would happen under a different intervention.

## Work through the arithmetic

Geometric stock a[t]=spend[t]+.5a[t-1] with initial stock 20 and new spend 100 gives 110, not 100. At half-saturation 100, response a/(100+a) is 110/210=.52381. A zero-start assumption gives .5 and shifts the explanatory feature even before regression.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace weekly sales and media construction with synchronized observed series and documented controls. Obtain pre-window spend to initialize stock. Keep the confounding experiment and prior-stability experiment as separate controlled illustrations rather than mixing their synthetic truths into business estimation.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: Is the question predictive sales, incremental effect or launch volume? What pre-window spend exists? Which demand drivers affect both spend and sales? What experimental calibration or defensible external priors exist?

## Interpret the actual lesson outputs

The lesson executes a transformed two-channel regression, then distinct attribution-stability and initial-state experiments. Gaussian posterior rows condition on fixed background, transforms and noise; they are not full Bayesian MMM. The oracle baseline is known only in simulation. Launch timing is a separate workflow with chapter-27 transfer safeguards.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,actual,prediction,baseline`.
- `summary.json`: `channels,controls,selected,alpha,coefficients,condition_number,test_mae,baseline_mae,response_curves,marginal_roas,refits,posterior,reallocation,origins` plus method, interpretation, assumptions, not_done and status.

For every channel the tool builds a geometric adstock and a saturation transform (`hill`, `log`, `negexp`, `none`, or `auto` to choose among them), choosing each channel's decay from `decay_grid` and the saturation kind on `origins` earlier blocks by predictive MAE, never on the holdout; the saturation scale is fixed on training data. It fits sales on trend, one seasonal harmonic, the transformed channels and standardised controls by closed-form ridge (`alpha`, penalising channel and control columns only), scores the untouched holdout against seasonal naive, and returns response curves and marginal response at current spend per channel, coefficient refits across `windows` expanding windows (attribution stability), an optional Gaussian posterior on the channel coefficients when `prior_mean` and `prior_sd` are supplied, and a budget reallocation that equalises marginal response under `reallocation_total`, labelled a conditional scenario. No experiment is used; coefficients are a fitted decomposition, not identified causal effects. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

The [fixture](../../../companion/data/examples/ch20.csv) and [config](../../../companion/configs/ch20.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

An accurate total forecast can hide unstable channel coefficients; a fixed but wrong baseline can produce stable wrong attribution. Keep initial stock separate from the intercept. Sensitivity to correlated media, priors and nuisance components belongs in the result.

Without pre-window history, vary initial stocks and disclose transient uncertainty. Without credible confounder or experiment evidence, do not infer incrementality. With missing channels or inconsistent currencies, narrow the scope rather than quietly assigning residual sales to observed media.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,actual,prediction,baseline`; `summary.json` keys: `channels,controls,selected,alpha,coefficients,condition_number,test_mae,baseline_mae,response_curves,marginal_roas,refits,posterior,reallocation,origins` plus method, interpretation, assumptions, not_done and status. Report the refit table beside the coefficients; a channel whose coefficient halves when the window moves has not been attributed, whatever the point estimate says.

## Three exercises with worked solutions

### Exercise 1

Decay .8, previous stock 50, current spend 10: new stock?

**Worked solution.** 10+.8×50=50.

### Exercise 2

A fixed baseline stabilizes channel coefficients but has no external support. Has identification improved?

**Worked solution.** Not established. The coefficients may be stably biased; test plausible backgrounds and seek stronger identification evidence.

### Exercise 3

A response curve has Hill exponent 2. Must it be globally concave?

**Worked solution.** No. It can be S-shaped; do not impose a universal diminishing-return interpretation over its full range.

## Business-reader application

Use this request with the skill:

> Apply chapter 20 to weekly_media.csv, account for initial carryover, evaluate sales prediction and attribution stability, and label which spending claims remain conditional.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
