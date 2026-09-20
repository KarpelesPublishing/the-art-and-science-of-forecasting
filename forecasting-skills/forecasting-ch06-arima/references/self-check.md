# Self-check: chapter 6, ARIMA

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **What differencing did the diagnostics call for, and did I check the differenced series looks stationary?**
   A bad answer looks like this: Orders chosen by fit alone, without the stationarity test, produce models that extrapolate a trend that is not there.

2. **Did the model beat seasonal naive at rolling origins, or only fit the history well?**
   A bad answer looks like this: White residuals are a necessary check, not evidence of forecast accuracy.

3. **If I used regressors, do I know their future values, or did I assume them?**
   A bad answer looks like this: An ARIMAX forecast conditional on regressors nobody has yet is a scenario and must be labelled one.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
