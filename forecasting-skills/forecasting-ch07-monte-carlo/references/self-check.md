# Self-check: chapter 7, Simulation

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **Are the input distributions and their dependence stated, and where did each come from?**
   A bad answer looks like this: A Monte Carlo over invented inputs produces a precise picture of the assumptions, not of the world.

2. **Is the Monte Carlo error small enough that another seed would give the same answer?**
   A bad answer looks like this: A quantile that moves with the seed has not converged, whatever the sample size sounds like.

3. **Which single input moves the answer most, and is that the one with the weakest evidence?**
   A bad answer looks like this: A tornado that is never drawn hides the input that decides the result.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
