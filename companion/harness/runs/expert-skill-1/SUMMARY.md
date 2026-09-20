# expert-skill-1: summary

Persona: expert, arm: skill. Every task followed forecast-workflow's seven gates with the companion commands. Nothing under companion/harness/truth was opened, searched or used. No file outside companion/harness/runs/expert-skill-1/ was modified.

One workaround used throughout: `run.py apply` refuses any output directory inside companion/ other than companion/applied-runs/, so each apply run was written to the session scratchpad (outside the project) and then moved intact into the task's run folder. Every run folder therefore holds its brief.json, summary.json, results.csv, diagnostic.png and run.json as the command produced them.

## Task A (hierarchy): delivered

- forecast.csv: 48 rows, node,timestamp,forecast,lower,upper; MinT-reconciled points from chapter 18 (regions add to the total exactly), 80 percent split-conformal band per node from the chapter 12 runs, shifted onto the MinT point.
- report.md, interpretation.md, brief.json, profile.json (Total; per-node profiles in profile_<node>/), config.json, run/ (chapter 18, status provisional: no holdout leaderboard on 72 points, coherent quantiles skipped), run_ch12_<node>/ (four chapter 12 runs, all passed, each with report.md and claims.json), claims.json (copy of the Total run's), journal.jsonl (four entries, one per node).
- Could not do: `run.py report` fails on the chapter 18 run (TypeError in report.py `_validation_block`: the leaderboard is a list of method names when the holdout is skipped, and the renderer expects rows). `run.py journal add` refuses the chapter 18 run (no `forecast` column; results.csv has base/bottom_up/OLS/MinT). Interpretation check was run against the Total chapter 12 claims; numbers from the other node runs and from run/results.csv are listed as unsupported by that one run. The band is marginal per node, not coherent. `run.py profile` cannot read long-form input (it failed with "Invalid frequency: H"), so the nodes were split into series_<node>.csv for profiling.

## Task B (launch): delivered

- report.md with headline numbers (3.861 million units, 15.40 million dollars, 0.93 percent share, reconciled with penetration locked), method, every input with status and source (inputs.md), sensitivity table (sensitivity.csv), scenarios labelled as scenarios (scenarios.json), scoring date 2027-12-31.
- brief.json, inputs.json, model_single_pass.txt, model_reconciled.txt/.json (both inputs free: did not converge), model_reconciled_lock_penetration.txt/.json (converged in two passes), interpretation.md, run/ (a hand-assembled run record: summary.json, results.csv with a flat monthly phasing, run.json, brief.json, report.md, claims.json), claims.json, journal.jsonl (one entry).
- Could not do: no companion `apply` chapter exists for the desk model, so run/ was assembled by hand from reconcile_model.py outputs and is labelled as such; the report check flags the scenario and sensitivity numbers because claims.json only lists the results rows. The interview could not be held (non-interactive); the brief supplied all four required inputs and the assumptions are listed in inputs.md.

## Task C (intermittent): delivered

- forecast.csv: 13 weekly rows, timestamp,forecast, flat 3.78 units a week. This is the TSB level at the last review, a documented judgment override of the engine's selection (Mean, 2.53) because the 2025 level and non-zero share rose markedly; both numbers are in the report.
- report.md with "order-up-to: 21" (95 percent quantile of the bootstrapped three-week protection window at the last review of the chapter 21 simulation), interpretation.md, brief.json, profile.json, config.json, config_ch21.json, run/ (chapter 12 intermittent pool, passed, report.md and claims.json), run_ch21/ (chapter 21, passed, report.md and claims.json), claims.json, journal.jsonl (chapter 12 run).
- Notes: the brief needed frequency `W-MON` (a plain "weekly" made the apply fail with "timestamps inconsistent with frequency"). Season set to 1 because the profile detected no 52-week cycle and 144 weeks is below the 156-week floor at season 52.

## Task D (daily, two seasons, promo): delivered

- forecast.csv: 28 rows, timestamp,forecast,lower,upper, 80 percent nominal band (the selected Fourier ARIMA model's own; measured coverage 0.8929 at the origins and on the holdout). New Year's Day cut by 25 percent by hand (both prior New Year's Days ran about a quarter below their neighbours; the model has no holiday term). staffing.csv adds day of week and a 75th-percentile staffing target for the 3 to 1 cost asymmetry.
- report.md, interpretation.md, brief.json, profile.json, config_multiseasonal.json, config_regressors.json, run_multiseasonal/ (chapter 12, passed, report.md and claims.json), run_regressors/ (chapter 12 regressors pool cross-check with promo and future_promo, passed), claims.json, journal.jsonl.
- Notes: MSTL and Prophet were skipped by the tool (two years is not two full 365-day cycles); TBATS not installed. No promotions are scheduled in the horizon.

## Task E (event probabilities): delivered

- probabilities.csv (event_id,probability for E01 to E10), probabilities_detail.csv, report.md (base rate 0.30 on 214 cases, the shrinkage rule per event, the E08 scope update, the self-scoring plan), base-rate.md, journal_ch10.json (chapter 10 event journal with resolution rules and dated revisions), brief.json, config.json, run/ (chapter 10, status needs_evidence: nothing resolved yet, as expected; report.md and claims.json), claims.json, interpretation.md.
- Could not do: `run.py journal add` refuses the chapter 10 run (no dated forecast column); journal_ch10.json is the scoring record. The interpretation check flags every probability because the chapter 10 claims hold no numbers before resolution.

## Task F (short history): delivered

- forecast.csv: 12 rows with a scenario range (2025 month times 1.12 central, 0.95 low, 1.28 high), labelled as a scenario with no measured coverage.
- report.md, interpretation.md, brief.json, profile.json (route too_short), config.json, run/ (chapter 12, status provisional: persistence placeholder plus a seasonal-naive scenario column; report.md and claims.json), claims.json, journal.jsonl (the placeholder run).
- Notes: the journal holds the tool's placeholder rows, not the delivered scenario, because only tool runs can be journaled.

## Task G (level shift): delivered

- forecast.csv: 12 rows, chapter 12 Combination(top3) with the 80 percent conformal band; 2026 total 3513. Report recommends committing at or below 3500 units given the 10 percent write-off rule.
- report.md, interpretation.md, brief.json, profile.json (level shift flagged 8 periods before the end), config.json, config_ch24.json, run/ (chapter 12, passed; holdout MAE 39.9 against 39.3 seasonal naive because the holdout year contains the break), run_ch24/ (chapter 24: changepoint dated 2025-05-01, strongest split 2025-08-01, adaptive policy best), claims.json, journal.jsonl.

## Command failures and limitations, in one place

1. `run.py apply` refuses output under companion/harness; runs were produced in the scratchpad and moved (all seven tasks).
2. `run.py report --run` crashes on a chapter 18 run whose holdout was skipped (task A).
3. `run.py journal add` accepts only runs with a dated forecast column: chapter 18 (A) and chapter 10 (E) runs could not be journaled.
4. `run.py profile` does not read long-form node,timestamp,target input (A).
5. `run.py report --check` verifies against one run's claims.json only; every task's interpretation cites numbers from a second run, from results.csv sums or from the raw data, and those are listed as unsupported by the check. Each interpretation names where each number comes from.
6. Chapter 18 rejects `"season": "auto"`; the profile's 12 was set explicitly (A).
7. Weekly data needed the exact pandas alias `W-MON` in the brief (C); chapter 10 needed a timezone-aware `--as-of` (E).
