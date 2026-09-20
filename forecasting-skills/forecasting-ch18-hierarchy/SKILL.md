---
name: forecasting-ch18-hierarchy
description: "Use when forecasts across stores, regions or products must add to consistent totals, or studying forecasting book chapter 18."
---

# Chapter 18: The Hierarchy

## Scope and intake

Use when forecasts across stores, regions or products must add to consistent totals. Do not use for assuming coherent totals automatically improve accuracy or preserve nonnegativity.

Ask only for unresolved material inputs: What are the bottom-level quantities and summing relationships? Do nodes overlap? Are base forecasts for the same origin/horizon? Are historical forecast errors available to estimate covariance?

## Input contract and additional evidence

Long format, one row per node and period: `node,timestamp,target`, with every node on an identical calendar and historical values that already add up within `history_tolerance`. The hierarchy is declared in config as `edges`, a list of `[child, parent]` pairs; the tool builds the summing matrix itself (aggregates first, leaves last). The older `node,forecast` input with a supplied `S` is still accepted for a one-shot reconciliation of forecasts you already hold.

Minimal **format illustration**, not sufficient training data:

```csv
node,timestamp,target
Total,2010-01-01,100.7
A,2010-01-01,60.4
B,2010-01-01,40.3
Total,2010-02-01,105.9
A,2010-02-01,63.1
B,2010-02-01,42.8
```

## Executable interface

Exact CLI columns: `node,timestamp,target | node,forecast`. Supported method controls: `S, as_of, coherent_quantiles, edges, frequency, history_tolerance, horizon, nodes, origins, past_errors, pool, season, seed, shrinkage, transform`.

The tool builds S from `edges`, forecasts every node with the companion engine (default `pool: smoothing`; `full` and `arima` are available), takes each node's base-forecast errors from the engine's own validation origins, shrinks their covariance toward the diagonal by `shrinkage` (default 0.2), and reconciles by bottom-up, OLS and MinT. Coherence is asserted for every reconciled column. Every method, including the unreconciled base, is scored per node on the untouched final holdout, so the leaderboard shows whether reconciliation helped this hierarchy rather than assuming it. `coherent_quantiles: true` reconciles 500 joint draws when every node's model has intervals and returns MinT q10/q50/q90. MinT is dropped, and reported under `not_done`, when fewer than n_nodes+2 matched errors exist or the covariance is not positive definite. Nonnegativity is not enforced.

When the history is too short to hold the engine's rolling origins twice over (for monthly data with a 12-step horizon, fewer than 84 observations), the tool still reconciles the production forecasts but skips the holdout leaderboard, takes the error covariance from the engine's own rolling origins, returns `status: provisional` and says so under `not_done`. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Build and audit S, including all node ordering and no double counting. Check rank, units and whether base forecasts already reconcile.
2. Compute bottom-up from bottom-level forecasts. For an unweighted projection use OLS reconciliation with W=I, labeling it separately from covariance-based MinT.
3. Estimate W only from earlier matched errors when enough exist; regularize unstable covariance and document the choice. Compute S(SᵀW⁻¹S)⁻¹SᵀW⁻¹ times the base vector using stable solves.
4. Verify coherence numerically, inspect negative values and compare base, bottom-up and eligible projections on unused outcomes.
5. For probabilistic forecasts reconcile joint samples or model the joint structure; do not add marginal quantiles as though they were coherent scenarios.

## Diagnostics, selection and uncertainty

Check matrix conditioning, covariance sample size and sensitivity to shrinkage. MinT rests on estimated error structure. Nonnegative operational quantities may require a separately implemented constrained method; clipping node forecasts independently breaks coherence.

## Missing evidence and fallback

Without past errors, use bottom-up or clearly labeled OLS, not fabricated MinT covariance. If hierarchy mapping is ambiguous, return inconsistencies before fitting. If constraints are required but unsupported, report infeasibility rather than hiding negative nodes.

## Applied report contract

`results.csv` columns: `node,timestamp,base,bottom_up,OLS,MinT`. `summary.json` keys: `nodes,leaves,S,selected,shrinkage,error_rows,holdout,leaderboard,coherence_max_abs_residual,pool,horizon` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Quote the holdout leaderboard beside the reconciled forecasts; a coherent forecast that lost accuracy on the holdout is a finding, not a success.

## Run it

The [notebook](../../companion/notebooks/18-hierarchy.ipynb) is the worked lesson; its editable [source](../../companion/lessons/18-hierarchy.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 18 \
  --input companion/data/examples/ch18.csv \
  --config companion/configs/ch18.json \
  --output companion/applied-runs/ch18-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 18`.

Learning prompt: “Teach me chapter 18 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 18 to reconcile hierarchy.csv using the supplied summing matrix, compare eligible methods and verify coherence without claiming accuracy from addition alone.”
