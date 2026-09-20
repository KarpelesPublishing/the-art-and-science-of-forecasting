---
name: forecasting-ch13-retail-ml
description: "Use when related retail series and known calendar, price or promotion features may support a pooled tree forecast, or studying forecasting book chapter 13."
---

# Chapter 13: The Walmart War Room

## Scope and intake

Use when related retail series and known calendar, price or promotion features may support a pooled tree forecast. Do not use for claiming a rolling one-day-ahead exercise is a fixed-origin multiweek forecast, or interpreting SHAP as causal lift.

Ask only for unresolved material inputs: Is the decision daily one-step replenishment or a fixed-origin horizon? Were promotions and prices known then? Are sales censored by stockouts? What defines a series?

## Input contract and additional evidence

A panel of at least four related series with any number of numeric covariate columns. Declare the covariates to use in config `covariates` and, within them, those whose future values are genuinely known at the forecast origin in `known_in_advance` (a promotion calendar, a list price). Covariates not known in advance are lagged one period by the tool; they never enter at their own timestamp.

Minimal **format illustration**, not sufficient training data:

```csv
series_id,timestamp,target,promo,price
item-0,2021-01-01,53.8,0,10
item-0,2021-01-02,55.1,1,8
item-1,2021-01-01,41.2,0,10
```

## Executable interface

Exact CLI columns: `series_id,timestamp,target[,covariates...]`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `ablation, as_of, covariates, frequency, horizon, known_in_advance, lags, origins, rolling, season, seed, shap_rows, strategy`. Unknown config keys are rejected.

LightGBM on leakage-safe grouped features: lags (`lags`), shifted rolling means (`rolling`), a calendar term (day of week for daily data, month otherwise), an entity code, and the declared covariates. `strategy: direct` (default) fits one booster per horizon step, each mapping the origin's lag features plus the target date's known covariates and calendar to that step's target; `recursive` fits a one-step model and feeds its own predictions back as lags. Evaluation uses expanding origins (`origins`) against seasonal naive computed from pre-origin history, then scores the untouched final holdout once. `ablation: true` drops each feature group (calendar, lags, rolling, covariates) in turn at every origin and reports the change in MAE. Additive contributions are returned for `shap_rows` rows with an additivity check. No hyperparameter search, no quantile objective.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Audit series keys, calendar gaps, stockouts and covariate publication times. Define exactly when each target becomes known.
2. Build grouped lag and rolling features with a shift before rolling. Derive calendar features without target information; fit encodings on training data.
3. Fit LightGBM on earlier data at chronological origins. Compare seasonal-naive and feature-ablation models on the same daily one-step targets.
4. Update observed lag inputs only as each day passes. For a fixed-origin multi-step request, implement recursive or horizon-safe direct features rather than consuming future actuals.
5. Inspect errors by series, promotion status and volume. Explain selected predictions with native contributions, retaining their baseline sum and predictive, not causal, meaning.

## Diagnostics, selection and uncertainty

Removing promotion while retaining discount price may leave the same information. Ablate dependent feature groups. Check negative predictions, lag availability and error concentration in sparse series. TreeSHAP allocations among correlated features depend on the model and are not identified marketing effects.

## Missing evidence and fallback

If LightGBM is unavailable, name the skipped model and run an eligible baseline; do not relabel a substitute. If future prices are unknown, use a known schedule or scenarios. If demand is censored, separate observed sales prediction from latent demand estimation. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

`results.csv` columns: `series_id,timestamp,horizon,actual,seasonal_naive,prediction`. `summary.json` keys: `strategy,features,feature_groups,covariates,known_in_advance,validation,ablation,test_mae,baseline_mae,first_explanation,origins` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`. State which covariates were treated as known in advance; a forecast that assumes next month's price is known must say so. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 13 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 13 to forecast retail_panel.csv one day ahead, audit every feature’s availability and compare LightGBM with seasonal-naive and a promotion/price ablation.”

The [notebook](../../companion/notebooks/13-retail-ml.ipynb) is a worked lesson; its editable [source](../../companion/lessons/13-retail-ml.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 13
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch13.csv) and [editable config](../../companion/configs/ch13.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 13 \
  --input companion/data/examples/ch13.csv \
  --config companion/configs/ch13.json \
  --output companion/applied-runs/ch13-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `series_id,timestamp,target,baseline,one_step,fixed_origin`, `summary.json` containing `mae,first_explanation`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
