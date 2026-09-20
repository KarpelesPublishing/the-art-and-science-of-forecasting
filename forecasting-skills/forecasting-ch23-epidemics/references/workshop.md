# Chapter 23 workshop: from lesson to decision

## Explain the mechanism

A nowcast estimates already-occurring but incompletely observed events. A future forecast predicts events not yet realized. Reporting processes and transmission dynamics therefore need distinct data and validation.

## Work through the arithmetic

If 40 cases have been reported for a date and its estimated completeness is .5, the simple nowcast is 80. With completeness .2 it becomes 200, showing sensitivity to delay assumptions. For SIR infection flow beta×S×I/N with beta=.3/day, S=900,I=100,N=1000, the flow is 27 infections/day.

## Adapt the lesson to reader data

Replace the generated reporting triangle with dated reports and a preserved cutoff. Keep delay probabilities separate from transmission parameters. Do not fit SIR prevalence directly to report-date incident counts without an explicit observation model.

For this chapter, settle these questions before fitting: Do counts represent event dates, report dates or prevalence? What was known as of the cutoff? Has reporting delay changed? What population and transmission assumptions are justified?

## Interpret the actual lesson outputs

The delay experiment knows its seven-day reporting law and evaluates nowcast error by reporting age. The separate fitted-SIR experiment has correctly specified dynamics and known removal/initial-state assumptions; it is unusually favorable. SEIR exposed-to-infectious rate is not automatically symptom-incubation rate.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `event_date,age,reported,completeness,nowcast,lower,upper`.
- `summary.json`: `delay_law,archived_evaluation,seir,as_of` plus method, interpretation, assumptions, not_done and status.

The tool builds the triangle at `as_of`, estimates the reporting-delay distribution from mature cohorts (truncated at `max_delay`) or takes the supplied `delay_prob`, nowcasts each incomplete cohort as reported count over completeness with negative-binomial 90 percent bounds, and evaluates the nowcast on archived mature cohorts by recomputing what it would have said at each younger age and scoring against the final count (an in-sample check, labelled as such). With `population` it fits an SEIR model (transmission rate, and the latent rate unless `sigma` is fixed) to incidence up to each of `origins` rolling origins and reports RMSE over `horizon` against persistence, with the implied basic reproduction number per origin. It does not model changes in testing, reporting holidays or interventions. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

## Decide what the evidence supports

Small completeness makes recent nowcasts unstable. A stable historical delay law can fail after reporting changes. Case reports do not directly measure infectious prevalence. SIR fixed-rate scenarios are not probabilities over policy futures.

At zero completeness, report unidentifiable current totals rather than divide by zero. Without vintage reports, retrospective nowcast scoring may be impossible. Without defensible delay probabilities, provide observed reports and sensitivity scenarios.

The applied deliverable must make these items inspectable: `results.csv` columns: `event_date,age,reported,completeness,nowcast,lower,upper`; `summary.json` keys: `delay_law,archived_evaluation,seir,as_of` plus method, interpretation, assumptions, not_done and status. Report the archived-evaluation error by age beside the nowcast; the youngest cohorts carry the largest correction and the least evidence.

## Three exercises with worked solutions

### Exercise 1

Observed reports 30, completeness .75: nowcast?

**Worked solution.** 40 events, conditional on that completeness estimate.

### Exercise 2

A report arrives after the historical as-of date. May it enter that origin’s nowcast input?

**Worked solution.** No. It belongs only to later-vintage truth or a subsequent origin.

### Exercise 3

Completeness is zero for today. What is the simple adjusted count?

**Worked solution.** Undefined/unidentified from those reports. Report that status rather than zero or infinity as a usable forecast.

## Business-reader application

Use this request with the skill:

> Use chapter 23 to nowcast reporting_triangle.csv at the stated cutoff, audit delay stability and keep retrospective completion estimates separate from future transmission scenarios.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.

Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
