# Evaluation scenarios: chapter 2

## Acceptance scenarios

1. **Scenario:** Beta(1,1), three successes in four trials: posterior?
   **Expected behavior:** Beta(4,2), mean 4/6=2/3.

2. **Scenario:** A database contains 90 successes but no count of attempts. What can be updated?
   **Expected behavior:** Not a binomial probability. Obtain the attempts denominator or report counts without a probability estimate.

3. **Scenario:** Low performers improved on retesting after coaching. Is coaching identified?
   **Expected behavior:** No. Measurement noise and selection can produce regression toward the mean. A credible comparator or experiment is needed.

4. **Transfer request:** Use chapter 2 to update the success probability from batches.csv, explain the prior in business terms, and audit whether missing failures invalidate the calculation.
   **Expected artifacts:** Return success/trial totals, prior and posterior parameters, posterior mean and credible interval, sensitivity to the prior and a selection-process note. Label future-count predictions separately.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
