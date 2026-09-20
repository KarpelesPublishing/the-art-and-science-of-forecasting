# Evaluation scenarios: chapter 21

## Acceptance scenarios

1. **Scenario:** Underage cost 4, overage cost 6: target quantile?
   **Expected behavior:** 4/(4+6)=.4.

2. **Scenario:** A zero record occurs because shelves were empty. Is it a true no-demand event for TSB?
   **Expected behavior:** Not established. It is censored sales; treating it as no demand can suppress forecasts incorrectly.

3. **Scenario:** Consumer variance 25 and order variance 100: amplification ratio?
   **Expected behavior:** 100/25=4, provided periods and warm-up treatment match.

4. **Transfer request:** Use chapter 21 to forecast intermittent demand.csv, distinguish zeros from stockouts and connect supported forecasts to explicit lead-time and inventory-cost assumptions.
   **Expected artifacts:** Return demand audit, pre-update method predictions and losses, declared policy/cost assumptions, inventory-conservation checks and service/cost/amplification results for executed policies.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
