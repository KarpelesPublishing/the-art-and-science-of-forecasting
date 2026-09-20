# Chapter 25 workshop: from lesson to decision

## Explain the mechanism

The outside view asks what actually happened to comparable efforts before accepting the internal plan. A forecast percentile is a decision choice: median accuracy and a high-confidence commitment are different objectives.

## Work through the arithmetic

Completed duration ratios [1,1.25,1.5,2] have median 1.375 under midpoint interpolation. A twelve-month plan multiplied by 1.375 gives 16.5 months. Quantile interpolation conventions matter in small samples and should be stated. An ongoing case at eighteen months is known only to exceed eighteen, not to finish then.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace generated durations with a documented class and preserve incomplete rows. The original lesson discusses censoring but does not model it; if using the applied Kaplan–Meier route, report its independent-censoring assumption and do not equate that extension with the original empirical-only chart.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: What outcome and decision percentile matter? Which projects were comparable before their outcomes were known? Are unfinished cases censored or failed? Do plans and actuals share units?

## Interpret the actual lesson outputs

The synthetic distribution deliberately contains overruns. The optimistic selected class drops long projects, illustrating outcome-conditioned selection. The percentile curve is empirical, not an estimate from Flyvbjerg’s proprietary database or personal-life advice.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `duration_ratio,at_risk,completed,survival`.
- `summary.json`: inspect `quantiles`.

Kaplan–Meier estimates the ratio survival curve under independent right-censoring. P50/P80/P90 are the first steps crossing their cumulative probabilities, not interpolated empirical quantiles. Unsupported upper quantiles remain null. Abandonment needs a separate outcome interpretation.

The [fixture](../../../companion/data/examples/ch25.csv) and [config](../../../companion/configs/ch25.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Completion-only data can underestimate durations. Independent censoring is an assumption, not guaranteed by a completed flag. Abandoned projects are not simply completed at their stop date. Small classes and changing execution conditions make high quantiles unstable.

If no comparable class exists, broaden it transparently and show sensitivity rather than asserting precision. If a survival curve never reaches the requested quantile, report that quantile not estimable. Without censoring metadata, show limitations of completed-case estimates.

The applied deliverable must make these items inspectable: Return class definition/inclusions, completion and censoring counts, empirical or survival quantiles, uplift factors, chosen commitment and its decision rationale, plus unidentifiable tail risks.

## Three exercises with worked solutions

### Exercise 1

Median overrun ratio 1.4, new plan 10 months: outside-view median?

**Worked solution.** 14 months, conditional on class comparability.

### Exercise 2

An unfinished project has elapsed 20 months. Should actual=20 be treated as a completed duration?

**Worked solution.** No. It is right-censored at 20 if the observation mechanism supports that interpretation.

### Exercise 3

Estimated completion probability reaches only .7 by last follow-up. Can P90 be reported numerically?

**Worked solution.** Not from that observed survival curve without additional tail assumptions; mark it unestimable.

## Business-reader application

Use this request with the skill:

> Apply chapter 25 to projects.csv, retain censored cases, defend the reference class and translate supported quantiles into a commitment aligned with delay costs.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
