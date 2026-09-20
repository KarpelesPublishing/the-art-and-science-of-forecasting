# Evaluation scenarios: chapter 10

## Acceptance scenarios

1. **Scenario:** Prior .4, supported LR=3: calculate the posterior.
   **Expected behavior:** Prior odds are 2/3; posterior odds are 2, so posterior probability is 2/3, approximately .667.

2. **Scenario:** An event has revisions .3 before cutoff and .99 after resolution; outcome=1. What scores?
   **Expected behavior:** Only .3 is eligible. Its Brier contribution is (.3-1)^2=.49. The .99 hindsight revision is preserved but excluded.

3. **Scenario:** Three launch scenarios exceed the target in two cases. Is the event probability 2/3?
   **Expected behavior:** No. The scenarios have no probability weights or model-error distribution. Report conditional outcomes and specify what evidence is needed to estimate event odds.

4. **Transfer request:** Use chapter 10 to define and journal whether our launch exceeds 50,000 units within 24 months. Separate business assumptions from measured evidence, give a justified initial probability or state why one is unsupported, and predeclare resolution and scoring rules.
   **Expected artifacts:** Return the event contract, base-rate source, initial and current probability, complete revision journal, update triggers, resolved-event score table and exclusions. Mark editable local JSON as unauthenticated; it is not tamper-proof storage.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
