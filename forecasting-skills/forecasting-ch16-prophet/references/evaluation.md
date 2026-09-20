# Evaluation scenarios: chapter 16

## Acceptance scenarios

1. **Scenario:** Trend 80, weekly +4, holiday -10 in additive mode: prediction?
   **Expected behavior:** 74.

2. **Scenario:** The last campaign shifts seven days after a forecast is issued. Was the original calendar necessarily leaked?
   **Expected behavior:** No; it may simply have become stale. Record the schedule vintage and assess the resulting forecast error.

3. **Scenario:** May a future event date be included in Prophet fitting?
   **Expected behavior:** Yes if genuinely known at the origin; its future outcome value must not enter fitting.

4. **Transfer request:** Use chapter 16 to forecast activity.csv with the actual known event calendar, select trend flexibility on earlier origins and explain components and held-out uncertainty.
   **Expected artifacts:** Return calendar provenance, validation losses and chosen prior, component audit, final forecast/nominal intervals, baseline or calendar-ablation comparison and event-specific errors.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
