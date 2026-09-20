# Run summary: novice-plain-1

Run date 2026-09-20. All seven tasks completed with own code (numpy, pandas, statsmodels). Nothing
under `forecasting-skills/`, `companion/src/`, `companion/scripts/`, `companion/notebooks/`,
`companion/lessons/` or `companion/harness/truth` was opened or used. No files outside this run
folder were modified. Scratch scripts lived in the session scratchpad, not the project.

## Delivered per task

| Task | Files | Method in one line | Headline |
|---|---|---|---|
| A-hierarchy | `forecast.csv` (48 rows, 80% coverage), `report.md` | Holt-Winters additive damped per region, chosen by 3-fold rolling backtest against 4 candidates and seasonal naive; bottom-up reconciliation (regions add exactly to Total); bootstrap-simulated intervals summed for Total | 2025 Total 3,919 (+3.2%), North 1,948, South 1,129, West 841 |
| B-launch | `report.md` | Two routes: trial-and-repeat build-up (6.5M units) and concept-test share of category (3.6M); reconciled to a base of 5.0M; eight assumed inputs listed with basis and ranges; one-at-a-time sensitivity table; low/base/high scenarios; scoring date and metric | Base 5.0M units, $20M retail; 80% range 3M to 8M; trial rate, awareness, distribution dominate |
| C-intermittent | `forecast.csv` (13 rows), `report.md` | Croston with SBA correction (alpha 0.1), cross-checked with recent means; order-up-to from 95th percentile of 3-week (review + lead time) demand by empirical and bootstrap resampling of demand sizes | 3.2 units/week flat; order-up-to: 20 |
| D-daily-multiseasonal | `forecast.csv` (28 rows, 80% coverage), `report.md` | OLS on log visits with trend, 3 annual Fourier harmonics, day-of-week, promo, US federal holiday dummies; 18-origin rolling 28-day backtest (MAPE 3.0% vs 7.0% seasonal naive) supplies interval quantiles; holiday intervals widened; staffing at 75th percentile for the 3:1 cost ratio | 4,990 visits over 28 days; New Year's Day and MLK Day at about 130; no promos scheduled |
| E-event-probability | `probabilities.csv` (10 rows), `report.md` | Beta-binomial update from base rate 0.30 (weight 8) with each team's last four releases; judgemental lift for E08's much smaller scope; sensitivity to prior weight; Brier and log score plan versus flat base rate | 0.20 to 0.37 for nine projects (intervene), E08 at 0.55 (do not) |
| F-short-history | `forecast.csv` (12 rows, 80% coverage), `report.md` | Blend of same-month-last-year with decaying growth (60%), log-linear trend with crude month adjustment (20%) and flat-on-2025 (20%); judgemental range widening 10% to 20%; plain statement of what 20 months can and cannot support | FY2026 about 1,281 units (+8%), range 1,085 to 1,475; assumed fiscal year = calendar 2026 |
| G-level-shift | `forecast.csv` (12 rows, 80% coverage), `report.md` | Break identified at May 2025 (about -16% against pre-break Holt-Winters counterfactual, persistent for 8 months); 2026 = old seasonal shape at new level, no growth; simulated annual distribution with common shift and drift terms; commitment table showing write-off probability at each commit level | 2026 about 3,585 units (-5.6% vs 2025), 80% range 3,340 to 3,855; commit at or below forecast (3% write-off risk at 3,585, 20% at 3,800) |

## Things I could not do or had to assume

- B-launch: no launch date in the brief, so the scoring date is stated relative to first shipment
  (12 months after) with a worked example. Leader share (15%) and leader awareness/ACV were assumed
  to read the "share of leader 25" index; both are flagged as assumptions.
- F-short-history: the fiscal year is not defined; calendar 2026 assumed and stated. No
  out-of-sample record exists with 20 months, so the range is judgemental rather than backtested.
- G-level-shift: the cause of the break is unknown; the forecast assumes it persists and says the
  recovery scenario is deliberately outside the range.
- A-hierarchy: interval bounds are not forced to add across the hierarchy (only point forecasts
  are); this is stated in the report.
- No task failed and no time limit was exceeded.
