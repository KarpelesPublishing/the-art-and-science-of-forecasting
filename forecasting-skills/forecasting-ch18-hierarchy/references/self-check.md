# Self-check: chapter 18, Hierarchies

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **Do the node histories add up before any forecasting, within a stated tolerance?**
   A bad answer looks like this: A hierarchy that does not reconcile in the past will not reconcile in the future.

2. **Did reconciliation improve accuracy on the holdout, or only enforce coherence?**
   A bad answer looks like this: Coherent and worse is a possible outcome; the leaderboard has to be shown.

3. **Where did the error covariance for MinT come from, and how many errors per node?**
   A bad answer looks like this: A covariance estimated from a few forecast errors, or from differenced actuals, is not the forecast-error covariance.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
