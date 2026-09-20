---
name: forecasting-ch21-supply-chain
description: "Use when inventory decisions, bullwhip amplification or intermittent demand need forecast-policy evaluation, or studying forecasting book chapter 21."
---

# Chapter 21: The Bullwhip

## Scope and intake

Use when inventory decisions, bullwhip amplification or intermittent demand need forecast-policy evaluation. Do not use for choosing a supply-chain policy from forecast MAE alone while ignoring lead times and shortage costs.

Ask only for unresolved material inputs: Are zeros true zero demand or stockouts? What lead time and review cadence apply? Are backlogs allowed? What underage/overage costs matter? Is end-customer demand visible upstream?

## Input contract and additional evidence

A regular demand series, zeros allowed. Declare the replenishment `lead_time` and `review_period` in periods of the series, the target cycle `service_level`, and the shortage and excess costs. Sales recorded during stockouts understate demand; say so in `source` if that is what the file holds.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target
2010-01-01,0
2010-02-01,3
2010-03-01,0
2010-04-01,7
```

## Executable interface

Exact CLI columns: `timestamp,target`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `underage_cost, overage_cost, lead_time, review_period, service_level, bootstrap_window, samples, echelons, holding_cost, backorder_cost, horizon, season, frequency, as_of, seed`. Unknown config keys are rejected.

The tool produces pre-update Croston, SBA and TSB one-step forecasts and their MAE over the test period, then simulates an order-up-to policy: at each review it bootstraps `samples` sums of `lead_time + review_period` draws from the trailing `bootstrap_window` demands, sets the order-up-to level at the `service_level` quantile (the cost-optimal quantile is reported beside it), receives pipeline arrivals, serves backlog then demand, and records on-hand, backlog and orders, yielding achieved cycle service, fill rate, mean on-hand, mean backlog and mean cost. It also runs an `echelons`-deep bullwhip simulation on the same demand, reporting variance amplification per echelon with local ordering and with a shared end-consumer signal. Lead time is fixed; demand is treated as uncensored.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Distinguish observed sales from unconstrained demand and genuine zeros from missing or censored periods. Summarize demand occurrence and positive-demand sizes.
2. Generate pre-update Croston, SBA and TSB estimates with declared initialization, and compare against eligible simple baselines at chronological origins.
3. Translate demand uncertainty into a stocking objective using lead time and explicit shortage/overage costs. Score realized decision costs as well as forecast loss.
4. For chain analysis simulate inventory conservation, pipeline arrivals and ordering rules after a warm-up. Compare local-information and shared-demand policies only if both are actually implemented on common demand paths.
5. Report service, backlog and order amplification alongside costs; test lead-time and obsolescence sensitivity.

## Diagnostics, selection and uncertainty

TSB updates occurrence probability even during zeros; Croston updates at positive events and can remain elevated after obsolescence. Demand classification is descriptive, not model selection. A bullwhip variance ratio depends on policy and initialization; exclude a justified warm-up.

## Missing evidence and fallback

If stockouts hide demand, forecast observed sales only or use a separately supported censoring method. Without costs, report service/quantity scenarios rather than one optimal order. Without pipeline information, the full policy is a scenario, not a reconstructed operation. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

`results.csv` columns: `timestamp,actual,Croston,SBA,TSB,order_up_to,cost_optimal_order_up_to,on_hand,backlog,order`. `summary.json` keys: `mae,lead_time,review_period,service_level,achieved_cycle_service,fill_rate,mean_on_hand,mean_backlog,mean_cost,bullwhip,training_quantile_order` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`. Report achieved cycle service and fill rate together with the target; a policy that hits 95 percent cycle service with a 60 percent fill rate is a different promise to the customer. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 21 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 21 to forecast intermittent demand.csv, distinguish zeros from stockouts and connect supported forecasts to explicit lead-time and inventory-cost assumptions.”

The [notebook](../../companion/notebooks/21-supply-chain.ipynb) is a worked lesson; its editable [source](../../companion/lessons/21-supply-chain.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 21
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch21.csv) and [editable config](../../companion/configs/ch21.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 21 \
  --input companion/data/examples/ch21.csv \
  --config companion/configs/ch21.json \
  --output companion/applied-runs/ch21-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,actual,Croston,SBA,TSB`, `summary.json` containing `mae,training_quantile_order,test_mean_cost`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
