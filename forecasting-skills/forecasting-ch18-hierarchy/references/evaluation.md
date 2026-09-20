# Evaluation scenarios: chapter 18

## Acceptance scenarios

1. **Scenario:** Base [100,40,50]: bottom-up result?
   **Expected behavior:** [90,40,50].

2. **Scenario:** No historical errors are available. Can W=I be called empirically estimated MinT?
   **Expected behavior:** No. Label it OLS/unweighted reconciliation; empirical covariance was not estimated.

3. **Scenario:** A negative bottom node is clipped to zero without changing total. What can fail?
   **Expected behavior:** Coherence. Enforce nonnegativity jointly or disclose that a constrained reconciliation is needed.

4. **Transfer request:** Use chapter 18 to reconcile hierarchy.csv using the supplied summing matrix, compare eligible methods and verify coherence without claiming accuracy from addition alone.
   **Expected artifacts:** Return node order/S definition, base and reconciled values, coherence residuals, covariance estimation assumptions and matched test losses where outcomes exist.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
