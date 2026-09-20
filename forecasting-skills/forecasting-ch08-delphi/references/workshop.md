# Chapter 8 workshop: from lesson to decision

## Explain the mechanism

Delphi structures communication so experts can revise without public pressure. Its value depends on better evidence and reasoning, not merely on getting numbers closer together. A group can become uniformly wrong.

## Work through the arithmetic

First-round estimates [80,100,140] have median 100. Final estimates [110,112,114] have median 112. If truth is 100, median absolute error rises from 0 to 12 despite lower spread; forecast value added, initial loss minus final loss, is -12.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace the generated expert views with actual round records. Do not replace their missing outcomes with the simulation truth=100. Summarize the same experts separately from the full panel if participants leave. Store reasons for revisions because a numerical movement alone cannot show whether evidence improved.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: What question and common units will every expert answer? What independent evidence does each have? How many rounds are justified? When will actual outcomes resolve?

## Interpret the actual lesson outputs

The lesson’s feedback rule pulls estimates toward a median while shared bias persists. Its original shared-error experiment adds common variance 144 to individual variance 225, so total marginal variance rises to 369; it does not isolate correlation at fixed individual variance. Check the current caption if the lesson has been revised.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `question,round,n,median,iqr,absolute_error`.
- `summary.json`: inspect `forecast_value_added`.

The adapter requires complete resolved actuals and compares round medians. Keep unresolved elicitation records in a separate journal until resolution. It does not solicit experts, authenticate independence or estimate a full opinion distribution.

The [fixture](../../../companion/data/examples/ch08.csv) and [config](../../../companion/configs/ch08.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Falling interquartile range measures agreement. It does not measure calibration or accuracy. Attrition can make later consensus appear stronger. Elicited quartiles alone do not determine a full probability distribution.

Without actuals, report agreement and unresolved status but no accuracy score. With one expert, report an expert judgment rather than a Delphi panel. Without independent evidence, explain common-source dependence and seek external information.

The applied deliverable must make these items inspectable: Return anonymized round tables, medians/spreads, rationale changes, dissenting evidence, stopping reason and resolved-question first-versus-final losses where available.

## Three exercises with worked solutions

### Exercise 1

Initial error 20, final error 12: forecast value added?

**Worked solution.** 20-12=8 units of absolute-error improvement.

### Exercise 2

Panel spread halves but outcomes are unresolved. What can be concluded?

**Worked solution.** Agreement increased; accuracy and calibration remain unknown.

### Exercise 3

Ten respondents repeat the same consultant report. Are there ten independent sources?

**Worked solution.** No. Their shared source creates dependence; disclose it and seek evidence with a different failure mechanism.

## Business-reader application

Use this request with the skill:

> Use chapter 8 to analyze expert_rounds.csv, distinguish consensus from accuracy, retain dissent and evaluate whether later rounds improved resolved forecasts.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
