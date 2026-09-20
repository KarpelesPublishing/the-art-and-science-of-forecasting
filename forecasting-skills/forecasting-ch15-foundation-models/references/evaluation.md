# Evaluation scenarios: chapter 15

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 263 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** The baseline beats Chronos on the frozen test. Should a new checkpoint be selected on that same test?
   **Expected behavior:** No. Report the result; selecting again uses that test as validation and requires a new untouched test.

2. **Scenario:** A known pattern resembles training data. Does that prove leakage?
   **Expected behavior:** No. Similarity alone is not evidence that the exact evaluation future was exposed.

3. **Scenario:** Download fails but seasonal-naive runs. What method label belongs on its output?
   **Expected behavior:** Seasonal naive, with foundation-model execution marked skipped or failed.

4. **Transfer request:** Use chapter 15 to benchmark the pinned foundation model on demand.csv with frozen origins, honest dependency status and matched baseline and interval scores.
   **Expected artifacts:** Return model/revision and environment record, input context/origin metadata, prediction quantiles, matched baseline losses, execution status and contamination limitations.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
