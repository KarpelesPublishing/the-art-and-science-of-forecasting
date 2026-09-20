---
name: forecasting-ch17-probabilistic
description: "Use when forecast intervals or quantiles need scoring, calibration and decision interpretation, or studying forecasting book chapter 17."
---

# Chapter 17: Living with Probability

## Scope and intake

Use when forecast intervals or quantiles need scoring, calibration and decision interpretation. Do not use for calling scenario endpoints calibrated probability bounds without evidence.

Ask only for unresolved material inputs: What nominal coverage or quantiles are claimed? Were forecasts issued before outcomes? What horizons and groups need coverage? Is a separate calibration period available?

## Input contract and additional evidence

Either a plain series `timestamp,target`, from which the tool builds and checks its own intervals, or intervals you already issued as `timestamp,actual,lower,median,upper`, which it only scores. The plain series needs enough history for training, a calibration block (`calibration_size`, default 36) and a later test block (`test_size`, default 24).

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target
2010-01-01,42.1
2010-02-01,44.8
2010-03-01,47.0
```

## Executable interface

Exact CLI columns: `timestamp,target | timestamp,actual,lower,median,upper`. Supported method controls: `alpha, as_of, calibration_size, frequency, gamma, horizon, origins, pool, season, seed, test_size, transform`.

On a plain series the tool selects a model with the companion engine on history before the calibration block, freezes that specification, refits it at every calibration origin to collect residuals by horizon step, and builds split-conformal intervals at level 1-`alpha` using the finite-sample rank ceil((m+1)(1-alpha)). It then runs the adaptive conformal update (alpha_t moves by `gamma` after each miss or cover) through the test block. Both intervals are scored on the test block: empirical coverage, mean width, interval score and pinball loss, per horizon step and pooled, and compared with the model's own nominal 80 percent band when one exists. If the engine selected a combination, the best atomic model is used and the summary says so. The split guarantee is marginal under exchangeability; the adaptive guarantee is long-run; neither is conditional coverage at a given date.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Audit forecast timing, interval order and nominal level. Align actuals to the target interval’s unit and horizon.
2. Compute empirical coverage and average width, alongside interval score: width+(2/alpha)×distance below or above the interval.
3. Inspect coverage and score by horizon, time and business segment. Score quantiles with pinball loss when available; use PIT only for a supplied predictive CDF.
4. If calibrating, use an earlier calibration block after training and retain a still-later test. Use the corrected finite-sample rank rather than a casual interpolated quantile.
5. Report dependence, drift and sample-size limits; connect a chosen quantile to the action’s costs when those costs are known.

## Diagnostics, selection and uncertainty

Arbitrarily wide intervals achieve coverage at the cost of usefulness. Marginal coverage does not imply simultaneous path coverage or groupwise coverage. Exchangeable conformal guarantees do not automatically apply to serially dependent residuals.

## Missing evidence and fallback

With missing actuals, export unscored forecasts and pending evaluation status. With no separate calibration block, do not tune and claim test coverage on the same observations. With only scenario limits, preserve that label and do not compute claimed probability calibration.

## Applied report contract

`results.csv` columns: `timestamp,origin,horizon,actual,forecast,split_lower,split_upper,adaptive_lower,adaptive_upper,alpha_t,covered_split,covered_adaptive,model_lower,model_upper,interval_score_split,interval_score_adaptive`. `summary.json` keys: `selected,alpha,gamma,calibration_rows,test_rows,radius,coverage,mean_width,interval_score,pinball,by_horizon,guarantee,calibration_block,test_block` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Report coverage and width together and by horizon; quote the test block dates so the reader can see the intervals were checked on data the model never fitted.

## Run it

The [notebook](../../companion/notebooks/17-probabilistic.ipynb) is the worked lesson; its editable [source](../../companion/lessons/17-probabilistic.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. [self-check.md](references/self-check.md) holds the three questions to answer before reporting. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 17 \
  --input companion/data/examples/ch17.csv \
  --config companion/configs/ch17.json \
  --output companion/applied-runs/ch17-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 17`.

Learning prompt: “Teach me chapter 17 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 17 to intervals.csv, score coverage and useful width by horizon, and distinguish any empirical recalibration from an unsupported guarantee.”
