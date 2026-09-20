# Learn-and-apply coverage and acceptance

Each chapter pairs the existing controlled figure lesson with a substantive workshop,
worked arithmetic, three solved exercises, a concrete input file/configuration, and
an executed applied calculation. The same calculation functions power the CLI.

| Chapter | Principal executed application | Failure/limitation to assess |
|---|---|---|
| 1 | OHLC audit; predeclared persistence, momentum and mean-reversion rules at expanding origins; directional hit rates with binomial test; Benford first-digit check | Bad bounds; exchange-session calendar; price error only, no trading-return claim |
| 2 | Beta-binomial updating and prior strength sensitivity | Invalid successes; exchangeability and selection |
| 3 | STL and component revision across vintages | Full-series preprocessing leakage |
| 4 | Eight-method rolling comparison, final holdout and refit | Sparse history returns provisional baseline |
| 5 | Unobserved-components state space (local level, linear or smooth trend, optional seasonal and cycle) with missing observations, filtered and smoothed states, interval forecasts, rolling check against last value; manual local-level filter retained | Smoothed states are retrospective; Gaussian noise; wrong dynamics show in Ljung-Box |
| 6 | Candidate ARIMA and seasonal AR with common origins | Nonconvergence and future regressors |
| 7 | Dependent cost simulation; four-chain posterior diagnostics | Monte Carlo error versus model error |
| 8 | Round-level medians, spread and FVA | Equal-variance dependence demonstration; convergence is not accuracy |
| 9 | Common-event scores and reliability-bin support | Small/dependent event samples |
| 10 | Revision eligibility, pending events and scoring | Hindsight and unresolved outcomes |
| 11 | Aggregation; learned weights evaluated on later events | Shared bias and unstable weights |
| 12 | Common-origin baseline comparisons and per-horizon records | Scaling and rank overinterpretation |
| 13 | LightGBM direct or recursive multi-step on lags, rolling means, calendar and declared covariates at expanding origins; seasonal-naive baseline; feature-group ablation; SHAP with additivity check | Known-in-advance covariates must be declared; unknown covariates are lagged; holdout scored once |
| 14 | Gaussian MLP, entity holdout and sampled paths | Calendar alignment; short-history transfer is not no-history prediction |
| 15 | Chronos-T5 zero-shot at a chosen checkpoint (tiny pinned; larger sizes on request) at the engine's own origins beside the baseline pool; sampled quantiles, coverage, latency | Download size stated before opting in; corpus exclusion not certified; no fine-tuning |
| 16 | Prophet with declared events and future regressors, prior grid at earlier origins, no-events and no-regressors ablation, holdout MAE and coverage | Nominal intervals; future regressor rows required for a future forecast |
| 17 | Engine-selected model with split and adaptive conformal intervals on a calibration block, interval score and pinball on a test block, comparison with the model's own band; supplied intervals still scored | Guarantee is marginal and exchangeability-based; combinations fall back to the best atomic model |
| 18 | Summing matrix from child-parent edges, per-node engine base forecasts, bottom-up, OLS and shrunk-covariance MinT with a holdout leaderboard; optional coherent quantiles | History must be coherent; MinT needs enough error rows; legacy node,forecast input still reconciled |
| 19 | Bass ceiling sensitivity with optional fixed q; adoption converted to unit sales under Bass and gamma launch timing with a repeat kernel; Parfitt-Collins share | Kernel assumed, not estimated; timing curves change year-one totals at identical eventual totals |
| 20 | Adstock and saturation per channel selected on earlier origins, closed-form ridge with controls, holdout against seasonal naive, response curves, marginal response, refit stability, optional Gaussian posterior, budget reallocation scenario | Fitted decomposition, not identified causal ROI; reallocation is conditional |
| 21 | Croston/SBA/TSB; bootstrapped order-up-to policy simulation with pipeline and backlog (cycle service, fill rate, on-hand, cost); N-echelon bullwhip with local versus shared signal | Fixed lead time; demand treated as uncensored |
| 22 | DiD, multi-control OLS counterfactual, synthetic control on a simplex, placebo-in-space and placebo-in-time p-values, event study with pre-trend test | Fit does not establish identification; the declared comparison is the reader's responsibility |
| 23 | Reporting-triangle nowcast with a delay law estimated from mature cohorts, negative-binomial bounds, archived evaluation by age; SEIR fitted at rolling origins against persistence | As-of truncation; in-sample archived check; testing and intervention changes not modelled |
| 24 | Binary-segmentation changepoint dating, strongest split, two-sided calibrated CUSUM, drift metrics, four adaptation policies scored after calibration | Repeated alarms mean a stale reference; seasonal series must be deseasonalised first |
| 25 | Kaplan–Meier reference-class ratios | Noninformative censoring; unidentified tail remains missing |
| 26 | Cost-sensitive actions and realized costs | Calibration; hindsight constant-policy comparison |
| 27 | General routing, sparse-history refusal and launch transfer | Mature units are not unique triers; conditional repeat |

Observed default applications: temperature in 3,4,6,12,15,16; Nile in 5,24.
Other domain applications use openly labeled synthetic schema examples because
no verified appropriate domain dataset was available in the bundled collection.
All chapters include real-data input instructions. Principal executable methods
are listed above; every tool records what it did not do under `not_done` in its
summary, and it runs only when the reader asks for it.
