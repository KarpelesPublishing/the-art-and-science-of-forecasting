# Conventions shared by every chapter skill

Every chapter skill follows these rules. They are stated once here so that each `SKILL.md` can be about its own method.

## The workflow's artifacts

The front door, [forecast-workflow](../../forecast-workflow/SKILL.md), passes seven gates and each leaves a file: `brief.json` (`run.py brief`), `profile.json` (`run.py profile`), the run folder with `summary.json`, `results.csv`, `diagnostic.png` and `run.json` (`run.py apply --brief`), `report.md` with `claims.json` (`run.py report`), and the journal entry (`run.py journal add`, scored later with `journal score`, read back with `journal calibration`). A run made with a brief carries it in `summary.json` and `run.json`; the brief's horizon, frequency, cutoff, units and scoring date override the config so a run cannot contradict the brief. A report is rendered from the run, never written; the assistant's interpretation is checked against `claims.json` with `run.py report --check`.

## Before running a tool

- A tool runs only when the reader asks for it. Decide with the reader whether the method fits before running it; the skill describes the method, it does not launch it.
- Record the target, its units, the horizon, the observation frequency, the as-of cutoff, the decision costs and which inputs are known in advance. Do not infer business definitions from column names.
- Every configuration needs `source` (where the data came from) and `units`; `outcome_due` is recorded so the forecast can be scored later. Unknown configuration keys are rejected, so a misspelt option fails loudly instead of being ignored.
- The command form is the same for all chapters:

  ```bash
  companion/.venv/bin/python companion/scripts/run.py apply --chapter N \
    --input my-data.csv --config my-config.json --output applied-runs/my-run
  ```

  Use a new, empty output directory for each run, outside `companion/` or under `companion/applied-runs/`. Publication folders (figures, notebooks, results, data) are refused.
- Copy a chapter's example input and configuration from `companion/data/examples/` and `companion/configs/` as a starting point; replace the synthetic `source` label with real provenance.

## Data floors

Each tool checks its own minimum and stops with a message when the data are too short. The floors that matter most:

| Chapter | Minimum | Below it |
|---|---|---|
| 4, 6, 12, 27 (history) | 2 seasons + 4 horizons (monthly, horizon 12: 72 points; horizon 6: 48; horizon 3: 36); the same for the `intermittent`, `multiseasonal` (longest period) and `regressors` pools | `status: provisional`, last value repeated, no validation |
| 3 | 3 seasons | error |
| 5 | 30 observed values (gaps allowed); rolling check needs 2 seasons + 3 horizons | error / check skipped under `not_done` |
| 13 | 4 series with 35 rows each; dates spanning 2 seasons + 3 horizons | error |
| 14 | 4 series with 50 rows each | error |
| 15 | max(3 seasons, horizon + 30) | error |
| 16 | max(4 horizons, 60) rows | error |
| 17 | 2 seasons (at least 24) + calibration window (36) + test window (24): 84 monthly points by default | error naming the total |
| 18 | per node, the chapter 12 floor above | reconciles, skips the holdout leaderboard, `status: provisional` |
| 20 | 60 rows, nonnegative spend | error |
| 21 | 30 rows | error |
| 22 | 30 rows: 15 before and 5 after the intervention; 2 or more controls for synthetic control | error / synthetic control under `not_done` |
| 23 | 10 cohorts old enough to be complete before the as-of date | error |
| 24 | 80 rows; calibration window under half the series | error |
| 1 | 30 sessions of open, high, low, close | error |
| 19 | 6 increasing time points; ceilings above the observed maximum | error |
| 27 (launch) | 3 calibration products and 2 validation products | error |

When a floor is not met: shorten the horizon, gather more history, or report the provisional result as a placeholder with its `not_done` list. Never pad a series to reach a floor.

## Reading the result

`summary.json` always carries five keys, whatever the chapter:

- `method`: what actually ran, in one line.
- `status`: `passed` (the method ran and was validated as the chapter describes), `provisional` (something ran, but a check the chapter requires could not be done; the `not_done` list says which), or `needs_evidence` (nothing was forecast; the summary says what evidence would unlock it).
- `interpretation`: the reading of the numbers, with the comparison the chapter insists on.
- `assumptions`: what has to be true for the result to mean what it says.
- `not_done`: what the chapter discusses that this run did not do. Repeat it to the reader; it is the honest boundary of the result.

