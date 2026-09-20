# Evaluation scenarios: chapter 6

## Acceptance scenarios

1. **Scenario:** Levels 10,13,12: first differences?
   **Expected behavior:** 3 and -1.

2. **Scenario:** Residual Ljung–Box does not reject. Is the chosen model proven optimal?
   **Expected behavior:** No. The test concerns a particular residual dependence diagnostic and has limited power; compare future losses.

3. **Scenario:** A future promotion variable becomes known only after the forecast date. May its realized value be used?
   **Expected behavior:** No. Use the schedule actually known at the origin or label a conditional scenario.

4. **Transfer request:** Apply chapter 6 to sales.csv with a twelve-period horizon, compare supported ARIMA and seasonal-naive candidates at earlier origins, and explain selection and residual limitations.
   **Expected artifacts:** Return differencing/order rationale, fit warnings, origin-by-horizon benchmark losses, residual diagnostics, dated forecasts and model-interval assumptions.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
