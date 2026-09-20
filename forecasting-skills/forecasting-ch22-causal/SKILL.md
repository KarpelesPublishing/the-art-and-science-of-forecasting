---
name: forecasting-ch22-causal
description: "Use when an intervention effect needs a defended comparison rather than a purely predictive forecast, or studying forecasting book chapter 22."
---

# Chapter 22: The Causal Forecaster

## Scope and intake

Use when an intervention effect needs a defended comparison rather than a purely predictive forecast. Do not use for treating pre-period fit, nonsignificant pretrends or plain OLS as proof of causal identification.

Ask only for unresolved material inputs: What treatment, alternative and population define the effect? When did treatment start? Why did it vary? Could controls be affected? What else changed at the same time?

## Input contract and additional evidence

A regular series with the treated outcome and at least one control series; name every control column in config `controls` (default `['control']`). Synthetic control and placebo-in-space need at least two, better three or more, controls. Declare `intervention` (the first treated timestamp) and write down the `identification` argument before running.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,control,control_2,control_3,treated
2010-01-01,99.9,80.7,49.1,104.3
2010-02-01,100.3,81.0,52.4,105.1
2010-03-01,100.1,80.9,47.8,104.6
```

## Executable interface

Exact CLI columns: `timestamp,control,treated[,controls...]`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `intervention, identification, controls, placebos, event_window, horizon, season, frequency, as_of, seed`. Unknown config keys are rejected.

The tool computes difference-in-differences, a pre-period OLS counterfactual on all declared controls, and, with two or more controls, a synthetic control with nonnegative weights summing to one fitted on the pre-period only. It then runs placebo-in-space (each control treated in turn against the remaining donors; the p-value is the treated unit's rank on post-effect over pre-RMSE), placebo-in-time (`placebos` pseudo interventions inside the pre period; p is the share at least as large as the estimate), and an event-study table of per-period effects over `event_window` pre periods and all post periods with a pre-trend slope test. Every estimate is conditional on the declared identification; the tool does not decide whether the comparison is defensible.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Define the causal estimand and assignment/comparison argument before fitting. Record reasons controls approximate untreated outcomes and threats from co-interventions.
2. Choose pre/post windows without optimizing the result. Plot pretrends and inspect timing, composition and spillovers.
3. Compute DiD from pre and post changes. Separately fit a pre-period control regression and project its untreated counterfactual with post controls only if those remain unaffected.
4. Run placebos and sensitivity cases targeted at plausible failures, including a treated-only post shock. Treat reassuring checks as limited evidence, not proof.
5. Return effect estimates conditional on assumptions or an unidentified scenario when the comparison fails. Specify the feasible informative experiment or missing evidence that could distinguish explanations.

## Diagnostics, selection and uncertainty

Estimation necessarily uses post outcomes; model/design selection must not chase the effect. Serial and group dependence require suitable inference, not naive independent row standard errors. Pretrend tests cannot rule out future differential shocks.

## Missing evidence and fallback

With no credible unaffected comparator or assignment argument, report observed changes and bounded scenarios rather than causal lift. If prehistory is short, disclose weak trend diagnostics. An experiment is useful only if ethical, feasible, adequately powered and uncontaminated. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Chapter-specific invariants

Separate prediction, causal effect and decision. Define treatment/reference condition,
population, timing, outcome and effect horizon. Choose the identification argument
before the model: why did treatment vary, what else changed, and what comparison
represents the untreated outcome?

- Adjustment: defend measured pre-treatment common causes and overlap; do not
  indiscriminately condition on treatment consequences or colliders.
- DiD: defend parallel untreated trends, no anticipation and the absence of relevant
  spillovers or differential concurrent shocks, or model their effects explicitly.
  Estimation uses pre AND post outcomes; only
  counterfactual-model fitting/design selection is confined to earlier information.
- Cutoff design: defend continuity/no manipulation/no coincident rule changes and
  report its local scope.
- Instrument/natural variation: defend assignment, relevance and exclusion of
  other outcome pathways, plus the assumptions needed for the chosen estimand.

Use placebo/pretrend and sensitivity checks to find weaknesses, not certify truth.
Prefer an ethical, feasible and sufficiently informative experiment when a material
decision remains unidentified. Check power, compliance, contamination and horizon.
If neither design supports identification, return scenarios and missing evidence.
Observational causality is possible under defensible assumptions, not impossible
by definition and not established by a good predictive fit.

Pretrend nonsignificance does not prove identification; plain OLS is not BSTS/CausalImpact and predictive fit is not causal validity.

## Applied report contract

`results.csv` columns: `timestamp,observed,ols_counterfactual,ols_effect,post,relative_period[,sc_counterfactual,sc_effect]`. `summary.json` keys: `did,post_mean_effect,pre_rmse,sc_weights,sc_post_mean_effect,sc_pre_rmse,placebo_space,placebo_time,event_study,pretrend,identification,controls` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`. Quote the placebo p-values and the pre-trend flag with the effect; an effect without them is a difference, not evidence. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 22 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 22 to intervention.csv, state the identifying assumptions before computing effects, and show how a plausible concurrent shock changes the interpretation.”

The [notebook](../../companion/notebooks/22-causal.ipynb) is a worked lesson; its editable [source](../../companion/lessons/22-causal.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 22
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch22.csv) and [editable config](../../companion/configs/ch22.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 22 \
  --input companion/data/examples/ch22.csv \
  --config companion/configs/ch22.json \
  --output companion/applied-runs/ch22-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,observed,counterfactual,effect,post`, `summary.json` containing `did,post_mean_effect,pre_rmse,identification`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
