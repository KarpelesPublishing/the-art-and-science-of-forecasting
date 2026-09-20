# novice-skill-2: summary

Workflow followed: `forecasting-skills/forecast-workflow/SKILL.md` (seven gates) with its references
(`launch.md`, `judgment.md`) and `all-chapters-forecasting/references/conventions.md`. Every task has
`brief.json` (gate 1), a profile or its substitute (gate 2), a `run.py apply` run folder with
`summary.json`, `results.csv`, `run.json`, `report.md` and `claims.json` (gates 4 to 7), an
`interpretation.md` checked with `run.py report --check` (with `--also` for every supporting run), a
top-level `report.md` (the rendered report followed by the checked interpretation), and a journal entry.
Nothing under `companion/harness/truth` was opened, listed or used. No file outside the run folders was
modified. Every run was a fresh run; no earlier harness run was reused.

## Delivered per task

### A-hierarchy (`A-hierarchy/`)
- `forecast.csv`: 48 rows, `node,timestamp,forecast,lower,upper`; MinT reconciled point forecasts from
  chapter 18 with `lower`/`upper` = MinT q10/q90 (nominal 80 percent, coverage not measured; regional
  points add to the total exactly, the quantile columns do not).
- `brief.json`, `profile.json` (route `hierarchy`), `config.json`, `run/` (chapter 18, status
  `provisional`: 72 observations per node is under the chapter 18 holdout floor), `run-total-ch12/`
  (supporting chapter 12 run on the Total for the seasonal-naive baseline: passed, Airline ARIMA
  validation MAE 10.2 vs 16.4 seasonal naive, holdout 5.45 vs 8.83), `report.md`, `claims.json`,
  `interpretation.md` (check passed with `--also run-total-ch12`), `journal.jsonl` (48 rows).

### B-launch (`B-launch/`)
- `report.md`: headline 3.858 million units, 15.39 million USD, 0.93 percent volume share (penetration
  locked); scenarios 3.662 million (frequency locked) and 4.724 million (unreconciled average); method;
  every input with source and kind (`inputs.md`); ranked sensitivity table (`sensitivity-table.md`);
  scoring date 2027-09-30. Gap before reconciliation 45 percent; the survey frequency was the input
  the two engines argued about.
- `brief.json`, `inputs.md` (inventory in place of a profile), `inputs.json`, the desk-model outputs
  (`model-*.txt/json`), `sensitivity.py`, `run-desk-model/` (hand-assembled run folder from the desk
  model's `--json` output so `run.py report` and `journal add` could run; status `provisional`),
  `claims.json`, `interpretation.md` (check passed), `journal.jsonl` (one period: the year-one total).

### C-intermittent (`C-intermittent/`)
- `forecast.csv`: 13 weekly rows, `timestamp,forecast`; the whole-history mean rate 2.528 units a week
  (chapter 12 `intermittent` pool selected the Mean baseline; no Croston-family method beat it).
- `report.md` states `order-up-to: 21` (chapter 21 order-up-to level at the last review, 95 percent
  quantile of bootstrapped three-week demand; cost-optimal alternative 14).
- `brief.json`, `profile.json` (route `intermittent`, 60 percent zeros), `config.json`, `run/`
  (chapter 12, passed), `config-ch21.json`, `run-ch21/` (chapter 21, passed; achieved cycle service
  100 percent, fill rate 100 percent, mean on-hand 12.72), `claims.json`, `interpretation.md` (check
  passed with `--also run-ch21`), `journal.jsonl` (13 rows).

### D-daily-multiseasonal (`D-daily-multiseasonal/`)
- `forecast.csv`: 28 rows, `timestamp,forecast,lower,upper`; Fourier ARIMA from the chapter 12
  `multiseasonal` pool with the model's 80 percent band (measured coverage 0.893 at the origins and on
  the holdout). Validation MAE 7.57 vs 11.7 seasonal naive; holdout 7.93 vs 14.8.
- `report.md` with uncertain days (New Year's Day has no holiday effect in the model and ran about a
  quarter low in both prior years; weekends; the last week) and the 3:1 cost lean to the upper band.
- `brief.json`, `profile.json` (route `multiseasonal`, periods 7 and 365), `config.json`, `run/`
  (passed), `config-regressors.json`, `run-regressors/` (comparison with the promo flag: promo-aware
  candidates lost to plain models; no promotion is scheduled in the window), `claims.json`,
  `interpretation.md` (check passed with `--also run-regressors`), `journal.jsonl` (28 rows).

### E-event-probability (`E-event-probability/`)
- `probabilities.csv`: ten probabilities (0.283 for 1-of-4 on time, 0.367 for 2-of-4, 0.20 for 0-of-4,
  0.537 for E08 with much smaller scope), from the 0.30 base rate (214 cases) as a Beta prior of
  strength 8 updated with each team's last four releases, plus a judgment likelihood ratio of 2 for E08.
- `report.md`: base rate, method per event, action at the 40 percent rule (intervene on all but E08),
  sensitivity to the prior strength (2-of-4 teams sit exactly at 0.40 with a weaker prior), and the
  scoring plan (chapter 10 rerun with outcomes, Brier vs the 0.30 baseline, chapter 9 bins).
