# Self-check: chapter 4, Exponential smoothing

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **How quickly should this series forget, and does the data or my preference say so?**
   A bad answer looks like this: A smoothing parameter chosen because the fitted line looks smooth is a preference, not evidence.

2. **Does the seasonal pattern survive two complete cycles of history, and is it additive or multiplicative?**
   A bad answer looks like this: Multiplicative seasonality forced on a series with zeros, or annual seasonality fitted to eighteen months, is a fit that cannot be trusted.

3. **Did the damped trend need to be tested, and what does the holdout say about the trend continuing?**
   A bad answer looks like this: An undamped trend projected twelve steps is the chapter's most frequent overreach.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
