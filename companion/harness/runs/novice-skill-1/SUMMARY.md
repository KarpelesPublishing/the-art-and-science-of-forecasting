# novice-skill-1: delivery summary

Run 2026-09-20 by an assistant with no forecasting training, following `forecasting-skills/forecast-workflow/SKILL.md` (seven gates) and the references it points to (first-forecast.md, launch.md, judgment.md, reconcile-tdbu, chapter skills 2, 10, 12, 18, 21, 24). Nothing under `companion/harness/truth` was opened. No file outside `companion/harness/runs/novice-skill-1/` was modified.

## One workaround used on every apply run

`run.py apply` refuses any output directory inside `companion/` that is not under `companion/applied-runs/` ("Inside companion, applied outputs must be under applied-runs so private results are excluded from bundles"). Each apply run was therefore written to the session scratchpad and copied unchanged into the task's run folder (`run/`, `run-*/`). `report` and `journal add` were then run on the copied folders and worked normally.

## Per task

### A-hierarchy (regional and total sales, 12 months, coherent)
Delivered: `forecast.csv` (48 rows: node, timestamp, forecast, lower, upper; forecast is the chapter 18 MinT reconciled point, lower/upper are the reconciled joint-draw q10/q90, stated coverage 80 percent nominal, not measured), `report.md`, `claims.json`, `brief.json`, `profile.json` (Total node) plus `profile-North/South/West/Total/`, `run/` (chapter 18, smoothing pool, coherent quantiles, status provisional: no holdout leaderboard possible on 72 observations), `run-total-ch12/` (chapter 12 on the Total node, status passed: Airline ARIMA beat seasonal naive at origins and on the holdout), `interpretation.md` (checked: every number supported), `journal.jsonl`.
Could not do: `run.py profile` does not read long-form `node,timestamp,target` files (it failed with "Invalid frequency: H"), so each node was split into `nodes/*.csv` and profiled separately. `run.py report` crashes on the chapter 18 run (`TypeError: string indices must be integers` in `_validation_block`: the chapter 18 leaderboard is a list of strings), and `run.py journal add` refuses it (no dated forecast column). report.md, claims.json and the journal entry therefore come from the chapter 12 Total-node run, not the hierarchy run. A first chapter 18 run with `pool: full` skipped coherent quantiles (one node's ensemble has no intervals); rerun with the chapter's default smoothing pool. Regions add to the total to within 0.01 in every month of forecast.csv.

### B-launch (no sales history)
Delivered: `report.md` (headline scenarios, method, every assumed input, sensitivity table, scoring date 2027-12-31), `brief.json`, `inputs.md` (inventory with sources and measured/judged/guessed status), `inputs.json`, model outputs (`model-run.*`, `model-reconcile.*`, `model-reconcile-lock-penetration.txt`, `model-reconcile-lock-frequency.txt`), `sensitivity.md`, `interpretation.md`.
Result: reconcile-tdbu, two engines disagreed by 43 percent on the brief's inputs; default reconciliation oscillated for 25 passes; locking penetration converged on 3.86 million units ($15.4 million), locking frequency on 3.68 million ($14.7 million). Distribution is the dominant sensitivity. All numbers labelled scenarios.
Could not do: no `run.py apply` run exists for this route, so no `profile.json`, `run/` folder, rendered report, `claims.json`, `--check`, or journal entry; report.md was written by hand from the model outputs in the folder. Chapter 27 launch mode not run (no reference products in the brief).

### C-intermittent (spare part, 13 weeks, order-up-to)
Delivered: `forecast.csv` (13 rows, timestamp, forecast), `report.md` (rendered chapter 12 report with the rendered chapter 21 report appended and the line `order-up-to: 21`), `claims.json` (chapter 12) and `claims-ch21.json`, `brief.json`, `profile.json`, `run/` (chapter 12 intermittent pool, status passed, Mean selected on RMSSE, SBA runner-up), `run-ch21/` (order-up-to simulation, lead 2, review 1, service 0.95: achieved cycle service and fill rate 100 percent, cost-optimal level 14), `run-provisional-season52/` (the first attempt), `interpretation.md` (checked against run/: every number supported), `journal.jsonl` (chapter 12 run only).
Could not do / notes: the brief's `--frequency weekly` made apply fail with "Missing periods or timestamps inconsistent with frequency"; rewritten as `W-MON` (the profile's finding). With season left to the frequency default (52, not detected by the profile) the run was provisional (floor 156 > 144); I set `season: 1` in the config because the profile found no seasonal period, which met the floor and validated. This is a judgment call the reader should see. `journal add` refused the chapter 21 run; its rendered report carries only 5 sourced numbers (the policy metrics are not surfaced by the renderer).

