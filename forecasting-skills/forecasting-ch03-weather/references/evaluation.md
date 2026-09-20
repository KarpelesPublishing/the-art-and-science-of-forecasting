# Evaluation scenarios: chapter 3

## Acceptance scenarios

1. **Scenario:** Frequency is .25 cycles per quarter. What is the period?
   **Expected behavior:** Four quarters, because 1/.25=4.

2. **Scenario:** Can a smoother using next December’s value construct a forecast for this June?
   **Expected behavior:** No. Full-sample decomposition leaks future observations; refit at June’s cutoff.

3. **Scenario:** A changed integration tolerance produces nearly identical short trajectories. Has initial uncertainty vanished?
   **Expected behavior:** No. That checks numerical stability locally; uncertainty in the true starting state remains.

4. **Transfer request:** Use chapter 3 to audit the seasonality of demand.csv and explain which components are retrospective and which can safely inform future forecasts.
   **Expected artifacts:** Return the calendar audit, chosen period and rationale, decomposition table, reconstruction error, and any origin-safe baseline comparison. For dynamics report initial-state and numerical-tolerance assumptions separately.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
