---
name: forecasting-ch16-prophet
description: "Use when a business series has defensible calendar effects and changing trend suitable for Prophet, or studying forecasting book chapter 16."
---

# Chapter 16: The Prophet

## Scope and intake

Use when a business series has defensible calendar effects and changing trend suitable for Prophet. Do not use for treating an automatically fitted holiday component as a causal campaign effect.

Ask only for unresolved material inputs: Which calendar events were known at the origin? Is their effect repeated in history? What trend flexibility is plausible? Which future regressors are actually supplied?

## Input contract and additional evidence

A regular series with optional numeric regressor columns. Events go in config `events` as a list of `{name, date, lower_window, upper_window}` (future event dates are welcome). Regressors are named in config `regressors`; to forecast the future with regressors, append exactly `horizon` trailing rows with an empty `target` and the known regressor values.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target,temp
2022-01-01,101.3,20.1
2022-01-02,103.7,20.9
2022-01-03,,21.4
```

## Executable interface

Exact CLI columns: `timestamp,target[,regressors...]`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, events, frequency, horizon, mode, origins, priors, regressors, season, seed, weekly, yearly`. Unknown config keys are rejected.

Prophet with the event calendar as holidays and the declared regressors. `mode: auto` chooses multiplicative seasonality when a Box-Cox check on training data calls for a log scale, else additive. The changepoint prior is chosen from `priors` on `origins` earlier blocks; the calendar and the regressors are each ablated on the same blocks so their contribution is measured, not assumed. The untouched holdout is scored once with MAE and the coverage of the nominal 80 percent band. The forecast table is the future when no regressors are needed or exactly `horizon` future regressor rows were supplied, otherwise the holdout, and the summary says which under `table_scope`.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Audit the calendar, target gaps and event-date provenance. Decide additive versus multiplicative components from units and behavior, not default habit.
2. Reserve a final horizon; compare a small changepoint-prior grid at earlier chronological origins with appropriate baselines.
3. Fit actual Prophet on past observations with known event dates, freezing the selected settings before final evaluation.
4. Inspect trend, seasonal and event components and reconstruct yhat according to the fitted mode. Compare a calendar ablation at matched dates.
5. Export forecasts and nominal intervals; evaluate coverage and residual behavior by event/non-event dates. Define how stale calendar information will be detected.

## Diagnostics, selection and uncertainty

Model components are fitted explanations, not independently observed causal effects. A good additive synthetic result favors that generator. MAP intervals omit some parameter uncertainty and can fail under breaks. Do not select flexibility using the final test.

## Missing evidence and fallback

Without repeated event history, use a stated event scenario or omit unsupported event estimation. If future regressors are unknown, provide conditional forecasts. If Prophet is unavailable, name the missing dependency and use a labeled baseline. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

`results.csv` columns: `timestamp,lower,forecast,upper`. `summary.json` keys: `mode,mode_note,prior,validation,ablation,test_mae,test_coverage,nominal,table_scope,events,regressors` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`. Quote the ablation: if removing the calendar barely changes validation MAE, the calendar is decoration and the report should say so. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 16 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 16 to forecast activity.csv with the actual known event calendar, select trend flexibility on earlier origins and explain components and held-out uncertainty.”

The [notebook](../../companion/notebooks/16-prophet.ipynb) is a worked lesson; its editable [source](../../companion/lessons/16-prophet.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 16
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch16.csv) and [editable config](../../companion/configs/ch16.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 16 \
  --input companion/data/examples/ch16.csv \
  --config companion/configs/ch16.json \
  --output companion/applied-runs/ch16-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,lower,forecast,upper`, `summary.json` containing `prior,validation_mae,test_mae`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
