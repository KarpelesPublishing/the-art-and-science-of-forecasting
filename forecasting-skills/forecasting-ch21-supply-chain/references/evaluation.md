# Evaluation scenarios: chapter 21

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 254 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** Underage cost 4, overage cost 6: target quantile?
   **Expected behavior:** 4/(4+6)=.4.

2. **Scenario:** A zero record occurs because shelves were empty. Is it a true no-demand event for TSB?
   **Expected behavior:** Not established. It is censored sales; treating it as no demand can suppress forecasts incorrectly.

3. **Scenario:** Consumer variance 25 and order variance 100: amplification ratio?
   **Expected behavior:** 100/25=4, provided periods and warm-up treatment match.

4. **Transfer request:** Use chapter 21 to forecast intermittent demand.csv, distinguish zeros from stockouts and connect supported forecasts to explicit lead-time and inventory-cost assumptions.
   **Expected artifacts:** Return demand audit, pre-update method predictions and losses, declared policy/cost assumptions, inventory-conservation checks and service/cost/amplification results for executed policies.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
