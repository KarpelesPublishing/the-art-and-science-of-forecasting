# Evaluation scenarios: chapter 7

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 269 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** Independent simulated mean has SE=.1 at N=1000. Approximate SE at N=4000?
   **Expected behavior:** SE=.05 under the same finite-variance model.

2. **Scenario:** You observe 90% interval coverage across simulator draws. Is empirical business coverage established?
   **Expected behavior:** No. Simulator draws came from assumed distributions; real later outcomes are required to assess operational coverage.

3. **Scenario:** MCMC has 10,000 draws but ESS=100. Which count informs mean precision?
   **Expected behavior:** Effective sample size, approximately 100, subject to valid diagnostics; raw draw count overstates independent information.

4. **Transfer request:** Apply chapter 7 to cost_components.csv, preserve the stated dependence assumptions, calculate budget-exceedance probabilities and distinguish simulation error from model uncertainty.
   **Expected artifacts:** Return input distributions and provenance, dependence assumptions, seed/draw count, outcome quantiles, exceedance probabilities, Monte Carlo precision and separate model-sensitivity results.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
