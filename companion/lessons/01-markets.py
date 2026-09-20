# %% [markdown]
# # Chapter 1: The Market Discovers the Future
# Seeded synthetic prices illustrate OHLC records, information adjustment and a
# holdout comparison. These are not reconstructed Dojima prices. A futures price
# also includes carry and risk premia; it is not simply an expected spot price.
# %%
from pathlib import Path
import sys
project=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'companion/src').exists())
sys.path.insert(0,str(project/'companion/src'))
from forecasting_companion.common import *
from matplotlib.patches import Rectangle
rng=begin(1)
# %% [markdown]
# ## A candle preserves information a closing price discards
# %%
close=100+np.cumsum(rng.normal(0,1,80)); opening=np.r_[100,close[:-1]]
high=np.maximum(opening,close)+rng.uniform(.1,1,80); low=np.minimum(opening,close)-rng.uniform(.1,1,80)
fig,ax=plt.subplots()
for t in range(30):
    ax.vlines(t,low[t],high[t],color='.2',lw=.7)
    ax.add_patch(Rectangle((t-.3,min(opening[t],close[t])),.6,max(.03,abs(close[t]-opening[t])),facecolor='white' if close[t]>opening[t] else '.25',edgecolor='.2'))
ax.set_xlim(-1,30); ax.set_ylim(low[:30].min()-1,high[:30].max()+1); ax.set_xlabel('Session'); ax.set_ylabel('Illustrative price')
save(1,1,'What a price candle records','Synthetic opening, high, low and closing prices. Hollow candles close above the opening; filled candles close below it.','## What the Market Knows')
# %% [markdown]
# ## Information reaches the market gradually in this toy mechanism
# %%
value=np.r_[np.ones(20)*100,np.ones(40)*110]; market=[100.]
for t in range(1,60): market.append(market[-1]+.22*(value[t]-market[-1])+rng.normal(0,.35))
plt.figure(); plt.plot(value,ls='--',label='New valuation'); plt.plot(market,label='Price'); plt.xlabel('Session'); plt.ylabel('Price'); plt.legend()
save(1,2,'Price adjustment after news','Synthetic information shock with partial adjustment and trading noise. The adjustment rule is assumed, not estimated from historical markets.','## Prediction Markets: The Mechanism Generalized')
# %% [markdown]
# ## Patterns must survive data they did not select
# A persistence forecast and a predeclared momentum rule are compared across many
# independent random walks. Any apparent single-walk advantage may be chance.
# %%
walks=np.cumsum(rng.normal(size=(400,100)),axis=1)
truth=walks[:,70:]; naive=walks[:,69:-1]; momentum=naive+.5*(walks[:,69:-1]-walks[:,68:-2])
errors=[np.mean(abs(truth-p),axis=1) for p in [naive,momentum]]
plt.figure(); plt.boxplot(errors,tick_labels=['Persistence','Momentum']); plt.ylabel('Holdout MAE');
save(1,3,'A plausible pattern needs a benchmark','Four hundred synthetic random walks, with the final thirty observations held out. Momentum is a fixed rule, not tuned on the holdout.','## A Sidebar on Patterns in Numbers')
# %% [markdown]
# ## Extension and exercise
# Benford probabilities are log10(1+1/d), d=1,...,9. They sum to one but do not
# apply to every price dataset. Change the generator to correlated returns and
# examine whether momentum now earns its place. Prediction-market prices require
# assumptions about incentives, risk preferences and trading frictions.
# %%
benford=np.log10(1+1/np.arange(1,10)); assert np.isclose(benford.sum(),1)
print('Benford reference probabilities:',benford)
# %% [markdown]
# <!-- APPLIED-WORKSHOP-START -->
# ## Guided application workshop
# The sections below connect the controlled figures to a complete applied input/output workflow.
# %% [markdown]
# # Chapter 1 workshop: from lesson to decision
#
# ## Explain the mechanism
#
# A price aggregates information through a market mechanism, but the resulting forecast contains frictions and incentives. OHLC summarizes within-period movement. A visually plausible pattern must beat a predeclared baseline after the information cutoff.
#
# ## Work through the arithmetic
#
# If the last two closes are 100 and 103, persistence predicts 103. A one-step extrapolation of the latest change predicts 106. If the next close is 102, absolute errors are 1 and 4. One example favors persistence but does not establish its general superiority.
#
# Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.
#
# ## Adapt the lesson to reader data
#
# Replace the simulated price/OHLC arrays with an adjusted, single-contract series. Preserve the difference between the partial-adjustment mechanism and the forecasting comparison: assumed information shocks are not measured market fundamentals. Retain a calendar of market sessions, rather than imputing holiday prices as new trades.
#
# Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.
#
# For this chapter, settle these questions before fitting: Is the target spot, futures or an event-contract price? What is the quote frequency? When could the signal have been known? Are transaction costs relevant?
#
# ## Interpret the actual lesson outputs
#
# Candles depict synthetic ranges. The adjustment plot assumes an information-processing rule; its speed is not estimated from a real market. The repeated random-walk comparison evaluates a prespecified momentum rule on 400 controlled paths, not a trading backtest or proof of market efficiency.
#
# The current applied adapter adds a separately inspectable numerical result:
#
# - `results.csv`: `timestamp,actual,persistence,momentum,mean_reversion,actual_direction,momentum_hit,mean_reversion_hit`.
# - `summary.json`: `rules,k,train_fraction,test_rows,mae,hit_rate,hit_rate_p_value,benford` plus method, interpretation, assumptions, not_done and status.
#
# The tool scores predeclared one-step rules on closing prices at every origin after the training share: persistence (last close), momentum (last close plus the average change over `k` periods) and mean reversion (mean of the last `k` closes). It reports MAE per rule, the directional hit rate of momentum and mean reversion with zero-change periods excluded and a binomial p-value against a coin, and a Benford first-digit chi-square test on `benford_column` as a data-integrity habit. It computes price error only: no returns, costs, position sizing, sessions or corporate-action checks. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.
#
# The [fixture](../data/examples/ch01.csv) and [config](../configs/ch01.json) match the current interface. Run the `apply` command in the [skill entrypoint](../../forecasting-skills/forecasting-ch01-markets/SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.
#
# ## Decide what the evidence supports
#
# Check sensitivity to lookback, corporate-action treatment and quote timing. Futures carry and risk premia prevent a simple expected-spot interpretation. Event-market probabilities additionally need defensible contract resolution and market assumptions. Price forecasts alone do not establish profitable trades.
#
# With close-only data, omit candlesticks and use close-based baselines. Without a reliable adjustment history, segment at discontinuities or state that change forecasts are unreliable. No historical data supports only a mechanism illustration.
#
# The applied deliverable must make these items inspectable: `results.csv` columns: `timestamp,actual,persistence,momentum,mean_reversion,actual_direction,momentum_hit,mean_reversion_hit`; `summary.json` keys: `rules,k,train_fraction,test_rows,mae,hit_rate,hit_rate_p_value,benford` plus method, interpretation, assumptions, not_done and status. A hit rate of 56 percent on 44 observations has a coin-flip p-value near a half; say so before anyone trades on it.
#
# ## Three exercises with worked solutions
#
# ### Exercise 1
#
# OHLC is 100,99,98,101. Is it valid?
#
# **Worked solution.** No: the reported high 99 is below open 100 and close 101. Correct the record from source or exclude it with a reason.
#
# ### Exercise 2
#
# Last close is 80, next actual 77. What is persistence absolute error?
#
# **Worked solution.** The prediction is 80 and absolute error is 3 price units.
#
# ### Exercise 3
#
# A momentum lookback was chosen after comparing the last month. Can that month remain final test?
#
# **Worked solution.** No. It is now selection data; evaluate on later untouched observations.
#
# ## Business-reader application
#
# Use this request with the skill:
#
# > Use chapter 1 to audit prices.csv and compare a prespecified momentum rule with persistence on later matched observations. Separate prediction error from trading profitability.
#
# Read the returned result as a decision record. Check that the forecast answers your unit and horizon, that its comparison uses information available at the time, and that any recommendation follows from the stated loss or business objective. Ask which missing measurement would most change the conclusion.
#
# ## Real-data boundary
#
# The [data registry](../data/registry.json) and [data notes](../data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
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
INPUT_PATH = project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists()) / 'companion/data/examples/ch01.csv'
CONFIG_PATH = project_path.parents[2] / 'configs/ch01.json'
# Input paths are explicit and may be replaced with reader-supplied files.
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = pd.read_csv(INPUT_PATH)
workshop_table, workshop_summary = analyze_chapter(1, workshop_input, workshop_config)
print(json.dumps(clean_json(workshop_summary), indent=2))
print(workshop_table.head(12).to_string(index=False))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', CONFIG_PATH.parents[1])) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch01-workshop-results.csv', index=False)
(workshop_output/'ch01-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\n')
# %% [markdown]
# ## Real-data boundary
#
# The bundled case is controlled, not a reconstruction of historical records. No
# verified, appropriately licensed domain dataset is supplied for this particular
# workflow. Use the input contract to supply your own observations and evidence.
# Do not substitute an unrelated public dataset simply to call the example real.
# The wider companion includes observed time-series applications in chapters
# 3–6, 12, 15–16 and 24; their data do not establish this chapter’s domain assumptions.
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
