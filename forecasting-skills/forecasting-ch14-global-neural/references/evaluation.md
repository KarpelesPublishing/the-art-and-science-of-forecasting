# Evaluation scenarios: chapter 14

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 268 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** Normalized output mean=-.2, SD=.1, scale=100. Original mean and SD?
   **Expected behavior:** Mean 80 and SD 10 under the lesson’s centering convention.

2. **Scenario:** Test entity history appears in training but future dates do not. Is this unseen-entity evaluation?
   **Expected behavior:** No. It is temporal generalization for a seen entity; label it accordingly.

3. **Scenario:** Why must sampled paths feed back their own values?
   **Expected behavior:** To propagate uncertainty through autoregressive dependence without importing future actuals.

4. **Transfer request:** Apply chapter 14 to panel.csv with an explicit unseen-entity holdout, compare the actual global Gaussian MLP with local baselines and report uncertainty limitations.
   **Expected artifacts:** Return entity/time split, context and scaling rules, model/training record, sampled forecast quantiles, local-baseline comparison and coverage/width by entity and horizon.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
