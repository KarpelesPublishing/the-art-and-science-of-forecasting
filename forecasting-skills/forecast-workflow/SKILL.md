---
name: forecast-workflow
description: Use whenever someone needs a forecast, a probability or a launch estimate and is not studying a specific chapter. Seven gates, each producing an artifact the next command requires, so a person with no forecasting experience and an expert follow the same auditable path from question to scored result.
---

# Forecast Workflow: the seven gates

This is the front door of the library. It does not teach a method; it makes sure the right one is
chosen and used honestly. Every gate produces a file, and the next command refuses to run without
it, so no gate can be skipped, whatever the reader's experience. The chapter skills
(`forecasting-chNN-*`) explain the methods; [all-chapters-forecasting](../all-chapters-forecasting/SKILL.md)
maps them; [conventions.md](../all-chapters-forecasting/references/conventions.md) holds the shared
rules. Commands run from the project root with `companion/.venv/bin/python companion/scripts/run.py`.

The reader may not know any of these words. Explain each gate in one sentence before asking its
questions. Never run a gate on the reader's behalf without telling them what it will do; never skip
one because the reader is in a hurry. A forecast produced without the brief or the profile is not
finished, and the report will say so.

## Gate 1: the brief (what number, for what decision)

```bash
run.py brief --output work/brief.json --target "..." --units ... --decision "..." --horizon N --frequency monthly --as-of YYYY-MM-DD --outcome-date YYYY-MM-DD
```

The command prints the questions still unanswered. Ask them in that order, one at a time, in the
reader's words, and rerun the command with the answers. It exits 0 only when the brief can support a
forecast (target, units, decision, horizon, frequency, scoring date). The two questions readers most
often cannot answer are the costs of being too high and too low; if they cannot, record "unknown" and
the report will state that the median is reported for want of a cost asymmetry.

Questions a good forecaster asks here: Is the target a quantity someone will actually measure? Would a
different horizon change the decision? Is there a date on which we will know we were wrong?

## Gate 2: the profile (what the data are)

```bash
run.py profile --input data.csv --config work/config.json --output work
```

Reads `timestamp,target` (plus any driver columns; long-form `node` or `series_id` files are profiled per series) and writes `work/profile.json`: frequency, length,
gaps and what to do about them, zero share and demand class, the seasonal periods found in the data,
trend, outliers, a possible level shift, the data floor for the brief's horizon, and a recommended
route with reasons. Show the reader the `describe()` lines and the warnings. Do not declare a season;
let the profile find it, and say so if the reader's belief differs.

Questions: Does the frequency match what the reader meant by "a period"? Are the gaps real zeros or
missing records? Does the reader know what caused the flagged outliers or the level shift?

Routes and where they go (the table in `all-chapters-forecasting` has the full detail):

| Route | Command | Then |
|---|---|---|
| `engine` | `run.py apply --chapter 12` (4 for smoothing only, 6 for ARIMA only) | gate 3 |
| `intermittent` | `run.py apply --chapter 12` with `"pool": "intermittent"`, then chapter 21 for the stocking policy | gate 3 |
| `multiseasonal` | `run.py apply --chapter 12` with `"pool": "multiseasonal"` | gate 3 |
| `regressors` | chapter 13 (four or more series) or 16 (one series with events or drivers) | gate 3 |
| `short` | `run.py apply --chapter 12` returns a provisional baseline; say what it lacks | gate 5 |
| `too_short` or `unusable` | no series model; use [judgment.md](references/judgment.md) or reference classes (chapter 25); fix the data source | stop and say why |
| `hierarchy` (long form `node,timestamp,target`) | `run.py apply --chapter 18` with `edges`; the profile lists every node | gate 3 |
| `panel` (long form `series_id,timestamp,target`) | `run.py forecast --engine full` or `--engine global`; chapter 13 when drivers are known | gate 3 |

No history at all (a launch): [launch.md](references/launch.md). A yes/no event: [judgment.md](references/judgment.md).

## Gate 3: the baseline (what the forecast must beat)

Every series tool computes seasonal naive (and naive) at the same origins as the candidates; every
probability workflow starts from the base rate. Before looking at any model, state the baseline number
to the reader: "If we just repeated last year's pattern, the next six months would be X". The gate is
passed when the reader has seen that number and the report can quote it.

## Gate 4: the method (chosen by the profile, not by preference)

Copy the chapter's example configuration from `companion/configs/`, set `source` and `units`, leave
`season` out (the profile supplies it) or set it to `"auto"`, and run with the brief attached:

