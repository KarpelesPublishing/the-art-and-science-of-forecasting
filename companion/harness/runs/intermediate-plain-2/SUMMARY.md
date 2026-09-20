# Run summary: intermediate-plain-2

Scoring date 2026-09-20. All work done with my own code (numpy, pandas, statsmodels) in the companion venv. Nothing under forecasting-skills/, companion/src, scripts, notebooks, lessons or harness/truth was read or used. No files outside this run folder were modified.

## Delivered per task

- A-hierarchy: `forecast.csv` (48 rows, node,timestamp,forecast,lower,upper, 80 percent bands, Jan to Dec 2025) and `report.md`. Method: damped additive Holt-Winters per node chosen by 12-month holdout against five configurations and seasonal naive; Total reconciled as a 50/50 blend of the direct Total model and the bottom-up sum, regions scaled so they add exactly to Total; bands from rolling-origin backtest errors by horizon (35 origins). 2025 Total 3,914 (+3.0 percent).
- B-launch: `report.md`. Two routes (awareness-trial-repeat chain and share-of-leader from the concept test), gap explained and weighted 2:1, every assumed input listed with its source or marked ASSUMED, one-at-a-time sensitivity table ranked by swing, Monte Carlo 80 percent range, labelled scenarios, scoring date and scoring plan. Headline 5.0 million units, $20 million, range 3.5 to 7.5 million.
- C-intermittent: `forecast.csv` (13 weekly rows, timestamp,forecast, flat 3.3 units a week) and `report.md` with "order-up-to: 21". Method: five rate estimators compared on a rolling backtest (52-week mean won); order-up-to as the 95th percentile of simulated 3-week (review plus lead) demand using recent demand frequency and observed sizes.
- D-daily-multiseasonal: `forecast.csv` (28 rows, timestamp,forecast,lower,upper, 80 percent bands, integers) and `report.md`. Method: OLS on log visits with trend, day-of-week, three annual Fourier pairs, promo, pooled holiday and Christmas Eve dummies; 28-day holdout MAPE 2.8 percent versus 7.0 for seasonal naive; bands from 15-origin rolling backtest errors, doubled on the two holidays (1 Jan, 19 Jan); staffing recommended at the 75th percentile because of the 3:1 cost ratio (table in report).
- E-event-probability: `probabilities.csv` (10 rows) and `report.md`. Method: Beta-binomial shrinkage of each team's last four releases toward the 0.30 base rate with prior strength 8; E08 adjusted by a likelihood ratio of 2.5 for the much smaller scope. Six projects clearly below 40 percent, three at 0.37 (near the line), E08 at 0.59. Scoring plan: Brier score versus base-rate and literal-record benchmarks, calibration by group, decision score.
- F-short-history: `forecast.csv` (12 rows, Jan to Dec 2026) and `report.md`. Method: same-month-last-year times a growth factor decaying from 1.12 to 1.05 (year-on-year growth was 20 percent but decelerating); judgement bands from a flat/slipping case to a compounding-launch case. 2026 total about 1,280 (+8 percent). Report states plainly that seasonality and launch ramp cannot be separated with 20 months.
- G-level-shift: `forecast.csv` (12 rows, Jan to Dec 2026) and `report.md`. Method: break identified in May 2025 (16 percent step down, seasonal shape unchanged); pre-break seasonal indices times a post-break level (last three deseasonalized months) with a half-strength downward drift; judgement bands. 2026 total about 3,480; recommended commitment 3,400 to stay clear of the 10 percent write-off trigger.

## Assumptions and things worth flagging

- Task F "next fiscal year" taken as calendar 2026, since the data end in December 2025.
- Tasks F and G: intervals are judgement bands (labelled 80 percent) rather than backtest-derived, because a 20-month history and an 8-month post-break window do not support a meaningful residual distribution. Tasks A and D bands are empirical from rolling-origin backtests.
- Task A: ETS model-theoretical intervals were too narrow on the holdout (58 to 75 percent coverage at nominal 80), so empirical backtest bands replaced them. West is the least reliable node (backtest bias grows to +11 percent at 12 months because of West's 2023 step up).
- Task B: with no test market, trial rate and awareness are guesses; the two routes differ by about 45 percent and that gap is the main reason the range is wide.
- Task D: forecast.csv carries the median and 80 percent band as asked; the cost-optimal staffing number (75th percentile) is in the report table, not the CSV, to keep the CSV to the four named columns.

## Could not do

Nothing was skipped. All seven tasks were completed within the time budget.
