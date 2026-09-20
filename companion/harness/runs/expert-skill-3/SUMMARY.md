# expert-skill-3: summary

Run folder: `companion/harness/runs/expert-skill-3/<task>/`. Every task followed the forecast-workflow gates: brief (`brief.json`), profile (`profile.json`, or an inputs inventory / base rate where no series exists), baseline stated, method chosen by the profile's route, validation read from `summary.json`, uncertainty quoted with measured coverage or labelled a scenario, `run.py report` rendered with `claims.json`, an interpretation checked with `run.py report --check` (all seven pass with every number sourced or declared on an `Assumption:` line), and a journal entry. Nothing under `companion/harness/truth` was opened. No file outside the run folder was modified.

## Task A (hierarchy): delivered

- `forecast.csv` (48 rows, `node,timestamp,forecast,lower,upper`, nominal 80% MinT q10/q90 band, regions add to Total), `report.md`, `interpretation.md`, `claims.json`, `brief.json`, `profile.json`, `journal.jsonl` (id 1c7f01956390).
- Route `hierarchy`: chapter 18 (`run/`, smoothing pool, MinT with shrinkage 0.2, coherent quantiles). Status `provisional`: 72 observations is below the tool's own-holdout floor, so the MinT/bottom-up ranking is unscored. Validation supplied by chapter 12 per node (`run_ch12_*`, all `passed`): the engine beats seasonal naive clearly for Total and West, is level with it for North and South. Cross-check with the `full` pool (`run_full/`) agrees on the Total within 0.2%.
- Coverage of the band was not measured (labelled a scenario band at nominal 80%); per-node chapter 12 coverages are quoted in the interpretation.

## Task B (launch): delivered

- `report.md` (headline numbers, method, every assumed input with source and firmness in `inputs.md`, sensitivity table in `sensitivity.md`), `brief.json`, `inputs.json`, `interpretation.md`, `claims.json`, `journal.jsonl` (id faea2a39668c, one year-one total, scoring date 2027-12-31).
- Method: `reconcile-tdbu` desk model (`forecasting-skills/reconcile-tdbu/scripts/reconcile_model.py`), the launch reference's route when no comparable products exist. Bottom-up 5.689 MM units against top-down 3.677 MM, a 43% gap; reconciled with penetration locked (survey frequency moved from 20 to 12.22 claimed trips) to 3.861 MM units, 15.40 MM dollars, 0.93% share. Lock-frequency alternative 3.677 MM. Both-move reconciliation oscillated and did not converge.
- Sensitivity: distribution, differentiation and evoked-set size move the number most; media least among the plan levers.
- Could not do: no `run.py apply` chapter accepts a launch with no history and no reference products. Chapter 27 `mode: estimate` was tried twice and refused (see command failures). The `run/` folder was therefore hand-assembled from the desk model's JSON outputs (`run/run.json` says so) so that `run.py report`, `--check` and `journal add` could run on it. No profile.json (no series).

## Task C (intermittent): delivered

- `forecast.csv` (13 rows, `timestamp,forecast`), `report.md` containing the line `order-up-to: 21`, `interpretation.md`, `claims.json`, `brief.json`, `profile.json`, `journal.jsonl` (id 83185a51de7b).
- Route `intermittent`: chapter 12 `pool: intermittent` (`run/`, `passed`) selected Mean (validation RMSSE 0.672; SBA, Croston, TSB within 0.03; no method beat the mean rate). Chapter 21 (`run_ch21/`, `passed`) order-up-to policy at lead time 2, review 1, service 0.95: achieved cycle service 1.0, fill rate 1.0, mean on-hand 12.7; order-up-to at the last review 21 (19 to 21 over the last 13 reviews). Cost-optimal quantile order (10 to 14) noted as lower.

## Task D (daily, multiseasonal): delivered

