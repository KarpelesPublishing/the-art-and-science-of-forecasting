# expert-skill-2: summary

All seven tasks run through the forecast-workflow gates (brief, profile or its substitute, baseline, method chosen by the profile, validation, uncertainty, report with claims check, journal). Every `interpretation.md` passes `run.py report --check` with zero unsupported numbers (with `--also` for the supporting runs). Nothing under `companion/harness/truth` was opened or searched. No file outside `companion/harness/runs/expert-skill-2/` was modified.

## Delivered per task

### A-hierarchy
- `forecast.csv` (48 rows: node,timestamp,forecast,lower,upper; MinT reconciled point, MinT q10/q90 as a nominal 80% coherent band; Total equals North+South+West exactly), `report.md` (interpretation plus rendered chapter 18 report), `interpretation.md`.
- Workflow files: `brief.json`, `profile.json` (route hierarchy), `config.json` (chapter 18, edges, coherent_quantiles), `run/` (summary.json, results.csv, report.md, claims.json, diagnostic.png, run.json), `claims.json`, `journal.jsonl`.
- Supporting: chapter 12 per node (`run_ch12_{Total,North,South,West}/` with `series_*.csv`, `config_ch12.json`) for the seasonal-naive baseline, leaderboards, holdout scores and conformal bands.
- Finding: chapter 18 status provisional (72 observations too few for its own holdout leaderboard). Per node the selections beat seasonal naive at the origins but lost to it on the single holdout for Total, North and South; reported plainly. Annual reconciled total 3,948 units.

### B-launch
- `report.md` (headline numbers, method, every assumed input, sensitivity table, scenarios labelled, scoring date), `interpretation.md`, `inputs.md` (inventory with source and measured/judged/guessed status), `inputs.json`, `sensitivity.csv`.
- Workflow files: `brief.json`, `run/` (hand-built from the reconcile-tdbu top-down bottom-up triangulation model by `build_run.py`: results.csv with a monthly phasing, summary.json, run.json, report.md, claims.json), `claims.json`, `journal.jsonl`. No profile: no series exists; `inputs.md` is the profile substitute per launch.md.
- Top-down bottom-up triangulation model outputs: `model_single_pass.txt`, `model_reconciled*.txt/json` (both-move, lock-penetration, lock-frequency).
- Finding: the two routes disagreed by 43% (survey frequency inconsistent with category size). Penetration locked, frequency absorbed the gap: 3.861 MM units, $15.40 MM, 0.93% share; lock-frequency alternative 3.677 MM. Scenario range 2.934 to 4.767 MM units. Distribution is the most sensitive input. No test market, no comparables: chapter 27 launch mode not possible.

