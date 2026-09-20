# Evaluation scenarios: chapter 5

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 255 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** Predicted variance 9 and R=3: gain?
   **Expected behavior:** 9/(9+3)=.75, so three quarters of the innovation updates the state.

2. **Scenario:** What happens to uncertainty during two missing readings with Q=2?
   **Expected behavior:** Without updates, state variance increases by 4.

3. **Scenario:** Can lower smoothed RMSE justify replacing recorded online predictions?
   **Expected behavior:** No. Smoothing uses later measurements; preserve the forecasts actually available at each origin.

4. **Transfer request:** Use chapter 5 to track the latent level in readings.csv, explain Q and R, retain online predictions and distinguish state uncertainty from observation uncertainty.
   **Expected artifacts:** Return predicted and filtered means/variances, innovations, state versus observation forecasts, noise assumptions and sensitivity results. Separate smoothed values from online estimates.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
