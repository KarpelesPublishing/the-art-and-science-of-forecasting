# Chapter 21 workshop: from lesson to decision

## Explain the mechanism

Forecasts and replenishment decisions form a feedback system. Upstream orders include inventory corrections and may amplify consumer variation. For intermittent demand, occurrence and size carry different information; prolonged zeros need not be treated like small positive demand.

## Work through the arithmetic

With positive-demand estimate 5 and interval estimate 4, Croston predicts 1.25 units per period. At alpha=.2, SBA gives (1-.1)×1.25=1.125. TSB with occurrence probability .25 predicts 1.25; after a zero at alpha=.2, probability becomes .2 and the next forecast is 1.0. For underage 9 and overage 3, the optimal single-period CDF quantile is .75.

## Adapt the lesson to reader data

Replace observed in the intermittent block with a complete nonnegative demand calendar. Replace demand in the chain block only after setting realistic inventory and lead times. The original lesson’s shared-information comparison is an exercise; add and verify that policy explicitly before reporting improvement.

For this chapter, settle these questions before fitting: Are zeros true zero demand or stockouts? What lead time and review cadence apply? Are backlogs allowed? What underage/overage costs matter? Is end-customer demand visible upstream?

## Interpret the actual lesson outputs

The chain conserves net inventory including backlogs and reports variance after warm-up. The stocking curve uses a known synthetic normal demand distribution. Intermittent forecasts are recorded before each observation update, so their response to the eventual all-zero regime can be evaluated without hindsight.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,actual,Croston,SBA,TSB,order_up_to,cost_optimal_order_up_to,on_hand,backlog,order`.
- `summary.json`: `mae,lead_time,review_period,service_level,achieved_cycle_service,fill_rate,mean_on_hand,mean_backlog,mean_cost,bullwhip,training_quantile_order` plus method, interpretation, assumptions, not_done and status.

The tool produces pre-update Croston, SBA and TSB one-step forecasts and their MAE over the test period, then simulates an order-up-to policy: at each review it bootstraps `samples` sums of `lead_time + review_period` draws from the trailing `bootstrap_window` demands, sets the order-up-to level at the `service_level` quantile (the cost-optimal quantile is reported beside it), receives pipeline arrivals, serves backlog then demand, and records on-hand, backlog and orders, yielding achieved cycle service, fill rate, mean on-hand, mean backlog and mean cost. It also runs an `echelons`-deep bullwhip simulation on the same demand, reporting variance amplification per echelon with local ordering and with a shared end-consumer signal. Lead time is fixed; demand is treated as uncensored. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Decide what the evidence supports

TSB updates occurrence probability even during zeros; Croston updates at positive events and can remain elevated after obsolescence. Demand classification is descriptive, not model selection. A bullwhip variance ratio depends on policy and initialization; exclude a justified warm-up.

If stockouts hide demand, forecast observed sales only or use a separately supported censoring method. Without costs, report service/quantity scenarios rather than one optimal order. Without pipeline information, the full policy is a scenario, not a reconstructed operation.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,actual,Croston,SBA,TSB,order_up_to,cost_optimal_order_up_to,on_hand,backlog,order`; `summary.json` keys: `mae,lead_time,review_period,service_level,achieved_cycle_service,fill_rate,mean_on_hand,mean_backlog,mean_cost,bullwhip,training_quantile_order` plus method, interpretation, assumptions, not_done and status. Report achieved cycle service and fill rate together with the target; a policy that hits 95 percent cycle service with a 60 percent fill rate is a different promise to the customer.

## Three exercises with worked solutions

### Exercise 1

Underage cost 4, overage cost 6: target quantile?

**Worked solution.** 4/(4+6)=.4.

### Exercise 2

A zero record occurs because shelves were empty. Is it a true no-demand event for TSB?

**Worked solution.** Not established. It is censored sales; treating it as no demand can suppress forecasts incorrectly.

### Exercise 3

Consumer variance 25 and order variance 100: amplification ratio?

**Worked solution.** 100/25=4, provided periods and warm-up treatment match.

## Business-reader application

Use this request with the skill:

> Use chapter 21 to forecast intermittent demand.csv, distinguish zeros from stockouts and connect supported forecasts to explicit lead-time and inventory-cost assumptions.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
