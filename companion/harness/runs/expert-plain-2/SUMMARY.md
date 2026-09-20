# expert-plain-2: run summary

Prepared 2026-09-20. All work done with own code (numpy, pandas, scipy, statsmodels) in the companion venv. Nothing under
forecasting-skills/, companion/src/, companion/scripts/, companion/notebooks/, companion/lessons/ or
companion/harness/truth was opened or used. No files outside this run folder were modified.

## Delivered per task

| Task | Files | Method in one line | Headline |
|---|---|---|---|
| A-hierarchy | forecast.csv (48 rows, 80% band), report.md | Damped-trend Holt-Winters per node, WLS (MinT-style) reconciliation so regions sum to Total; intervals from rolling-origin backtest RMSE by horizon | 2025 Total 3,914 (3,764 to 4,064); North 1,946, South 1,128, West 840 |
| B-launch | report.md | ATAR (awareness x distribution x trial x repeat) and concept-share routes, Monte Carlo over assumed inputs, tornado table, three labelled scenarios, scoring date | Year one 5.5 M units, $22 M retail; P10 3.5 M, P90 8.0 M; trial rate and awareness dominate |
| C-intermittent | forecast.csv (13 rows), report.md | Croston-SBA vs recent-year mean (demand is rising, recent mean wins in backtest); lead-time demand simulated over 3-week protection period | 3.3 units/week flat; order-up-to: 21 |
| D-daily-multiseasonal | forecast.csv (28 rows, 80% band), report.md | Log-linear regression: trend, 3 annual Fourier harmonics, weekday, promo, holiday dummies; intervals from backtest relative-error quantiles; 75th-percentile staffing rule for the 3:1 cost asymmetry | 28-day total about 5,010; Jan 1 flagged as the uncertain day |
| E-event-probability | probabilities.csv (10 rows), report.md | Beta prior at company base rate 0.30 (weight 8), updated with each team's last four releases; judgemental odds x2 for the one team with much smaller scope | Six clear interventions (0.20 to 0.27), three marginal at 0.37, E08 at 0.55 |
| F-short-history | forecast.csv (12 rows), report.md | Two routes (2025 shape x 1.10; flat recent level with 0.5%/month) blended 50/50; judgemental widening range; states plainly that seasonality is not identifiable from 20 months | FY2026 about 1,320 units (1,030 to 1,660); plan on the annual, not the monthly shape |
| G-level-shift | forecast.csv (12 rows, 80% band), report.md | Break in May 2025 (-15 to -20% vs trend); pre-break seasonal indices applied to post-break level, no trend; simulation with drift, noise and a 15% chance of a further step; commitment table | 2026 median 3,510 (3,300 to 3,720); recommended commit 3,400 (write-off risk under 1%) |

## Things to know

- Task A: model-based prediction intervals were too narrow (fitted smoothing parameters near zero), so the band uses
  empirical backtest errors instead. Regions sum to Total exactly after rounding (Total column recomputed as the sum).
- Task B: the brief's survey purchase frequency implies a category four times the stated 415 M units; the report uses
  415 M and says why. Leader share is not in the brief and is the largest assumption in the share route.
- Task C: forecast.csv gives the same 3.3 in every week by design; the report explains why spiking particular weeks
  would be false precision, and notes that 95 percent cycle service is a soft target for intermittent demand.
- Task D: forecast.csv holds the median; the staffing plan at the 75th percentile is in report.md (the task's file
  spec did not include an extra column, so it was not added).
- Task F: fiscal year assumed to equal the calendar year (Jan to Dec 2026); stated in the report.
- Task G: no rolling backtest is reported because it would only test the pre-break model; the post-break fit check is
  reported instead.

## Not done or could not do

- Nothing failed. All seven tasks delivered the files named. No task exceeded the ten-minute guideline by a meaningful
  margin.
