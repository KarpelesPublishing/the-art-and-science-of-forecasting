# Evaluation scenarios: chapter 23

## Acceptance scenarios

1. **Scenario:** Observed reports 30, completeness .75: nowcast?
   **Expected behavior:** 40 events, conditional on that completeness estimate.

2. **Scenario:** A report arrives after the historical as-of date. May it enter that origin’s nowcast input?
   **Expected behavior:** No. It belongs only to later-vintage truth or a subsequent origin.

3. **Scenario:** Completeness is zero for today. What is the simple adjusted count?
   **Expected behavior:** Undefined/unidentified from those reports. Report that status rather than zero or infinity as a usable forecast.

4. **Transfer request:** Use chapter 23 to nowcast reporting_triangle.csv at the stated cutoff, audit delay stability and keep retrospective completion estimates separate from future transmission scenarios.
   **Expected artifacts:** Return as-of reporting audit, age-specific completeness, observed and nowcast counts, unidentifiable dates and later-vintage evaluation where available. For compartment scenarios include conservation checks and assumptions.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
