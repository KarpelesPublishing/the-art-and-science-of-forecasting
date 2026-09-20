# Evaluation scenarios: chapter 15

## Acceptance scenarios

1. **Scenario:** The baseline beats Chronos on the frozen test. Should a new checkpoint be selected on that same test?
   **Expected behavior:** No. Report the result; selecting again uses that test as validation and requires a new untouched test.

2. **Scenario:** A known pattern resembles training data. Does that prove leakage?
   **Expected behavior:** No. Similarity alone is not evidence that the exact evaluation future was exposed.

3. **Scenario:** Download fails but seasonal-naive runs. What method label belongs on its output?
   **Expected behavior:** Seasonal naive, with foundation-model execution marked skipped or failed.

4. **Transfer request:** Use chapter 15 to benchmark the pinned foundation model on demand.csv with frozen origins, honest dependency status and matched baseline and interval scores.
   **Expected artifacts:** Return model/revision and environment record, input context/origin metadata, prediction quantiles, matched baseline losses, execution status and contamination limitations.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
