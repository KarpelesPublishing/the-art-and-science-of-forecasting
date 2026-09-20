# Evaluation scenarios: chapter 13

## Acceptance scenarios

1. **Scenario:** At a Monday origin, may Wednesday’s observed sales be a lag for Friday’s fixed-origin forecast?
   **Expected behavior:** No. They are unknown Monday. Use recursive predictions or horizon-safe direct features.

2. **Scenario:** Ablation removes promo but leaves promo-discount price. What is the problem?
   **Expected behavior:** Price still encodes much of the promotion; the ablation does not isolate that information group.

3. **Scenario:** SHAP assigns +10 to promotion. Is causal lift 10 units?
   **Expected behavior:** No. It explains a fitted prediction under model assumptions, not an intervention effect.

4. **Transfer request:** Use chapter 13 to forecast retail_panel.csv one day ahead, audit every feature’s availability and compare LightGBM with seasonal-naive and a promotion/price ablation.
   **Expected artifacts:** Return feature availability/audit table, origin-level one-step predictions, baseline and ablation losses, selected contribution explanations, and a clear horizon-mode declaration.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
