# Run summary: novice-plain-2

Run date: 2026-09-20. All tasks done with my own code (numpy, pandas, scipy, statsmodels) in the project venv. Nothing under `forecasting-skills/`, `companion/src/`, `companion/scripts/`, `companion/notebooks/`, `companion/lessons/` or `companion/harness/truth` was opened or used. No file outside this run folder was modified. Each task folder also contains a `model.py` that reproduces its numbers (run from the `companion` folder).

## Delivered per task

### A-hierarchy
- `forecast.csv`: 48 rows (North, South, West, Total x 12 months, Jan to Dec 2025), columns `node,timestamp,forecast,lower,upper`, 90 percent interval.
- `report.md`: method (Holt-Winters per node, configuration chosen by rolling backtest; WLS reconciliation so regions sum exactly to Total; bootstrap simulation intervals), headline table, caveats.
- Point forecasts: Total 3,925 for 2025 (+3.3 percent on 2024). Regions add to Total in every month (Total row is the sum of the rounded regional rows).

### B-launch
- `report.md`: year-one forecast for the RTD coffee launch. Base 3.0 million units, $11.8 million retail; scenarios low 1.7M / high 4.7M (labelled as scenarios). Two routes (trial-and-repeat build-up; concept preference share) reconciled at 2.98M vs 2.95M with the shared-assumption caveat explained. All given inputs listed with source (brief.md), all assumed inputs listed with rationale, sensitivity table ranked by swing (distribution and awareness first), scoring date stated (year-one close, against syndicated retail units).

### C-intermittent
- `forecast.csv`: 13 weekly rows (2025-10-06 to 2025-12-29), `timestamp,forecast`, constant 3.16 units/week (Croston with SBA correction, alpha 0.1 chosen by backtest).
- `report.md`: "order-up-to: 19" for weekly review with two-week lead time and 95 percent cycle service (bootstrap, negative binomial and empirical estimates of three-week demand agree at 18 to 20), reasoning and caveats (demand frequency rising).

### D-daily-multiseasonal
- `forecast.csv`: 28 daily rows (2025-12-31 to 2026-01-27), `timestamp,forecast,lower,upper`, 80 percent interval.
- `report.md`: staffing table with the 75th-percentile "staff for" number (understaffing costs 3x overstaffing, so the cost-optimal quantile is 0.75), uncertain days flagged (New Year's Day, New Year's Eve, weekends), method (log-linear regression: day-of-week, annual Fourier terms, trend, promo, holiday dummies; block-bootstrap intervals), backtests (MAE 5 to 8 visits/day vs 12 to 15 for seasonal naive).

### E-event-probability
- `probabilities.csv`: 10 rows. E01/E02/E04/E06 = 0.28, E03/E05/E07 = 0.37, E08 = 0.59, E09/E10 = 0.20.
- `report.md`: base rate 0.30 (214 cases) as a Beta prior worth 8 pseudo-releases, updated on each team's last four releases, odds x2.5 for E08's much smaller scope; sensitivity to prior strength (the three 2-of-4 teams straddle the 40 percent threshold and are flagged as borderline); scoring plan (Brier vs base-rate benchmark, log score, calibration buckets, decision hits).

### F-short-history
- `forecast.csv`: 12 monthly rows (Jan to Dec 2026, assuming fiscal year = calendar year), `timestamp,forecast,lower,upper`, 80 percent interval.
- `report.md`: FY2026 point 1,356 (+15 percent on 2025's 1,181), range 1,250 to 1,460; average of a log-linear trend-plus-harmonic model and a fading year-on-year growth model; plain statement of what 20 months can support (level, growth, rough seasonal shape) and cannot (twelve monthly factors, whether growth persists, the launch-ramp vs seasonality confound in year one).

### G-level-shift
- `forecast.csv`: 12 monthly rows (Jan to Dec 2026), `timestamp,forecast,lower,upper`, 80 percent interval.
- `report.md`: identified a one-time level drop of about 16 percent in May 2025 that persisted; forecast = post-break level (296, exponentially weighted) x pre-break seasonal indices, no trend; 2026 point 3,549, range 3,415 to 3,680 (includes a 25 percent chance of a further shift); recommended purchase commitment 3,450 to 3,500 with the write-off probability quantified per commitment level; Q1 2026 review triggers.

## Could not do / limitations

- Nothing failed. All named deliverables were produced.
- Task B has no data, so every behavioural input (awareness response, trial rate, repeat rate, share of requirements, leader share) is an assumption; each is flagged in the report and tested in the sensitivity table.
- Task F: the fiscal year was not defined; I assumed calendar 2026 and said so.
- Interval widths across tasks are model-based plus judgemental widening where noted (A: none, so treat as optimistic; F and G: widened for model disagreement and possible further shifts). They are stated as 90 percent (A) or 80 percent (D, F, G) in each report and file.
