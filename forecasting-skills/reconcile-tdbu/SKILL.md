---
name: reconcile-tdbu
description: Interviews the user, then builds and runs a top-down/bottom-up new-product volume forecast that reconciles a trial-and-repeat model against a market-share model. Use this whenever someone wants to forecast first-year volume, units, or share for a new product or concept; mentions trial and repeat, repeat rate, share of choice, category penetration, MPCT (a monadic product concept test, the survey a concept is shown to one respondent group at a time), depth of repeat, or a volumetric concept test; asks to reconcile two forecasts or two modelling approaches that disagree; asks why a bottom-up estimate does not match a top-down one; or brings up the top-down bottom-up triangulation model from *The Art and Science of Forecasting* (chapters 20 and 27). Also use it for teaching or writing about reconciliation between estimation procedures, balancing variables, or survey overstatement correction. Trigger it even when the user has only partial data, the skill is built to interview for the missing inputs rather than require them upfront.
---

# Top-down / bottom-up volume reconciliation

## What this does

Two accepted ways to forecast a new product's first-year volume usually disagree:

- **Bottom-up (trial and repeat).** Start from how many people will try it and how
  often they will come back. Category penetration is given; market size falls out.
- **Top-down (market share).** Start from the size of the category and take a share
  of it. Market size is given; penetration falls out.

Each answer is defensible in isolation. When they disagree, at least one input is
wrong, and the disagreement tells you which one. This skill runs both engines,
measures the gap, reports what each engine implies about the inputs, and drives
the two into agreement.

`scripts/reconcile_model.py` is the author's top-down bottom-up triangulation model, the one described in
*The Art and Science of Forecasting*, chapters 20 and 27. It began life as a
spreadsheet and now lives here. Its `--selftest` reproduces the reference case
the book quotes (3.55 and 3.53 million units, a 0.6 percent gap, two passes to
reconcile).

Every coefficient and curve constant in it is an illustrative starting value,
from no particular source: generic numbers, set by judgment, that put an
ordinary packaged-goods launch in the right ballpark. Tell the user this the
first time a modelled number appears. If they have launch history, fit the
trial and awareness relationships to it; if not, help them tune the constants
against launches they know and record what changed. The structure is the
durable part; the numbers are theirs to own.

## Your role

Act as an analyst walking someone through a study, not a form to be filled in.
Most people arrive with three or four of the numbers and vague feelings about the
rest. That is normal and the model is built for it.

Work in this order:

1. Interview for what you can get.
2. Fill the gaps with defaults, and say out loud which ones you filled.
3. Run the model.
4. Read the gap, explain what it means, and reconcile.
5. Report the forecast with its caveats.

Do not ask for all ten inputs in one block. Ask the first four, run something, and
let the output drive the rest of the conversation. A forecast on defaults that
the user can react to beats a perfect interview they abandon halfway through.

## Step 1: the four questions that matter

Start here. Everything else has a workable default.

1. **How many households or people are in the market?** In millions. If they know
   the country but not the figure, estimate it and say you estimated it.
2. **What share of them buy this category in a year?** Category penetration. If
   they have no idea, ask whether it is closer to a staple (70%+), a regular
   category (40–60%), or a niche (under 25%), and use 0.75, 0.50, or 0.20.
3. **How big is the category?** In millions of units or volume equivalents. This
   is the top-down anchor. If they genuinely do not have it, set
   `market_size_mm` to `null` and the bottom-up engine will supply it, but then
   there is nothing to reconcile against, so press gently before giving up.
4. **What distribution will you get?** Weighted distribution as a fraction, by the
   end of year one.

If the user has survey data, also ask **how many times a year people say they buy
the category** and **how many units they buy per trip**. If not, use 20 and 1.43
and tell them those are placeholders.

`references/interview-guide.md` has the full question set, the ranges each input
must fall in, and what to do when someone does not know an answer. Read it when
the conversation goes past these four questions.

## Step 2: write the inputs file

Build a JSON file. Only the fields you are changing need to appear; everything
else falls back to the model's default.

```json
{
  "repeat_units": 1.43,
  "category_purchases_year": 20.0,
  "distribution": 0.63,
  "penetration": 0.53,
  "population_mm": 118.0,
  "market_size_mm": 415.0,
  "price": 3.99,
  "build_speed": "standard",
  "awareness_inputs": {"spend_mm": 4.6, "cost_per_grp": 10000.0, "brand_name_recall": 0.55},
  "trial_inputs": {"brands_evoked_set": 5, "differentiation": 122, "relevance": 98},
  "overrides": {"share_of_choice": 0.25}
}
```

