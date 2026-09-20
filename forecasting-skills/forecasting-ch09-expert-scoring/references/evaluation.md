# Evaluation scenarios: chapter 9

## Acceptance scenarios

1. **Scenario:** Forecast .9, outcome 0: Brier?
   **Expected behavior:** .81, a large penalty for confident error.

2. **Scenario:** Every event has true rate .2. Is a constant .5 forecast calibrated?
   **Expected behavior:** No. In its single forecast bin, observed frequency would approach .2 rather than .5.

3. **Scenario:** Expert A scored easy events, B scored difficult ones. Can mean Brier rank skill fairly?
   **Expected behavior:** Not without adjusting the comparison design; use common events and lead times or explicitly defend a different comparison.

4. **Transfer request:** Use chapter 9 to score probabilities.csv on eligible resolved events, compare the recorded baseline and explain calibration with bin counts rather than unsupported rankings.
   **Expected artifacts:** Return per-event and mean Brier, baseline difference, eligibility/exclusion counts, bin means and counts, and limitations of expert comparison.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
