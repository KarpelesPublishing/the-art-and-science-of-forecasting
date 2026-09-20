# Self-check: chapter 13, Pooled tree models

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **Is every feature known at the forecast origin for the whole horizon, including prices and promotions?**
   A bad answer looks like this: A model fed next month's price forecasts a world where next month's price is already known.

2. **Does the ablation show which feature groups earn their place on the holdout?**
   A bad answer looks like this: A feature that does not help on unseen data is complexity paid for without return.

3. **Are the explanations read as descriptions of the model, not as causal effects?**
   A bad answer looks like this: Treating a contribution value as the lift a promotion would cause is the chapter's central warning.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