```bash
run.py apply --chapter N --input data.csv --config work/config.json --output work/run --brief work/brief.json
```

The brief's horizon, frequency, cutoff, units and scoring date override the config, so the run cannot
contradict the brief. The tool selects among its candidates at rolling origins and scores the selection
once on an untouched holdout. Record why this chapter, in one sentence, from the profile's
`route_reasons`.

## Gate 5: validation (did it beat the baseline, and what was not done)

Read `work/run/summary.json`: `status`, `interpretation`, the leaderboard against the baseline, the
holdout score, and `not_done`. The gate is passed when the reader has heard three things in plain words:
whether the selected method beat the baseline at the selection origins and on the holdout; what the
tool did not do that the chapter discusses; and what `status` means for them (`passed`: validated as
the chapter describes; `provisional`: something was skipped, the list says what; `needs_evidence`: no
number, and what would unlock one). A method that lost to seasonal naive at most origins is not a
forecast; say so and use the baseline.

Two cases the tools flag and the assistant must act on:

- **Short history** (`status: provisional`): the table's `forecast` is the best placeholder a careful
  forecaster would write down (last season's pattern re-levelled by recent growth, or the last value),
  with `scenario_low/high` from in-sample errors. Deliver it as a labelled scenario with the
  `not_done` list, never as a validated forecast, and say what history would unlock one.
- **Recent level shift** (`break_scenario` in the summary and a `break_scenario` column in the table):
  the validated selection was chosen at origins that mostly predate the shift. Run chapter 24 on the
  same file; if the shift is believed to persist (a closed store, a lost customer, a price change,
  or simply no reason to expect a reversal), `forecast.csv` takes its `forecast` from the
  `break_scenario` column and its range from `break_scenario_low/high` (journal it with
  `run.py journal add --column break_scenario`), and the report says why; if
  the shift may reverse, deliver both with the reason. Do not deliver the pre-shift model's number
  without comment: its selection origins predate the shift, so its validation does not cover it.

## Gate 6: uncertainty (a range with measured coverage, or an honest scenario)

The tool returns the selected model's own band with its coverage measured at the origins, split-conformal
bands pooled from every origin residual (`conformal_lower/upper`), and empirical residual quantiles.
Quote the measured coverage, never the nominal level alone; prefer the conformal band when the model
band's measured coverage falls short of nominal. After a level shift no band from before the shift is
trustworthy; say so. If the brief
has a cost asymmetry, say which end of the range the decision should lean to and why. If no coverage
could be measured (short history, judgment inputs), label the range a scenario, not an interval. For a
distribution-free guarantee, run chapter 17 on the same series.

## Gate 7: the report and the journal (render, do not write; then keep score)

```bash
run.py report --run work/run
run.py journal add --run work/run
```

`report.md` is rendered from the run's own files and every number in it is listed in `claims.json`
with its source. Add interpretation around it; do not add numbers to it. Write the interpretation to a
file and check it:

```bash
run.py report --run work/run --check work/interpretation.md
```

The command lists any number in the interpretation that no claim supports (dates, years and small
counts are ignored). When the interpretation draws on two runs (a series run and a chapter 21 policy
run, say), add `--also other/run` so both sets of claims count. Fix the text or point to the claim;
never publish an unsupported number.

The journal entry records the forecast rows, the brief and the scoring date. When actuals arrive:

```bash
run.py journal score --actuals actuals.csv        # timestamp,actual
run.py journal calibration
```

`calibration` reads the reader's whole track record back: whether their bands held, which way their
errors lean, how error grows with the horizon. Verdicts start at five scored forecasts. Tell the reader
now when the scoring date is and that this is the step that makes the next forecast better.

## What the gates refuse to do

- Produce a number without a brief, or a report without a run.
- Declare a season, a frequency or a data class the profile did not find.
- Present a placeholder (`provisional`) as a forecast, or a scenario as an interval.
- Let a number into the report that is not in `claims.json`.
- Finish without a scoring date and a journal entry.

## Walkthroughs

- [first-forecast.md](references/first-forecast.md): one complete pass on the shipped `sales.csv`, thirty minutes, no prior knowledge.
- [judgment.md](references/judgment.md): a yes/no event or a quantity with no series, through chapters 10, 9 and 26.
- [launch.md](references/launch.md): a product with no sales history, through `reconcile-tdbu` and chapter 27.
