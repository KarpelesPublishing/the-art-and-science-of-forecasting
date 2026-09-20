# %% [markdown]
# # Chapter 12: The Competition
# A small synthetic panel provides repeated rolling origins and a common test for
# naive, seasonal-naive, trend and combination forecasts. This is not an M-series
# competition reproduction. No algorithm is required to win for the notebook to pass.
# %%
from pathlib import Path
import sys
project=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'companion/src').exists())
sys.path.insert(0,str(project/'companion/src'))
from forecasting_companion.common import *
rng=begin(12); series=np.array([seasonal_series(rng)+rng.normal(0,4,144) for _ in range(30)])
names=['Naive','Seasonal naive','Drift','Ensemble']; errors=np.zeros((30,4,5,12))
# %% [markdown]
# ## The origin defines what is knowable
# Every model receives only values before its origin. The ensemble has fixed equal
# weights; the held-out errors are not used to choose weights.
# %%
for j,y in enumerate(series):
    for k,origin in enumerate([72,84,96,108,120]):
        train=y[:origin]; truth=y[origin:origin+12]
        preds=[np.repeat(train[-1],12),train[-12:],train[-1]+np.arange(1,13)*(train[-1]-train[0])/(len(train)-1)]
        preds.append(np.mean(preds,axis=0))
        for m,pred in enumerate(preds): errors[j,m,k]=abs(truth-pred)
plt.figure()
for name,err in zip(names,errors.mean(axis=(0,2))): plt.plot(range(1,13),err,label=name)
plt.xlabel('Horizon (months)'); plt.ylabel('Mean absolute error'); plt.legend(fontsize=7)
save(12,1,'Compare the same forecast horizons','Thirty synthetic monthly series and five rolling origins. Every method is evaluated against the same future observations.','## Section Three: The Problem of Measuring Accuracy')
# %%
origin_errors=errors.mean(axis=(0,3))
relative_errors=100*(origin_errors/origin_errors[1]-1)
plt.figure()
for i,name in enumerate(names):
    if i != 1: plt.plot([72,84,96,108,120],relative_errors[i],'o-',label=name)
plt.axhline(0,color='black',ls='--',label='Seasonal-naive reference')
plt.xlabel('Origin (month index)'); plt.ylabel('MAE difference from reference (%)'); plt.legend(fontsize=6)
save(12,2,'How large is the gap to the benchmark?','At each origin, average errors cover the same thirty synthetic series and twelve horizons. Values are 100 × (method MAE / seasonal-naive MAE − 1); zero ties the benchmark and negative is better. Stable ranks can still hide changing error gaps.','## Section Four: A Systematic Account of What the Competitions Established')
# %%
plt.figure(); plt.boxplot(list(errors.mean(axis=(2,3)).T),tick_labels=['Naive','Seasonal','Drift','Ensemble']); plt.ylabel('Per-series MAE')
save(12,3,'Combination is a candidate, not a guarantee','Per-series mean errors across the same rolling origins. Equal-weight combinations can be robust without beating every constituent.','## Section Five: What This Means for Your Organization')
assert np.isfinite(errors).all()
print(dict(zip(names,errors.mean(axis=(0,2,3)))))
# %% [markdown]
# ## RMSE and MASE answer different questions
# Squaring errors emphasizes large misses. MASE instead divides each held-out
# absolute error by that series' training seasonal-naive scale, recomputed inside
# every origin. Never estimate the scale from future observations. Constant
# seasonal histories have undefined MASE and would be reported rather than hidden.
# %%
scales = np.empty((len(series), 5))
for j, values in enumerate(series):
    for k, origin in enumerate([72,84,96,108,120]):
        training = values[:origin]
        scales[j,k] = np.mean(np.abs(training[12:]-training[:-12]))
assert np.all(scales > 0), 'This fixture requires positive seasonal scaling errors.'
scaled_errors = errors/scales[:,None,:,None]
metrics = {name: {'MAE': float(errors[:,i].mean()),
                  'RMSE': float(np.sqrt(np.mean(errors[:,i]**2))),
                  'seasonal_MASE': float(scaled_errors[:,i].mean())}
           for i, name in enumerate(names)}
