# Chapter 15 workshop: from lesson to decision

## Explain the mechanism

A pretrained forecasting model transfers patterns learned elsewhere. Zero-shot means no task-specific fitting in this workflow; it does not mean no relevant prior training or guaranteed superiority. Evaluation still needs a credible future test.

## Work through the arithmetic

For actuals [10,12], a model median [9,13] has MAE 1. A baseline [10,10] also has MAE 1. If the model’s nominal 80% intervals cover both values, the observed coverage is 2/2=100%, which is not enough to establish 80% calibration.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace the demonstration series and origin list, preserving past-only context. Keep the checkpoint pin from the source unless deliberately changing the experiment. Run the retrieval-contamination toy separately; it has a different method and should never be mixed into model scores.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: Which checkpoint and revision will be fixed? When did the data become public? Are private later data available? What context, horizon and baseline are appropriate? Can the environment run the actual dependency?

## Interpret the actual lesson outputs

The source uses actual pinned Chronos inference. Its small evaluation consists of two series and eight cases and can legitimately lose to its baseline. The separate nearest-neighbor contamination illustration inserts test pairs deliberately; it neither measures nor diagnoses Chronos training overlap.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,forecast,q10,q50,q90 (one column per requested quantile)`.
- `summary.json`: `checkpoint,model_id,revision,download_warning,origins,per_origin,engine_baselines,test_mae,test_coverage,mean_latency_s,quantiles,samples` plus method, interpretation, assumptions, not_done and status.

The tool runs Chronos-T5 zero-shot in a separate worker process (so it can share a session with LightGBM), sampling `samples` paths and reporting the requested `quantiles` at `origins` expanding origins plus the untouched final holdout: median MAE, coverage of the outer quantile band and latency per call. It runs the engine's baseline pool (naive, seasonal naive, drift, equal ensemble) at exactly the same origins and reports both leaderboards side by side, then issues the future forecast from full history. No fine-tuning, no covariates, and no certification that the series was absent from pretraining. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

The [fixture](../../../companion/data/examples/ch15.csv) and [config](../../../companion/configs/ch15.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

A frozen model avoids local fitting leakage but may still have unknown pretraining exposure. A contamination toy is not evidence of contamination in a particular checkpoint. Sample quantiles have Monte Carlo error; few cases cannot establish a broad ranking.

If downloads or the dependency are unavailable, return baseline forecasts and an explicit not-run status for the foundation model. Never substitute a generic smoother and call it Chronos. If overlap is unknown, preserve the uncertainty and prioritize later private data.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,forecast,q10,q50,q90 (one column per requested quantile)`; `summary.json` keys: `checkpoint,model_id,revision,download_warning,origins,per_origin,engine_baselines,test_mae,test_coverage,mean_latency_s,quantiles,samples` plus method, interpretation, assumptions, not_done and status. Report the pretrained model beside the seasonal naive at the same origins; a model that does not beat the seasonal naive on this series has not earned the download.

## Three exercises with worked solutions

### Exercise 1

The baseline beats Chronos on the frozen test. Should a new checkpoint be selected on that same test?

**Worked solution.** No. Report the result; selecting again uses that test as validation and requires a new untouched test.

### Exercise 2

A known pattern resembles training data. Does that prove leakage?

**Worked solution.** No. Similarity alone is not evidence that the exact evaluation future was exposed.

### Exercise 3

Download fails but seasonal-naive runs. What method label belongs on its output?

**Worked solution.** Seasonal naive, with foundation-model execution marked skipped or failed.

## Business-reader application

Use this request with the skill:

> Use chapter 15 to benchmark the pinned foundation model on demand.csv with frozen origins, honest dependency status and matched baseline and interval scores.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Observed-data transfer exercise

A bundled [observed series](../../../companion/data/observed/monthly-temperature.csv) and [matching config](../../../companion/configs/ch15-observed.json) provide a second application after the controlled fixture. Read the [data registry](../../../companion/data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 15 \
  --input companion/data/observed/monthly-temperature.csv \
  --config companion/configs/ch15-observed.json \
  --output companion/applied-runs/ch15-observed-reader
```

Compare the fixed checkpoint with seasonal-naive, preserving a loss even if the foundation model loses. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.
