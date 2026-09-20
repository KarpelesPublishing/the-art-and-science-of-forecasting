# The Forecasting Skill Library

**New reader? Open [Start Here](../companion/START-HERE.md).** It explains what
a skill is, what a notebook is, and which one to use for your task.

There are **27 individual chapter skills, the integrated
[Complete Forecasting Skill](all-chapters-forecasting/SKILL.md)** (the map and router),
and the **[Forecast Workflow](forecast-workflow/SKILL.md)**, the front door for any
forecast: seven gates (brief, profile, baseline, method, validation, uncertainty, report
and journal), each leaving a file the next command requires, so a reader with no
forecasting training and an expert follow the same auditable path. Use individual skills
to learn or apply a method; use the workflow for a forecast.

Use the [chapter map](all-chapters-forecasting/references/chapter-map.md) to find a
specific lesson. The [technical guide](../companion/README.md) covers setup. The only
skill that is not a chapter is [reconcile-tdbu](reconcile-tdbu/SKILL.md), the desk
model from chapters 20 and 27 for a launch with no sales history.

## Practitioner workflows

- Chapters 20 and 27: calibrate across established products, test shared assumptions,
  account for research age, then adapt interest, awareness and distribution for a
  new product. Gamma trial timing has standard mode 4 months, faster 3, slower 5;
  standard year-one share is 80% of the full 24-month trial total. The
  predetermined horizon is 24 months or longer. Awareness/distribution development
  supplies the delays once. Trials and repeat-purchase units are separate.
- Chapter 20: assess prediction and attribution separately;
  compare background assumptions, priors, refits and pre-window carryover. Stable
  estimates are not necessarily accurate or causal.
- Chapter 10: define resolvable probability questions, preserve dated revisions,
  exclude unresolved/hindsight records and score against a pre-recorded baseline.
- Chapter 22: assess observational identification, failure cases and when an
  ethical, feasible, informative experiment is needed.

## Tools and limits

The launch implementation is the chapter 27 notebook,
`companion/src/forecasting_companion/practitioner.py` and the `reconcile-tdbu`
desk model. Every chapter tool under `companion/src/forecasting_companion/applied/`
is covered by the companion's tests, validates its inputs, scores itself at
rolling origins where a forecast is produced, and records under `not_done` what
the chapter discusses that the run did not do. The tools run only when asked.

No fixed intent weights, buying-rate index, disagreement threshold or ROI cap should
be presented as a universal empirical rule without suitable evidence. Shared-input
agreement is not independent validation; scenario bands are not calibrated intervals.

## Run and adapt

Follow `companion/README.md` for the pinned environment, chapter commands and local
skill discovery. Start an applied request with:

```text
Use $all-chapters-forecasting to frame my question, select supported methods, and report assumptions, validation and uncertainty.
```

Nothing in these skills authorizes publication, cloud spending or changes to business
budgets; they describe methods and tell an assistant how to run the companion's tools.
