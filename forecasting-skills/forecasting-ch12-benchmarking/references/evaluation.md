# Evaluation scenarios: chapter 12

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 262 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** Method MAE=8, baseline MAE=10: relative gap?
   **Expected behavior:** 100×(8/10-1)=-20%, a 20% lower MAE on those matched cases.

2. **Scenario:** Training seasonal-naive error scale is zero. What is MASE?
   **Expected behavior:** Undefined, not zero. Flag it and report an appropriate unscaled metric.

3. **Scenario:** Weights are tuned using the final test. Is it still a final test?
   **Expected behavior:** No. It became selection data; evaluate the frozen combination on later untouched cases.

4. **Transfer request:** Use chapter 12 to build a common rolling-origin benchmark for panel.csv, retain prediction-level records and compare methods under explicit business weights.
   **Expected artifacts:** Return prediction-level records, per-series/per-origin/per-horizon losses, weighting rules, coverage and failed-fit counts, baseline comparisons and final-selection separation.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
