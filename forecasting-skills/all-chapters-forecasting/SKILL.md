---
name: all-chapters-forecasting
description: Use when applying the forecasting book across multiple methods, reproducing its chapter notebooks, or forecasting a collection of time series with one instruction.
---

# Complete Forecasting Skill

This is the integrated entry point coordinating the 27 chapter skills: the map and the
router. For a reader who wants a forecast rather than a chapter, start with
[forecast-workflow](../forecast-workflow/SKILL.md): seven gates (brief, profile, baseline,
method, validation, uncertainty, report and journal), each producing a file the next
command requires, so the same honest path is followed whatever the reader knows. This
skill and the chapter skills are what the workflow routes into.

For the human reader: a **skill is instructions for an AI assistant**, while a
**notebook is an executable lesson with code and results**. Start with
[the reader's guide](../../companion/START-HERE.md). Use this skill for a whole
problem, or go directly to one chapter skill for a specific lesson.

This folder is **not standalone**: retain the 27 sibling chapter-skill folders,
`reconcile-tdbu` and `companion/` in the supplied relative layout. The library is
27 chapter skills, this integrated skill, and one desk-model skill
(`reconcile-tdbu`); this is the book's integrated entry point.

One-line entry: `Use $all-chapters-forecasting to forecast my dataset for the next 12 periods, compare applicable methods, and report uncertainty and validation.`

Read the [27-chapter map](references/chapter-map.md) and load only the chapter
skills relevant to the task. Every chapter is available; not every method applies
to every target. The map is the full library, not a mandatory 27-model ensemble.

## Three modes

1. **Learn:** select a chapter and run its notebook, explaining the worked example.
2. **Reproduce:** run every chapter from a clean kernel, export charts and assemble the
   catalog with `run.py chapters --all` and `catalog.py` (see `companion/README.md`).
3. **Apply:** frame the target, gather inputs, choose supported methods, evaluate,
   produce forecasts/estimates, quantify uncertainty, and save a scoring record.

## Applied routing

Record target, units, horizon, frequency, forecast date/as-of cutoff, available
history, decision costs, and which covariates are known in advance (`run.py brief`
asks exactly these). Do not infer missing business definitions from column names
alone. Then look at the data before choosing anything:

```bash
companion/.venv/bin/python companion/scripts/run.py profile --input data.csv --brief brief.json
```

The profile reports frequency, length, gaps and what to do about them, zero share and
demand class, the seasonal periods found in the data, trend, outliers, a possible level
shift, the floor for the brief's horizon, and a `route`. Find the row that matches:

| The reader has | Chapter and tool | Needs at least | If the floor is not met |
|---|---|---|---|
| One regular series, no drivers (route `engine`) | 12 (`run.py apply --chapter 12`; 4 for smoothing only, 6 for ARIMA only) | 2 seasons + 4 horizons (monthly, horizon 12: 72 points) | provisional persistence baseline; shorten the horizon or gather history |
| Mostly zeros (route `intermittent`) | 12 with `pool: intermittent` (Croston, SBA, TSB, ADIDA, IMAPA on RMSSE), then 21 for the stocking policy | 2 seasons + 4 horizons | provisional; consider aggregating to a coarser period |
| Two cycles, daily or hourly data (route `multiseasonal`) | 12 with `pool: multiseasonal` (MSTL, Fourier ARIMA, Prophet, TBATS when installed) | 2 cycles of the longest period + 4 horizons | 12 `full` on the shorter cycle, and say the longer one is unmodelled |
| Gaps in the record | the profile fills few short gaps for fitting only (interpolate, or zero for intermittent) and refuses many; 5 handles missing observations natively | as the route | fix the source; do not pad |
| Many such series at once | `run.py forecast --engine full` (per series), `--engine global` (one LightGBM across all series, mlforecast when installed) or `--engine neural` (NHITS, needs neuralforecast), each compared with seasonal naive per series | same per series | that series fails in `failures.json`; the rest continue |
| A series and a guaranteed interval | 12 then 17 (conformal) | 2 seasons + 36 calibration + 24 test points | error naming the total; reduce `calibration_size`/`test_size` |
| Series with promotions, prices or other drivers (route `regressors`) | 12 with `regressors` and `future_regressors` (ARIMAX, LightGBM with drivers, Prophet with regressors); 13 for four or more series; 16 for an event table | 12: 2 seasons + 4 horizons; 13: 4 series × 35 rows; 16: max(4 horizons, 60) | no future driver values: 12 `full` and say the drivers are unmodelled |
| Related series that must add up | 18 (long form + child-parent edges) | per node, the chapter 12 floor | reconciles anyway, `status: provisional`, no holdout leaderboard |
| Hidden states, sensors, gaps in the record | 5 | 30 observed values | error |
| A pretrained model as one more candidate | 15 (Chronos, tiny checkpoint cached), or 12 with `pool: foundation` (Chronos-Bolt small, about 190 MB, and TimesFM 2.5, about 800 MB, download only with FORECAST_ALLOW_DOWNLOADS=1) | max(3 seasons, horizon + 30) | error; larger checkpoints download, ask first |
| A new product with no sales history | `reconcile-tdbu` (interview, desk model, reconciliation) | the interview's four inputs | it runs on defaults and reports which inputs drive the gap |
| A new product with comparable launched products | 27 `mode: launch`; 19 to turn an adoption curve into sales with repeat | 27: 3 calibration + 2 validation products; 19: 6 adoption points | 27 refuses; fall back to `reconcile-tdbu` |
| A yes/no event to forecast | the assistant estimates it with chapter 10's decomposition and journal; 2 updates a rate; 9 and 26 only score probabilities already made | 9/26: resolved outcomes | nothing to score yet: keep the journal, `status: needs_evidence` |
| A marketing budget question | 20 (named channel columns) | 60 periods, nonnegative spend | error; attribution stays conditional, never causal |
| A reorder or stocking question | 21 | 30 periods | error |
| Did an action change the outcome? | 22 (two or more controls) | 15 pre + 5 post periods | error; one control: no synthetic control, DiD only |
| Reporting delays, an epidemic curve | 23 | 10 complete cohorts | error |
| A break in the series, when to refit | 24 | 80 periods | error |
| A plan to check against similar past cases | 25 | the reference class | unidentified quantiles stay null |
| Price rules on a market series | 1 | 30 sessions | error |
| Decomposition or sensitivity to starting conditions | 3, 7 | 3: 3 seasons | error |

The full floors and the meaning of each `status` are in
[conventions.md](references/conventions.md). Detail per route:

- Ordinary series: run the engine (below) through chapter 12's adapter or `run.py forecast --engine full`.
  It fits the chapter 4 smoothing family, the chapter 6 ARIMA family with diagnostic differencing
  and a log transform when the data ask for it, Theta, STL+ETS, LightGBM when history allows, and
  combinations, all selected by rolling-origin validation. Consider 13–16 when panel size justifies them.
- Hidden states, noisy sensors or gaps in the record: 5, whose tool fits an
  unobserved-components model with missing observations and separates the
  filtered (real-time) path from the smoothed (retrospective) one. Simulation
  and distributions: 7; intervals with a coverage guarantee: 17, whose tool wraps
  the engine's selection in split and adaptive conformal bands and scores them.
- Covariates and known future regressors: 13 (LightGBM direct or recursive with
  declared known-in-advance covariates, ablation and SHAP) when there are four or
  more related series with 35 or more rows each; a single series with drivers goes
  to 16 (Prophet with an event table, future regressor rows, ablation), and a single
  series whose future driver values are unknown goes to 12 with the limitation stated.
- A pretrained model as one more candidate: 15, at the engine's own origins beside
  the baselines. The tiny checkpoint is cached; larger ones download, so state
  the size and ask before choosing one.
- Expert/event probabilities: 2 and 8–11. No tool produces the probability; the
  assistant does, with chapter 10's base rate, decomposition and likelihood-ratio
  updating, and records it in the chapter 10 journal. Chapter 2 updates a rate from
  successes and trials, 8 compares Delphi rounds, 11 aggregates a crowd, 9 scores
  resolved probabilities and 26 turns them into a cost-weighted action rule.
  Define resolution source, timezone, cutoff and baseline in advance. Preserve
  timestamped revisions; score one eligible pre-resolution forecast per resolved
  event, exclude unresolved/hindsight entries, and show calibration-bin counts.
- Hierarchies: 18. Give the tool the node histories in long form and the
  child-parent edges; it builds the summing matrix, forecasts every node with the
  engine, and compares bottom-up, OLS and MinT on a holdout.
- New products/simulated-test-market logic: 19, 20, 25 and 27, with one rule. No
  sales history and no comparable launched products: `reconcile-tdbu`. Comparable
  products with observed 24-month units and defended reach inputs: chapter 27
  `mode: launch`. An established product: chapter 27 `mode: history` (the chapter 12
  engine). Chapter 27's notebook shows the launch model worked through; chapter 19's tool turns Bass adoption
  into unit sales under two timing curves with a repeat kernel and a
  Parfitt-Collins share; chapter 20 supplies the marketing context and chapter 25
  the reference-class checks. Calibrate shared assumptions across current
  products, test held-out products, assess dated research and re-base for the new
  product. Specify trials versus units. The author's standard allocates the full
  trial total over 24 months; use that horizon denominator, extending the horizon
  explicitly if warranted. Gamma modes 3/4/5 months are the author's timing
  scenarios, standard 80% trials in year one. Awareness/distribution levels
  constrain potential volume; their development supplies ALL delays. No extra ramp.
  Chapter 19 Bass is a distinct adoption model, not a required additional delay or
  interchangeable formula.
- Marketing attribution: 20, with named channel columns. The tool selects adstock
  and saturation per channel on earlier origins, fits by ridge with controls, and
  reports response curves, refit stability, an optional posterior and a
  reallocation scenario. Compare predictive accuracy AND attribution stability
  across refits, backgrounds, priors and initial carryover. Fixed guessed effects
  can be stably wrong; priors need provenance/sensitivity.
- Causal action questions: 22, with two or more controls when possible. The tool
  runs DiD, an OLS counterfactual, synthetic control, placebo-in-space and
  placebo-in-time p-values and an event study with a pre-trend test. Defend the
  observational or experimental comparison; predictive fit, stable coefficients
  and passing pretrend checks do not identify effects. Prefer an ethical, feasible,
  informative experiment when the decision remains unidentified; otherwise report
  conditional scenarios and missing evidence.
- Inventory: 21, whose tool simulates a bootstrapped order-up-to policy (cycle
  service, fill rate, on-hand, cost) and an N-echelon bullwhip experiment.
- Epidemics and reporting delays: 23, whose tool estimates the delay law from
  mature cohorts, nowcasts with bounds, checks itself on archived cohorts and fits
  SEIR at rolling origins when a population is given.
- Regime changes: 24, whose tool dates changepoints, runs a two-sided calibrated
  CUSUM and scores frozen, rolling, expanding and alarm-adaptive policies.
- Market signals: 1 (predeclared rules with hit rates and a binomial test, price
  error only); dynamical sensitivity/decomposition: 3; decisions and monitoring: 26.

Every tool returns through the same contract: `method`, `interpretation`,
`assumptions`, `not_done` (what the chapter discusses that this run did not do) and
`status` (`passed`, `provisional` or `needs_evidence`). The tools run only when
asked; decide with the reader whether the method fits first.

## Reading the result

Start with `interpretation`, then `status`, then `not_done`; repeat the last to the
reader in the report. `passed` means the chapter's own validation ran; `provisional`
means something ran but a required check could not (the list says which); `needs_evidence`
means no number was produced and the summary names the evidence that would unlock it.
[conventions.md](references/conventions.md) shows a real `summary.json` from chapter 4
in both the `passed` and the `provisional` case and says what to do with each.
`results.csv` is the calculation, not permission to act.

For a new-product launch with no sales history, use [reconcile-tdbu](../reconcile-tdbu/SKILL.md),
the author's desk model from chapters 20 and 27: it interviews for the inputs, runs the
trial-and-repeat and market-share engines, reports the gap and reconciles them.

## Executable engine

The engine in `companion/src/forecasting_companion/engine.py` is what makes this
skill more than a reading list. For one regular series it:

1. chooses the working scale on training data only (Box-Cox lambda near zero and
   positive data selects a log transform, as in the airline example);
2. fits a pool of candidates anew at up to five expanding origins before a final
   untouched holdout: naive, seasonal naive, drift, SES, Holt, damped Holt, an
   AICc-selected ETS form (additive or multiplicative error and seasonality),
   Theta, STL+ETS, an AICc-selected seasonal ARIMA whose d and D come from KPSS
   and seasonal-strength checks, the airline model ARIMA(0,1,1)(0,1,1)s, LightGBM on
   lags when history allows, a median of the top three, and an equal ensemble;
3. scores every candidate at every origin on MAE, RMSE and training-scaled MASE,
   and measures the coverage of each model's nominal 80% interval;
4. selects on earlier-origin MAE, scores the selection once on the final holdout,
   refits on all history and returns point forecasts, the model's own intervals
   with their measured coverage, and empirical residual quantiles by horizon step.

Specifications are frozen on the first training slice, so later actuals cannot
influence the choice; the tests prove it by corrupting the holdout and checking
that the leaderboard does not move. On the book's airline series the engine picks
the log transform and the airline model: holdout MAE 13 against 48 for seasonal
naive, with 87% measured coverage of the 80% bands.

Pools: `full` (everything above, chapter 12 and this skill), `smoothing` (chapter 4),
`arima` (chapter 6), `baseline` (naive, seasonal naive, drift, ensemble). Config keys
for the chapter adapters: `horizon, season, frequency, as_of, pool, transform
(auto|none|log), origins`.

### Many series

From the project root:

```bash
companion/.venv/bin/python companion/scripts/run.py forecast --input companion/data/examples/sales.csv --horizon 12 --frequency MS --workers 4 --resume --engine full --output companion/applied-runs/sales
```

CSV columns: `series_id,timestamp,target` (the shipped `sales.csv` has six monthly series of seven years). `--engine full` runs the engine above on
every series (a few seconds each); `--engine baseline` (the default) runs only the
transparent baselines and is the right choice for thousands of series or a first
pass. Both write `forecast.csv` (quantile rows per horizon step; with the full
engine also `model_interval_80` rows), `metrics.csv` (selected model, transform,
validation and holdout MAE, interval coverage, skipped candidates) and
`failures.json`. Failures are per series; resume keys cover data, settings, code
and library versions.

### One series, one chapter

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 12 --input my.csv --config my.json --output applied-runs/my-forecast
```

`my.json` must declare `source` and `units`; add `horizon`, `season`, `frequency`
and optionally `pool`, `transform`, `origins`. Chapter 4 defaults to the smoothing
pool, 6 to ARIMA, 12 and 27 to the full pool. `results.csv` carries the forecast,
`lower/upper` when the selected model has intervals, and `empirical_q10/50/90`;
`summary.json` carries the leaderboard, per-origin scores, holdout scores, interval
coverage, the chosen specification and every skipped candidate with its reason.

### What it still does not do

Fine-tuning a foundation model (chapter 15 runs Chronos zero-shot only), global
count-data models for many intermittent series (chapter 21 handles one series at
a time), and causal identification without a defensible comparison (chapter 22
computes the estimators; the reader supplies the argument). A short series
(fewer than 2 seasons + 4 horizons) returns `status: provisional` with a persistence
baseline and no validation claims rather than a fitted seasonal model.

## Safeguards that survive deadline pressure

- Training, transformations and tuning use only information available at each origin.
- Never describe agreement or disagreement between two methods as a calibrated 95% interval.
- Four monthly observations cannot estimate annual seasonality or validate 95% coverage.
  Ordinary split conformal with fewer than 19 residuals has no finite 95% endpoint
  under its usual finite-sample guarantee. Time dependence requires further assumptions.
- Hierarchy inputs must be complete. Never replace missing nodes with zero silently.
  Estimate MinT covariance from earlier base-forecast errors, not differenced actuals;
  use qualified bottom-up/OLS when covariance is unsupported.
- Apply no-history estimation with explicit inputs and sensitivity, not invented history.
- Do not convert low/base/high launch scenarios into event probabilities without
  justified input dependence and model uncertainty. Agreement of shared-input routes
  is not independent validation. Research relevance decay is not automatic sales decay.
- Report exactly which model ran, failures/skips, source limits, and unexecuted extensions.

Return forecast tables, benchmark scores, uncertainty interpretation, assumptions,
figure paths and a saved forecast/outcome review date. Automatic publication,
cloud spending or business actions are not part of this skill.

## Execute a reader-data application

Read the selected chapter's executable-adapter contract and its
`references/workshop.md` before preparing input. Unknown config keys fail rather
than being silently ignored. Inputs are chapter-specific: series, event revisions,
hierarchy nodes, reference products and reporting triangles have different
meanings and schemas. Keep source, units, horizon and available-as-of information
explicit. Results are written to a new isolated directory, never to publication
artifacts. Forecast readiness may be provisional or needs_evidence even after
successful execution. Do not turn a pending result into a forecast.

For chapter 27 route sufficient history to the chronological comparison, sparse
history to an evidence request, and supported launch assumptions to trial/repeat.
Mature-sales calibration alone does not authorize trial conversion: require a
stated conversion assumption or defended trial total and explicit repeat inputs.
Cross-check against genuinely different evidence when available. Shared inputs
or alternative phasing of the same total do not create independent validation.
