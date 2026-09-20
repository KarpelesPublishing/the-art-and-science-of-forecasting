# %% [markdown]
# # Chapter 24: The Anomaly
# A level shift breaks a stable process. Use only past observations to produce
# forecasts and CUSUM alarms; compare adaptation policies on the same stream.
# %%
from pathlib import Path
import sys
project=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'companion/src').exists())
sys.path.insert(0,str(project/'companion/src'))
from forecasting_companion.common import *
rng=begin(24); y=np.r_[rng.normal(50,2,100),rng.normal(65,2,100)]; origin=50
baseline=y[:origin].mean(); sd=y[:origin].std(ddof=1)
# %%
plt.figure(); plt.plot(y,label='Observed'); plt.axhline(baseline,label='Frozen forecast',ls='--'); plt.axvline(100,color='.5',ls=':'); plt.xlabel('Period'); plt.ylabel('Units'); plt.legend(fontsize=7)
save(24,1,'The old model keeps predicting the old world','Synthetic series with a level increase at period 100. The frozen model is estimated only on the first fifty observations.','## Section One: The Dashboard Turns Red')
# %%
stat=[]; s=0.; alarms=[]; threshold=8.
for t in range(origin,len(y)):
    s=max(0,s+(y[t]-baseline)/sd-.5); stat.append(s)
    if s>threshold: alarms.append(t); s=0
plt.figure()
# Values are recorded BEFORE reset. Break lines after alarms so resets are visible.
plot_time=[]; plot_stat=[]
for period,value in zip(range(origin,len(y)),stat):
    plot_time.append(period); plot_stat.append(value)
    if period in alarms: plot_time.append(period+.01); plot_stat.append(np.nan)
plt.plot(plot_time,plot_stat,label='Before-reset statistic',lw=.8)
plt.scatter(alarms,[stat[t-origin] for t in alarms],marker='x',s=12,label='Alarm, then reset')
plt.axhline(threshold,ls='--',color='.4',label='Threshold'); plt.axvline(100,color='.5',ls=':')
plt.xlabel('Period'); plt.ylabel('One-sided CUSUM'); plt.legend(fontsize=6)
save(24,2,'An alarm accumulates evidence','Online standardized residual CUSUM on the synthetic stream. Values are recorded before resetting to zero after each marked alarm; connecting lines break at resets. Each alarm is available only after its observation; the threshold is illustrative.','## Section Three: Building for Structural Breaks')
# %%
predictions={'Frozen':np.repeat(baseline,150),'Rolling 20':np.array([y[t-20:t].mean() for t in range(50,200)]),'Expanding':np.array([y[:t].mean() for t in range(50,200)])}
plt.figure()
for name,pred in predictions.items():
    err=abs(pred-y[50:]); rolling=np.convolve(err,np.ones(10)/10,mode='valid'); plt.plot(np.arange(59,200),rolling,label=name)
