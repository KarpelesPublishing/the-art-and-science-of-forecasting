---
name: forecasting-ch19-diffusion
description: "Use when first adoption of a durable product or category may follow diffusion with an uncertain ceiling, or studying forecasting book chapter 19."
---

# Chapter 19: Frank Bass and the Television

## Scope and intake

Use when first adoption of a durable product or category may follow diffusion with an uncertain ceiling. Do not use for forecasting recurring purchase units directly from a unique-adopter Bass curve.

Ask only for unresolved material inputs: Does the series count cumulative unique adopters? What is the market ceiling’s evidence? Are time units consistent? Has the inflection or peak been observed? What repeat behavior lies outside adoption?

## Input contract and additional evidence

Cumulative unique adopters at six or more increasing times, with `ceilings` naming at least one defended market ceiling above the observed total. `repeat_kernel` lists expected repeat units per original trier at cohort ages one, two, three and so on; `units_at_trial` is the first-purchase quantity. `parfitt_collins` takes `T` (eventual trial share), `R` (repeat share) and optional `B` (buying-rate index).

Minimal **format illustration**, not sufficient training data:

```csv
time,adopters
1,2944
2,6931
3,12179
4,18839
```

## Executable interface

Exact CLI columns: `time,adopters`. Supported method controls: `as_of, ceilings, fix_q, frequency, future_times, horizon, parfitt_collins, peak, repeat_kernel, sales_horizon, season, seed, time_unit, units_at_trial`.

The tool fits the Bass model for each declared ceiling (with early-fit holdout, Jacobian condition and peak time), optionally refits with `fix_q` held, then converts adoption into sales over `sales_horizon` periods (24 or more) under two timing curves that share the same trial total: Bass incidence and the author's gamma-shaped launch curve with its `peak` month. Each timing is spread with the repeat kernel into unit sales, and the tool compares peak period, twelve-period units and total units between them. With `parfitt_collins` inputs it reports the steady-state share and a plus or minus 20 percent band on repeat. Price, distribution and advertising are not in the curve; the kernel is assumed, not estimated.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Audit cumulative counts, duplicates, population changes and any resets. Define eligible market m independently where possible.
2. Compute Bass cumulative adoption and incidence for defensible p,q,m scenarios. Keep parameter units consistent with the data’s elapsed time.
3. Fit p,q on an early calibration window under several supported ceilings; inspect residuals and sensitivity to starting values and bounds.
4. Evaluate later observations where available and retain ceiling uncertainty when early fits cannot distinguish it. Do not select the best-looking long-run scenario after the fact.
5. Convert adoption to sales only through a separate documented units-at-trial and repeat-cohort model.

## Diagnostics, selection and uncertainty

Early adoption often weakly identifies m and can trade off with p,q. An interior incidence peak formula requires q>p. Saturation is a structural assumption, not proof that the market cannot expand. Scenario curves are not a calibrated interval.

## Missing evidence and fallback

With no adoption history use defended analogue parameters and explicit scenarios. With only sales units, obtain unique-adopter/cohort information or change the target; do not treat cumulative repeat sales as cumulative adoption.

## Applied report contract

`results.csv` columns: `time,ceiling,bass_trials,gamma_trials,bass_units,gamma_units`. `summary.json` keys: `fits,ceilings,sales_horizon,peak,kernel,timing_comparison,parfitt_collins,bass_table_rows` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Show both timing curves; the same eventual total can put half the first year in a different quarter.

## Run it

The [notebook](../../companion/notebooks/19-diffusion.ipynb) is the worked lesson; its editable [source](../../companion/lessons/19-diffusion.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 19 \
  --input companion/data/examples/ch19.csv \
  --config companion/configs/ch19.json \
  --output companion/applied-runs/ch19-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 19`.

Learning prompt: “Teach me chapter 19 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 19 to adoption.csv, defend several market ceilings and show which long-run differences are unsupported by the early history.”
