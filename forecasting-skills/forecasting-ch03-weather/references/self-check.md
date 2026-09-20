# Self-check: chapter 3, Structure before forecasting

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **Which pattern is stable enough to project: the seasonal shape, the trend, or neither?**
   A bad answer looks like this: Projecting a component whose vintage-to-vintage revisions are as large as its size is projecting noise.

2. **How sensitive is the path to its starting point, and how far ahead does that sensitivity matter?**
   A bad answer looks like this: A forecast horizon longer than the system's predictability limit is a scenario, whatever the model says.

3. **Did the decomposition use only information available at the origin?**
   A bad answer looks like this: A full-series STL fed into a backtest leaks the future into every feature.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
