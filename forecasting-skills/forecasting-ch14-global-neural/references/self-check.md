# Self-check: chapter 14, Global models for many series

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **Were the held-out entities excluded from training, and does the model transfer to them?**
   A bad answer looks like this: Scoring on entities the model has seen tests memory, not transfer.

2. **Is the nominal band's coverage measured on the held-out entities?**
   A bad answer looks like this: A quantile model whose coverage is never checked is a point forecast with decoration.

3. **Do the local baselines lose to the global model on the same entities and horizons?**
   A bad answer looks like this: A global model that does not beat per-series seasonal naive is expensive noise.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
