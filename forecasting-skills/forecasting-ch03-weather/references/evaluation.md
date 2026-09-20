# Evaluation scenarios: chapter 3

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 271 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** Frequency is .25 cycles per quarter. What is the period?
   **Expected behavior:** Four quarters, because 1/.25=4.

2. **Scenario:** Can a smoother using next December’s value construct a forecast for this June?
   **Expected behavior:** No. Full-sample decomposition leaks future observations; refit at June’s cutoff.

3. **Scenario:** A changed integration tolerance produces nearly identical short trajectories. Has initial uncertainty vanished?
   **Expected behavior:** No. That checks numerical stability locally; uncertainty in the true starting state remains.

4. **Transfer request:** Use chapter 3 to audit the seasonality of demand.csv and explain which components are retrospective and which can safely inform future forecasts.
   **Expected artifacts:** Return the calendar audit, chosen period and rationale, decomposition table, reconstruction error, and any origin-safe baseline comparison. For dynamics report initial-state and numerical-tolerance assumptions separately.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
