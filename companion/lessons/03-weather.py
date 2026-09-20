# %% [markdown]
# # Chapter 3: The Weather That Could Be Computed
# Lorenz dynamics are a small educational example of sensitivity to initial
# conditions, not an operational weather forecast. We also extract a seasonal
# component from synthetic monthly data and inspect its frequency spectrum.
# %%
from pathlib import Path
import sys
project=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'companion/src').exists())
sys.path.insert(0,str(project/'companion/src'))
from forecasting_companion.common import *
from scipy.integrate import solve_ivp
from statsmodels.tsa.seasonal import STL
rng=begin(3)
# %% [markdown]
# ## Deterministic equations, uncertain initial state
# %%
def lorenz(t,s):
    x,y,z=s
    return [10*(y-x),x*(28-z)-y,x*y-8*z/3]
t=np.linspace(0,30,1500)
paths=np.array([solve_ivp(lorenz,[0,30],[1+e,1,1],t_eval=t,rtol=1e-8,atol=1e-10).y[0] for e in [0,.0001,.001,.01]])
fig,axes=plt.subplots(3,1,figsize=(4.3,4.8),sharex=True,sharey=True)
for ax,e,path in zip(axes,[.0001,.001,.01],paths[1:]):
    ax.plot(t,paths[0],color='.6',lw=.7,label='Reference')
    ax.plot(t,path,color='black',ls='--',lw=.8,label=f'Initial change {e}')
    ax.set_ylabel('Lorenz x'); ax.legend()
