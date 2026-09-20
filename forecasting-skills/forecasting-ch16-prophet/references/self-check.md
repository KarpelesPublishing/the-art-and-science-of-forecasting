# Self-check: chapter 16, Calendar effects

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **Are the events and holidays known for the forecast period, with their dates and windows?**
   A bad answer looks like this: An event calendar that stops at the last observation cannot help the forecast.

2. **Does the model with events beat the same model without them at the earlier origins?**
   A bad answer looks like this: Adding a regressor that does not improve validation accuracy adds parameters, not information.

3. **Was the changepoint flexibility chosen on earlier origins, and is the band's coverage measured?**
   A bad answer looks like this: Prophet's nominal band is not a measured one; quote the measured coverage.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
