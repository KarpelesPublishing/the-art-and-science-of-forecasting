# Evaluation scenarios: chapter 11

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 269 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** All five estimates are 120 while truth is 100. What do mean and median do?
   **Expected behavior:** Both remain 120; aggregation cannot remove a shared 20-unit bias.

2. **Scenario:** rho=1 and individual SD=20. What is aggregate SD at n=100?
   **Expected behavior:** 20: perfectly common error does not average away.

3. **Scenario:** May the spread of five opinions be called an 80% prediction interval?
   **Expected behavior:** Not without a justified link between opinion dispersion and outcome uncertainty; call it disagreement or a scenario range.

4. **Transfer request:** Apply chapter 11 to estimates.csv, compare transparent aggregators and explain whether apparent agreement comes from independent information or shared evidence.
   **Expected artifacts:** Return respondent count, mean/median/trimmed estimates, source-dependence notes, outlier sensitivity and held-out aggregation losses if available.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
