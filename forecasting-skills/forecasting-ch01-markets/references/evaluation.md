# Evaluation scenarios: chapter 1

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 277 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** OHLC is 100,99,98,101. Is it valid?
   **Expected behavior:** No: the reported high 99 is below open 100 and close 101. Correct the record from source or exclude it with a reason.

2. **Scenario:** Last close is 80, next actual 77. What is persistence absolute error?
   **Expected behavior:** The prediction is 80 and absolute error is 3 price units.

3. **Scenario:** A momentum lookback was chosen after comparing the last month. Can that month remain final test?
   **Expected behavior:** No. It is now selection data; evaluate on later untouched observations.

4. **Transfer request:** Use chapter 1 to audit prices.csv and compare a prespecified momentum rule with persistence on later matched observations. Separate prediction error from trading profitability.
   **Expected artifacts:** Return cleaned price checks, dated persistence and candidate predictions, matched-horizon error comparison, timing assumptions and costs excluded from the analysis.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
