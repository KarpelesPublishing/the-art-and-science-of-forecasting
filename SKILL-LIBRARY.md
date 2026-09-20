# The Forecasting Skill Library

A runnable library that lets an AI forecast *properly*, the way the rest of this book
describes forecasting being done: instead of guessing a number that looks plausible.

It exists because of one observation: **given the right structure, skills, and pre-work, an
AI is a very good forecaster, but you cannot just ask it to make a forecast.** Left to
itself, a model will eyeball a number from whatever data is in front of it, pick the first
method that comes to mind, skip the alternatives, and never build an ensemble. This library
supplies the missing direction: which method to use, which proxies are good, when to model
and when to estimate, and how to combine everything into one defensible figure with an
honest interval.

---

## The one rule

> **If you have data and can model it, ALWAYS model it. Never have the AI judge the number
> from the data when the data can produce the number itself.**

A language model's free-floating judgment is the weakest instrument available: unanchored,
uncalibrated, quietly overconfident. The moment a quantity can be tied to a fitted
relationship (a regression, a diffusion curve, a trial-repeat decomposition, a base rate),
tie it.

And the corollary, equally important:

> **When you genuinely cannot model it, do not pretend to. Estimate it, explicitly, from
> defended proxies, with triangulation.**

A new product has no history of its own; forcing a curve onto four noisy points yields a
fake-tight interval that is worse than an honest structured estimate. Knowing *which
situation you are in* is the first forecast you make. Modelling isn't always right;
estimating isn't always right. The library's job is to route you to the correct one.

---

## How an AI should use this library

```
1. Read forecasting-skills/all-chapters-forecasting/SKILL.md.   <- always first
2. Frame the target: units, horizon, as-of date, decision costs, what is known in advance.
3. Route to the chapter skills the problem needs (table below); load only those.
4. Run the chapter tool when the reader agrees the method fits:
       companion/.venv/bin/python companion/scripts/run.py apply --chapter N --input data.csv --config config.json --output companion/applied-runs/name
5. Build a SECOND method (the other of model/estimate is the canonical pair).
6. Combine, attach an interval and a scoring plan, and check the regime
   (chapters 12, 17 and 24 respectively).
```

Never ship step 4 alone. The single most robust finding in forecasting (the M-competitions)
is that a sensible **combination** of methods beats the best single method. Build several;
combine.

---

## The skills

The library is 27 chapter skills, one integrated skill and one desk model, all under
`forecasting-skills/`. Each chapter skill has a `SKILL.md` (the directions, the input
contract and the exact executable interface) and `references/` (the workshop and the
evaluation notes). The executable tools live in `companion/src/forecasting_companion/`
and run through `companion/scripts/run.py`; they run only when asked.

| Skill | When to load it |
|---|---|
| **all-chapters-forecasting** | Always first. Frames the target and routes to the chapters. |
| **reconcile-tdbu** | A launch with no sales history: the desk model from chapters 20 and 27 (interview, two engines, reconcile). |
| **forecasting-ch25-reference-classes** | Picking analogues and base rates (the outside view) before any number. |
| **forecasting-ch19-diffusion** | S-curve adoption and its conversion to unit sales under two timing curves; Parfitt-Collins share. |
| **forecasting-ch27-directed-forecasting** | The launch model: calibrate on current products, re-base for the new one, apply the build-up. |
| **forecasting-ch20-marketing-mix** | Which channel drives sales: adstock, saturation, ridge, refit stability, reallocation scenario. |
| **forecasting-ch18-hierarchy** | Multi-level forecasts that must add up (bottom-up, OLS, MinT from child-parent edges). |
| **forecasting-ch12-benchmarking** | The engine: smoothing, ARIMA, Theta, STL, LightGBM and combinations selected at rolling origins. |
| **forecasting-ch17-probabilistic** | Intervals with a coverage guarantee (split and adaptive conformal) and interval scoring. |
| **forecasting-ch24-structural-breaks** | Is the historical relationship still valid? Changepoint dating, CUSUM, adaptation policies. |
| **forecasting-ch22-causal** | Did the action work? DiD, synthetic control, placebo tests, event study. |
| **forecasting-ch11-crowds** | Combining many judgments; extremizing probabilities. |