### C-intermittent
- `forecast.csv` (13 rows: timestamp,forecast; flat validated Mean rate 2.53 units/week), `report.md` containing "order-up-to: 21", `interpretation.md`.
- Workflow files: `brief.json`, `profile.json` (route intermittent, 60% zeros), `config.json`, `run/` (chapter 12 intermittent pool), `claims.json`, `journal.jsonl`.
- Supporting: `run_ch21/` (bootstrapped order-up-to policy, lead time 2, review 1, 95% service), `run_ch24/` (break check: no dated changepoint, frozen best), `run_policy/` (hand-built evidence run recording the level at the last review and empirical 3-week demand quantiles so the report's stocking numbers are claim-backed).
- Finding: Mean beat the Croston family on RMSSE at the origins; demand rate has drifted up year over year, flagged; order-up-to 21 from the chapter 21 policy at the last review (empirical 95% quantile of 3-week sums 16.9 all history, 18.9 last year, max 21).

### D-daily-multiseasonal
- `forecast.csv` (28 rows: timestamp,forecast,lower,upper; Fourier ARIMA point with 80% conformal band; 1 January adjusted by a documented holiday ratio), `report.md`, `interpretation.md`.
- Workflow files: `brief.json` (3:1 cost asymmetry recorded), `profile.json` (route multiseasonal, periods 7 and 365), `config_ms.json`, `run_ms/` (selected run), `claims.json`, `journal.jsonl`.
- Supporting: `run_reg/` (regressors pool with the promo flag and future_promo.csv: promo models lost; no promotions in the horizon), `run_holiday/` (evidence run for the New Year adjustment: prior-year ratios and the adjusted row).
- Finding: Fourier ARIMA validation MAE 7.573 vs 11.707 seasonal naive; holdout 7.925 vs 14.8; model band coverage 0.893 at 80% nominal. Staff to the upper band given the cost ratio; 1 January is the uncertain day (model 176.9, adjusted 149.5).

### E-event-probability
- `probabilities.csv` (10 rows: event_id,probability), `report.md` (base rate, how each probability was reached, scoring plan), `interpretation.md`, `base-rate.md`, `probabilities_detail.csv`, `journal_ch10.json` (chapter 10 event journal: every revision with timestamp, reason, evidence source, counterargument).
- Workflow files: `brief.json`, `run/` (chapter 10 on the journal: needs_evidence, as expected before resolution), `claims.json`; `run_ch02_{zero,one,two}/` (Beta posterior for 0, 1, 2 on-time of 4 with a Beta(2.4,5.6) prior at the company rate); `run_probs/` (evidence run holding the probability table, the 40% rule count and expected Brier).
- Finding: 0.20 (E09, E10), 0.283 (E01, E02, E04, E06), 0.367 (E03, E05, E07), 0.591 (E08, with a judgment likelihood ratio 2.5 for much smaller scope). Intervene on 9 of 10 under the 40% rule.
- Not delivered: `journal.jsonl` via `run.py journal add` (refused: event runs have no dated forecast column). The event journal is `journal_ch10.json`, which is what judgment.md prescribes. Chapter 26 refused unresolved outcomes (by design); `ch26_input.csv` and `config_ch26.json` are left ready for the resolution date.

### F-short-history
- `forecast.csv` (12 rows: timestamp,forecast,lower,upper; the tool's provisional placeholder, last season re-levelled by growth 1.179, scenario band), `report.md`, `interpretation.md`.
- Workflow files: `brief.json`, `profile.json` (route too_short: 20 observations against a floor of 72), `config.json`, `run/` (chapter 12, status provisional), `claims.json`, `journal.jsonl`; `run_evidence/` (year-over-year ratios and annual sums so the fading-growth discussion is claim-backed).
- Finding: labelled scenario only, 1,393 units for the year, range 1,214 to 1,572, seasonal-naive floor 1,181; growth fading (Jul 1.30 to Dec 1.13); one seasonal cycle seen. Says what would unlock a validated forecast.

### G-level-shift
- `forecast.csv` (12 rows: timestamp,forecast,lower,upper; validated Combination(top3) point, scenario range spanning the combination and the break scenario widened by twice the post-shift deseasonalised sd), `report.md`, `interpretation.md`.
- Workflow files: `brief.json` (write-off asymmetry recorded), `profile.json` (route engine with a level-shift warning 8 periods back), `config.json`, `run/` (chapter 12, passed, with break_scenario), `claims.json`, `journal.jsonl`; `run_ch24/` (chapter 24: changepoints dated, adaptive policy best), `run_scenario/` (evidence run: deseasonalised levels, annual totals, write-off floors).
- Finding: step down of about 59 units a month (17%) from May 2025, assumed to persist. Annual 3,513 (range 3,341 to 3,754) against 3,799 for repeating last year; the seasonal-naive commitment would be written off inside the scenario range. Pre-shift bands untrustworthy (holdout coverage 0.333), so the range is labelled a scenario.

## What I could not do
- Task B: no chapter 27 launch mode (no comparable launched products); triangulation-model constants untuned (no launch history).
- Task E: no `run.py journal add` entry (see below); no chapter 26 decision loss until outcomes exist.
- Task A: chapter 18 could not score reconciliation on a holdout at 72 observations; ERM/trace-minimisation variants not installed.
- Task D: TBATS unavailable (statsforecast not installed); MSTL and Prophet skipped by the tool (fewer than two yearly cycles).
- Where the rendered reports lacked a number the interpretation needed (stocking level, holiday ratio, launch inputs and sensitivities, y/y ratios, scenario sums), I built small evidence run folders (`run_policy`, `run_holiday`, `run_probs`, `run_evidence`, `run_scenario`, and B's `run/`) from the tools' own outputs and the task data, rendered them with `run.py report`, and passed them with `--also`; each is labelled as a reading or judgment, not a validated model.

## Command failures met
1. Task C: `run.py apply --chapter 24` with `"season": "auto"` stopped: "season must be an integer >= 1". Rerun with `"season": 1` succeeded (chapter 24 does not accept auto).
2. Task E: `run.py apply --chapter 26` on unresolved events stopped: "Numeric inputs must be finite and complete" (the tool requires resolved outcomes; expected).
3. Task E: `run.py journal add --run .../E-event-probability/run` stopped: "this run has no dated forecast column (forecast, prediction, median or nowcast); only series forecasts are journaled" (expected for an event journal).
4. Task B: `reconcile_model.py --reconcile` with both inputs free oscillated for 25 passes and did not settle (reported by the model itself); resolved by `--lock-penetration` (converged in 2 passes). Two attribute-name errors in my own `build_run.py` (EngineResult fields) were fixed before the run folder was built.
5. `run.py report --check` flagged unsupported numbers on the first pass for A (500 draws), B (input values and sensitivity bounds), C (32, 48, 52, 8.96), D (365) and E (95, 1.15); each was fixed by adding the number to an evidence run's summary or by rewording, and every final check passes.