plt.axvline(100,color='.5',ls=':'); plt.xlabel('Period'); plt.ylabel('Trailing ten-period MAE'); plt.legend(fontsize=7)
save(24,3,'Adaptation policies have different costs','Synthetic one-step forecasts computed before each observation. Rolling windows adapt faster here but discard data that could help in stable periods.','## Section Four: The Full Methodology')
print('Pre-break false alarms:',sum(t<100 for t in alarms),'first post-break delay:',min(t for t in alarms if t>=100)-100)
# %% [markdown]
# ## Limits and exercise
# Replace the abrupt shift with slow drift or a temporary outlier. Recalibrate
# thresholds using separate stable data before operational use. L1 penalizes the
# sum of absolute coefficients; it is not the count of nonzero coefficients.
# %% [markdown]
# <!-- APPLIED-WORKSHOP-START -->
# ## Guided application workshop
# The sections below connect the controlled figures to a complete applied input/output workflow.
# %% [markdown]
# # Chapter 24 workshop: from lesson to decision
#
# ## Explain the mechanism
#
# A detector accumulates evidence that the existing model no longer fits. It does not identify the cause. Operational value depends on what happens after an alarm and on the costs of both needless changes and delayed adaptation.
#
# ## Work through the arithmetic
#
# For k=.5, threshold h=3 and standardized residuals [1,2,2], CUSUM values before reset are [.5,2,3.5]. The third observation triggers an alarm; the next update starts from zero under a resetting policy. Drawing a continuous line from 3.5 without showing the reset can misrepresent the detector.
#
# Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.
#
# ## Adapt the lesson to reader data
#
# Replace the generated series while preserving the initial training and subsequent monitoring split. Plot alarm markers and reset-aware paths. The original lesson used an illustrative threshold and no alarm-triggered override; the applied interface must explicitly report which calibration and policies it actually runs.
#
# Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.
#
# For this chapter, settle these questions before fitting: What stable period can calibrate the detector? What false-alarm burden is tolerable? Which errors are available online? What action follows the first alarm? Could the anomaly be bad data?
#
# ## Interpret the actual lesson outputs
#
# The original controlled level shift occurs at period 100. Its frozen/rolling/expanding curves use past observations. A resetting detector can produce many later alarms, so the first post-break delay and the action after that alarm matter more than raw alarm count alone.
#
# The current applied adapter adds a separately inspectable numerical result:
#
# - `results.csv`: `timestamp,actual,frozen,rolling,expanding,adaptive,cusum_before_reset,alarm,rolling_mean,rolling_var,mean_shift_sd,variance_ratio,segment_id`.
# - `summary.json`: `changepoints,changepoint_positions,best_split,threshold,alarm_count,alarms,detection,drift,mae,best_policy,calibration_size` plus method, interpretation, assumptions, not_done and status.
#
# The tool dates mean shifts by binary segmentation with a Gaussian cost and a penalty of three times log(n) times a robust noise variance (about a one percent false split rate on white noise), reports the strongest single split with its Welch t statistic, runs a two-sided CUSUM alarm calibrated by simulation to a five percent false-alarm probability over the monitored span, tracks rolling mean and variance against the calibration window as standardised drift metrics, and scores four adaptation policies after the calibration window: frozen calibration mean, rolling mean over `rolling_window`, expanding mean, and an alarm-adaptive mean that restarts at each alarm. Detection delay is the gap between the first dated changepoint and the first alarm after it. Variance-only changes appear in the drift metrics but are not dated. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.
#
# The [fixture](../data/examples/ch24.csv) and [config](../configs/ch24.json) match the current interface. Run the `apply` command in the [skill entrypoint](../../forecasting-skills/forecasting-ch24-structural-breaks/SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.
#
# ## Decide what the evidence supports
#
# Repeated alarms after resets are not independent discoveries. An iid-normal calibration is conditional on that null model; serial correlation changes false-alarm behavior. Fast adaptation can overreact to temporary outliers. Threshold performance and forecast-policy performance are different outcomes.
#
# Without a plausible stable calibration period, report exploratory alarms with no controlled false-alarm claim. If no response policy was implemented, state that monitoring alone was evaluated. Missing observations require an explicit skip/elapsed-time treatment.
#
# The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,actual,frozen,rolling,expanding,adaptive,cusum_before_reset,alarm,rolling_mean,rolling_var,mean_shift_sd,variance_ratio,segment_id`; `summary.json` keys: `changepoints,changepoint_positions,best_split,threshold,alarm_count,alarms,detection,drift,mae,best_policy,calibration_size` plus method, interpretation, assumptions, not_done and status. Quote the detection delay with the alarm count; a monitor that fires eleven times after one break has not found eleven breaks, it has kept a stale reference mean.
#
# ## Three exercises with worked solutions
#
# ### Exercise 1
#
# S=1,z=-2,k=.5: next S?
#
# **Worked solution.** max(0,1-2-.5)=0.
#
# ### Exercise 2
#
# An alarm at period 50 leads to refitting including y50. When can the revised forecast first be available?
#
# **Worked solution.** After observing period 50, for period 51 or later; never retroactively for period 50.
#
# ### Exercise 3
#
# A threshold was simulated under iid normal noise. Is its false-alarm rate guaranteed under autocorrelated demand?
#
# **Worked solution.** No. Validate under an appropriate dependent null or disclose the calibration mismatch.
#
# ## Business-reader application
#
# Use this request with the skill:
#
# > Apply chapter 24 to monitored_series.csv, predeclare threshold calibration and post-alarm action, and compare false alarms, delay and forecasting costs honestly.
#
# Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.
#
# ## Observed-data transfer exercise
#
# A bundled [observed series](../data/observed/annual-nile.csv) and [matching config](../configs/ch24-observed.json) provide a second application after the controlled fixture. Read the [data registry](../data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.
#
# ```bash
# companion/.venv/bin/python companion/scripts/run.py apply --chapter 24 \
#   --input companion/data/observed/annual-nile.csv \
#   --config companion/configs/ch24-observed.json \
#   --output companion/applied-runs/ch24-observed-reader
# ```
#
# Inspect first and repeated alarms, and distinguish a historical regime-change signal from evidence of its cause. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.
# %% [markdown]
# ## Configure and run the applied case
#
# The input file and JSON below are the only entry-point changes needed to try another
# case with the same schema. Keep the original examples for comparison. Supply source
# and units in the configuration; resolve missing periods rather than silently filling
# unknown observations with zeros. These calculations call the same tested functions
# as the `run.py apply` command. A failed validation is a reason to inspect the data,
# not to replace it with invented observations.
#
# The default input here is a **seeded synthetic schema example**, separate from any
# observed-data application below. Read the summary before interpreting its results.
# %%
from forecasting_companion.applied.methods import analyze as analyze_chapter
from forecasting_companion.applied.core import clean_json
import pandas as pd
import json, os
INPUT_PATH = project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists()) / 'companion/data/examples/ch24.csv'
CONFIG_PATH = project_path.parents[2] / 'configs/ch24.json'
# Input paths are explicit and may be replaced with reader-supplied files.
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = pd.read_csv(INPUT_PATH)
workshop_table, workshop_summary = analyze_chapter(24, workshop_input, workshop_config)
print(json.dumps(clean_json(workshop_summary), indent=2))
print(workshop_table.head(12).to_string(index=False))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', CONFIG_PATH.parents[1])) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch24-workshop-results.csv', index=False)
(workshop_output/'ch24-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\n')
# %% [markdown]
# ## Apply the same workflow to observed data
#
# This second case uses a bundled public-domain historical dataset documented in
# `data/registry.json`. It is a revised snapshot, not an archived real-time vintage.
# The earlier time cuts prevent fitting on held-out outcomes; they do not undo
# revisions that may have occurred before the snapshot was published. Compare the
# actual output below with the controlled case. A method need not win to be useful.
# The source, transformation and units are in the configuration and registry.
# %%
observed_input = pd.read_csv(CONFIG_PATH.parents[1]/'data/observed/annual-nile.csv')
observed_config = json.loads((CONFIG_PATH.parent/'ch24-observed.json').read_text())
observed_table, observed_summary = analyze_chapter(24, observed_input, observed_config)
print('Observed-data source:', observed_config['source'])
print(json.dumps(clean_json(observed_summary), indent=2))
print(observed_table.head(12).to_string(index=False))
observed_table.to_csv(workshop_output/'ch24-observed-results.csv', index=False)
(workshop_output/'ch24-observed-summary.json').write_text(json.dumps(clean_json(observed_summary), indent=2)+'\n')
# %% [markdown]
# ## Read the result as a decision record
#
# Start with the summary’s **interpretation**, then examine its numerical evidence.
# Distinguish what was fitted, what was supplied, and what remains unidentified.
# The results table is the calculation; it is not permission to act. Explain which
# assumption would most change the answer and what new evidence would test it.
# For a live forecast, set an outcome date and keep the original result for scoring.
#
# The exercises and worked solutions above test interpretation, calculation, and
# adaptation. Re-run a changed assumption and compare the actual output; do not
# reuse numbers from the book when your input or horizon changes.
