# Interview guide

Every input, what to ask, what it must fall between, what to do when the user does
not know, and which JSON field it lands in.

## Contents

- [Tier 1: ask first](#tier-1-ask-first)
- [Tier 2: ask if the study has them](#tier-2-ask-if-the-study-has-them)
- [Tier 3: media and awareness](#tier-3-media-and-awareness)
- [Tier 4: the trial detector](#tier-4-the-trial-detector)
- [Tier 5: overrides](#tier-5-overrides)
- [Handling "I don't know"](#handling-i-dont-know)
- [Sanity checks before running](#sanity-checks-before-running)

## Tier 1: ask first

These four carry the forecast. Get them before anything else.

| Field | Question | Range | Default |
| --- | --- | --- | --- |
| `population_mm` | How many households or people are in this market, in millions? | 0.01–2000 | 118 |
| `penetration` | What fraction of them buy the category in a year? | 0–1 | 0.53 |
| `market_size_mm` | How big is the category, in millions of units? | 0.01–2,000,000 | 415 |
| `distribution` | What weighted distribution will you have by the end of year one? | 0–1 | 0.63 |

Phrasing that works better than the field names:

- Population: "Is this a national launch? Which country, and are we counting
  households or individuals?" Then supply the figure yourself and say you did.
- Penetration: "Out of every hundred households, how many buy anything in this
  category over a year?" People answer a count more readily than a percentage.
- Market size: "How many units does the whole category move in a year?" If they
  only have a dollar figure, ask for average price and divide, but then set
  `price` to 1 so the share calculation stays in one unit.
- Distribution: "Where will this be on shelf a year in, every major grocer, or a
  regional test?" Convert to a fraction yourself.

## Tier 2: ask if the study has them

| Field | Question | Range | Default |
| --- | --- | --- | --- |
| `category_purchases_year` | How many times a year do buyers say they purchase the category? | 0.01–1000 | 20 |
| `repeat_units` | How many units do they buy on a typical trip? | 0.0001–5 | 1.43 |
| `price` | What will it retail for? | > 0 | 3.99 |
| `build_speed` | How fast will this build: very fast, somewhat fast, standard, somewhat slow, very slow? | one of those five | standard |
| `external_frequency` | Do you have a panel-observed purchase frequency? | > 1 | 4.667 |

`category_purchases_year` is the **claimed** survey figure and the model expects it
to be overstated. It deflates it by a factor of three before use. Do not
pre-correct it, enter what respondents said.

`build_speed` maps to a peak period of 2 through 6. It drives repeats per
repeater and the share of triers who try within the first year. Ask it as a
question about the category rather than the product: impulse snacks build fast,
durables build slowly.

If the user has no panel frequency, set `use_external_frequency` to false so the
survey figure drives the volume build too.

## Tier 3: media and awareness

All inside `awareness_inputs`. Skip this whole tier if the user supplies an
awareness figure directly, set `calculate_awareness` to false and pass
`awareness_manual` as a fraction.

| Field | Question | Range | Default |
| --- | --- | --- | --- |
| `spend_mm` | What is the year-one media budget, in millions? | ≥ 0 | 4.6 |
| `cost_per_grp` | What does a GRP cost in this market? | > 0 | 10000 |
| `brand_name_recall` | What share of people who see the ad will recall the brand name? | 0–1 | 0.55 |
| `branding` | Is this a line extension of a known brand, or a new brand? | "LX" or "NB" | "LX" |
| `horizon_weeks` | How many weeks are we forecasting? | > 0 | 52 |

`branding` matters: for a line extension the awareness curve carries a 1.32 factor
that a new brand does not, and in this model the factor *lowers* media-driven
awareness for the line extension (the same rating points build less awareness of
the new item when the advertising is read as the parent brand's). Say which way
it worked when you report. Ask it plainly, "is this going out under an existing
brand name?"

## Tier 4: the trial detector

All inside `trial_inputs`. These are concept-test diagnostics on an index scale
where 100 is the category norm. Skip the tier if the user has a trial rate , 
set `calculate_trial` to false and pass `trial_manual` as a fraction.

| Field | Question | Default |
| --- | --- | --- |
| `differentiation` | How different is the concept from what is out there, indexed to 100? | 122 |
| `relevance` | How relevant is it to the category buyer, indexed to 100? | 98 |
| `share_of_leader` | What share does the category leader hold, in points? | 25 |
| `visibility` | How visible will it be on shelf, indexed to 100? | 55 |
| `brands_80pct_share` | How many brands make up 80% of the category? | 22 |
| `brands_evoked_set` | How many brands would a buyer name unprompted? | 5 |
| `expensiveness` | How expensive does it feel versus the category, indexed to 100? | 114 |

**`brands_evoked_set` dominates the others.** Its coefficient is −3.03 against
roughly ±0.25 for everything else. One brand more or less in the evoked set moves
trial more than a twenty-point swing in differentiation. Flag this whenever a
user's answer here produces a surprising trial rate, and be careful that they are
answering "brands named unprompted" rather than "brands on shelf".

## Tier 5: overrides

Inside `overrides`. Each replaces a model-derived value. Leave out or set to
`null` to keep the model's own figure.

| Field | What it replaces | Range |
| --- | --- | --- |
| `share_of_choice` | Derived from the repeat rate | 0.001–1 |
| `repeats_per_repeater` | Derived from frequency and build speed | 0.001–1000 |
| `first_repeat_rate` | Derived from claimed frequency | 0.001–1 |
| `units_at_trial` | Derived from repeat units | 1–5 |
| `triers_try_first_year` | Derived from build speed | 0.001–1 |
| `volume_equiv_category` / `volume_equiv_product` | Volume per pack, both default 1 | 0.00001–5000 |
| `price_per_volume_category` / `price_per_volume_product` | Both default 1 | 0.01–5000 |
| `range_width_category` / `range_width_product` | Both default 1 | 0.01–5000 |

`share_of_choice` ships set to 0.25 because the original modeller overrode it.
Mention this when reporting, the model's own derived figure on baseline inputs
is 0.33, which is a materially different forecast.

Overriding both `repeats_per_repeater` and `triers_try_first_year` makes
`build_speed` inert, because nothing else depends on it. The model warns when
this happens.

The six volume, price, and range-width fields only matter when the test product
comes in a different pack size or price architecture from the category. All at 1
means "same as category", which is the usual case.

## Handling "I don't know"

The pattern that works: offer a bracket, not a number.

> "No problem. Is this closer to something almost every household buys, bread,
> laundry detergent, or something a minority of households buy in a year?"

Then use the bracket's midpoint and record the assumption. Brackets worth having
ready:

| Input | Staple | Regular | Niche |
| --- | --- | --- | --- |
| `penetration` | 0.75 | 0.50 | 0.20 |
| `category_purchases_year` | 30 | 15 | 6 |
| `repeat_units` | 2.0 | 1.4 | 1.1 |

For `distribution`, the useful brackets are national grocery (0.85), broad but
incomplete (0.60), and regional or single-retailer (0.25).

Never silently substitute a default. Every assumed value gets named in the final
report, because the user will quote the forecast to someone who will ask.

## Sanity checks before running

Catch these in conversation rather than in the output.

- **Penetration times population should look like a plausible buyer count.** At
  53% of 118 million that is 62.5 million buyers. If it comes out at three
  people or at more than the population, something was entered as a percentage
  where a fraction belonged.
- **Market size divided by buyers divided by repeat units** gives annual purchase
  occasions per buyer. Under 1 or over 100 means market size and penetration are
  describing different universes.
- **Distribution, penetration, awareness, and trial are all fractions**, never
  percentages. 63 instead of 0.63 will not error, it will produce a forecast
  a hundred times too large.
- **Market size in dollars with a price other than 1** double-counts price. Pick
  one unit and stay in it.
