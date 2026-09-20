---
name: forecasting-ch20-marketing-mix
description: "Use when media carryover, response saturation or attribution stability must be assessed against business sales, or studying forecasting book chapter 20."
---

# Chapter 20: The Marketing Mix

## Scope and intake

Use when media carryover, response saturation or attribution stability must be assessed against business sales. Do not use for confusing prelaunch trial calibration with retrospective MMM, or certifying causal ROI from predictive fit.

Ask only for unresolved material inputs: Is the question predictive sales, incremental effect or launch volume? What pre-window spend exists? Which demand drivers affect both spend and sales? What experimental calibration or defensible external priors exist?

## Input contract and additional evidence

A regular series of `sales` with one nonnegative spend column per channel and any numeric control columns (weather, price, competitor activity). Name the channels in config `channels` and the controls in `controls`. The older two-channel example (`spend_a,spend_b` with fixed `decay_a`, `half_a`, ...) still runs unchanged.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,sales,tv,digital,radio,temp
2010-01-01,131.2,54.0,22.5,8.1,-0.4
2010-02-01,128.7,61.3,19.0,12.6,0.2
2010-03-01,140.9,12.8,70.4,3.3,1.1
```

## Executable interface

Exact CLI columns: `timestamp,sales,<channels...>[,controls...]`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `alpha, as_of, channels, controls, decay_a, decay_b, decay_grid, frequency, half_a, half_b, horizon, initial_a, initial_b, noise_sd, origins, prior_mean, prior_sd, reallocation_total, saturation, season, seed, windows`. Unknown config keys are rejected.

For every channel the tool builds a geometric adstock and a saturation transform (`hill`, `log`, `negexp`, `none`, or `auto` to choose among them), choosing each channel's decay from `decay_grid` and the saturation kind on `origins` earlier blocks by predictive MAE, never on the holdout; the saturation scale is fixed on training data. It fits sales on trend, one seasonal harmonic, the transformed channels and standardised controls by closed-form ridge (`alpha`, penalising channel and control columns only), scores the untouched holdout against seasonal naive, and returns response curves and marginal response at current spend per channel, coefficient refits across `windows` expanding windows (attribution stability), an optional Gaussian posterior on the channel coefficients when `prior_mean` and `prior_sd` are supplied, and a budget reallocation that equalises marginal response under `reallocation_total`, labelled a conditional scenario. No experiment is used; coefficients are a fitted decomposition, not identified causal effects.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Separate the estimand: forecast sales under a schedule, attribute fitted components, or estimate incremental intervention effects. Document identification assumptions before optimization.
2. Audit spend/outcome frequency, channel correlation, pre-window carryover and potential common causes. Set or estimate transforms within training data.
3. Construct adstock with explicit initial state; transform stock through the stated saturation curve. Fit sales with justified trend/seasonality/background controls.
4. Evaluate chronological prediction with spend schedules known at each origin. Refit across windows, background assumptions and defensible priors to examine attribution stability.
5. Report predictive and attribution conclusions separately. Use experiments or a defensible causal design for material spend-response claims; if unavailable, return conditional scenarios rather than identified ROI.

## Diagnostics, selection and uncertainty

An accurate total forecast can hide unstable channel coefficients; a fixed but wrong baseline can produce stable wrong attribution. Keep initial stock separate from the intercept. Sensitivity to correlated media, priors and nuisance components belongs in the result.

## Missing evidence and fallback

Without pre-window history, vary initial stocks and disclose transient uncertainty. Without credible confounder or experiment evidence, do not infer incrementality. With missing channels or inconsistent currencies, narrow the scope rather than quietly assigning residual sales to observed media. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Chapter-specific invariants

For MMM, use this chapter's tool (`run.py apply --chapter 20` with named channel
columns): compare predictive accuracy AND attribution stability across refits,
plausible backgrounds and priors.
Separate initial carryover from background sales; guessed fixed effects can be
stably wrong. Removing an intercept or relevant controls does not earn causality.

For launch calibration, use [chapter 27](../forecasting-ch27-directed-forecasting/SKILL.md).
Calibrate shared assumptions across as many comparable established products as
possible; retain held-out products. Final awareness/distribution levels affect
potential volume, while their development supplies all delays. Gamma timing is an
alternative representation of that development, not an extra multiplier. Standard
mode=4 months with 80% of the full 24-month trial total in year one; faster=3
gives a larger first-year share and slower=5 a smaller one. This is the author's
confirmed standard. Extend the horizon or use eventual trials only for an
explicitly different scenario; see chapter 27 for the gamma formula and calculation.
Research-age relevance is not automatic demand decay; separate trial from repeat units.

Observational attribution and SHAP credit are not automatically causal lift. Use
chapter 22 to assess observational identification and whether an informative
experiment is needed. Bayesian priors can use real external evidence but must be
sensitivity-tested; fixed assumptions deserve the same scrutiny. Avoid universal
ROI caps and claims that all Hill curves are concave. The notebook's Gaussian
posterior is conditional on fixed transforms/background/noise, not full Bayesian MMM.

## Applied report contract

`results.csv` columns: `timestamp,actual,prediction,baseline`. `summary.json` keys: `channels,controls,selected,alpha,coefficients,condition_number,test_mae,baseline_mae,response_curves,marginal_roas,refits,posterior,reallocation,origins` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`. Report the refit table beside the coefficients; a channel whose coefficient halves when the window moves has not been attributed, whatever the point estimate says. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 20 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 20 to weekly_media.csv, account for initial carryover, evaluate sales prediction and attribution stability, and label which spending claims remain conditional.”

The [notebook](../../companion/notebooks/20-marketing-mix.ipynb) is a worked lesson; its editable [source](../../companion/lessons/20-marketing-mix.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 20
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch20.csv) and [editable config](../../companion/configs/ch20.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 20 \
  --input companion/data/examples/ch20.csv \
  --config companion/configs/ch20.json \
  --output companion/applied-runs/ch20-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,actual,prediction`, `summary.json` containing `coefficients,condition_number,refits,test_mae`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.

## Desk model skill

For a launch forecast without a test market, use [reconcile-tdbu](../reconcile-tdbu/SKILL.md): it interviews for the inputs, runs the trial-and-repeat and market-share engines, reports the gap and the implied inputs, and reconciles them. Its constants are illustrative starting values; tune them to launches the user knows.
