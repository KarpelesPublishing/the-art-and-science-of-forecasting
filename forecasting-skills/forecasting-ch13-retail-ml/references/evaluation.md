# Evaluation scenarios: chapter 13

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 267 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** At a Monday origin, may Wednesday’s observed sales be a lag for Friday’s fixed-origin forecast?
   **Expected behavior:** No. They are unknown Monday. Use recursive predictions or horizon-safe direct features.

2. **Scenario:** Ablation removes promo but leaves promo-discount price. What is the problem?
   **Expected behavior:** Price still encodes much of the promotion; the ablation does not isolate that information group.

3. **Scenario:** SHAP assigns +10 to promotion. Is causal lift 10 units?
   **Expected behavior:** No. It explains a fitted prediction under model assumptions, not an intervention effect.

4. **Transfer request:** Use chapter 13 to forecast retail_panel.csv one day ahead, audit every feature’s availability and compare LightGBM with seasonal-naive and a promotion/price ablation.
   **Expected artifacts:** Return feature availability/audit table, origin-level one-step predictions, baseline and ablation losses, selected contribution explanations, and a clear horizon-mode declaration.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