axes[-1].set_xlabel('Model time')
save(3,1,'Small initial differences become different futures','Each panel compares the same reference with one perturbed initial x on common axes. Numerical Lorenz trajectories; model time is dimensionless, not forecast days.','## II. The ENIAC Run and the Modern Era',fig)
# %%
plt.figure()
for e,path in zip([.0001,.001,.01],paths[1:]): plt.semilogy(t,np.maximum(abs(path-paths[0]),1e-9),label=f'delta={e}')
plt.xlabel('Lead time (model units)'); plt.ylabel('Absolute trajectory difference'); plt.legend(fontsize=7)
save(3,2,'Uncertainty grows with the forecast horizon','Absolute divergence from the reference trajectory. Growth is irregular and bounded by the dynamical system; it is not indefinite exponential growth.','## II. The ENIAC Run and the Modern Era')
# %% [markdown]
# ## Separate trend, seasonality and remainder
# Decomposition uses the full example for description. Forecasting would refit
# it at each origin; full-series components must not leak into validation features.
# %%
y=seasonal_series(rng); fit=STL(y,period=12,robust=True).fit()
fig,axes=plt.subplots(3,1,figsize=(4.3,4),sharex=True)
for ax,values,label in zip(axes,[y,fit.trend,fit.seasonal],['Observed','Trend','Seasonal']): ax.plot(values); ax.set_ylabel(label)
axes[-1].set_xlabel('Month')
save(3,3,'Structure beneath a noisy series','STL decomposition of synthetic monthly observations. Trend and seasonality are estimates, not independently observed causes.','## IV. Time Series Structure as Methodology',fig)
freq=np.fft.rfftfreq(len(y)); power=abs(np.fft.rfft(y-fit.trend))**2
print('Dominant nonzero frequency:',freq[1:][np.argmax(power[1:])])
assert np.allclose(y,fit.trend+fit.seasonal+fit.resid)
# %% [markdown]
# ## Limits and exercise
# Try a different integration tolerance and initial perturbation. Try two seasonal
# periods and compare STL with MSTL. X-13 and regime-switching models are extensions
# requiring additional assumptions; weather-scale assimilation is outside this toy.
# Wold's moving-average component contains predictable past innovations; only
# innovations not yet observed are unpredictable under its assumptions.
# %% [markdown]
# <!-- APPLIED-WORKSHOP-START -->
# ## Guided application workshop
# The sections below connect the controlled figures to a complete applied input/output workflow.
# %% [markdown]
# # Chapter 3 workshop: from lesson to decision
#
# ## Explain the mechanism
#
# Deterministic equations can be sensitive to uncertain starting conditions. Business decomposition asks a related but distinct question: what slowly changing and repeating patterns summarize observations? Neither computation removes uncertainty about whether those patterns persist.
#
# ## Work through the arithmetic
#
# If a monthly observation is 120, estimated trend is 100 and seasonal component is 15, the remainder is 5. A spectral frequency 1/12 cycles per month corresponds to a 12-month period. Frequency is reciprocal period, not the number of months itself.
#
# Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.
#
# ## Adapt the lesson to reader data
#
# Replace seasonal_series in the STL block with the regular user series and update period. Leave Lorenz simulation separate from that business analysis. If using decomposition features in a model, move the STL fit inside the historical-origin loop rather than decomposing once before splitting.
#
# Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.
#
# For this chapter, settle these questions before fitting: What interval is sampled? Which seasonal periods are physically or commercially plausible? Is the goal descriptive decomposition or future forecasting? Are current state estimates uncertain?
#
# ## Interpret the actual lesson outputs
#
# The Lorenz panels compare initial perturbations against the same reference with shared axes. Their horizontal units are dimensionless. The STL reconstruction assertion checks arithmetic, not forecast quality; the printed dominant frequency describes the controlled series.
#
# The current applied adapter adds a separately inspectable numerical result:
#
# - `results.csv`: `timestamp,observed,trend,seasonal,remainder`.
# - `summary.json`: inspect `max_trend_revision`.
#
# STL is descriptive. At least three seasonal cycles are required. The adapter refits an earlier vintage and reports the maximum historical trend revision; it does not issue a weather or business forecast.
#
# The [fixture](../data/examples/ch03.csv) and [config](../configs/ch03.json) match the current interface. Run the `apply` command in the [skill entrypoint](../../forecasting-skills/forecasting-ch03-weather/SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.
#
# ## Decide what the evidence supports
#
# A spectral peak may reflect trend, aliasing or limited sample length; detrend and inspect calendar plausibility. Estimated components are not observed causes. Lorenz trajectories do not specify a calibrated business prediction interval.
#
# With irregular sampling, first decide whether calendar aggregation is defensible; do not run a regular-grid FFT uncritically. With too few cycles, use plots and a simple baseline and mark seasonal decomposition provisional.
#
# The applied deliverable must make these items inspectable: Return the calendar audit, chosen period and rationale, decomposition table, reconstruction error, and any origin-safe baseline comparison. For dynamics report initial-state and numerical-tolerance assumptions separately.
#
# ## Three exercises with worked solutions
#
# ### Exercise 1
#
# Frequency is .25 cycles per quarter. What is the period?
#
# **Worked solution.** Four quarters, because 1/.25=4.
#
# ### Exercise 2
#
# Can a smoother using next December’s value construct a forecast for this June?
#
# **Worked solution.** No. Full-sample decomposition leaks future observations; refit at June’s cutoff.
#
# ### Exercise 3
#
# A changed integration tolerance produces nearly identical short trajectories. Has initial uncertainty vanished?
#
# **Worked solution.** No. That checks numerical stability locally; uncertainty in the true starting state remains.
#
# ## Business-reader application
#
# Use this request with the skill:
#
# > Use chapter 3 to audit the seasonality of demand.csv and explain which components are retrospective and which can safely inform future forecasts.
#
# Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.
#
# ## Observed-data transfer exercise
#
# A bundled [observed series](../data/observed/monthly-temperature.csv) and [matching config](../configs/ch03-observed.json) provide a second application after the controlled fixture. Read the [data registry](../data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.
#
# ```bash
# companion/.venv/bin/python companion/scripts/run.py apply --chapter 3 \
#   --input companion/data/observed/monthly-temperature.csv \
#   --config companion/configs/ch03-observed.json \
#   --output companion/applied-runs/ch03-observed-reader
# ```
#
# Inspect max_trend_revision and explain why full-history decomposition cannot supply origin-known features. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.
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
INPUT_PATH = project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists()) / 'companion/data/examples/ch03.csv'
CONFIG_PATH = project_path.parents[2] / 'configs/ch03.json'
# Input paths are explicit and may be replaced with reader-supplied files.
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = pd.read_csv(INPUT_PATH)
workshop_table, workshop_summary = analyze_chapter(3, workshop_input, workshop_config)
print(json.dumps(clean_json(workshop_summary), indent=2))
print(workshop_table.head(12).to_string(index=False))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', CONFIG_PATH.parents[1])) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch03-workshop-results.csv', index=False)
(workshop_output/'ch03-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\n')
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
observed_input = pd.read_csv(CONFIG_PATH.parents[1]/'data/observed/monthly-temperature.csv')
observed_config = json.loads((CONFIG_PATH.parent/'ch03-observed.json').read_text())
observed_table, observed_summary = analyze_chapter(3, observed_input, observed_config)
print('Observed-data source:', observed_config['source'])
print(json.dumps(clean_json(observed_summary), indent=2))
print(observed_table.head(12).to_string(index=False))
observed_table.to_csv(workshop_output/'ch03-observed-results.csv', index=False)
(workshop_output/'ch03-observed-summary.json').write_text(json.dumps(clean_json(observed_summary), indent=2)+'\n')
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
