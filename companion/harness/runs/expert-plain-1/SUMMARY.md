# expert-plain-1: summary

Run folder: `companion/harness/runs/expert-plain-1/`. Scoring date 2026-09-20. All work done with my own code (numpy, pandas, statsmodels) in the companion venv; nothing under `forecasting-skills/`, `companion/src/`, `companion/scripts/`, `companion/notebooks/`, `companion/lessons/` or `companion/harness/truth` was opened or used. No files outside the run folder were modified.

## Delivered per task

| Task | Files delivered | Method in one line | Headline |
|---|---|---|---|
| A-hierarchy | `forecast.csv` (48 rows, 90 pct coverage), `report.md`, `run_a.py` | Damped additive Holt-Winters per series, MinT-shrink reconciliation, bootstrap simulation paths reconciled, interval widths calibrated on three rolling origins (x2.24) | 2025 Total 3,913 (+3.0 pct); North 1,946, South 1,128, West 839; regions sum to Total |
| B-launch | `report.md`, `sensitivity.csv`, `run_b.py` | Trial-repeat build (6.4m) and concept-share route (5.7m) reconciled; every assumed input listed with source and range; one-at-a-time sensitivity; Monte Carlo; scenarios labelled | 6.1m units, $24m retail, 80 pct range 3.5m to 9.5m (widened by hand); awareness and distribution dominate; brief's survey frequency inconsistent with category size, flagged |
| C-intermittent | `forecast.csv` (13 rows), `report.md` (contains "order-up-to: 22"), `run_c.py` | TSB rate forecast (demand incidence rising 33 to 62 pct of weeks); compound Bernoulli-size simulation over 3-week protection period with p uncertainty | 3.5 units per week flat; order-up-to 22 for 95 pct cycle service |
| D-daily-multiseasonal | `forecast.csv` (28 rows, 80 pct coverage), `report.md`, `staffing_table.csv`, `run_d.py` | OLS on log visits: trend, day-of-week, annual Fourier, promo, holiday dummies incl. Monday federal holidays; block bootstrap intervals scaled to out-of-sample error; holiday days widened | 28-day total about 5,020; New Year's Day 137 and MLK Day 126 flagged; staff to P75 because understaffing costs 3x |
| E-event-probability | `probabilities.csv` (10 rows), `probabilities_detail.csv`, `report.md` | Beta prior at base rate 0.30 (strength 8) updated with each team's 4-release record; scope-size odds adjustment for E08; scoring plan (Brier vs base-rate reference, log score, aggregate calibration) | 0.28 (1 of 4), 0.37 (2 of 4, borderline), 0.20 (0 of 4), E08 0.59; nine of ten below the 40 pct line |
| F-short-history | `forecast.csv` (12 rows, 80 pct coverage), `report.md`, `run_f.py` | Log-linear trend plus one Fourier pair on 20 months; damped growth scenarios (-12 to +22 pct) simulated; plain statement of what 20 months cannot separate (launch ramp vs winter trough) | 2026 total about 1,300 (+10 pct), range 1,210 to 1,400 |
| G-level-shift | `forecast.csv` (12 rows, 80 pct coverage), `report.md`, `run_g.py` | Seasonality from 112 pre-break months; May 2025 step of -16 pct quantified; new level from 8 post-break months; scenario mixture for 2026 drift plus 10 pct chance of a second step; commitment table against the 10 pct write-off rule | 2026 total about 3,490 (median), range 3,235 to 3,720; recommended commitment 3,350 (about 2 pct write-off risk) |

## Things I could not do or chose not to do

- Task B has no data, so no backtest; the confidence range is judgmental and says so. Retailer margin (for factory dollars) and the category leader's share were not in the brief and are assumed, with ranges.
- Task A: the raw ETS simulation intervals were too narrow in backtest (North 58 pct at nominal 90); I calibrated a single width multiplier from pooled backtest errors rather than per series, because three origins per series is too few to do it per series honestly.
- Task D: the promo coefficient was estimated from 40 promo days; no promos are scheduled in the window so it does not affect the delivered numbers. Weather and unscheduled promos are not modelled.
- Task F: with one observation of January to April, the seasonal factors for those months cannot be separated from the launch ramp; this is stated in the report and reflected in the interval, not resolved.
- Task G: the cause of the break is unknown; the drift and second-step scenarios are judgment, and the report says which early-2026 readings would move the number.
- Nothing failed; every task was completed within its time budget.
