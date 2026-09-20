# Evaluation scenarios: chapter 20

## Acceptance scenarios

1. **Scenario:** Decay .8, previous stock 50, current spend 10: new stock?
   **Expected behavior:** 10+.8×50=50.

2. **Scenario:** A fixed baseline stabilizes channel coefficients but has no external support. Has identification improved?
   **Expected behavior:** Not established. The coefficients may be stably biased; test plausible backgrounds and seek stronger identification evidence.

3. **Scenario:** A response curve has Hill exponent 2. Must it be globally concave?
   **Expected behavior:** No. It can be S-shaped; do not impose a universal diminishing-return interpretation over its full range.

4. **Transfer request:** Apply chapter 20 to weekly_media.csv, account for initial carryover, evaluate sales prediction and attribution stability, and label which spending claims remain conditional.
   **Expected artifacts:** Return transformed media definitions, initial-state assumptions, prediction errors, coefficients/contributions across refits and assumptions, causal-identification status, and any conditional spend scenarios.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
