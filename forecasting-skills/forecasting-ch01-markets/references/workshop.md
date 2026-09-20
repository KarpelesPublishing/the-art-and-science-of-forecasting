# Chapter 1 workshop: from lesson to decision

## Explain the mechanism

A price aggregates information through a market mechanism, but the resulting forecast contains frictions and incentives. OHLC summarizes within-period movement. A visually plausible pattern must beat a predeclared baseline after the information cutoff.

## Work through the arithmetic

If the last two closes are 100 and 103, persistence predicts 103. A one-step extrapolation of the latest change predicts 106. If the next close is 102, absolute errors are 1 and 4. One example favors persistence but does not establish its general superiority.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace the simulated price/OHLC arrays with an adjusted, single-contract series. Preserve the difference between the partial-adjustment mechanism and the forecasting comparison: assumed information shocks are not measured market fundamentals. Retain a calendar of market sessions, rather than imputing holiday prices as new trades.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: Is the target spot, futures or an event-contract price? What is the quote frequency? When could the signal have been known? Are transaction costs relevant?

## Interpret the actual lesson outputs

Candles depict synthetic ranges. The adjustment plot assumes an information-processing rule; its speed is not estimated from a real market. The repeated random-walk comparison evaluates a prespecified momentum rule on 400 controlled paths, not a trading backtest or proof of market efficiency.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,actual,persistence,momentum,mean_reversion,actual_direction,momentum_hit,mean_reversion_hit`.
- `summary.json`: `rules,k,train_fraction,test_rows,mae,hit_rate,hit_rate_p_value,benford` plus method, interpretation, assumptions, not_done and status.

The tool scores predeclared one-step rules on closing prices at every origin after the training share: persistence (last close), momentum (last close plus the average change over `k` periods) and mean reversion (mean of the last `k` closes). It reports MAE per rule, the directional hit rate of momentum and mean reversion with zero-change periods excluded and a binomial p-value against a coin, and a Benford first-digit chi-square test on `benford_column` as a data-integrity habit. It computes price error only: no returns, costs, position sizing, sessions or corporate-action checks. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

The [fixture](../../../companion/data/examples/ch01.csv) and [config](../../../companion/configs/ch01.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Check sensitivity to lookback, corporate-action treatment and quote timing. Futures carry and risk premia prevent a simple expected-spot interpretation. Event-market probabilities additionally need defensible contract resolution and market assumptions. Price forecasts alone do not establish profitable trades.

With close-only data, omit candlesticks and use close-based baselines. Without a reliable adjustment history, segment at discontinuities or state that change forecasts are unreliable. No historical data supports only a mechanism illustration.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,actual,persistence,momentum,mean_reversion,actual_direction,momentum_hit,mean_reversion_hit`; `summary.json` keys: `rules,k,train_fraction,test_rows,mae,hit_rate,hit_rate_p_value,benford` plus method, interpretation, assumptions, not_done and status. A hit rate of 56 percent on 44 observations has a coin-flip p-value near a half; say so before anyone trades on it.

## Three exercises with worked solutions

### Exercise 1

OHLC is 100,99,98,101. Is it valid?

**Worked solution.** No: the reported high 99 is below open 100 and close 101. Correct the record from source or exclude it with a reason.

### Exercise 2

Last close is 80, next actual 77. What is persistence absolute error?

**Worked solution.** The prediction is 80 and absolute error is 3 price units.

### Exercise 3

A momentum lookback was chosen after comparing the last month. Can that month remain final test?

**Worked solution.** No. It is now selection data; evaluate on later untouched observations.

## Business-reader application

Use this request with the skill:

> Use chapter 1 to audit prices.csv and compare a prespecified momentum rule with persistence on later matched observations. Separate prediction error from trading profitability.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
