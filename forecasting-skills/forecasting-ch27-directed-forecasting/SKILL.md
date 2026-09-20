---
name: forecasting-ch27-directed-forecasting
description: "Use when a business question needs routing from available evidence to a defensible forecast, especially proxy-based launch volumes and trial/repeat timing, or studying forecasting book chapter 27."
---

# Chapter 27: Giving the Oracle Direction

## Scope and intake

Use when a business question needs routing from available evidence to a defensible forecast, especially proxy-based launch volumes and trial/repeat timing. Do not use for an automatic request to run every forecasting method, or a causal spend recommendation without an identification design.

Ask only for unresolved material inputs: What decision changes with the answer? What target, population, unit, horizon and cutoff apply? Is usable history present? Are analogues comparable and current? Does stated volume mean unique trials or total units? Which genuinely distinct cross-check and eventual scoring outcome are available?

## Input contract and additional evidence

Three routes share one command: `mode: history` runs the chapter 12 engine on an established product's `timestamp,target` series (2 seasons + 4 horizons of history, else provisional; fewer than 36 points returns needs_evidence); `mode: estimate` returns the evidence request; `mode: launch` (default) needs the reference-product table below. A launch with no reference products belongs to [reconcile-tdbu](../reconcile-tdbu/SKILL.md). Intake record: target,units,population,horizon_months,as_of,decision,history_available,source,outcome_due. Mature-product table: product,eligible_buyers,awareness,availability_given_awareness,interest,units_per_buyer_24m,observed_units_24m,research_date,source,split. Probabilities are conditional fractions in [0,1]; quantities are nonnegative. For the CLI launch route, config new_product supplies eligible_buyers, awareness, availability_given_awareness and interest; horizon defaults to 24. Supply either trial_conversion_assumption to explicitly defend transferring calibrated scale, or a defended declared_trial_total. Supply either repeat_rate or a full-horizon repeat_kernel. The CLI runs fixed peaks 3/4/5; custom timing peaks require notebook adaptation.

Minimal **format illustration**, not sufficient training data:

```csv
product,eligible_buyers,awareness,availability_given_awareness,interest,units_per_buyer_24m,observed_units_24m,research_date,source,split
A,100000,0.5,0.6,0.2,4,20400,2025-03-18,Illustrative,calibration
```

## Executable interface

Exact CLI columns: `eligible_buyers,awareness,availability_given_awareness,interest,units_per_buyer_24m,observed_units_24m,split`. Supported method controls: `as_of, declared_trial_total, frequency, horizon, mode, new_product, origins, pool, repeat_kernel, repeat_rate, season, seed, transform, trial_conversion_assumption`.

Launch requires at least three calibration and two validation products and runs peaks 3,4,5. Explicitly defend scale transfer or supply declared_trial_total; trials may not exceed jointly reached eligible buyers. Supply a constant repeat_rate (one unit at trial) or an explicit repeat_kernel with one nonnegative units-per-trier entry per horizon month. No default repeat assumption is invented; custom timing peaks are not accepted. Standard horizon=24; larger horizons are explicitly different scenarios. mode=estimate and insufficient history return needs_evidence, not a fabricated numeric forecast.

## Applied procedure

1. Translate the request into target, decision, as-of evidence and resolution contract. Audit units, population overlap, vintage and missing observations before researching model names.
2. Route sufficient comparable time history to an evaluated baseline and eligible chapter model. Route sparse-history questions to a defended reference class or decomposition; keep unsupported branches as scenarios. Record why each route is admissible.
3. For a product build-up, define conditional reach and align all reference sales to the same period. Hold measured factors fixed; estimate one shared calibration relationship on calibration products, then inspect leave-one-product-out stability and unused-product errors.
4. Defend every transferred proxy, including research age and changes in category, price or channel. Obtain cohort/panel evidence for trial conversion and repeat; mature total units alone cannot identify both.
5. Phase a declared 24-month trial total using the standard gamma or explicit conditional joint-reach increments, once. Convolve trials with a separate repeat-unit kernel. Compare faster/base/slower timing while preserving total trials.
6. Cross-check against evidence with a meaningfully different failure mechanism. List shared inputs before calling estimates independent. Export a dated decision/scoring record, scenario sensitivities and follow-up evidence priorities.

## Diagnostics, selection and uncertainty

