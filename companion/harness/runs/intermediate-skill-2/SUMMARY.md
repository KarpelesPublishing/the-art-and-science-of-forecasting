# intermediate-skill-2: summary

Run 2026-09-20 following `forecasting-skills/forecast-workflow/SKILL.md` (seven gates) for every task.
Every task has brief.json, profile.json (where the input is a series), an apply run folder with
summary.json and results.csv, rendered report.md and claims.json, interpretation.md checked with
`run.py report --check` (exit 0 on the final check for every task), and one journal entry in
`<task>/journal.jsonl`. `report.md` in each run folder is the rendered report followed by the
interpretation (and the second run's report where one was used). Nothing under `companion/harness/truth`
was opened, searched or used. No file outside `companion/harness/runs/intermediate-skill-2/` was modified.

## A-hierarchy

Delivered: `forecast.csv` (48 rows, node,timestamp,forecast,lower,upper; forecast = MinT reconciled
point, lower/upper = MinT q10/q90 from reconciled joint draws, stated coverage 80 percent nominal, not
measured), `report.md`, brief, profile, `run/` (chapter 18, edges North/South/West to Total,
coherent_quantiles), `run_ch12_Total/` (chapter 12 on the Total node for the baseline comparison),
claims, journal, interpretation.
Findings: histories coherent within 0.1; chapter 18 is `provisional` (72 observations is below the 84
its holdout leaderboard needs), so MinT was reported without a holdout comparison; the Total node alone
through chapter 12 passed (Airline ARIMA, validation MAE 10.2 vs 16.4 seasonal naive, holdout 5.45)
and its annual sum matches the reconciled total within one unit. Regions add to the total exactly;
the quantile columns do not.

## B-launch

Delivered: `report.md` (headline numbers, method, every assumed input, sensitivity table),
`inputs.md` (inventory with sources and measured/judged/guessed), `inputs.json`, desk-model outputs
(single pass, reconciled with penetration locked, frequency locked and both free), `sensitivity.py`
and `sensitivity.csv`, a constructed `run/` (summary.json, results.csv with an even monthly split for
journaling, run.json, brief.json) so `run.py report` and `run.py journal add` could run, claims,
journal, interpretation.
Findings: route reconcile-tdbu (no comparable launched products, so chapter 27 launch mode could not
run). Unreconciled gap 42.96 percent (trial-and-repeat 5.689 MM vs market-share 3.677 MM); the model
argued with the claimed purchase frequency; penetration locked, frequency moved 20 to 12.22, converged
in 2 passes at 3.861 MM units, 15.4 MM dollars, 0.93 percent share; locking frequency instead gives
3.677 MM. Distribution is the biggest lever, then category size, then the concept-test scores.
All labelled scenarios; scoring date 2027-10-01. Letting both inputs move did not converge in 25
passes (oscillated), which is recorded as a model outcome, not a command failure.

## C-intermittent

Delivered: `forecast.csv` (13 rows, timestamp,forecast), `report.md` with "order-up-to: 21",
brief, profile, `run/` (chapter 12 intermittent pool), `run_ch21/` (order-up-to simulation, lead time
2, review 1, service 0.95), claims, journal, interpretation.
Findings: 60 percent zeros; Mean selected on RMSSE (0.6716) ahead of SBA and Croston; naive baseline
validation MAE 3.415 vs 2.923; holdout MAE 3.45. Chapter 21 simulation at the 95 percent quantile of
bootstrapped three-week demand reached cycle service 1 and fill rate 1, mean on-hand 12.72; final
order-up-to level 21 (cost-optimal alternative 14). Level declared on an Assumption line because the
renderer does not list per-row policy values in claims.

## D-daily-multiseasonal

Delivered: `forecast.csv` (28 rows, timestamp,forecast,lower,upper; split-conformal band at nominal
80 percent, measured holdout coverage 0.8571), `report.md`, brief, profile, `run/` (chapter 12
multiseasonal pool), `run_regressors/` (chapter 12 regressors pool with promo and future_promo.csv
as a cross-check), claims, journal, interpretation.
Findings: Fourier ARIMA selected, validation MAE 7.573 vs 11.71 seasonal naive (35 percent better),
holdout 7.925 vs 14.8; the promo-driven models lost to plain ETS and no promotion is scheduled in the
horizon, so the driver adds nothing here. Uncertain days flagged: 2026-01-01 (New Year's Day ran about
40 visits low in both prior years; no holiday term in the model; left high because understaffing is
the costly error), 2025-12-31, the two January weekends, and the last week. Staffing lean to the
upper band stated from the 3:1 cost asymmetry. MSTL and Prophet were skipped by the tool (needs two
full yearly cycles); TBATS not installed.

## E-event-probability

Delivered: `probabilities.csv` (10 rows), `report.md`, brief, `base-rate.md`, `ch02/` (three chapter 2
Beta-binomial runs for the 0/4, 1/4 and 2/4 records), `journal_ch10.json` (events with resolution rule
plus revisions), `run/` (chapter 10 on that journal: `needs_evidence`, nothing resolved yet),
`run_journal/` (a carrier run so the series journal could record the ten probabilities), claims,
journal, interpretation.
Findings: base rate 0.30 (214 cases); prior Beta(3,7); posteriors 0.214 (late 4 of 4), 0.286 (late 3 of
4), 0.357 (on time 2 of 4); E08 raised to 0.526 by a declared likelihood ratio of 2 for much smaller
scope. Nine of ten fall below the 0.40 intervention line; teams 3, 5, 7 are the marginal cases.
Scoring method described (rerun chapter 10 with outcomes on 2026-12-31; Brier vs base rate; calibration
bins over quarters).

## F-short-history

Delivered: `forecast.csv` (12 rows; forecast = provisional placeholder, lower/upper = scenario_low/high,
a scenario band, no coverage), `report.md`, brief, profile, `run/` (chapter 12, `provisional`),
claims, journal, interpretation.
Findings: 20 observations against a floor of 72; route `too_short`; the engine returned the placeholder
(last season re-levelled by growth 1.179), annual 1,393 units, band 1,214 to 1,572, seasonal-naive
1,181. The report says plainly that nothing was validated, that the "season" is one year of data and
may be a launch ramp, and that December's growth is already below the ratio applied.

## G-level-shift

Delivered: `forecast.csv` (12 rows; forecast = `break_scenario`, lower/upper = `break_scenario_low/high`),
`report.md`, brief, profile, `run/` (chapter 12, passed, with break_scenario), `run_ch24/` (chapter 24
changepoints, CUSUM, policies), claims, journal (journaled with `--column break_scenario`),
interpretation.
Findings: level shift of -54.1 eight months before the end, confirmed by chapter 24 (changepoint
2025-05-01, adaptive policy best MAE 15.33 vs frozen 25.42). The validated Combination(top3) had
holdout MAE 39.9 vs 39.3 seasonal naive and conformal coverage 0.3333 across the shift, so the
break scenario is delivered instead: annual 3,582, range 3,284 to 3,880. Commitment recommendation:
the lower band (3,284) given the 10 percent write-off rule, with the survival thresholds on
Assumption lines.

## Could not do

- A: no holdout leaderboard for the reconciliation methods (history below the chapter 18 floor); the
  hierarchicalforecast cross-check is not installed.
- B: chapter 27 launch mode impossible without reference products; no coverage can be measured.
- D: TBATS not installed; MSTL/Prophet skipped by the tool for lack of two full yearly cycles.
- E: `run.py journal add` refuses an event run (see failures), so a carrier run was built for the
  series journal; the scoreable record is `journal_ch10.json`.
- F: no validated forecast is possible on 20 observations; delivered as a labelled scenario.

## Command failures met

1. E: `run.py journal add --run E-event-probability/run` stopped with "this run has no dated forecast
   column (forecast, prediction, median or nowcast); only series forecasts are journaled". Worked
   around with `run_journal/` (node,timestamp,forecast rows dated at the resolution date).
2. `run.py report --check` exited 4 on the first pass of every interpretation (A, B, D, E, F, G) for
   numbers not in claims (hand sums, profile numbers not carried into hierarchy claims, row counts,
   nominal percentages such as "95%" and "365"); each was fixed by rephrasing or by moving the number to
   its own `Assumption:` line. Note: the checker reads only the first line of an `Assumption:`
   paragraph, so multi-line assumptions had to be split into one line each.
3. B: the desk model's default reconciliation (both inputs free) did not converge in 25 passes; the
   penetration-locked run converged in 2 and was used.
No `run.py brief`, `profile` or `apply` command failed.
