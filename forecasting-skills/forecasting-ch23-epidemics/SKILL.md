---
name: forecasting-ch23-epidemics
description: "Use when reporting delays distort recent counts or a compartment model is being used for conditional epidemic scenarios, or studying forecasting book chapter 23."
---

# Chapter 23: The Epidemiologist's Dilemma

## Scope and intake

Use when reporting delays distort recent counts or a compartment model is being used for conditional epidemic scenarios. Do not use for presenting the controlled SIR/SEIR lesson as a medically validated operational forecast.

Ask only for unresolved material inputs: Do counts represent event dates, report dates or prevalence? What was known as of the cutoff? Has reporting delay changed? What population and transmission assumptions are justified?

## Input contract and additional evidence

A reporting triangle in long form: one row per (event date, report date) with the count reported on that date for that event date. Set `as_of` to the cutoff; later rows are discarded. The delay law is estimated from cohorts at least `mature_age` periods old (at least ten of them) unless `delay_prob` is supplied. Give `population` to fit the SEIR model; without it the mechanistic forecast is skipped and listed under `not_done`.

Minimal **format illustration**, not sufficient training data:

```csv
event_date,report_date,count
2020-01-01,2020-01-01,16
2020-01-01,2020-01-02,34
2020-01-02,2020-01-02,25
```

## Executable interface

Exact CLI columns: `event_date,report_date,count`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. Supported method controls: `as_of, mature_age, max_delay, delay_prob, origins, population, recovery_rate, sigma, horizon, season, frequency, seed`. Unknown config keys are rejected.

The tool builds the triangle at `as_of`, estimates the reporting-delay distribution from mature cohorts (truncated at `max_delay`) or takes the supplied `delay_prob`, nowcasts each incomplete cohort as reported count over completeness with negative-binomial 90 percent bounds, and evaluates the nowcast on archived mature cohorts by recomputing what it would have said at each younger age and scoring against the final count (an in-sample check, labelled as such). With `population` it fits an SEIR model (transmission rate, and the latent rate unless `sigma` is fixed) to incidence up to each of `origins` rolling origins and reports RMSE over `horizon` against persistence, with the implied basic reproduction number per origin. It does not model changes in testing, reporting holidays or interventions.

The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Applied procedure

1. Reconstruct the reporting triangle at the actual as-of date; exclude later reports even if present in the current file. Distinguish incident cases from infectious prevalence.
2. Estimate delay completeness from older sufficiently observed cohorts or use a documented external delay law. Inspect calendar and regime changes.
3. For each event date, divide currently observed counts by estimated completeness when it is positive. Flag the youngest dates and propagate reporting/count uncertainty when supported.
4. Keep nowcast evaluation separate from future forecasts. Evaluate archived nowcasts against later finalized counts by reporting age.
5. For an SIR/SEIR extension specify states/rates, verify conservation and nonnegativity, estimate only on earlier observations and score future horizons against persistence. Label conditional parameter scenarios explicitly.

## Diagnostics, selection and uncertainty

Small completeness makes recent nowcasts unstable. A stable historical delay law can fail after reporting changes. Case reports do not directly measure infectious prevalence. SIR fixed-rate scenarios are not probabilities over policy futures.

## Missing evidence and fallback

At zero completeness, report unidentifiable current totals rather than divide by zero. Without vintage reports, retrospective nowcast scoring may be impossible. Without defensible delay probabilities, provide observed reports and sensitivity scenarios. Never invent observations, provenance, executed methods, validation scores or interval coverage. Label controlled examples, real observations, judgment and scenarios distinctly.

## Applied report contract

`results.csv` columns: `event_date,age,reported,completeness,nowcast,lower,upper`. `summary.json` keys: `delay_law,archived_evaluation,seir,as_of` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`. Report the archived-evaluation error by age beside the nowcast; the youngest cohorts carry the largest correction and the least evidence. Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.

## Learn and apply

Read [workshop.md](references/workshop.md) for worked arithmetic, data replacement guidance, output interpretation and solved exercises. Use [evaluation.md](references/evaluation.md) to assess transfer; its expected answers are not executed agent-test results.

Learning prompt: “Teach me chapter 23 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 23 to nowcast reporting_triangle.csv at the stated cutoff, audit delay stability and keep retrospective completion estimates separate from future transmission scenarios.”

The [notebook](../../companion/notebooks/23-epidemics.ipynb) is a worked lesson; its editable [source](../../companion/lessons/23-epidemics.py) defines what is actually executed. Run the controlled example from the project root after installing the companion environment:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 23
```

A successful lesson run does not mean all applied steps above were executed on user data. The workshop states the adaptation boundary. Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) when the decision genuinely needs multiple chapters.

## Apply the supplied input or your own file

The [controlled fixture](../../companion/data/examples/ch23.csv) and [editable config](../../companion/configs/ch23.json) provide a complete runnable example:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 23 \
  --input companion/data/examples/ch23.csv \
  --config companion/configs/ch23.json \
  --output companion/applied-runs/ch23-reader-example
```

Use a new empty output directory for each run. Copy and edit the input/config for real observations; replace the fixture’s synthetic source label with actual provenance. The command writes `results.csv` with `event_date,reported,completeness,nowcast`, `summary.json` containing `interpretation`, `diagnostic.png`, and a hashed `run.json` execution record. These files cover the numerical adapter; the fuller applied report above also requires evidence and business interpretation. `execution_status=passed` means execution succeeded, not that the forecast is accurate.
