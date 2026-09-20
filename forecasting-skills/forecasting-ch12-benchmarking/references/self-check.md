# Self-check: chapter 12, Benchmarking methods

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **Does every method face the same origins, horizons and actuals, including the baseline?**
   A bad answer looks like this: A comparison where one method saw more data is not a comparison.

2. **Did the selected method beat seasonal naive at most origins, or only on average?**
   A bad answer looks like this: A method that wins on average because of one origin loses in production.

3. **Was the final holdout used once, after selection, and never before?**
   A bad answer looks like this: A holdout consulted during selection is training data with another name.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