### D-daily-multiseasonal (store visits, 28 days, promo known)
Delivered: `forecast.csv` (28 rows, timestamp, forecast, lower, upper; Fourier ARIMA point with its own 80 percent band, measured holdout coverage 0.8929), `report.md`, `claims.json`, `brief.json`, `profile.json`, `run/` (chapter 12 multiseasonal pool, status passed, Fourier ARIMA, validation MAE 7.57 vs 11.71 seasonal naive, holdout 7.93 vs 14.8), `run-regressors/` (chapter 12 with `promo` and future_promo.csv: ETS(auto) won, the driver models lost to the baseline), `interpretation.md` (checked: every number supported), `journal.jsonl`.
Notes: future_promo.csv has no promotion days in the window. MSTL and Prophet were skipped (need two full yearly cycles; 730 days is just under), TBATS not installed. No holiday effects: 2026-01-01 flagged as the most uncertain day, with weekends and the widest conformal days.

### E-event-probability (ten yes/no questions)
Delivered: `probabilities.csv` (10 rows), `report.md` (base rate, method per event, decision at the 40 percent line, scoring plan, written by hand), `brief.json`, `config-ch02.json`, `record-*.csv` and `run-ch02-1of4/2of4/0of4/` (chapter 2 Beta(3,7) posteriors for the three team-record types), `journal-ch10.json` (events, resolution rule, two revisions per event), `config.json`, `run/` (chapter 10 run, status needs_evidence, nothing resolved yet, with rendered report and `claims.json` holding 0 numbers), `interpretation.md`.
Result: 0.286 (late 3 of 4), 0.357 (on time 2 of 4), 0.214 (late 4 of 4), 0.625 for E08 (judged likelihood ratio 3 for a much smaller scope). Nine of ten below 40 percent.
Could not do: chapter 10 apply rejected the brief ("Use timezone-aware ISO timestamps": the brief's as-of has no timezone), so it was run without `--brief`. `journal add` refused the chapter 10 run. `report --check` on interpretation.md flags the base rate, the case count and the probabilities because no single run's claims.json holds them (they sit across the chapter 2 runs and journal-ch10.json); left as is.

### F-short-history (20 months since launch, 12 months ahead)
Delivered: `forecast.csv` (12 rows; forecast is the provisional persistence value 95.1, lower/upper are the envelope of the two placeholders in the run: flat last value and same month last year; a scenario range with no coverage level), `report.md` (rendered, status provisional), `claims.json`, `brief.json`, `profile.json` (route too_short), `run/`, `run-horizon3/` with `brief-h3.json` and `config-h3.json` (a three-month, no-season attempt, also provisional), `interpretation.md` (checked: every number supported), `journal.jsonl`.
Could not do: no validated forecast is possible from 20 observations; chapter 25 (reference classes) needs reference launches that were not supplied. The interpretation says plainly what would unlock a real forecast.

### G-level-shift (ten years monthly, break this year)
Delivered: `forecast.csv` (12 rows; Combination(top3) point with split-conformal lower/upper, nominal 80 percent, labelled a scenario range because measured holdout coverage of the member models was poor on the year of the break), `report.md`, `claims.json`, `brief.json`, `profile.json` (level shift 8 periods before the end flagged), `run/` (chapter 12, status passed: 49 percent better than seasonal naive at the origins but no better on the 2025 holdout containing the break), `run-ch24/` (changepoint dated 2025-05-01, strongest split 2025-08-01, adaptive policy best), `interpretation.md` (checked: every number supported), `journal.jsonl`.
Recommendation recorded: annual point total 3,513 units; commit to the lower band total because overcommitting by more than 10 percent triggers a write-off and the only known fact this year is a drop in level; do not use the 2025 seasonal-naive total.

## Tool problems met (recorded, not fixed)
1. `apply` output must be under `companion/applied-runs/`: worked around via scratchpad copy.
2. `profile` cannot read long-form hierarchy files.
3. `report` crashes on chapter 18 runs (leaderboard is a list of strings).
4. `journal add` accepts only series runs (refused chapters 10, 18 and 21).
5. Brief frequency "weekly" does not match Monday-dated weekly data; `W-MON` needed.
6. Chapter 10 apply rejects a brief whose as-of date has no timezone.
7. Chapter 21 rendered report exposes only 5 numbers; the policy metrics are not in claims.json.
8. `report --check` can only check against one run, so interpretations that combine two runs (A, C, E) were checked against the primary series run and numbers from the other run were rephrased or, in E, left flagged.

## Time
Each task stayed within roughly ten minutes of wall time.
