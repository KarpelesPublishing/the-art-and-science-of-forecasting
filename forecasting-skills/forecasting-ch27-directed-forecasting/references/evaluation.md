# Evaluation scenarios: chapter 27

## Acceptance scenarios

1. **Scenario:** A declared trial total is 4,000. Under standard timing, how many occur in each year?
   **Expected behavior:** 3,200 in year one and 800 in year two. A slower timing scenario lowers year-one trials while retaining the 4,000 total.

2. **Scenario:** Trial cohorts are [100,50], and expected unit kernel is [1,.2]. What are first two months’ sales?
   **Expected behavior:** Month one is 100. Month two is 50+100×.2=70. The remaining 50×.2=10 repeat units fall after this two-month reporting window.

3. **Scenario:** The sales top-down and bottom-up checks both use the same market-size estimate and survey interest. Is their agreement independent validation?
   **Expected behavior:** No. Record shared evidence and seek a distinct comparison such as observed cohort conversion or comparable launches. Without it, disclose a dependent cross-check.

4. **Transfer request:** Apply chapter 27 to our new product: first determine whether available history supports a model or only an estimate, defend proxy inputs, calibrate across comparable mature products, separate trials from repeat units, preserve 24-month trial totals, and save a forecast/scoring record.
   **Expected artifacts:** Return an intake/routing record, proxy/source register, reference-product calibration and held-out errors, monthly trial and total-unit tables, Y1/Y2/tail reconciliation, sensitivity table, missing-evidence priorities and dated scoring plan. State which methods were executed and which remain proposed.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
