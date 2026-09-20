# Self-check: chapter 5, Filtering a hidden state

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **Is the filtered path or the smoothed path the one the decision needs, and did I mix them?**
   A bad answer looks like this: Reporting the smoothed path as what was known in real time credits the model with hindsight.

2. **Do the innovations look like noise, or is the model missing a component?**
   A bad answer looks like this: Autocorrelated innovations mean the state equations are wrong, not that the noise is large.

3. **How were the noise variances chosen, and would doubling them change the band materially?**
   A bad answer looks like this: Noise variances tuned on the whole series and then quoted as if fixed in advance overstate the band's meaning.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
