# %% [markdown]
# # Chapter 6: The Unexpected Route
# We difference a synthetic integrated autoregression, inspect ACF/PACF, fit ARIMA,
# and evaluate its future forecast. Diagnostics guide judgment; white-noise
# residuals do not prove that all nonlinear predictability has been exhausted.
# %%
from pathlib import Path
import sys
project=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'companion/src').exists())
sys.path.insert(0,str(project/'companion/src'))
from forecasting_companion.common import *
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
from statsmodels.tsa.stattools import adfuller,kpss
from statsmodels.stats.diagnostic import acorr_ljungbox
rng=begin(6)
d=np.zeros(220)
for t in range(1,len(d)): d[t]=.65*d[t-1]+rng.normal()
y=100+np.cumsum(d); train=y[:190]; test=y[190:]
# %%
fig,axes=plt.subplots(2,1,figsize=(4.3,3.6)); axes[0].plot(train); axes[0].set_ylabel('Level'); axes[1].plot(np.diff(train)); axes[1].set_ylabel('First difference'); axes[1].set_xlabel('Time')
save(6,1,'Difference the changing level','Synthetic integrated autoregressive observations. First differencing removes the accumulated level without assuming that every trend should be differenced.','## Part Three: What ARIMA Actually Is',fig)
# %%
fig,axes=plt.subplots(2,1,figsize=(4.3,3.8)); plot_acf(np.diff(train),lags=24,ax=axes[0]); plot_pacf(np.diff(train),lags=24,ax=axes[1],method='ywm'); axes[1].set_xlabel('Lag')
save(6,2,'A signature in the lag structure','ACF and PACF of training differences only. Approximate confidence bands help screen candidate models; they do not select an order with certainty.','## Part Four: The Full Methodology',fig)
# %% [markdown]
# ## Forecast before seeing the answers
# ARIMA(1,1,0) is prespecified from the demonstration generator. Real selection
# must occur within the training window using diagnostics and temporal validation.
# %%
model=ARIMA(train,order=(1,1,0)).fit(); prediction=model.get_forecast(len(test)); ci=np.asarray(prediction.conf_int())
plt.figure(); plt.plot(np.arange(160,190),train[-30:],color='.5',label='Train'); plt.plot(np.arange(190,220),test,label='Actual'); plt.plot(np.arange(190,220),prediction.predicted_mean,label='ARIMA'); plt.fill_between(np.arange(190,220),ci[:,0],ci[:,1],alpha=.2); plt.xlabel('Time'); plt.ylabel('Level'); plt.legend(fontsize=7)
save(6,3,'Forecast uncertainty accumulates','Held-out synthetic observations with the ARIMA model\'s nominal 95% prediction interval. Coverage on one path is not a calibration guarantee.','## Part Five: Listening to the Residuals')
print('MAE ARIMA:',mae(test,prediction.predicted_mean),'naive:',mae(test,train[-1]))
print('ADF differenced p:',adfuller(np.diff(train))[1]); print(acorr_ljungbox(model.resid[10:],lags=[12],return_df=True))
# %% [markdown]
# ## Seasonal ARIMA in a real rolling-origin comparison
# A second synthetic series has a lag-12 dependence. At each origin we fit
# SARIMA(0,0,0)(1,0,0)[12] to earlier observations and forecast twelve steps.
# Orders are prespecified, not selected on the evaluated outcomes. Compare the
# same horizons with a nonseasonal ARIMA and seasonal naive; no winner is assumed.
# %%
seasonal_y = np.zeros(180)
for day in range(12, len(seasonal_y)):
    seasonal_y[day] = .85*seasonal_y[day-12]+rng.normal(0, 2)
seasonal_y += 40
rolling_errors = {'SARIMA': [], 'ARIMA': [], 'Seasonal naive': []}
for origin in [120, 144, 168]:
    history, actual = seasonal_y[:origin], seasonal_y[origin:origin+12]
    seasonal_fit = ARIMA(history, order=(0,0,0), seasonal_order=(1,0,0,12), trend='c').fit()
    ordinary_fit = ARIMA(history, order=(1,0,0), trend='c').fit()
    forecasts = {'SARIMA': seasonal_fit.forecast(12), 'ARIMA': ordinary_fit.forecast(12),
                 'Seasonal naive': history[-12:]}
    for name, forecast in forecasts.items():
        rolling_errors[name].append(mae(actual, forecast))
