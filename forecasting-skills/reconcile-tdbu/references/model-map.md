# Model map

Every formula in `scripts/reconcile_model.py`, in the order the model computes
them, with the name each quantity carries in the code and what it means. Read
this when explaining where a number came from, or when writing about the method.

A note on the constants before anything else. Every coefficient and curve
constant here is an illustrative starting value. None was taken from a
published study, a vendor model or a client dataset. They are generic numbers,
set by judgment, chosen so that an ordinary packaged-goods launch lands in the
right ballpark. They are meant to be tuned: if the user has launch history, fit
the trial and awareness relationships to it; if not, adjust the constants until
the model reproduces launches the user knows, and record what changed. The
architecture is the durable part.

## Contents

- [The shape of the thing](#the-shape-of-the-thing)
- [Survey overstatement correction](#survey-overstatement-correction)
- [Derived quantities](#derived-quantities)
- [Trial detector](#trial-detector)
- [Awareness model](#awareness-model)
- [The volume chain](#the-volume-chain)
- [The two engines](#the-two-engines)
- [Diagnostics and the implication check](#diagnostics-and-the-implication-check)
- [Reconciliation](#reconciliation)
- [Name index](#name-index)

## The shape of the thing

Six typed inputs, a handful of settings, and a set of derived quantities that
stand in for everything a test-market panel would have measured. Two engines
then compute first-year volume from the same derived quantities:

| | Bottom-up (`bottom_up`) | Top-down (`top_down`) |
| --- | --- | --- |
| Given | Category penetration | Market size |
| Solved | Market size (`market_size`) | Penetration (`penetration`) |
| Reported volume | `tr_build` | `share_build` |

Penetration can be solved in one step because the top-down engine computes its
trial and repeat terms *without* the penetration factor and then divides:

```
i17 = population * trial * awareness * distribution * triers_first_year * units_at_trial
i18 = population * trial * awareness * distribution * (freq - 1) * share_of_choice * dynamics_ratio * repeat_units
penetration = min(1, share_build / ((i17 + i18) * penetration_denominator))
```

The bottom-up engine keeps penetration inline and derives market size instead.
Neither engine needs iteration, which is why the model is auditable line by line.

## Survey overstatement correction

Respondents overstate how often they buy a category. The model deflates the
claimed figure by a factor of three:

```
adjusted_frequency   = (category_purchases_year - 1) / 3 + 1
purchase_cycle_days  = 365 / adjusted_frequency
```

`SURVEY_DEFLATOR = 3.0` is a convention, not a law. It is the single most
consequential constant in the file for the implication check below.

Two frequencies exist. `model_frequency` is what the engines use for the
repeat build: `external_frequency` (default 4.667 purchases a year, a
panel-observed figure) when `use_external_frequency` is true, otherwise
`adjusted_frequency`. The claimed figure still drives `first_repeat_rate` and
the awareness model.

## Derived quantities

Each of these has a default the model computes and an override the user can
supply. `_pick(override, default)` returns the override when it is not `None`.

```
peak                    = BUILD_SPEEDS[build_speed] + 1          # 2 to 6, month of peak trial
repeats_per_repeater    = max(0, model_frequency * ln(2.65 * peak^-0.31) - 1)
dynamics_ratio          = repeats_per_repeater / model_frequency
first_repeat_rate       = (-11.7 * ln(((365/claimed - 1)/3 + 1) / 7) + 50) / 100
units_at_trial          = 1 + (repeat_units - 1) / 2
soc_low                 = 100 / (3 / first_repeat_rate - 2)             # percent
soc_high                = 100 * (first_repeat_rate - 0.02 * ln(101))    # percent
share_of_choice         = (soc_low + soc_high) / 2 / 100  if soc_simulator else 0
triers_try_first_year   = polynomial(peak) with TRIERS_POLY
units_to_volume_boost   = (range_prod/range_cat)^0.2 * (vol_cat/vol_prod)^0.5
                          / ((vol_cat/price_cat) / (vol_prod/price_prod))
```

`share_of_choice` defaults to a manual override of 0.25 in `Overrides`. The
model's own derived value on the reference inputs is 0.33. Set the override to
`null` to use the derived value, and say which one is active.

`triers_try_first_year` on the reference case: 92.6 percent at a four-month
peak, 97.0 percent at three months, 86.8 percent at five.

## Trial detector

Seven judged attributes, each scored on an index where 100 is roughly the
category norm, weighted and passed through a curve:

```
index             = sum(score_i * coef_i) + TRIAL_INTERCEPT + 10
trial_probability = 0.01                               if index < 0.001
                  = round(1.75 + index^1.5 / 10, 1) / 100  otherwise
```

| Attribute | Coefficient | Reference score | Contribution |
| --- | --- | --- | --- |
| differentiation | +0.27 | 122 | +32.9 |
| relevance | +0.23 | 98 | +22.5 |
| share_of_leader | +0.30 | 25 | +7.5 |
| visibility | +0.28 | 55 | +15.4 |
| brands_80pct_share | -0.22 | 22 | -4.8 |
| brands_evoked_set | -3.0 | 5 | -15.0 |
| expensiveness | -0.15 | 114 | -17.1 |
| intercept | -15.5 | | |

Reference index 35.9, trial 23.3 percent. Per point of score, the evoked-set
weight is by far the heaviest: one more brand in the shopper's mind costs three
index points, more than ten times the penalty for one more brand on the shelf.
Flag this when a user's evoked-set answer swings the result.

## Awareness model

A logistic in rating points and five other terms, then a shelf-presence uplift:

```
grps        = spend_mm * 1e6 / cost_per_grp
media_term  = grps * 0.00044 + adjusted_frequency * 0.012
inner       = media_term * horizon_weeks^-0.28 * exp(brand_name_recall)^1.95
              * exp(trial_probability / brand_name_recall)^0.63 * (distribution*100)^0.9
lambda      = 1.32 if branding == "LX" else 1.0
awareness_media_only = 1 / (1 + lambda * 26.5 * inner^-0.77)
lift        = (1 - a) / a * 0.66 * 0.33 * 0.9 * max(1 - a / 0.3, 0)     with a = awareness_media_only
awareness   = a * (1 + lift)
```

Reference case: 460 rating points, 18.9 percent from media, 24.8 percent with
the shelf effect. Media spend is a weak lever near this level; moving the plan
from $4.6M to $6.0M adds about one point of awareness.

## The volume chain

Identical in both engines (`_volume_chain`); the engines differ only in which
of `penetration` or `market_size` is an input.

```
buyers          = (market_size / model_frequency) / repeat_units        # category buyers, MM
repeat_base     = (market_size / repeat_units - buyers) * trial
max_units       = share_of_choice * repeat_base
combined        = dynamics_ratio * max_units * repeat_units
                  + buyers * trial * triers_first_year * units_at_trial
share_build     = distribution * awareness * combined * units_to_volume_boost
```

For the bottom-up engine `market_size` is first derived from penetration:

```
market_size = vol_equiv_category * penetration * population * repeat_units * model_frequency
```

so that `buyers` equals `penetration * population` exactly.

## The two engines

```
bottom_up:  market_size solved as above; tr_build = (i18 + i19) * units_to_volume_boost
            where i18, i19 are the penetration-inclusive trial and repeat terms
top_down:   market_size given; share_build from the chain; penetration solved by division
```

On the reference inputs: bottom-up 3.545 MM units, top-down 3.525 MM units.

## Diagnostics and the implication check

```
gap                     = |tr_build - share_build| / mean(tr_build, share_build)
implied_purchases_year  = max(0, ((market_size / vol_equiv_category) / (population * penetration * repeat_units) - 1) * 3 + 1)
implied_penetration     = top_down.penetration
implied_market_size     = adjusted_frequency * repeat_units * population * penetration * vol_equiv_category
forecast_value_mm       = tr_build * vol_equiv_product * price
volume_share            = mean(tr_build, share_build) / market_size
```

`implied_purchases_year` is reported on the survey's claimed scale, so it can
be compared directly with what the user typed. Reference case: typed 20,
implied 11.9; typed market size 415, implied 656. The two typed inputs cannot
both be right.

## Reconciliation

`reconcile()` copies `implied_purchases_year` into `category_purchases_year`
and `implied_penetration` into `penetration`, re-runs, and repeats until neither
moves. On the reference case: pass 0 typed 20 / 53%, pass 1 typed 11.9 / 52.7%,
pass 2 typed 12.0 / 52.7%, gap zero. Volume settles at 3.45 MM units, $13.77 MM.

`lock_frequency` or `lock_penetration` holds one input fixed. The gap then
settles at whatever the free input can absorb, and the message says so. If
penetration pins at 100 percent the balancing variable is saturated and the
message says that too; the usual cause is a market size too large for the
population, or repeat units too low.

## Name index

| Name | Meaning |
| --- | --- |
| `Inputs` | the six typed inputs and settings |
| `TrialInputs` | seven attribute scores |
| `AwarenessInputs` | media plan and branding |
| `Overrides` | replacements for derived values |
| `run(inp)` | one pass; returns `Result` |
| `reconcile(inp, ...)` | fixed-point iteration; returns `Solution` |
| `sensitivity(inp, field, values)` | one-input sweep for tornado tables |
| `selftest()` | reproduces the reference case |
| `Result.gap` | engine disagreement |
| `Result.implied_*` | what each typed input would have to be |
| `Result.warnings` | saturation, missing market size, override conflicts |