Check product-level residuals and scale instability, out-of-population analogues, double timing, probability denominator errors, unit reconciliation and conservation of the trial total. A mature-product fit validates only the fitted relationship on comparable products, not causal marketing effects or an unmeasured trial-transfer assumption.

## Missing evidence and fallback

If history is sparse, do not fabricate backtests; use explicit analogue/scenario estimates. If repeat data are absent, report trials separately and show repeat assumptions as scenarios. If no distinct cross-check exists, record that absence and the shared-input dependence rather than presenting two formulas as triangulation.

## Chapter-specific invariants

Calibrate on as many comparable established products as possible, then adapt for
launch. Align sales periods, eligible populations, awareness, conditional
availability, interest and purchase units. Hold reliable measurements fixed; fit
shared assumptions, inspect leave-one-product-out stability and test unused products.
Do not tune every product separately until its sales match.

Record research date, source, population and relevant market changes. Research
relevance decay is distinct from actual interest decay; any half-life is an explicit
scenario unless validated. Propagate uncertainty instead of silently reducing demand.

State whether predetermined volume means trials or total units, and whether its
24-month-or-longer horizon excludes an eventual tail. Mature sales do not identify
trial conversion separately from repeat purchasing. Support any transfer to new
products with panel/cohort evidence or label it as an additional assumption.

The author's standard allocates the full trial total over 24 months, with a gamma
trial-density mode at month 4 and 80% in year one. Faster mode=3 or less gives
more year-one trials; slower mode=5 or more gives fewer, preserving the declared
total. Use `denominator='horizon'`; eventual-tail treatment is only for an
explicitly different scenario, not an unresolved question about this standard.
It holds gamma shape fixed when varying peak scale; this is an implementation
convention, not a recovered proprietary formula.

For shape k>1 and scale theta, f(t)=t^(k-1) exp(-t/theta)/(Gamma(k) theta^k).
The mode is (k-1)theta. Solve mode=4 and F(12)/F(24)=0.8; month m trials are
T × [F(m)-F(m-1)]/F(24). The ordinary gamma has an infinite tail; normalization
allocates the declared total within the horizon. A continuous peak at t=4 is not
the same as the largest discrete monthly bin; integrate for monthly totals.

Final awareness/distribution levels affect potential volume. Their progress curves
supply ALL delays: gamma summarizes that combined timing OR explicit conditional
joint-reach increments supply timing. Never apply both as successive delays. Do not
multiply correlated marginal awareness/availability without justification or treat
ACV as customer reach. Mature products have no new-launch penalty, not flat sales.
Keep trial cohorts and repeat-unit kernels separate; report year-one, year-two and
tail results. Save assumptions and a dated forecast before outcomes arrive.

Agreement between routes sharing inputs is not independent validation. Preserve
the DECLARED horizon total, never force slower launches to retain first-year volume.
Do not feed total sales units into a unique-trier gamma without a supported conversion.
Do not claim the synthetic calibration establishes an advertising causal effect.

## Applied report contract

`results.csv` columns: `month,peak,trials,units`. `summary.json` keys: `scale,trial_total,held_out_mae,year_one_units` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return an intake/routing record, proxy/source register, reference-product calibration and held-out errors, monthly trial and total-unit tables, Y1/Y2/tail reconciliation, sensitivity table, missing-evidence priorities and dated scoring plan. State which methods were executed and which remain proposed.

## Run it

The [notebook](../../companion/notebooks/27-directed-forecasting.ipynb) is the worked lesson; its editable [source](../../companion/lessons/27-directed-forecasting.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 27 \
  --input companion/data/examples/ch27.csv \
  --config companion/configs/ch27.json \
  --output companion/applied-runs/ch27-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 27`.

Learning prompt: “Teach me chapter 27 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 27 to our new product: first determine whether available history supports a model or only an estimate, defend proxy inputs, calibrate across comparable mature products, separate trials from repeat units, preserve 24-month trial totals, and save a forecast/scoring record.”

## Desk model skill

For a launch forecast without a test market, use [reconcile-tdbu](../reconcile-tdbu/SKILL.md): it interviews for the inputs, runs the trial-and-repeat and market-share engines, reports the gap and the implied inputs, and reconciles them. Its constants are illustrative starting values; tune them to launches the user knows.
