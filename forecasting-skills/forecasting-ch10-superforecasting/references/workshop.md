# Chapter 10 workshop: from lesson to decision

## Explain the mechanism

Superforecasting is a disciplined sequence of questions, evidence and revisions. Odds provide a coherent update only when the likelihood information is meaningful. A forecast journal makes future scoring possible; it cannot recover a genuinely pre-outcome forecast after the fact.

## Work through the arithmetic

Start at p=.2: odds=.2/.8=.25. A likelihood ratio of 2 gives odds .5 and probability 1/3. A subsequent conditionally independent LR=.5 returns odds .25 and probability .2. Multiplying .2 directly by 2 would incorrectly produce .4. A prediction .7 for an event that occurs has Brier (.7-1)^2=.09.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace the synthetic events/revisions construction in the journal sublesson with user records; preserve the score_journal selection rules. Keep as_of explicit and timezone-aware. Do not overwrite originals while cleaning. The odds toy accepts assumed likelihood ratios; business news does not supply those ratios automatically. Replace the piano-tuner factors only after defining numerator and denominator units.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: Exactly what counts as yes, by what deadline and timezone? Which resolution source and ambiguity rule apply? What comparable-event base rate exists? Which evidence items share a source? At what lead time will forecasts be scored?

## Interpret the actual lesson outputs

The lesson’s 100 scored events, 20 unresolved exclusions and one late-update exclusion are controlled checks of eligibility, not an audited human forecasting record. The extremization curve evaluates an earlier-selected multiplier on separate events; inspecting its later minimum and selecting again would contaminate evaluation. The tuner estimate is 110 under its assumptions, and its ranges are one-at-a-time sensitivity, not probabilities.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `event_id,timestamp,probability,outcome,brier,baseline_brier (plus retained scoring fields)`.
- `summary.json`: inspect `brier,baseline_brier,excluded_event_ids,unselected_revision_count` when events are scoreable. Unselected revisions include superseded valid forecasts as well as ineligible entries.

Input is JSON with events and revisions arrays. score_journal chooses the latest eligible revision for each resolved event; if none are scoreable it returns status=needs_evidence with event_id/scoring_status rows. The JSON file can retain unresolved events, but editable timestamps are not authenticated.

The [fixture](../../../companion/data/examples/ch10.json) and [config](../../../companion/configs/ch10.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Check duplicated evidence, hindsight entries and multiple revisions counted as events. Evaluate later-event Brier, calibration with counts and discrimination separately. AI personas do not supply independent information. A neat calibration curve with tiny bins is not calibration evidence.

With no defensible base rate, give a range of plausible reference classes and a labeled judgment probability if a decision requires one. Without a resolution rule, keep a draft question rather than a scoreable forecast. Null outcomes remain unresolved, never zero.

The applied deliverable must make these items inspectable: Return the event contract, base-rate source, initial and current probability, complete revision journal, update triggers, resolved-event score table and exclusions. Mark editable local JSON as unauthenticated; it is not tamper-proof storage.

## Three exercises with worked solutions

### Exercise 1

Prior .4, supported LR=3: calculate the posterior.

**Worked solution.** Prior odds are 2/3; posterior odds are 2, so posterior probability is 2/3, approximately .667.

### Exercise 2

An event has revisions .3 before cutoff and .99 after resolution; outcome=1. What scores?

**Worked solution.** Only .3 is eligible. Its Brier contribution is (.3-1)^2=.49. The .99 hindsight revision is preserved but excluded.

### Exercise 3

Three launch scenarios exceed the target in two cases. Is the event probability 2/3?

**Worked solution.** No. The scenarios have no probability weights or model-error distribution. Report conditional outcomes and specify what evidence is needed to estimate event odds.

## Business-reader application

Use this request with the skill:

> Use chapter 10 to define and journal whether our launch exceeds 50,000 units within 24 months. Separate business assumptions from measured evidence, give a justified initial probability or state why one is unsupported, and predeclare resolution and scoring rules.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