assert all(np.isfinite(values).all() for values in rolling_errors.values())
print('Twelve-step MAE by chronological origin:', rolling_errors)
print('Mean rolling MAE:', {name: float(np.mean(values)) for name, values in rolling_errors.items()})
# %% [markdown]
# ## Limits and exercise
# Change the AR coefficient or seasonal lag. Add exogenous inputs only when their
# future values are known or explicitly scenarized. VAR,
# cointegration, GARCH and fractional integration are distinct extensions requiring
# separate multivariate or volatility examples; the present notebook is the ARIMA core.
# %% [markdown]
# <!-- APPLIED-WORKSHOP-START -->
# ## Guided application workshop
# The sections below connect the controlled figures to a complete applied input/output workflow.
# %% [markdown]
# # Chapter 6 workshop: from lesson to decision
#
# ## Explain the mechanism
#
# AR terms use past values; MA terms use past innovations. Integration describes accumulated change requiring differencing. Seasonal versions add dependence at calendar lags. Order selection and forecast validation are separate tasks.
#
# ## Work through the arithmetic
#
# For levels [100,103,105], differences are [3,2]. If the last difference is 2 and its AR(1) coefficient is .6 with zero drift, next expected difference is 1.2 and next expected level is 106.2. The second future difference is .72, making the two-step level 106.92.
#
# Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.
#
# ## Adapt the lesson to reader data
#
# Replace generated y before train/test splitting. For the separate seasonal experiment replace seasonal_y and choose a justified seasonal period. Orders in the teaching source are prespecified from its generator; do not claim they were automatically discovered for user data.
#
# Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.
#
# For this chapter, settle these questions before fitting: What is the target frequency and forecast horizon? Are trends deterministic or accumulated shocks? What seasonality exists? Will any future regressors actually be known?
#
# ## Interpret the actual lesson outputs
#
# ADF and ACF/PACF use training differences. The forecast chart’s band is nominal model uncertainty. The separate seasonal comparison reports three origins at a twelve-step horizon and does not implement VAR, cointegration or GARCH.
#
# The current applied adapter adds a separately inspectable numerical result:
#
# - `results.csv`: `timestamp,forecast,model`.
# - `summary.json`: inspect `selected,validation,validation_predictions,test_mae,intervals`.
#
# The adapter runs the companion engine with the `arima` pool: naive, seasonal naive, drift, ARIMA(0,1,1), ARIMA(1,1,0), the airline model ARIMA(0,1,1)(0,1,1)s, and an AICc-selected seasonal ARIMA whose regular differencing comes from repeated KPSS tests and whose seasonal differencing comes from STL seasonal strength, searched over p,q in 0–2 and P,Q in 0–1 on the first training slice. A log transform is chosen on training data when the series asks for it. Up to five expanding origins select the model; a final untouched holdout scores it once; model intervals are produced and their validation coverage is measured. Short valid histories return a provisional naive baseline and optional seasonal-naive scenario, with no claimed validation.
#
# The [fixture](../data/examples/ch06.csv) and [config](../configs/ch06.json) match the current interface. Run the `apply` command in the [skill entrypoint](../../forecasting-skills/forecasting-ch06-arima/SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.
#
# ## Decide what the evidence supports
#
# White residuals do not rule out nonlinear predictability. Differencing can remove useful structure or induce noise when excessive. Intervals depend on parameter/model assumptions and should be assessed by horizon on held-out origins.
#
# With a short series use naive or low-order candidates and mark seasonal fitting unsupported. For calendar gaps, audit the measurement process before imputation. If regressors are unknown, show conditional forecasts or omit the regressor model.
#
# The applied deliverable must make these items inspectable: Return differencing/order rationale, fit warnings, origin-by-horizon benchmark losses, residual diagnostics, dated forecasts and model-interval assumptions.
#
# ## Three exercises with worked solutions
#
# ### Exercise 1
#
# Levels 10,13,12: first differences?
#
# **Worked solution.** 3 and -1.
#
# ### Exercise 2
#
# Residual Ljung–Box does not reject. Is the chosen model proven optimal?
#
# **Worked solution.** No. The test concerns a particular residual dependence diagnostic and has limited power; compare future losses.
#
# ### Exercise 3
#
# A future promotion variable becomes known only after the forecast date. May its realized value be used?
#
# **Worked solution.** No. Use the schedule actually known at the origin or label a conditional scenario.
#
# ## Business-reader application
#
# Use this request with the skill:
#
# > Apply chapter 6 to sales.csv with a twelve-period horizon, compare supported ARIMA and seasonal-naive candidates at earlier origins, and explain selection and residual limitations.
#
# Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.
#
# ## Observed-data transfer exercise
#
# A bundled [observed series](../data/observed/monthly-temperature.csv) and [matching config](../configs/ch06-observed.json) provide a second application after the controlled fixture. Read the [data registry](../data/registry.json) for provenance and transformations. These are historical snapshots, not archived real-time release vintages.
#
# ```bash
# companion/.venv/bin/python companion/scripts/run.py apply --chapter 6 \
#   --input companion/data/observed/monthly-temperature.csv \
#   --config companion/configs/ch06-observed.json \
#   --output companion/applied-runs/ch06-observed-reader
# ```
#
# Compare seasonal and nonseasonal candidates without changing their orders after viewing the final test. Record the actual result of your run. Do not import the controlled example’s winner or interpret a successful numerical execution as evidence of operational accuracy.
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
INPUT_PATH = project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists()) / 'companion/data/examples/ch06.csv'
CONFIG_PATH = project_path.parents[2] / 'configs/ch06.json'
# Input paths are explicit and may be replaced with reader-supplied files.
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = pd.read_csv(INPUT_PATH)
workshop_table, workshop_summary = analyze_chapter(6, workshop_input, workshop_config)
print(json.dumps(clean_json(workshop_summary), indent=2))
print(workshop_table.head(12).to_string(index=False))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', CONFIG_PATH.parents[1])) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch06-workshop-results.csv', index=False)
(workshop_output/'ch06-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\n')
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
observed_config = json.loads((CONFIG_PATH.parent/'ch06-observed.json').read_text())
observed_table, observed_summary = analyze_chapter(6, observed_input, observed_config)
print('Observed-data source:', observed_config['source'])
print(json.dumps(clean_json(observed_summary), indent=2))
print(observed_table.head(12).to_string(index=False))
observed_table.to_csv(workshop_output/'ch06-observed-results.csv', index=False)
(workshop_output/'ch06-observed-summary.json').write_text(json.dumps(clean_json(observed_summary), indent=2)+'\n')
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
