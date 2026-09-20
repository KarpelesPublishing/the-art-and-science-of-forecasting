---
name: forecasting-ch06-arima
description: "Use when a regular series has lag dependence that may support ARIMA or seasonal ARIMA, or studying forecasting book chapter 6."
---

# Chapter 6: The Unexpected Route

## Scope and intake

Use when a regular series has lag dependence that may support ARIMA or seasonal ARIMA. Do not use for a multivariate, volatility or causal problem presented as though univariate ARIMA already solves it.

Ask only for unresolved material inputs: What is the target frequency and forecast horizon? Are trends deterministic or accumulated shocks? What seasonality exists? Will any future regressors actually be known?

## Input contract and additional evidence

CSV timestamp,target, unique regular observations; config horizon,season,as_of. Candidate orders are fixed in the CLI; proposed alternatives require notebook adaptation. Future exogenous values require their own known-at-origin schedule or explicit scenarios.

Minimal **format illustration**, not sufficient training data:

```csv
timestamp,target
2026-01-01,100
2026-01-02,102
2026-01-03,101
```

## Executable interface

Exact CLI columns: `timestamp,target`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, frequency, horizon, origins, pool, season, seed, transform`. Unknown config keys are rejected. General intake requirements above may call for additional evidence or notebook adaptation; they are not all accepted configuration keys.

The adapter runs the companion engine with the `arima` pool: naive, seasonal naive, drift, ARIMA(0,1,1), ARIMA(1,1,0), the airline model ARIMA(0,1,1)(0,1,1)s, and an AICc-selected seasonal ARIMA whose regular differencing comes from repeated KPSS tests and whose seasonal differencing comes from STL seasonal strength, searched over p,q in 0–2 and P,Q in 0–1 on the first training slice. A log transform is chosen on training data when the series asks for it. Up to five expanding origins select the model; a final untouched holdout scores it once; model intervals are produced and their validation coverage is measured. Short valid histories return a provisional naive baseline and optional seasonal-naive scenario, with no claimed validation.

## Applied procedure

1. Plot training levels and differences; use ACF/PACF and stationarity diagnostics to propose a small candidate set, not to declare one certain order.
2. Reserve final evaluation periods. Fit eligible ARIMA/SARIMA candidates at earlier rolling origins and compare naive/seasonal-naive on matching horizons.
3. Check fit convergence, stability and residual autocorrelation after initialization effects. Avoid repeated differencing solely to obtain a preferred p-value.
4. Choose the specification using earlier-origin loss and parsimony, refit through cutoff and export forecasts with model-based intervals. State uncertainty in unknown future regressors separately.

## Diagnostics, selection and uncertainty

White residuals do not rule out nonlinear predictability. Differencing can remove useful structure or induce noise when excessive. Intervals depend on parameter/model assumptions and should be assessed by horizon on held-out origins.

## Missing evidence and fallback

With a short series use naive or low-order candidates and mark seasonal fitting unsupported. For calendar gaps, audit the measurement process before imputation. If regressors are unknown, show conditional forecasts or omit the regressor model. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

Return the chosen orders with the KPSS and seasonal-strength evidence behind d and D (in `summary.json` under `specification`), skipped candidates with reasons, origin-by-horizon losses, dated forecasts with model intervals and their measured coverage. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 6 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Apply chapter 6 to sales.csv with a twelve-period horizon, compare supported ARIMA and seasonal-naive candidates at earlier origins, and explain selection and residual limitations.”

The [notebook](../../companion/notebooks/06-arima.ipynb) is a worked lesson; its editable [source](../../companion/lessons/06-arima.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 6
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch06.csv) and [editable config](../../companion/configs/ch06.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 6 \
  --input companion/data/examples/ch06.csv \
  --config companion/configs/ch06.json \
  --output companion/applied-runs/ch06-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `timestamp,forecast,model`, `summary.json` containing `selected,validation,validation_predictions,test_mae,intervals`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