- `brief.json`, `base-rate.md` (in place of a profile), `journal-ch10.json` (chapter 10 event journal
  with reason, counterargument, update trigger per event), `config-ch10.json`, `run/` (chapter 10,
  status `needs_evidence`: nothing resolved yet, as expected), `claims.json`, `interpretation.md`.

### F-short-history (`F-short-history/`)
- `forecast.csv`: 12 rows, `timestamp,forecast,lower,upper`; the chapter 12 provisional placeholder
  (last twelve months re-levelled by recent growth) with `scenario_low/high` as the range. Labelled a
  scenario throughout; yearly sum 1,393 units; the plain seasonal naive is given as the floor.
- `report.md` says plainly what 20 months cannot support (route `too_short`; the engine floor is 72;
  a season cannot be seen; year one is a launch ramp) and what would unlock a forecast.
- `brief.json`, `profile.json`, `config.json`, `run/` (status `provisional`), `claims.json`,
  `interpretation.md` (check passed), `journal.jsonl` (12 rows).

### G-level-shift (`G-level-shift/`)
- `forecast.csv`: 12 rows, `timestamp,forecast,lower,upper`; the chapter 12 selection
  (Combination(top3), refit on all data so it sits at the post-shift level), annual total 3,513 units,
  with the split-conformal 80 percent band (flagged as pre-shift and not trustworthy).
- `report.md`: the shift (profile warning 8 periods before the end; chapter 24 dates the last
  changepoint at 2025-05-01, strongest split 2025-08-01, adaptive policy best), persistence delivered
  as the forecast with the reversal scenario stated, and the commitment advice under the 10 percent
  write-off rule (do not commit above 3,513; last year's total would overcommit by well over 10 percent).
- `brief.json`, `profile.json`, `config.json`, `run/` (chapter 12, passed at the origins; holdout 39.9
  vs 39.3 seasonal naive because the shift fell inside the holdout), `config-ch24.json`, `run-ch24/`
  (chapter 24, passed), `claims.json`, `interpretation.md` (check passed with `--also run-ch24`),
  `journal.jsonl` (12 rows).

## What I could not do

- B-launch: no `run.py apply` chapter fits a launch with no comparable products (chapter 27 launch mode
  needs calibration products), so the run folder `run-desk-model/` was assembled by hand from the
  desk model's JSON output (documented inside its `summary.json` and `run.json`). The desk model gives
  a year-one total only, so the journal entry has one period rather than a monthly phasing. The
  reconcile-tdbu default reconciliation (both inputs free) oscillated and did not converge in 25
  passes; the locked reconciliations were used instead.
- E-event-probability: `run.py journal add` refuses an event journal (series forecasts only), so the
  chapter 10 journal file `journal-ch10.json` is the journal record and there is no `journal.jsonl`.
  `run.py report --check` lists every probability as unsupported because the chapter 10 run scores
  nothing before resolution and its `claims.json` holds only the horizon; the interpretation states
  the source of each number (`probabilities.csv`, `journal-ch10.json`, `base_rate.json`) instead.
  Chapter 26 (decision rule under costs) was not run: its adapter needs resolved outcomes.
- A-hierarchy: chapter 18 could not run its holdout leaderboard on 72 observations per node, so the
  reconciled forecast is `provisional` and the MinT q10/q90 band has no measured coverage.
- D-daily-multiseasonal: MSTL and Prophet were skipped by the tool (they need two full annual cycles
  and the file holds exactly two years) and TBATS is not installed; only Fourier ARIMA ran from the
  multiseasonal family. No holiday calendar was applied.
- F-short-history: nothing could be validated; a labelled scenario was delivered as the workflow
  prescribes.

## Command failures met

1. `run.py apply --chapter 26` (task E) with config keys `cost_false_alarm`/`cost_miss`: "Unsupported
   config keys for this adapter" (the keys are `false_alarm_cost`/`miss_cost`); not retried because the
   adapter also requires resolved outcomes. The attempt's files were removed.
2. `run.py journal add --run E-event-probability/run`: "this run has no dated forecast column ...
   only series forecasts are journaled". Expected for an event journal; recorded above.
3. `run.py apply --chapter 24` (task G) with `"season": "auto"`: "season must be an integer >= 1".
   Rerun with `"season": 12`, the period the profile found (`config-ch24.json`).
4. `reconcile_model.py --reconcile` (task B) with both inputs free: did not converge in 25 passes
   (oscillated between two states); `--lock-penetration` and `--lock-frequency` converged in 2 passes.
5. `run.py report --check` first passes flagged unsupported numbers in A (profile warning values and
   the row count), C (bullwhip ratios from the chapter 21 summary text), D (the 365-day period, the
   residual count, a rounded band edge), F (growth ratio quoted from the summary text, band sums, data
   floors) and B (the label "80 percent share" in the inputs inventory); each was reworded or pointed
   to the claim and the checks then passed. E's check remains failing for the reason given above.