- `forecast.csv` (28 rows, `timestamp,forecast,lower,upper`, the selected model's own 80% band, measured holdout coverage 0.893), `report.md`, `interpretation.md`, `staffing_plan.csv` (75th-percentile staffing level for the 3:1 cost asymmetry), `claims.json`, `brief.json`, `profile.json`, `journal.jsonl` (id 75e71a8f30af).
- Route `multiseasonal`: chapter 12 `pool: multiseasonal` (`run_ms/`, `passed`) selected Fourier ARIMA (validation MAE 7.57 vs 11.71 seasonal naive; holdout 7.93 vs 14.82). A second run with `pool: regressors` and `future_promo.csv` (`run_reg/`, `passed`) showed the promo models lose to ETS at the origins, and no promotion is scheduled in the horizon.
- Declared judgment: 2026-01-01 scaled by 0.80 and 2026-01-19 (MLK Day) by 0.85, from the holiday ratios in the history; neither run models holidays. The journal holds the unadjusted model rows.
- MSTL and Prophet skipped by the tool (need two full yearly cycles; 730 days is one short); TBATS not installed.

## Task E (event probabilities): delivered

- `probabilities.csv` (10 rows), `report.md` (base rate, derivation per event, scoring plan), `interpretation.md`, `claims.json`, `brief.json`, `journal_ch10.json` (chapter 10 event journal: every revision with reason, source, counterargument).
- Method: base rate 0.30 (214 cases) as a Beta(2.4, 5.6) prior (strength 8, declared), updated with each team's last four releases via chapter 2 (`run_ch02_0of4`, `_1of4`, `_2of4`, all `passed`): 0.200 / 0.283 / 0.367; E08's much-smaller scope given a declared likelihood ratio of 2.0, giving 0.537. Nine of ten fall below the 40% intervention line. Chapter 10 (`run/`) returned `needs_evidence` as expected (nothing resolved yet).
- Could not do: `run.py journal add` refuses event runs (no dated forecast column), so there is no `journal.jsonl` for E; `journal_ch10.json` is the journal, scored by rerunning chapter 10 with outcomes filled in.

## Task F (short history): delivered

- `forecast.csv` (12 rows, `timestamp,forecast,lower,upper`), `report.md`, `interpretation.md`, `claims.json`, `brief.json`, `profile.json`, `journal.jsonl` (id c799be7e7f4b).
- Route `too_short` (20 observations; floor 72). Chapter 12 (`run/`) returned its `provisional` placeholder: last season re-levelled by growth 1.179, 1,393 units for the year, scenario band 1,214 to 1,572 (in-sample, no coverage). Delivered as a labelled scenario with the no-growth floor (1,181) and a declared central budget case of about 1,300 (growth decelerating through late 2025). No reference-class table was supplied, so chapter 25 could not run.

## Task G (level shift): delivered

- `forecast.csv` (12 rows, `timestamp,forecast,lower,upper`, the `break_scenario` and its scenario band), `report.md`, `interpretation.md`, `claims.json`, `brief.json`, `profile.json`, `journal.jsonl` (id 4912728379d4, journaled with `--column break_scenario`).
- Chapter 12 (`run/`, `passed`) selected Combination(top3) at the origins but its holdout (the post-shift year) MAE was 39.9 against 39.3 for seasonal naive with 33% band coverage: validation does not cover the horizon. Chapter 24 (`run_ch24/`, `passed`, season 12, calibration 36) dated the last changepoint at 2025-05-01 and preferred the adaptive policy. Shift of -54.1 a month, persistent for eight months, no reason given to expect reversal, so the scenario is delivered: 3,582 for 2026 (band 3,284 to 3,880); the refit model says 3,513. Declared recommendation: commit about 3,500 given the ten-percent write-off rule.

## Command failures met

1. Task B: `run.py apply --chapter 27` with `mode: estimate` and a header-only reference-product CSV: `Application stopped: Missing columns: target, timestamp` (exit 2).
2. Task B: same with a header-only `timestamp,target` file: `Application stopped: Input has no rows` (exit 2). Resolved by assembling the run folder by hand from the desk model outputs.
3. Task B: first `run.py report --run` / `journal add` on the hand-built run: `could not convert string to float` because results.csv carried a text `scenario` column (my own formatting; removed, then both ran).
4. Task E: `run.py journal add --run run` and `--run run_ch02_1of4`: `Journal stopped: this run has no dated forecast column ... only series forecasts are journaled` (exit 2). Not resolvable with the tool; the chapter 10 JSON journal stands in.
5. Task G: `run.py apply --chapter 24` with `"season": "auto"`: `Application stopped: season must be an integer >= 1` (exit 2). Resolved by declaring season 12 in `config_ch24.json` (the profile had found 12).
6. Task D: `pandas.to_markdown` needs `tabulate`, which is not installed in the venv; the staffing table was rendered by hand instead (not a run.py failure).
7. Several `report --check` passes flagged numbers with no claim (holdout baseline MAEs, bullwhip ratios, row counts, data arithmetic); each was reworded, moved to an `Assumption:` line, or backed by an extra `--also` run until the check passed.

## Notes on the tools

- Chapter 18 skips its holdout leaderboard at exactly 72 monthly observations although its message says "at least 72 observations are needed"; the rendered report then prints "Method ranking on the holdout: MinT, bottom_up", which is an ordering, not a score.
- Chapter 2's report lists only the posterior parameters in `claims.json`, not the posterior means in `results.csv`, so the means had to be declared as arithmetic on the parameters.
- `report --check` treats a dict of numbers in `summary.json` as claims only when it has at most 12 keys; the task B summary was split accordingly.
