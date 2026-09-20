# intermediate-skill-1: summary

Persona: knows basic statistics, has made spreadsheet forecasts. All seven tasks were run through the forecast-workflow gates (brief, profile or its substitute, baseline stated, method chosen by the profile's route, validation read from summary.json, uncertainty quoted with measured coverage or labelled scenario, rendered report with claims check, journal entry). Every `interpretation.md` passes `run.py report --check` with zero unsupported numbers (with `--also` for supporting runs; judgment numbers on `Assumption:` lines). Nothing under `companion/harness/truth` was opened, searched or used. No file outside `companion/harness/runs/intermediate-skill-1/` was modified (every journal call used `--journal` inside the run folder).

## Delivered per task

### A-hierarchy
- `forecast.csv` (48 rows: node,timestamp,forecast,lower,upper; MinT-reconciled point with MinT q10/q90 as a nominal 80% coherent band; regions add to Total within 0.1 units), `report.md` (interpretation plus the rendered chapter 18 report), `interpretation.md`.
- Workflow files: `brief.json`, `profile.json` (route hierarchy), `config.json` (chapter 18, three edges, coherent_quantiles), `run/` (summary.json, results.csv, report.md, claims.json, diagnostic.png, run.json), `claims.json`, `journal.jsonl`.
- Supporting: chapter 12 per node (`run_ch12_{Total,North,South,West}/`, `series_*.csv`, `config_ch12.json`) to state the seasonal-naive baseline and the per-node holdout scores.
- Finding: chapter 18 is provisional (72 observations too few to hold out a slice for the reconciliation leaderboard). Per node the models beat seasonal naive at the origins; on the holdout Total and West won, North and South lost narrowly. Annual reconciled Total 3,948 units; no cost asymmetry, median reported.

### B-launch
- `report.md` (headline numbers, method, every input with source and status, sensitivity table, scenarios labelled, scoring date), `interpretation.md`, `inputs.md` (inventory: measured/judged/guessed), `inputs.json` and `inputs_survey.json`, `sensitivity.csv`, `sensitivity_base.json`, the desk-model outputs (`model_*.txt/json`).
- Workflow files: `brief.json` (yearly, horizon 1, outcome 2027-10-01), `run/` (evidence run hand-built from reconcile_model.py outputs: summary.json of every model scalar and sensitivity, one-row results.csv, run.json, brief.json), `claims.json`, `journal.jsonl`. No profile: no series exists; `inputs.md` is the profile substitute per launch.md.
- Finding: routes disagreed by 44.98% (survey frequency inconsistent with the category size); penetration locked, frequency absorbed the gap: 3.46 MM units, 13.8 MM dollars, 0.83% share; lock-frequency alternative 2.951 MM; input-scenario range 2.247 to 4.852 MM. Distribution and the concept-test differentiation move the number most. Everything labelled scenario; desk-model constants untuned; chapter 27 launch mode impossible (no comparable launches).

### C-intermittent
- `forecast.csv` (13 rows, timestamp,forecast; flat Mean rate 2.528 units a week), `report.md` containing "order-up-to: 21", `interpretation.md`.
- Workflow files: `brief.json`, `profile.json` (route intermittent, 60% zeros), `config.json`, `run/` (chapter 12 intermittent pool, passed), `claims.json`, `journal.jsonl`.
- Supporting: `run_ch21/` (bootstrapped order-up-to simulation, lead time 2, review 1, service 0.95: level 21 at the last review, achieved cycle service and fill rate 1, mean on-hand 12.72), `run_ch24/` (no dated changepoint, frozen policy best, but 2 CUSUM alarms and a 0.7 sd drift flagged for rerun).
- Finding: Mean beat SBA, Croston and TSB on RMSSE and never lost to the baseline; holdout MAE 3.45; conformal band covered 0.7692 of the holdout at nominal 80%.

### D-daily-multiseasonal
- `forecast.csv` (28 rows, timestamp,forecast,lower,upper; Fourier ARIMA point with the 80% conformal band; 2026-01-01 scaled by a declared holiday ratio 0.84), `report.md`, `interpretation.md`.
- Workflow files: `brief.json` (3:1 cost asymmetry recorded), `profile.json` (route multiseasonal, periods 7 and 365), `config_ms.json`, `run_ms/` (selected run), `claims.json`, `journal.jsonl`.
- Supporting: `run_reg/` (regressors pool with the promo flag and future_promo.csv: promo models lost at the origins; no promotions in the horizon).
- Finding: Fourier ARIMA validation MAE 7.57 vs 11.7 seasonal naive, holdout 7.93 vs 14.8; conformal coverage 0.8571, model band 0.8929. Staff to the upper band given the cost ratio; New Year's Day, weekends and the fourth week are the uncertain days.

### E-event-probability
- `probabilities.csv` (10 rows), `report.md` (base rate, how each probability was reached, scoring plan), `interpretation.md`, `base-rate.md`, `journal_ch10.json` (chapter 10 event journal: ten events with resolution rules, one revision each with reason, evidence source and counterargument).
- Workflow files: `brief.json`, `run/` (chapter 10 on the journal: needs_evidence, as expected before resolution), `claims.json`; `run_ch02_{0,1,2}of4/` (Beta(2.4, 5.6) prior at the company rate 0.3 updated with 0, 1, 2 on-time of 4).
- Finding: 0.2 (E09, E10), 0.2833 (E01, E02, E04, E06), 0.3667 (E03, E05, E07), 0.591 (E08, with a declared likelihood ratio 2.5 for much smaller scope). Nine of ten below the 40% line.
- Not delivered: `journal.jsonl` (see command failures); the chapter 10 journal is the event journal judgment.md prescribes.

### F-short-history
- `forecast.csv` (12 rows; the tool's provisional placeholder: last season re-levelled by growth 1.179, scenario band from in-sample errors), `report.md`, `interpretation.md`.
- Workflow files: `brief.json`, `profile.json` (route too_short: 20 observations against a floor of 72), `config.json`, `run/` (chapter 12, status provisional), `claims.json`, `journal.jsonl`.
- Finding: labelled scenario only, 1,393 units for the year against a seasonal-naive floor of 1,181 (declared reading of the data); year-over-year growth is fading (1.30 in July to 1.13 in December), so the lower half of the band is the likelier landing; says what history would unlock a validated forecast.

### G-level-shift
- `forecast.csv` (12 rows; break_scenario point and break_scenario_low/high range, per the workflow's level-shift rule), `report.md`, `interpretation.md`.
- Workflow files: `brief.json` (write-off asymmetry recorded), `profile.json` (route engine, level shift 8 periods back), `config.json`, `run/` (chapter 12, passed, with break_scenario), `claims.json`, `journal.jsonl` (journaled with `--column break_scenario`); `run_ch24/` (changepoint dated 2025-05-01, adaptive policy best).
- Finding: shift of -54.1 units a month assumed to persist. Scenario total 3,582 (range 3,284 to 3,880); validated model refit 3,513; recommend committing 3,513 so the write-off line (3,194, declared arithmetic) sits below the scenario's lower bound. Pre-shift bands untrustworthy (holdout coverage 0.3333), so the range is a scenario.

## What I could not do
- Task E: no `journal.jsonl` via `run.py journal add` (the command refuses event runs); no chapter 26 decision loss until outcomes exist.
- Task B: no chapter 27 launch mode (no comparable launched products); no monthly phasing (the desk model gives annual volume only, so the journal holds one yearly row); the evidence run folder was hand-built from the model's outputs so that the report and claims could be rendered.
- Task A: chapter 18 could not score reconciliation methods on a holdout at 72 observations; hierarchicalforecast cross-check not installed.
- Task D: TBATS unavailable (statsforecast not installed); MSTL and Prophet skipped by the tool (fewer than two yearly cycles).
- Task F: no validated forecast is possible; the deliverable is the tool's placeholder scenario.
- Numbers that the rendered reports do not carry (a data reading such as last year's total, a holiday ratio, a write-off floor) were declared on `Assumption:` lines rather than added to the reports.

## Command failures met
1. Task E: `run.py journal add --run .../E-event-probability/run --journal ...` exited 2: "this run has no dated forecast column (forecast, prediction, median or nowcast); only series forecasts are journaled". Expected for an event journal; `journal_ch10.json` is the journal.
2. `run.py report --check` exited 4 on the first pass for A (seasonal-naive holdout MAEs and a draw count not in claims), B (input values and sensitivity bounds not yet in the evidence summary), D (365, 40), E (214, 95), F (band sums, 52) and G (Welch t 12.5, shift standard error 2.65). Each was fixed by rewording, by declaring the number on an `Assumption:` line, or (B) by adding the inputs and sensitivity bounds to the evidence run's summary.json; every final check passes.
3. No `run.py apply`, `profile` or `brief` call failed.
