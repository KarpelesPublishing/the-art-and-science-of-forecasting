# Chapter 11 workshop: from lesson to decision

## Explain the mechanism

Crowd wisdom depends on the error structure. Diversity of labels or biographies does not guarantee diversity of information. Robust aggregators protect against particular contamination patterns; their usefulness must match the actual errors.

## Work through the arithmetic

For [90,100,110,1000], the mean is 325 and the median is 105. A 25% trim from each tail leaves [100,110], mean 105. With individual SD=10, rho=.2 and n=10, aggregate SD is sqrt(100(.2+.8/10))=sqrt(28)=5.292; it does not fall to 10/sqrt(10)=3.162.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace guesses or the repeated panel with question-level observed estimates. Keep resolved questions separate from open ones. If comparing trim levels, choose them on earlier resolved questions and preserve the later event set for assessment.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: Do estimates share a target, horizon and units? Who saw whose answer? Which sources are common? Are there past resolved questions for testing weights?

## Interpret the actual lesson outputs

The ox distribution is synthetic. The correlation experiment holds individual marginal variance fixed, unlike adding an extra shared noise term without rescaling. The contamination figure injects upward extremes; performance under that mechanism does not establish robustness to shared moderate bias.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `question,actual,mean,median,trimmed`.
- `summary.json`: inspect `mae`.

The adapter requires resolved question actuals and compares fixed mean, median and 20%-each-tail trimmed mean. When the estimates are event probabilities with binary actuals, `extremize_a` (a positive number, 2.5 is the usual starting value) adds a logit-extremized pool and scores every rule by Brier as well as MAE; extremization helps only when experts share information and the plain pool is too timid, and the tool refuses it on non-probability data. It does not learn weights or turn disagreement into calibrated outcome intervals.

The [fixture](../../../companion/data/examples/ch11.csv) and [config](../../../companion/configs/ch11.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Mean aggregation cancels idiosyncratic error but not common bias. Median robustness to extremes does not correct shared moderate error. With equal individual variance sigma² and correlation rho, mean variance is sigma²[rho+(1-rho)/n].

With few estimates, report each judgment and simple aggregates rather than unstable learned weights. Without resolved outcomes, compare robustness and assumptions only. If everyone shares one source, state that the aggregate contains little independent information.

The applied deliverable must make these items inspectable: Return respondent count, mean/median/trimmed estimates, source-dependence notes, outlier sensitivity and held-out aggregation losses if available.

## Three exercises with worked solutions

### Exercise 1

All five estimates are 120 while truth is 100. What do mean and median do?

**Worked solution.** Both remain 120; aggregation cannot remove a shared 20-unit bias.

### Exercise 2

rho=1 and individual SD=20. What is aggregate SD at n=100?

**Worked solution.** 20: perfectly common error does not average away.

### Exercise 3

May the spread of five opinions be called an 80% prediction interval?

**Worked solution.** Not without a justified link between opinion dispersion and outcome uncertainty; call it disagreement or a scenario range.

## Business-reader application

Use this request with the skill:

> Apply chapter 11 to estimates.csv, compare transparent aggregators and explain whether apparent agreement comes from independent information or shared evidence.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
