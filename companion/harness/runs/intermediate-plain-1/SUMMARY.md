# Run summary: intermediate-plain-1

Scoring date 2026-09-20. All seven tasks delivered; nothing skipped. Own code only (numpy, pandas,
scipy, statsmodels); no skills, companion source, notebooks, lessons or truth files touched.

## A-hierarchy: forecast.csv (48 rows), report.md
- Holt-Winters additive damped-trend, additive seasonal per region; average of a free fit and one with
  level weight pinned at 0.2 (free fit froze North's level and ignored its 2024 flattening).
- Bottom-up reconciliation (Total = sum of regions, coherent to the decimal); bottom-up beat direct and
  blended Total on a 12-month holdout (MAE 5.1 vs 5.7 vs 5.3; seasonal naive 8.8).
- 90 percent intervals from rolling-origin errors (3 origins x 12 horizons), not model theory; model
  intervals covered only about 80 percent.
- 2025 Total forecast 3,906 vs 2024 actual 3,799.

## B-launch: report.md (no truth file; process task)
- Two routes: awareness-trial-repeat build-up (3.76M units) and share-of-leader top-down (2.76M);
  gap explained (leader share guess, repeat assumptions), base case = geometric mean 3.2M units, $12.9M.
- Flagged the brief's internal inconsistency: survey-claimed frequency implies 1.79B category units vs
  the stated 415M; anchored on 415M.
- Every assumed input tabled with a reason; 12-row one-at-a-time sensitivity ranked by swing (media
  weight, ACV build, awareness, trial rate top the list); low/base/high labelled as scenarios; scoring plan.

## C-intermittent: forecast.csv (13 rows), report.md
- Croston with SBA correction vs recent-mean; demand is drifting up and every method back-tested low,
  so the rate was set at 3.25 units per week (flat).
- order-up-to: 22 (95th percentile of 3-week demand: negative binomial 22, bootstrap 21, empirical 19 to
  21; took the highest because of the upward drift).

## D-daily-multiseasonal: forecast.csv (28 rows), report.md
- Log-linear OLS: trend, day-of-week, annual Fourier (3 pairs), promo (+19 percent), federal holidays
  (-27 percent, identified from the data). Residual sd 3.9 percent, near white.
- Holdout 28 days: MAE 5.1 visits (2.6 percent) vs 14.8 for repeat-last-week; 90 percent band covered 93 percent.
- 90 percent regression prediction intervals; staffing table at the 75th percentile (3:1 cost ratio);
  Jan 1 and Jan 19 (MLK) flagged as holiday troughs and the most uncertain days. No promos in window.

## E-event-probability: probabilities.csv (10 rows), report.md
- Beta-binomial shrinkage from the 0.30 base rate with a prior worth 8 releases: 0/4 on time -> 0.20,
  1/4 -> 0.28, 2/4 -> 0.37; E08 (much smaller scope) lifted by likelihood ratio 2.7 to 0.60.
- Nine of ten fall below the 40 percent line; E03/E05/E07 flagged as borderline (0.37).
- Scoring plan: Brier with skill vs base-rate-only, log score, bucket calibration, decision-quality count.

## F-short-history: forecast.csv (12 rows), report.md
- Twenty months cannot support a seasonal model; used last-12-months (lightly smoothed) x growth 1.12,
  with growth 0 to 25 percent bounding an approximately 80 percent range plus 7 percent month noise.
- 2026 forecast 1,319 units (range 1,095 to 1,575); stated plainly what the data can and cannot support
  and gave finance a Q1 checkpoint rule.

## G-level-shift: forecast.csv (12 rows), report.md
- Found a persistent 15 percent step down in May 2025 (deseasonalized level 353 -> 297) with a slight,
  non-significant further drift.
- Seasonal index from the nine pre-break years, level from the post-break months (295), no trend carried
  forward; 2026 total 3,540 (80 percent range 3,370 to 3,670).
- Commitment advice: commit at or a little below 3,540; only a second break would breach the 10
  percent overcommit line; explained why a full-history Holt-Winters or ARIMA would overshoot by 5 to
  10 percent.

## Could not do / caveats
- Nothing failed. Intervals in F and G are judgement-based (stated as such) because the histories
  cannot calibrate statistical intervals; A and D intervals are empirically checked.
- No file outside this run folder was modified.