## Step 3: run it

```bash
python scripts/reconcile_model.py --inputs inputs.json
python scripts/reconcile_model.py --inputs inputs.json --reconcile
python scripts/reconcile_model.py --inputs inputs.json --reconcile --json
```

Import it instead when you need to loop, chart, or build a scenario table:

```python
from reconcile_model import Inputs, run, reconcile, sensitivity
```

Run `--selftest` once if you have reason to doubt the environment. It prints a
line per checked quantity against the reference case.

## Step 4: read the gap

The gap is the headline diagnostic, not the forecast.

| Gap | What it means | What to do |
| --- | --- | --- |
| Under 2% | The two stories agree | Report the forecast |
| 2–10% | Acceptable, some tension | Report it, note which input is doing the work |
| Over 10% | The inputs contradict each other | Reconcile before quoting any number |

When the gap is wide, the `implied_*` fields say where the contradiction sits.
Compare each against what the user gave you:

- `implied_purchases_year` far below the claimed figure means the survey
  frequency is overstated relative to the category size. This is extremely
  common: people overstate purchase frequency, which is why the model deflates claimed
  frequency by a factor of three before using it.
- `implied_penetration` far from the given penetration means the category size
  and the buyer base disagree about how many people are in the market.
- `implied_market_size` far from the given market size means the bottom-up build
  cannot reach the category the reader described.

Say which input the model is arguing with, in words, before you touch anything.

## Step 5: reconcile

`--reconcile` copies each implied value back into its input and re-runs until the
two engines agree. On the reference case this settles in two passes.

The important judgement call: **which input is allowed to move.** That choice is
the modelling decision, not a technicality.

- The user trusts their penetration figure (a syndicated panel number, say) →
  `--lock-penetration`, and let frequency absorb the adjustment.
- The user trusts their survey frequency → `--lock-frequency`.
- Neither is firm → let both move, which is the default.

Always report what the reconciliation changed and by how much. A forecast where
penetration silently moved from 53% to 39% is not the same forecast, and the user
needs to see that happen.

If penetration pins at 100%, the balancing variable is saturated and there is no
solution. The model warns about this. It usually means market size is too large
for the population given, or repeat units are too low.

## Step 6: report

Give them:

- Volume in millions of units, value in dollars, and share.
- The gap, and whether reconciliation was needed.
- Which inputs moved and which held.
- Every default you filled in on their behalf.

That last one matters more than it sounds. Someone who does not know a forecast
rests on a placeholder repeat-units figure of 1.43 will quote the number as
though it were measured.

## Things that will trip you up

**Share of choice defaults to a manual 0.25.** The model's own derived value on
the reference inputs is 0.33; the reference case overrides it. Keep the override
if you are reproducing the book's numbers, drop it (`"share_of_choice": null`) if
you want the model's own estimate, and tell the user which one is active.

**Frequency comes from two places.** `use_external_frequency` defaults to true,
which makes the engines use `external_frequency` (4.667, a panel-observed figure)
and ignore the survey frequency for the volume build. The survey figure still
drives the repeat rate and the awareness model. Set `use_external_frequency` to
false when you have no panel number and want the survey to drive everything.

**Share is a volume share.** `volume_share` divides units by the category's unit
volume; `forecast_value_mm` is dollars. Do not divide the dollar figure by unit
volume. If the user's market size is in dollars, say so and compare value to it
instead.

**Awareness and trial are modelled by default.** To supply your own, set
`calculate_awareness` or `calculate_trial` to false and provide
`awareness_manual` or `trial_manual` as fractions.

**The trial detector's heaviest weight is evoked set size.** Per point of score
its coefficient is an order of magnitude larger than any other: one more brand in
the shopper's mind costs three index points. If a user gives you a number of
brands in the evoked set, that single input will move trial more than most
others combined. Worth flagging when it produces a surprising result, and worth
reminding them the weight is a starting value they can change.

## Reference files

- `references/interview-guide.md`: the full question set, valid ranges, defaults,
  and how to handle "I don't know" for each input.
- `references/model-map.md`: every formula, its name in the code, and what it means.
  Read this when someone asks how a number was produced, when you need to explain
  the method, or when writing about the model.
