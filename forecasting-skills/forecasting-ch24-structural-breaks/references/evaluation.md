# Evaluation scenarios: chapter 24

## Acceptance scenarios

1. **Scenario:** S=1,z=-2,k=.5: next S?
   **Expected behavior:** max(0,1-2-.5)=0.

2. **Scenario:** An alarm at period 50 leads to refitting including y50. When can the revised forecast first be available?
   **Expected behavior:** After observing period 50, for period 51 or later; never retroactively for period 50.

3. **Scenario:** A threshold was simulated under iid normal noise. Is its false-alarm rate guaranteed under autocorrelated demand?
   **Expected behavior:** No. Validate under an appropriate dependent null or disclose the calibration mismatch.

4. **Transfer request:** Apply chapter 24 to monitored_series.csv, predeclare threshold calibration and post-alarm action, and compare false alarms, delay and forecasting costs honestly.
   **Expected artifacts:** Return baseline/cutoff, residual stream, threshold calibration assumptions, alarm and reset log, first-alarm timing, false alarms and matched forecast-policy losses.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
