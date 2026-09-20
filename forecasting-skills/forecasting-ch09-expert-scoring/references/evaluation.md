# Evaluation scenarios: chapter 9

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 262 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** Forecast .9, outcome 0: Brier?
   **Expected behavior:** .81, a large penalty for confident error.

2. **Scenario:** Every event has true rate .2. Is a constant .5 forecast calibrated?
   **Expected behavior:** No. In its single forecast bin, observed frequency would approach .2 rather than .5.

3. **Scenario:** Expert A scored easy events, B scored difficult ones. Can mean Brier rank skill fairly?
   **Expected behavior:** Not without adjusting the comparison design; use common events and lead times or explicitly defend a different comparison.

4. **Transfer request:** Use chapter 9 to score probabilities.csv on eligible resolved events, compare the recorded baseline and explain calibration with bin counts rather than unsupported rankings.
   **Expected artifacts:** Return per-event and mean Brier, baseline difference, eligibility/exclusion counts, bin means and counts, and limitations of expert comparison.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
