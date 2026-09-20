# Chapter 17 workshop: from lesson to decision

## Explain the mechanism

A probabilistic forecast is judged on both honesty and usefulness. Coverage measures how often intervals contain actuals; sharpness measures concentration. Proper interval scores balance narrowness against costly misses.

## Work through the arithmetic

For an 80% interval [8,12], alpha=.2 and actual 14, interval score is (12-8)+(2/.2)(14-12)=4+20=24. If actual is 10, score is 4. With 80 calibration residuals and alpha=.1, corrected rank is ceil(81×.9)=73, so use the 73rd ordered residual.

Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.

## Adapt the lesson to reader data

Replace forecast/actual arrays with timestamp-aligned reader forecasts. Preserve the nominal level rather than inferring it from observed coverage. For calibration, replace the ordered-series block with training, calibration and later test records that respect actual data availability.

Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.

For this chapter, settle these questions before fitting: What nominal coverage or quantiles are claimed? Were forecasts issued before outcomes? What horizons and groups need coverage? Is a separate calibration period available?

## Interpret the actual lesson outputs

The fan chart shows marginal quantiles from assumed random-walk paths. The coverage experiment uses independent normal outcomes. The later AR calibration lesson explicitly retains serial dependence and therefore makes no exchangeable finite-sample guarantee.

The current applied adapter adds a separately inspectable numerical result:

- `results.csv`: `timestamp,origin,horizon,actual,forecast,split_lower,split_upper,adaptive_lower,adaptive_upper,alpha_t,covered_split,covered_adaptive,interval_score_split,interval_score_adaptive[,model_lower,model_upper]`.
- `summary.json`: `selected,alpha,gamma,calibration_rows,test_rows,radius,coverage,mean_width,interval_score,pinball,by_horizon,guarantee,calibration_block,test_block` plus method, interpretation, assumptions, not_done and status.

On a plain series the tool selects a model with the companion engine on history before the calibration block, freezes that specification, refits it at every calibration origin to collect residuals by horizon step, and builds split-conformal intervals at level 1-`alpha` using the finite-sample rank ceil((m+1)(1-alpha)). It then runs the adaptive conformal update (alpha_t moves by `gamma` after each miss or cover) through the test block. Both intervals are scored on the test block: empirical coverage, mean width, interval score and pinball loss, per horizon step and pooled, and compared with the model's own nominal 80 percent band when one exists. If the engine selected a combination, the best atomic model is used and the summary says so. The split guarantee is marginal under exchangeability; the adaptive guarantee is long-run; neither is conditional coverage at a given date. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.

The [fixture](../../../companion/data/examples/ch17.csv) and [config](../../../companion/configs/ch17.json) match the current interface. Run the `apply` command in the [skill entrypoint](../SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.

## Decide what the evidence supports

Arbitrarily wide intervals achieve coverage at the cost of usefulness. Marginal coverage does not imply simultaneous path coverage or groupwise coverage. Exchangeable conformal guarantees do not automatically apply to serially dependent residuals.

With missing actuals, export unscored forecasts and pending evaluation status. With no separate calibration block, do not tune and claim test coverage on the same observations. With only scenario limits, preserve that label and do not compute claimed probability calibration.

The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,origin,horizon,actual,forecast,split_lower,split_upper,adaptive_lower,adaptive_upper,alpha_t,covered_split,covered_adaptive,interval_score_split,interval_score_adaptive[,model_lower,model_upper]`; `summary.json` keys: `selected,alpha,gamma,calibration_rows,test_rows,radius,coverage,mean_width,interval_score,pinball,by_horizon,guarantee,calibration_block,test_block` plus method, interpretation, assumptions, not_done and status. Report coverage and width together and by horizon; quote the test block dates so the reader can see the intervals were checked on data the model never fitted.

## Three exercises with worked solutions

### Exercise 1

90% interval [0,10], actual -2: interval score?

**Worked solution.** Width 10 plus (2/.1)×2=40, total 50.

### Exercise 2

A nominal 90% interval covers 9 of 10 outcomes. Is calibration established?

**Worked solution.** No. Observed coverage is 90% on a very small sample; uncertainty and dependence still matter.

### Exercise 3

Each of twelve monthly intervals has 90% marginal coverage. Is the whole path covered with probability 90%?

**Worked solution.** Not necessarily. Simultaneous path coverage is a different event and depends on the joint distribution.

## Business-reader application

Use this request with the skill:

> Apply chapter 17 to intervals.csv, score coverage and useful width by horizon, and distinguish any empirical recalibration from an unsupported guarantee.

Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.

## Real-data boundary

The [data registry](../../../companion/data/registry.json) and [data notes](../../../companion/data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
