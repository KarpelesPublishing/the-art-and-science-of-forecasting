# Evaluation scenarios: chapter 7

## Acceptance scenarios

1. **Scenario:** Independent simulated mean has SE=.1 at N=1000. Approximate SE at N=4000?
   **Expected behavior:** SE=.05 under the same finite-variance model.

2. **Scenario:** You observe 90% interval coverage across simulator draws. Is empirical business coverage established?
   **Expected behavior:** No. Simulator draws came from assumed distributions; real later outcomes are required to assess operational coverage.

3. **Scenario:** MCMC has 10,000 draws but ESS=100. Which count informs mean precision?
   **Expected behavior:** Effective sample size, approximately 100, subject to valid diagnostics; raw draw count overstates independent information.

4. **Transfer request:** Apply chapter 7 to cost_components.csv, preserve the stated dependence assumptions, calculate budget-exceedance probabilities and distinguish simulation error from model uncertainty.
   **Expected artifacts:** Return input distributions and provenance, dependence assumptions, seed/draw count, outcome quantiles, exceedance probabilities, Monte Carlo precision and separate model-sensitivity results.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
