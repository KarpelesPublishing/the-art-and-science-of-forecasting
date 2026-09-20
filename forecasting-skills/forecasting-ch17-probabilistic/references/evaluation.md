# Evaluation scenarios: chapter 17

## Acceptance scenarios

1. **Scenario:** 90% interval [0,10], actual -2: interval score?
   **Expected behavior:** Width 10 plus (2/.1)×2=40, total 50.

2. **Scenario:** A nominal 90% interval covers 9 of 10 outcomes. Is calibration established?
   **Expected behavior:** No. Observed coverage is 90% on a very small sample; uncertainty and dependence still matter.

3. **Scenario:** Each of twelve monthly intervals has 90% marginal coverage. Is the whole path covered with probability 90%?
   **Expected behavior:** Not necessarily. Simultaneous path coverage is a different event and depends on the joint distribution.

4. **Transfer request:** Apply chapter 17 to intervals.csv, score coverage and useful width by horizon, and distinguish any empirical recalibration from an unsupported guarantee.
   **Expected artifacts:** Return nominal and empirical coverage, width, mean/per-case interval scores, sample counts and horizon/group summaries; if adjusted, return calibration cutoff, rank/radius and later-test results.

How to use these scenarios: [conventions.md](../../all-chapters-forecasting/references/conventions.md), Learning mode. Expected behaviour is a specification, not a recorded test result.
