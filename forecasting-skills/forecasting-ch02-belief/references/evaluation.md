# Evaluation scenarios: chapter 2

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 262 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** Beta(1,1), three successes in four trials: posterior?
   **Expected behavior:** Beta(4,2), mean 4/6=2/3.

2. **Scenario:** A database contains 90 successes but no count of attempts. What can be updated?
   **Expected behavior:** Not a binomial probability. Obtain the attempts denominator or report counts without a probability estimate.

3. **Scenario:** Low performers improved on retesting after coaching. Is coaching identified?
   **Expected behavior:** No. Measurement noise and selection can produce regression toward the mean. A credible comparator or experiment is needed.

4. **Transfer request:** Use chapter 2 to update the success probability from batches.csv, explain the prior in business terms, and audit whether missing failures invalidate the calculation.
   **Expected artifacts:** Return success/trial totals, prior and posterior parameters, posterior mean and credible interval, sensitivity to the prior and a selection-process note. Label future-count predictions separately.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
