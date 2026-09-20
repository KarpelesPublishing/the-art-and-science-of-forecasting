---
name: forecasting-ch14-global-neural
description: "Use when many related short histories may benefit from a global probabilistic neural model, or studying forecasting book chapter 14."
---

# Chapter 14: The Globalizer

## Scope and intake

Use when many related short histories may benefit from a global probabilistic neural model. Do not use for claiming zero-observation transfer or calling the demonstrated Gaussian MLP DeepAR.

Ask only for unresolved material inputs: Which entities are related and which will be unseen at deployment? How much recent context exists? Is the outcome continuous, count or nonnegative? What horizon and distributional loss matter?

## Input contract and additional evidence

CSV series_id,timestamp,target with regular ordered observations per entity. Config context,horizon,season,epochs. The CLI holds out the last quarter of sorted entity groups; use notebook adaptation for a different declared entity split. The Gaussian MLP assumes a continuous response; test entities still need observed context.

Minimal **format illustration**, not sufficient training data:

```csv
series_id,timestamp,target
A,2026-01-01,20
A,2026-01-02,22
B,2026-01-01,60
```

## Executable interface

Exact CLI columns: `series_id,timestamp,target`. Supported method controls: `as_of, context, epochs, frequency, horizon, season, seed`.

At least four aligned related series are required. The last quarter of sorted entity groups is held out, not a user-configurable split. The actual Gaussian MLP uses 100 recursive paths for nominal 80% bands. It does not implement DeepAR or tune hyperparameters on held-out entities.

## Applied procedure

1. Define time and entity holdouts before feature creation. Exclude test entities from model fitting if claiming transfer to unseen entities.
2. Build lag contexts and scale each example using only its available context. Keep calendar alignment consistent across entities.
3. Train the actual Gaussian-output MLP with a positive scale parameter and record architecture, seed and training examples. Select hyperparameters on earlier validation data.
4. At a fixed forecast origin, sample recursively: each path feeds its own generated value into subsequent lags. Compare with a local baseline receiving the same observed context.
5. Evaluate error, interval width and empirical coverage by entity and horizon. Investigate negative support, poor transfer and distribution shift before deployment.

## Diagnostics, selection and uncertainty

Lower training loss does not establish generalization. Gaussian likelihood can assign impossible negative demand. Coverage from many dependent horizon rows is not equivalent to the same count of independent forecast cases. Test entity exclusion and time cutoff explicitly.

## Missing evidence and fallback

With one or a few unrelated series, use a local baseline rather than assuming pooling helps. With no context for a new entity, the demonstrated model is unsupported. If the required neural dependency is missing, report the skipped method honestly.

## Applied report contract

`results.csv` columns: `series_id,timestamp,actual,baseline,lower,median,upper`. `summary.json` keys: `training_entities,held_out_entities,coverage,interval_score,mae,baseline_mae` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return entity/time split, context and scaling rules, model/training record, sampled forecast quantiles, local-baseline comparison and coverage/width by entity and horizon.

## Run it

The [notebook](../../companion/notebooks/14-global-neural.ipynb) is the worked lesson; its editable [source](../../companion/lessons/14-global-neural.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 14 \
  --input companion/data/examples/ch14.csv \
  --config companion/configs/ch14.json \
  --output companion/applied-runs/ch14-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 14`.

Learning prompt: “Teach me chapter 14 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 14 to panel.csv with an explicit unseen-entity holdout, compare the actual global Gaussian MLP with local baselines and report uncertainty limitations.”
