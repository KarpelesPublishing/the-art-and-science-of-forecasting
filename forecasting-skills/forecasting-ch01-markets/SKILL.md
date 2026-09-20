---
name: forecasting-ch01-markets
description: "Use when market prices or trading signals need a persistence benchmark and information-timing audit, or studying forecasting book chapter 1."
---

# Chapter 1: The Market Discovers the Future

## Scope and intake

Use when market prices or trading signals need a persistence benchmark and information-timing audit. Do not use for investment allocation advice based only on chart patterns.

Ask only for unresolved material inputs: Is the target spot, futures or an event-contract price? What is the quote frequency? When could the signal have been known? Are transaction costs relevant?

## Input contract and additional evidence

A regular OHLC price series of at least 30 rows with consistent bounds (low at or below open and close, high at or above them). Declare `rules` (the shipped config declares persistence, momentum and mean reversion) before running; `k` is the lookback for momentum and mean reversion and `train_fraction` the share of history reserved before scoring begins.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,open,high,low,close
2010-01-01,100.0,101.7,99.0,100.7
2010-02-01,100.7,102.2,99.7,101.2
```

## Executable interface

Exact CLI columns: `timestamp,open,high,low,close`. Supported method controls: `as_of, benford_column, frequency, horizon, k, rules, season, seed, train_fraction`.

The tool scores predeclared one-step rules on closing prices at every origin after the training share: persistence (last close), momentum (last close plus the average change over `k` periods) and mean reversion (mean of the last `k` closes). It reports MAE per rule, the directional hit rate of momentum and mean reversion with zero-change periods excluded and a binomial p-value against a coin, and a Benford first-digit chi-square test on `benford_column` as a data-integrity habit. It computes price error only: no returns, costs, position sizing, sessions or corporate-action checks.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Audit OHLC consistency, missing trading periods, contract rolls and adjustments. Do not merge currencies or maturities as one series.
2. Define the forecast target and a signal computable at the origin. Reserve later observations and specify any momentum lookback before evaluating them.
3. Generate persistence and a fixed momentum alternative on identical origins and horizons. For trading applications evaluate feasible execution prices and costs separately from statistical prediction loss.
4. Compare per-origin errors and stability across regimes. Report a conditional pattern finding if it fails to persist; do not select a rule after inspecting the final period.

## Diagnostics, selection and uncertainty

Check sensitivity to lookback, corporate-action treatment and quote timing. Futures carry and risk premia prevent a simple expected-spot interpretation. Event-market probabilities additionally need defensible contract resolution and market assumptions. Price forecasts alone do not establish profitable trades.

## Missing evidence and fallback

With close-only data, omit candlesticks and use close-based baselines. Without a reliable adjustment history, segment at discontinuities or state that change forecasts are unreliable. No historical data supports only a mechanism illustration.

## Applied report contract

`results.csv` columns: `timestamp,actual,persistence,momentum,mean_reversion,actual_direction,momentum_hit,mean_reversion_hit`. `summary.json` keys: `rules,k,train_fraction,test_rows,mae,hit_rate,hit_rate_p_value,benford` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

A hit rate of 56 percent on 44 observations has a coin-flip p-value near a half; say so before anyone trades on it.

## Run it

The [notebook](../../companion/notebooks/01-markets.ipynb) is the worked lesson; its editable [source](../../companion/lessons/01-markets.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. [self-check.md](references/self-check.md) holds the three questions to answer before reporting. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 1 \
  --input companion/data/examples/ch01.csv \
  --config companion/configs/ch01.json \
  --output companion/applied-runs/ch01-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 1`.

Learning prompt: “Teach me chapter 1 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 1 to audit prices.csv and compare a prespecified momentum rule with persistence on later matched observations. Separate prediction error from trading profitability.”
