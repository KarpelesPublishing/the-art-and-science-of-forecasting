# Evaluation scenarios: chapter 11

## Acceptance scenarios

1. **Scenario:** All five estimates are 120 while truth is 100. What do mean and median do?
   **Expected behavior:** Both remain 120; aggregation cannot remove a shared 20-unit bias.

2. **Scenario:** rho=1 and individual SD=20. What is aggregate SD at n=100?
   **Expected behavior:** 20: perfectly common error does not average away.

3. **Scenario:** May the spread of five opinions be called an 80% prediction interval?
   **Expected behavior:** Not without a justified link between opinion dispersion and outcome uncertainty; call it disagreement or a scenario range.

4. **Transfer request:** Apply chapter 11 to estimates.csv, compare transparent aggregators and explain whether apparent agreement comes from independent information or shared evidence.
   **Expected artifacts:** Return respondent count, mean/median/trimmed estimates, source-dependence notes, outlier sensitivity and held-out aggregation losses if available.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
