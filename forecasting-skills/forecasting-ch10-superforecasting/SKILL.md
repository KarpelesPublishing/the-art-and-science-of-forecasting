---
name: forecasting-ch10-superforecasting
description: "Use when a resolvable event needs an explicit probability, evidence-based updates and a forecast journal, or studying forecasting book chapter 10."
---

# Chapter 10: The Superforecaster

## Scope and intake

Use when a resolvable event needs an explicit probability, evidence-based updates and a forecast journal. Do not use for an undefined success criterion, a quantity-only launch scenario with no uncertainty model, or a request to prove causation from a probability.

Ask only for unresolved material inputs: Exactly what counts as yes, by what deadline and timezone? Which resolution source and ambiguity rule apply? What comparable-event base rate exists? Which evidence items share a source? At what lead time will forecasts be scored?

## Input contract and additional evidence

Two linked tables or a JSON journal: events require event_id, question, cutoff, deadline, resolution_source, resolution_rule, baseline; outcome is 0/1 or null with resolved_at. Revisions require event_id,timestamp,probability,reason,evidence_source,counterargument,update_trigger. Timestamps include timezone; probabilities lie in [0,1]. Retain every revision.

Minimal **journal-format illustration**, unresolved and therefore not yet scoreable:

```json
{
  "events": [
    {
      "event_id": "launch-1",
      "question": "Will 24-month units exceed 50000?",
      "cutoff": "2026-09-18T12:00:00+00:00",
      "deadline": "2028-09-18T12:00:00+00:00",
      "resolution_source": "Audited sales register",
      "resolution_rule": "Strictly greater than 50000 net units",
      "baseline": 0.2,
      "outcome": null,
      "resolved_at": null
    }
  ],
  "revisions": [
    {
      "event_id": "launch-1",
      "timestamp": "2026-09-18T12:00:00+00:00",
      "probability": 0.2,
      "reason": "Comparable launches",
      "evidence_source": "Internal cohort",
      "counterargument": "Channel access differs",
      "update_trigger": "Distribution agreement signed"
    }
  ]
}
```

## Executable interface

Exact CLI columns: `events,revisions (JSON)`. Supported method controls: `as_of, frequency, horizon, season, seed`.

Input is JSON with events and revisions arrays. score_journal chooses the latest eligible revision for each resolved event; if none are scoreable it returns status=needs_evidence with event_id/scoring_status rows. The JSON file can retain unresolved events, but editable timestamps are not authenticated.

## Applied procedure

1. Write the event contract and scoring cutoff before inspecting outcomes. Establish the base rate from a named reference class, recording inclusion rules and sample size.
2. Record initial reasoning, counterargument and the evidence that would change the estimate. Separate measured frequencies from judgment and assumption.
3. Convert probability to odds p/(1-p). Multiply only supported, appropriately conditional likelihood ratios; convert back with odds/(1+odds). If evidence is qualitative, record a judgment update without inventing a numerical likelihood ratio.
4. Append timestamped revisions and evidence. For quantity decompositions, document units and dependence, and do not turn low/base/high scenarios into probability weights without justification.
5. After resolution, select one latest eligible pre-cutoff, pre-resolution revision per event. Score Brier against the pre-recorded baseline; show exclusions and calibration-bin counts. Learn any aggregation or extremization rule only on earlier resolved events.

## Diagnostics, selection and uncertainty

Check duplicated evidence, hindsight entries and multiple revisions counted as events. Evaluate later-event Brier, calibration with counts and discrimination separately. AI personas do not supply independent information. A neat calibration curve with tiny bins is not calibration evidence.

## Missing evidence and fallback

With no defensible base rate, give a range of plausible reference classes and a labeled judgment probability if a decision requires one. Without a resolution rule, keep a draft question rather than a scoreable forecast. Null outcomes remain unresolved, never zero.

## Chapter-specific invariants

Define the event, deadline/timezone, resolution source and ambiguity rule. Record
the base rate, initial probability, evidence provenance, counterargument and update
triggers before outcomes arrive. Append timestamped revisions; do not overwrite
history. The notebook's JSON is editable, not authenticated append-only storage.

Update odds when likelihood ratios are supported; otherwise label a probability
revision as judgment rather than inventing a precise likelihood ratio. Decompose
into defensible factors and propagate dependencies. AI personas are not independent
experts. For launch quantities use chapter 27's calibrated analogue workflow, but
require justified input/model uncertainty before turning scenarios into event odds.

Choose a forecast lead time/cutoff before seeing outcomes. Score one latest eligible
pre-cutoff, pre-resolution revision per event; exclude unresolved events and hindsight
entries. Report exclusions and compare Brier scores against a pre-recorded baseline.
Show calibration-bin counts; small samples do not certify calibration. Train any
aggregation/extremization on earlier resolved events, evaluate later events separately.

Do not multiply prior probability by a likelihood ratio directly or extremize merely
to sound confident. Never score missing outcomes as zero or count repeated updates
as independent events. A prediction of success is not the causal effect of an action.

## Applied report contract

`results.csv` columns: `event_id,probability,outcome,timestamp,brier,baseline_brier`. `summary.json` keys: `brier,baseline_brier,excluded_event_ids,unselected_revision_count` plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`.

Return the event contract, base-rate source, initial and current probability, complete revision journal, update triggers, resolved-event score table and exclusions. Mark editable local JSON as unauthenticated; it is not tamper-proof storage.

## Run it

The [notebook](../../companion/notebooks/10-superforecasting.ipynb) is the worked lesson; its editable [source](../../companion/lessons/10-superforecasting.py) defines what is executed. [workshop.md](references/workshop.md) holds the mechanism, the hand arithmetic, exercises with worked solutions and the reading of the lesson's actual outputs; [evaluation.md](references/evaluation.md) holds acceptance scenarios. The rules every chapter shares (evidence, provenance, output folders, what `status` means and what to do about it, data floors, how to combine chapters) are in [conventions.md](../all-chapters-forecasting/references/conventions.md); read it once.

Apply the tool to the shipped example or to your own file, always into a new empty output directory:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 10 \
  --input companion/data/examples/ch10.json \
  --config companion/configs/ch10.json \
  --output companion/applied-runs/ch10-example
```

It writes `results.csv` and `summary.json` with exactly the columns and keys listed under Applied report contract, `diagnostic.png`, and a hashed `run.json` execution record. To run the lesson itself: `run.py chapters --chapter 10`.

Learning prompt: “Teach me chapter 10 using the workshop’s numerical example. Ask me to explain the failure case before showing its worked solution.”

Applied prompt: “Use chapter 10 to define and journal whether our launch exceeds 50,000 units within 24 months. Separate business assumptions from measured evidence, give a justified initial probability or state why one is unsupported, and predeclare resolution and scoring rules.”
