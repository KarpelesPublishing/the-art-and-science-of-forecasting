# Evaluation scenarios: chapter 5

## Acceptance scenarios

1. **Scenario:** Predicted variance 9 and R=3: gain?
   **Expected behavior:** 9/(9+3)=.75, so three quarters of the innovation updates the state.

2. **Scenario:** What happens to uncertainty during two missing readings with Q=2?
   **Expected behavior:** Without updates, state variance increases by 4.

3. **Scenario:** Can lower smoothed RMSE justify replacing recorded online predictions?
   **Expected behavior:** No. Smoothing uses later measurements; preserve the forecasts actually available at each origin.

4. **Transfer request:** Use chapter 5 to track the latent level in readings.csv, explain Q and R, retain online predictions and distinguish state uncertainty from observation uncertainty.
   **Expected artifacts:** Return predicted and filtered means/variances, innovations, state versus observation forecasts, noise assumptions and sensitivity results. Separate smoothed values from online estimates.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
