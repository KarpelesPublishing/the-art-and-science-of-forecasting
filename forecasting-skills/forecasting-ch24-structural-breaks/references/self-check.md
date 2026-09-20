# Self-check: chapter 24, Structural breaks

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **When did the break happen, and does the changepoint date agree with what the business knows?**
   A bad answer looks like this: A break dated by an algorithm and unexplained by any event deserves suspicion before action.

2. **Which forecasting policy handles the break best on the data after it: frozen, rolling, or adaptive?**
   A bad answer looks like this: Keeping the pre-break model because it validated well before the break is the error the chapter names.

3. **Was the alarm threshold calibrated on stable data, and how many false alarms would it raise?**
   A bad answer looks like this: An alarm that fires every month is silence with extra steps.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
