# Chapter 22 workshop: from lesson to decision

## Explain the mechanism

A counterfactual is the outcome that would have occurred without treatment. It is unobserved for treated units, so an effect estimate depends on a comparison argument. More sophisticated prediction cannot by itself supply missing identification.

## Work through the arithmetic

Treated rises from 100 to 120; control rises from 80 to 90. DiD is (120-100)-(90-80)=10. If an unrelated treated-only event contributed 6, the same observed DiD would combine treatment 4 and shock 6. The pre-period data cannot distinguish those explanations.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace treated/control/time arrays and intervention boundary with aligned observed outcomes. Keep candidate-control and pre-period selection separate from post-effect estimation. Do not label the regression block CausalImpact or BSTS; it is a pre-period OLS counterfactual.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: What treatment, alternative and population define the effect? When did treatment start? Why did it vary? Could controls be affected? What else changed at the same time?

## Interpret the actual lesson outputs

The controlled lesson has an eight-unit treatment effect. Adding a six-unit treated-only post shock preserves identical prehistory while increasing DiD by six. The placebo simulation describes a known generator; it is not a randomization p-value for an arbitrary observational dataset.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,observed,ols_counterfactual,ols_effect,post,relative_period[,sc_counterfactual,sc_effect]`.
- `summary.json`: `did,post_mean_effect,pre_rmse,sc_weights,sc_post_mean_effect,sc_pre_rmse,placebo_space,placebo_time,event_study,pretrend,identification,controls` plus method, interpretation, assumptions, not_done and status.

The tool computes difference-in-differences, a pre-period OLS counterfactual on all declared controls, and, with two or more controls, a synthetic control with nonnegative weights summing to one fitted on the pre-period only. It then runs placebo-in-space (each control treated in turn against the remaining donors; the p-value is the treated unit's rank on post-effect over pre-RMSE), placebo-in-time (`placebos` pseudo interventions inside the pre period; p is the share at least as large as the estimate), and an event-study table of per-period effects over `event_window` pre periods and all post periods with a pre-trend slope test. Every estimate is conditional on the declared identification; the tool does not decide whether the comparison is defensible. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

The [fixture](../../../companion/data/examples/ch22.csv) and [config](../../../companion/configs/ch22.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Estimation necessarily uses post outcomes; model/design selection must not chase the effect. Serial and group dependence require suitable inference, not naive independent row standard errors. Pretrend tests cannot rule out future differential shocks.

With no credible unaffected comparator or assignment argument, report observed changes and bounded scenarios rather than causal lift. If prehistory is short, disclose weak trend diagnostics. An experiment is useful only if ethical, feasible, adequately powered and uncontaminated.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,observed,ols_counterfactual,ols_effect,post,relative_period[,sc_counterfactual,sc_effect]`; `summary.json` keys: `did,post_mean_effect,pre_rmse,sc_weights,sc_post_mean_effect,sc_pre_rmse,placebo_space,placebo_time,event_study,pretrend,identification,controls` plus method, interpretation, assumptions, not_done and status. Quote the placebo p-values and the pre-trend flag with the effect; an effect without them is a difference, not evidence.

## Three exercises with worked solutions

### Exercise 1

Treated change 30, control change 12: DiD?

**Worked solution.** 18 outcome units under the design assumptions.

### Exercise 2

The control receives spillover advertising after launch. Is its post outcome a clean untreated comparator?

**Worked solution.** No. Spillover contaminates the counterfactual; use another defended design or report the limitation.

### Exercise 3

Pretrend p-value is .7. Does this prove parallel untreated future trends?

**Worked solution.** No. Nonsignificance does not establish the identifying assumption or rule out later shocks.

## Business-reader application

Use this request with the skill:

> Apply chapter 22 to intervention.csv, state the identifying assumptions before computing effects, and show how a plausible concurrent shock changes the interpretation.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
