# Evaluation scenarios: chapter 12

## Acceptance scenarios

1. **Scenario:** Method MAE=8, baseline MAE=10: relative gap?
   **Expected behavior:** 100×(8/10-1)=-20%, a 20% lower MAE on those matched cases.

2. **Scenario:** Training seasonal-naive error scale is zero. What is MASE?
   **Expected behavior:** Undefined, not zero. Flag it and report an appropriate unscaled metric.

3. **Scenario:** Weights are tuned using the final test. Is it still a final test?
   **Expected behavior:** No. It became selection data; evaluate the frozen combination on later untouched cases.

4. **Transfer request:** Use chapter 12 to build a common rolling-origin benchmark for panel.csv, retain prediction-level records and compare methods under explicit business weights.
   **Expected artifacts:** Return prediction-level records, per-series/per-origin/per-horizon losses, weighting rules, coverage and failed-fit counts, baseline comparisons and final-selection separation.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
