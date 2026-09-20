# A product with no sales history

A launch has no series and no base rate of its own. The workflow keeps its gates; the profile gate
becomes an inventory of what the reader does know, and the method is the author's top-down bottom-up triangulation model.

1. **Brief.** The target is first-year (or 24-month) volume in units or currency; the decision is
   usually a production or budget commitment; the outcome date is the end of the period. Ask
   whether any comparable launched products with observed sales exist; the answer chooses the route.
2. **Inventory instead of profile.** Write down, with sources and dates, what is known: category size
   and penetration, distribution plan, media plan, concept-test scores, price, comparable launches.
   Mark each as measured, judged or guessed. This list is `work/inputs.md` and it goes into the report.
3. **Baseline.** The category share a no-name entrant of this kind typically reaches, or the average of
   the comparable launches. State it before running any model.
4. **Method.**
   - No comparable products: [reconcile-tdbu](../../reconcile-tdbu/SKILL.md). It interviews for the
     four inputs it needs, runs on illustrative constants for the rest, and reports the gap between the
     trial-and-repeat build-up and the market-share view. Follow its interview; do not fill inputs it
     did not ask for.
   - Comparable launched products with observed 24-month units and reach inputs: chapter 27
     `mode: launch` (`run.py apply --chapter 27`), which calibrates a shared scale on those products,
     holds some out, and phases trials over the horizon with repeat.
   - An adoption curve for a durable: chapter 19, which turns Bass adoption into sales with a repeat
     kernel under two timing assumptions.
5. **Validation.** There is no holdout of the future. The checks are: the held-out reference products
   in chapter 27; the reconciliation gap in `reconcile-tdbu` (two mechanisms disagreeing is the
   evidence); the sensitivity table (which input moves the number most). Say plainly that agreement
   between routes sharing inputs is not independent validation.
6. **Uncertainty.** The top-down bottom-up triangulation models give scenarios (timing peaks, ceilings, input ranges), not
   intervals. Label them scenarios and show the tornado of input sensitivities; the brief's cost
   asymmetry says which scenario the commitment should protect against.
7. **Report and journal.** Render the run's report; journal the monthly volume scenario the reader
   commits to, with the outcome date. Launch forecasts are the ones most worth scoring, because the
   inputs that were guessed become known.