The remaining chapter skills cover markets (1), belief updating (2), weather and decomposition
(3), smoothing (4), state space with missing data (5), ARIMA (6), simulation (7), Delphi (8),
expert scoring (9), superforecasting journals (10), retail machine learning with covariates
(13), global neural models (14), pretrained foundation models (15), calendars and events (16),
inventory policy (21), epidemic nowcasting (23) and decision readiness (26).

---

## The canonical worked example: the build-up problem

This is the case that proves the whole philosophy, and it appears constantly: **forecast a
new product that has no sales history of its own.**

Existing products are at steady state: their history shows no ramp, because their build-up
finished years ago. So you cannot read the new product's launch shape off any single
existing product's flat sales. The correct move layers modelling and estimating:

1. **Model the steady-state economics from existing products.** Build a cross-sectional
   model across many *current* products relating their drivers: distribution/outlets,
   awareness, trial, repeat, price, to their sales. This part has data, so you model it.
   (Chapters 20 and 27.)
2. **Re-base for the new product.** Plug the new product's *estimated* trial rate, repeat
   rate, awareness, and distribution into that fitted relationship to get its eventual
   steady-state level. (Chapter 27; chapter 25 for the estimates.)
3. **Apply the build-up.** Existing products carry no build-up; the new one ramps. Lay the
   diffusion curve (the build-up shape) on top of the steady-state level to spread it across
   time. (Chapter 19, or the gamma launch curve of chapter 27.) Steady-state × shape-over-time = launch forecast.
4. **Triangulate.** Cross-check against a top-down (market size × share) route and any
   comparable ratio, then reconcile. (`reconcile-tdbu` does both routes and the
   reconciliation; chapter 12 for the combination.)

You modelled the part with data and estimated the part without it, then combined them. That
is the entire library in one procedure.

*(Terminology note: "build-up" is the term used here for the launch ramp. Verify against
current diffusion-forecasting usage; it overlaps with "diffusion curve" / "adoption ramp."
The mechanics are the Bass S-curve regardless of the label.)*

---

## What good direction looks like (the shoe-company example)

> Take a shoe company's current sales. Use their number of stores or outlets (or an estimate)
> as the reach proxy. Estimate unaided awareness: weight-averaged with aided awareness only
> if it's a very small brand, where unaided is near zero and uninformative. Bring in trial-
> and repeat-rate estimates as the conversion engine. Now you have an estimate. If it's a
> *new* product or service, add the build-up; current products won't have one.

Every noun in that paragraph is a **proxy choice the AI would not have made on its own**.
That is what "the model needs direction" means: a human (or the research step) supplies the
proxy map; the AI executes the modelling and arithmetic faithfully. The library's job is to
make those proxy choices *explicit and defended*, never silent.

**The proxy-validity gate:** before any number is used as a proxy, write the one sentence
that says *why it should track the target*. "Outlets gate reach because distribution limits
who can buy." If you can't write the sentence, the proxy isn't earned. This single gate
prevents the most common AI forecasting failure: grabbing a plausible-looking number with
no causal link and propagating its error through everything downstream.

---

## Anti-patterns (how AI forecasts fail)

- **Judging instead of modelling**: data was available; the AI eyeballed a number anyway.
- **Modelling instead of estimating**, a curve forced onto four points, reported with a
  tight interval that is fiction.
- **One method, shipped**, no combination, no cross-check.
- **Unearned proxy**, a number used as a proxy with no causal sentence.
- **Stale regime**, a historical relationship trusted straight through a structural break.
- **Hidden point estimate**, a number with no uncertainty around it.
- **No score**, no way set up to learn later whether the forecast was any good.

---

## Setup

Follow `companion/README.md` for the pinned environment (`companion/.venv`). Every chapter
tool, the batch runner and the 27 notebooks run from that environment; nothing needs to
be installed per skill.

---

## Installing as Claude skills

Run `companion/.venv/bin/python companion/scripts/install_skills.py` to expose the 29 skill
folders to an agent runtime, or point the assistant at
`forecasting-skills/all-chapters-forecasting/SKILL.md` directly. Keep the supplied folders in
their relative layout: the integrated skill links to the chapter skills, `reconcile-tdbu`
and `companion/`, so it is not a standalone installation. Start every forecasting task by
having the model read the integrated skill; `companion/START-HERE.md` is the reader's guide.