print(metrics)
assert all(row['RMSE'] >= row['MAE']-1e-12 for row in metrics.values())
# %% [markdown]
# ## Limits and exercise
# MASE divides by an in-sample naive error scale, so MASE=1 does not mean tied with
# the held-out naive forecast. Try series without seasonality or with level breaks.
# Formal model confidence sets and dependence-aware significance tests need a
# larger, appropriately structured evaluation than a single convenient panel.
# %% [markdown]
# <!-- APPLIED-WORKSHOP-START -->
# ## Guided application workshop
# The sections below come from the chapter skill: the mechanism, the arithmetic, how to adapt the lesson to your data, exercises with worked solutions, and the exact contract of the applied tool.
# %% [markdown]
# ## Input contract and format example
# CSV timestamp,target and optional series_id; unique timestamp per series with regular frequency. Config horizon,season,origins and aggregation weights. Every compared method must face the same eligible targets. The rolling comparison needs 2 seasons + 4 horizons of history (72 monthly points for a 12-month horizon, 48 for six months, 36 for three); with less, the tool returns a provisional persistence baseline and says how many points are missing.
#
# Minimal **format illustration**, not sufficient training data:
#
# ```csv
# series_id,timestamp,target
# A,2025-01-01,100
# A,2025-02-01,104
# B,2025-01-01,20
# ```
#
# ## Explain the mechanism
#
# A benchmark is an experimental design. Common target dates, equal information and frozen selection rules matter as much as the error formula. An ensemble is a candidate; averaging is not a guarantee of improvement.
#
# ## Work through the arithmetic
#
# Actuals [10,20] with forecasts [12,16] give errors [2,4], MAE=3 and RMSE=sqrt(10)=3.162. If the training seasonal-naive scale is 2, MASE=1.5. That 1.5 does not compare directly with a held-out naive forecast unless its actual held-out loss is separately calculated.
#
# ## Adapt the lesson to reader data
#
# Replace the generated panel with sorted grouped series. Recompute each scale inside its training window. Keep the lesson’s per-horizon error array structure or an equivalent long table; averaging too early hides cases and makes fair alignment hard to audit.
#
# For this chapter, settle these questions before fitting: What horizon and loss match the decision? Which series and origins define deployment? Are weights business volume weights or equal-series weights? Is there an untouched final test?
#
# ## Interpret the actual lesson outputs
#
# The relative-error chart uses 100×(method MAE/seasonal-naive MAE-1), so negative is better and zero ties that origin’s baseline. The boxplot shows per-series heterogeneity. These synthetic seasonal series are not an M-competition reproduction.
#
# The current applied adapter adds a separately inspectable numerical result:
#
# - `results.csv`: `timestamp,forecast,model,empirical_q10,empirical_q50,empirical_q90,conformal_lower,conformal_upper,band_lower,band_upper`.
# - `summary.json`: `profile,gaps_filled,pool,selected,criterion,baseline,forced_baseline,robustness,unavailable,conformal,conformal_test_coverage,selected_by_bucket,band_method,band_note,conformal_m,conformal_level_effective,transform,specification,origins,horizon,season,leaderboard,validation,validation_predictions,test_mae,test_interval_coverage,skipped,executed,evaluation,intervals` plus method, interpretation, assumptions, not_done and status.
#
# Each series independently runs the companion engine with the `full` pool: the chapter 4 smoothing family with an AICc-selected ETS form, Theta, STL+ETS, the chapter 6 ARIMA family with diagnostic differencing, LightGBM on lags when history allows, a median of the top three, an equal ensemble, and the naive, seasonal-naive and drift benchmarks. Validation includes MAE, RMSE and training-scaled MASE at up to five origins plus a final untouched holdout; interval coverage is measured for every model that produces intervals. No pooled business-weight ranking or formal significance test is produced. Short valid histories return a provisional naive baseline and optional seasonal-naive scenario; these are not validated model comparisons.
#
# ## Decide what the evidence supports
#
# MAE is unit-dependent; RMSE emphasizes large misses. Seasonal MASE divides by training seasonal-naive absolute differences, not held-out naive error. Zero scale makes MASE undefined. Overlapping origins and related series weaken naive significance calculations.
#
# If histories differ, report the common eligible evaluation subset and separately report deployment coverage. If MASE scale is zero, flag it and use an unscaled metric rather than adding an arbitrary epsilon. With few origins, report descriptive results without broad superiority claims.
#
# The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,forecast,model,empirical_q10,empirical_q50,empirical_q90,conformal_lower,conformal_upper,band_lower,band_upper`; `summary.json` keys: `profile,gaps_filled,pool,selected,criterion,baseline,forced_baseline,robustness,unavailable,conformal,conformal_test_coverage,selected_by_bucket,band_method,band_note,conformal_m,conformal_level_effective,transform,specification,origins,horizon,season,leaderboard,validation,validation_predictions,test_mae,test_interval_coverage,skipped,executed,evaluation,intervals` plus method, interpretation, assumptions, not_done and status. Return prediction-level records, per-series/per-origin/per-horizon losses, weighting rules, coverage and failed-fit counts, baseline comparisons and final-selection separation.
#
# ## Three exercises with worked solutions
#
# ### Exercise 1
#
# Method MAE=8, baseline MAE=10: relative gap?
#
# **Worked solution.** 100×(8/10-1)=-20%, a 20% lower MAE on those matched cases.
#
# ### Exercise 2
#
# Training seasonal-naive error scale is zero. What is MASE?
#
# **Worked solution.** Undefined, not zero. Flag it and report an appropriate unscaled metric.
#
# ### Exercise 3
#
# Weights are tuned using the final test. Is it still a final test?
#
# **Worked solution.** No. It became selection data; evaluate the frozen combination on later untouched cases.
#
# ## Business-reader application
#
# Use this request with the skill:
#
# > Use chapter 12 to build a common rolling-origin benchmark for panel.csv, retain prediction-level records and compare methods under explicit business weights.
#
# ## Observed-data transfer exercise
#
# A bundled [observed series](../data/observed/monthly-temperature.csv) and [matching config](../configs/ch12-observed.json) provide a second application after the controlled fixture. Read the [data registry](../data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.
#
# ```bash
# companion/.venv/bin/python companion/scripts/run.py apply --chapter 12 \
#   --input companion/data/observed/monthly-temperature.csv \
#   --config companion/configs/ch12-observed.json \
#   --output companion/applied-runs/ch12-observed-reader
# ```
#
# Explain why a ranking on this one observed series does not establish an across-industry ranking. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.
#
# Shared rules for data replacement, provenance, output folders and reading `status`: [conventions.md](../../forecasting-skills/all-chapters-forecasting/references/conventions.md).
# %% [markdown]
# ## Apply this chapter to your own data
#
# The two paths below are the only things to change: point `INPUT_PATH` at a file with the
# columns in the input contract above and `CONFIG_PATH` at a copy of the shipped configuration
# with your `source` and `units`. The call is the same tested function behind `run.py apply`.
# The printed digest shows what ran, its status, the interpretation, the assumptions and the
# `not_done` list; the full summary is saved beside the table. A validation error is a reason to
# inspect the data, not to fill gaps with invented observations. Shared rules for provenance,
# output folders and reading `status` are in the Complete Forecasting Skill's conventions reference.
# %%
from forecasting_companion.applied.methods import analyze as analyze_chapter
from forecasting_companion.applied.core import clean_json, summarize, preview
import pandas as pd
import json, os
project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists())
INPUT_PATH = project_path / 'companion/data/examples/ch12.csv'      # replace with your file
CONFIG_PATH = project_path / 'companion/configs/ch12.json'            # replace with your configuration
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = pd.read_csv(INPUT_PATH)
workshop_table, workshop_summary = analyze_chapter(12, workshop_input, workshop_config)
print(summarize(workshop_summary, workshop_table))
print()
print(preview(workshop_table))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', project_path / 'companion')) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch12-workshop-results.csv', index=False)
_ = (workshop_output/'ch12-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\n')
# %% [markdown]
# ## The same workflow on observed data
#
# A second run on a bundled public-domain series documented in `data/registry.json` (a revised
# historical snapshot, not an archived real-time vintage). The earlier time cuts prevent fitting
# on held-out outcomes; they do not undo revisions made before the snapshot was published.
# Compare this digest with the controlled case above: a method need not win to be useful, and
# the winner on synthetic data has no claim on observed data.
# %%
observed_input = pd.read_csv(project_path/'companion/data/observed/monthly-temperature.csv')
observed_config = json.loads((project_path/'companion/configs/ch12-observed.json').read_text())
observed_table, observed_summary = analyze_chapter(12, observed_input, observed_config)
print('Observed-data source:', observed_config['source'])
print(summarize(observed_summary, observed_table))
print()
print(preview(observed_table))
observed_table.to_csv(workshop_output/'ch12-observed-results.csv', index=False)
_ = (workshop_output/'ch12-observed-summary.json').write_text(json.dumps(clean_json(observed_summary), indent=2)+'\n')
# %% [markdown]
# ## Self-check
#
# The three questions a good forecaster asks in this situation. A bad answer to any one of them is a reason to stop and fix the work before reporting.
#
# 1. **Does every method face the same origins, horizons and actuals, including the baseline?**
#    A bad answer looks like this: A comparison where one method saw more data is not a comparison.
#
# 2. **Did the selected method beat seasonal naive at most origins, or only on average?**
#    A bad answer looks like this: A method that wins on average because of one origin loses in production.
#
# 3. **Was the final holdout used once, after selection, and never before?**
#    A bad answer looks like this: A holdout consulted during selection is training data with another name.
#
# Shared rules for every chapter: [conventions.md](../../forecasting-skills/all-chapters-forecasting/references/conventions.md).