The rest of the summary is evidence specific to the chapter (leaderboards, validation tables, weights, p-values). `results.csv` is the calculation. It is not permission to act; explain which assumption would most change the answer and what new evidence would test it. `run.json` records the inputs, code and library versions by hash; its `execution_status: passed` means the code ran, not that the forecast is accurate.

A real excerpt (chapter 4 on its example series):

```json
{
  "method": "Rolling-origin model comparison with final holdout",
  "status": "passed",
  "interpretation": "ETS(auto) had the lowest mean validation MAE (1.86); the runner-up was Theta (1.97). Final-holdout MAE for the selection: 1.67. Compare against Seasonal naive before trusting the gain.",
  "assumptions": ["Regular series with the declared season and no missing periods", "The training history's pattern continues over the horizon (no regime change)", "Specifications are frozen on the first training slice, so later actuals cannot steer selection"],
  "not_done": ["No regressors, promotions or calendar effects (chapter 13 or 16 add them)", "No hierarchy or coherence constraints (chapter 18)", "Intervals are the selected model's own plus empirical residual quantiles; no distribution-free guarantee (chapter 17)"],
  "selected": "ETS(auto)",
  "leaderboard": [{"model": "ETS(auto)", "mae": 1.86, "interval_coverage": 0.8}, {"model": "Theta", "mae": 1.97, "interval_coverage": 1.0}]
}
```

And the same chapter on 40 monthly points with a 12-month horizon:

```json
{
  "status": "provisional",
  "interpretation": "Only 40 observations; the rolling comparison needs 72 (a training slice of 2 seasons + 1 horizon, then 3 more horizons for two selection origins and a holdout). The forecast repeats the last value (54.07) with a seasonal-naive scenario column. Nothing was validated ...",
  "not_done": ["No model comparison: 32 more observations are needed at horizon 12 and season 12", "No intervals", "No seasonal model"]
}
```

What to do with each status:

- `passed`: report the interpretation, the comparison against the baseline, the interval coverage measured (never the nominal level alone), and the `not_done` list.
- `provisional`: say plainly what was skipped and why. Offer the concrete remedy from the message (shorter horizon, more history, another chapter). Do not present the placeholder as a forecast.
- `needs_evidence`: no number was produced. Return the `required_evidence` or `not_done` items as the next questions for the reader.

## Evidence rules

- Never invent observations, provenance, executed methods, validation scores or interval coverage.
- Label controlled examples, real observations, judgment and scenarios distinctly. Never label synthetic output as an external dataset.
- Real data need a named source, an extraction date, a usable-as-of date and units. If an actual is revised later, preserve the vintage that was available when the forecast would have been issued.
- Work in a copy when replacing an example's data. Keep the raw input, the cleaned table and an explanation of every exclusion. Keep the shipped example unchanged as a reproducible teaching case.
- Training, transformations and tuning use only information available at each origin. A successful lesson run does not mean the applied steps were carried out on the reader's data.

## Reporting

Every applied report includes units, horizon, evidence cutoff, sources, assumptions and limitations, the `not_done` list, and, for a live forecast, the creation time and the date on which the outcome will be scored. Include the file paths written by the run.

## Combining chapters

- Point forecast then guaranteed intervals: chapter 12 (or 4, 6) selects the model; chapter 17 wraps that selection in split and adaptive conformal bands.
- Several related series that must add up: chapter 18 with the node histories and the child-parent edges; set `pool` to choose the base-forecast family.
- Promotions or prices known in advance: chapter 13 (four or more series) or chapter 16 (one series with an event table).
- Probability forecasts feeding a decision: chapter 10 keeps the journal, chapter 9 scores it, chapter 26 turns the probabilities into a cost-weighted action rule.
- A launch with no sales history: `reconcile-tdbu` interviews for the inputs and runs the top-down bottom-up triangulation model; chapter 27 launch mode applies when calibration products with observed 24-month units exist; chapter 19 turns an adoption curve into a sales curve with repeat.
- An intervention whose effect must be measured: chapter 22, after chapter 12 has shown what the series would have done on its own.

## Learning mode

`references/workshop.md` holds the mechanism, the hand arithmetic, the exercises with worked solutions and the reading of the notebook's actual outputs. `references/evaluation.md` lists acceptance scenarios with expected behaviour. To use them: give the reader or the assistant the scenario and the skill without the answer key; check the arithmetic, the evidence cutoff, unsupported claims and artifact completeness; record actual outputs separately. Expected answers are specifications, not evidence that a usability or accuracy test has passed.
