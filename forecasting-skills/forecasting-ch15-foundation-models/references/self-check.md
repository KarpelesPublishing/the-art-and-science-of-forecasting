# Self-check: chapter 15, Pretrained models

The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.

1. **Which checkpoint and revision ran, and could the training corpus have contained this series?**
   A bad answer looks like this: A benchmark on data the model may have seen during training measures recall.

2. **At identical origins, does the pretrained model beat the local baselines and the tuned engine?**
   A bad answer looks like this: A zero-shot forecast is a candidate like any other; it earns selection or it does not.

3. **What did the run cost in download, latency and memory, and was the reader told before it ran?**
   A bad answer looks like this: A model that downloads a gigabyte without asking is a process failure regardless of accuracy.

Shared rules for every chapter: [conventions.md](../../all-chapters-forecasting/references/conventions.md).
