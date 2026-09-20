# Memo: the AI chapter, and which new chapters the skill library implies

You asked me to (a) build a runnable forecasting skill library an AI can actually use, and
(b) flag where the library reaches *beyond* the book's current chapters so you can decide
what to add. Here's the map.

## Where the library lands in the book

Your chapters already supply the intellectual content for most of the library. The skills
are, in effect, the book's methods turned into directions an AI can execute:

| Skill | Already covered by chapter(s) |
|---|---|
| reference-class (outside view, base rates) | 9 (The Oracle Problem), 10 (The Superforecaster) |
| bass-diffusion | 19 (Frank Bass and the Television) |
| trial-repeat | 19 (Section Four mentions Parfitt–Collins) |
| market-sizing (conjoint for *m*) | 19 (conjoint subsection) |
| mmm-attribution | 20 (The Marketing Mix) |
| hierarchical-reconcile | 18 (The Hierarchy) |
| triangulation-superforecast (Fermi, Delphi, proxies) | 8 (The Delphi Room), 10, 11 (The Crowd and the Ox) |
| ensemble-combine (M-competition, extremizing) | 10, 26 (the combination finding) |
| uncertainty-backtest (Brier, calibration, conformal) | 10, 17 (Living with Probability), 26 |
| structural-breaks | 24 (The Anomaly), referenced in 26 |
| model-vs-estimate + forecasting-router | **NOT a chapter yet: this is the new one** |
| deep-research-intake | **NOT a chapter yet: part of the new one** |

So the library is ~85% a faithful operationalization of what you already wrote. The two
genuinely new pieces, the *router* (model vs. estimate, proxy discipline, direction) and
the *intake* (pre-work): are exactly the AI chapter you described.

## The AI chapter (slot: Chapter 22: it's currently empty)

Chapter 22 is unused; it sits right after the marketing/supply-chain cluster (19–21) and
before the anomaly/structural-break material (23–24). That's the correct home: the AI
chapter should arrive *after* the reader has met diffusion, MMM, and the bullwhip, because
its whole thesis is "AI can do everything in the previous chapters, if it has direction."

Suggested title in your house style: **"The Machine That Forecasts"** or **"Giving the
Oracle Direction."** Core argument, matching your draft:

1. Given the right structure and skills, AI is a strong forecaster, but you cannot just ask
   it for a forecast. The work is in the pre-work: deep research, assembling data, building
   the forecasting skill with best practices.
2. AI can execute every method in the earlier chapters. What it won't do unprompted is pick
   the *best* model, run *multiple* methods, and build an *ensemble*. It needs direction.
3. **The rule: ** if you have data and can model it, always model it, never have AI judge the
   number from the data itself. The corollary: when you genuinely can't model it (new
   product, novel category), estimate it via triangulation; don't force a curve onto nothing.
4. Direction means proxy selection: AI must be told which figures are good proxies and which
   are noise (outlets → reach; unaided awareness → demand-readiness; trial × repeat →
   conversion). Each proxy earns its place with a causal sentence.
5. The build-up worked example: model existing products' steady-state, re-base with the new
   product's estimated trial/repeat/awareness, apply the build-up, triangulate. This is the
   chapter's set-piece and it ties together Bass (19), trial-repeat (19), and MMM (20).

The chapter can close by pointing at the library as the artifact: the best-practices skill
the chapter argues you must build, actually built.

## New chapters the library reaches *beyond* your current text

These are methods the library includes that the book either touches only lightly or not at
all. Flagging so you can decide whether each warrants its own chapter:

1. **Conformal prediction / distribution-free intervals.** The book covers Brier and
   calibration (10, 17) but not conformal intervals, which are now the standard way to put
   honest, guaranteed-coverage error bars on *any* model (especially ML). Worth a short
   chapter or a section in the uncertainty material: it's the modern answer to "how wrong
   might I be?" and it's in `uncertainty-backtest`.

2. **Modern ML forecasting (gradient boosting, global models, foundation models).** Your
   Source Ledger in 26 already name-checks DeepAR and foundation models. The library leans on
   regularized regression and could be extended to LightGBM/quantile models. If you want the
   book to feel current, a chapter on **"When the Model Has No Theory"**: purely
   data-driven ML forecasting, its strengths (M5 was won by LightGBM) and its danger
   (no mechanism, fails silently on structural breaks): would complement the
   mechanism-driven chapters nicely and motivate the model-vs-estimate fork.

3. **The intake / deep-research discipline as its own idea.** The notion that *the forecast
   is mostly setup*: collecting data, choosing proxies, defining the reference class before
   any math, is implicit across 8/9/10 but never stated as a standalone method. It's the
   spine of `deep-research-intake`. Could be a section in the AI chapter rather than its own
   chapter, but it's distinct enough to consider.

4. **Optimal probabilistic reconciliation.** Chapter 18 covers MinT for point forecasts;
   the library's reconcile script does too. The *probabilistic* extension (Panagiotelis et
   al., already in your 18 source ledger): reconciling whole distributions, not just means
, is a natural half-section to add if you want 18 to be complete.

5. **Adstock & saturation as named concepts.** Chapter 20 covers MMM and attribution; the
   library makes adstock (carryover) and saturation (diminishing returns) explicit and
   runnable. If 20 doesn't already name these two transforms, a couple of paragraphs would
   close the gap between the chapter's narrative and what an AI actually has to compute.

My recommendation: write **Chapter 22 (the AI chapter)** as the priority: it's the cover
promise and the library's reason for existing, and fold items 1, 3, and 5 in as
*sections* of existing chapters (22, 26, 20 respectively). Items 2 and 4 are the only
candidates for genuinely new standalone chapters, and only if you want the book to extend
into the modern ML/probabilistic frontier.

## What I'd verify before print

- **"Build-up"** as the term for the launch ramp: confirm current diffusion-forecasting
  usage; it overlaps with "diffusion curve" / "adoption ramp." (Flagged in the README too.)
- The Bass priors (p ≈ 0.03, q ≈ 0.38) are from Sultan, Farley & Lehmann (1990), already in
  your Chapter 19 source notes: consistent.
- Extremizing (Satopää et al. 2014) and MinT (Wickramasuriya et al. 2019) are already in your
  source ledgers, so the library's citations match the book's.
