# Evaluation scenarios: chapter 14

## Acceptance scenarios

1. **Scenario:** Normalized output mean=-.2, SD=.1, scale=100. Original mean and SD?
   **Expected behavior:** Mean 80 and SD 10 under the lesson’s centering convention.

2. **Scenario:** Test entity history appears in training but future dates do not. Is this unseen-entity evaluation?
   **Expected behavior:** No. It is temporal generalization for a seen entity; label it accordingly.

3. **Scenario:** Why must sampled paths feed back their own values?
   **Expected behavior:** To propagate uncertainty through autoregressive dependence without importing future actuals.

4. **Transfer request:** Apply chapter 14 to panel.csv with an explicit unseen-entity holdout, compare the actual global Gaussian MLP with local baselines and report uncertainty limitations.
   **Expected artifacts:** Return entity/time split, context and scaling rules, model/training record, sampled forecast quantiles, local-baseline comparison and coverage/width by entity and horizon.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
