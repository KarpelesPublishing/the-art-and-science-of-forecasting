# Evaluation scenarios: chapter 4

Status: specification and documentation comparison, not executed agent testing.

## Before the upgrade

The entrypoint contained 263 words. Its concise method guidance did not provide the complete schema, worked adaptation, three solved exercises and output interpretation now supplied together. Preserve the existing scientific safeguards; expanding the instructions does not establish forecasting accuracy.

## Acceptance scenarios

1. **Scenario:** Recalculate the SES update with alpha=.8. What changes?
   **Expected behavior:** The level is 116. It reacts more quickly to the shock, but this calculation alone says nothing about future accuracy.

2. **Scenario:** Actuals are 100,120 and forecasts A=110,110, B=100,100. Compare MAE.
   **Expected behavior:** A has MAE (10+10)/2=10; B has (0+20)/2=10. Prefer neither on this score alone; examine the decision costs and further origins.

3. **Scenario:** You receive eighteen monthly observations with three unknown months. May you report annual Holt-Winters as validated?
   **Expected behavior:** No. There are not two complete annual cycles, much less a separate evaluation period. Audit missingness, use an eligible simple baseline and disclose the unsupported seasonal fit.

4. **Transfer request:** Apply chapter 4 to monthly demand.csv for the next six months. Audit gaps and stockouts, compare supported smoothing methods at earlier six-month origins, retain a final holdout, and return the forecast plus a defensible uncertainty statement.
   **Expected artifacts:** Forecast table: timestamp,forecast,model,lower,upper,interval_level,empirical_q10,empirical_q50,empirical_q90. The adapter reports measured interval coverage; include lower/upper and interval_level only if a separate justified interval calculation was performed. Also return a per-origin MAE table, skipped-method reasons, seasonal assumptions and whether uncertainty was calibrated or only scenarized.

## Review procedure

Give a reader or agent the scenario and the skill without the answer key. Check arithmetic, evidence cutoff, unsupported claims and artifact completeness. Record actual outputs and failures separately. Do not turn these expected responses into a claim that a usability or accuracy test has passed.
