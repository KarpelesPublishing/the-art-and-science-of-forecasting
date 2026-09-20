# %% [markdown]
# # Chapter 9: The Oracle Problem
# Evaluate probability forecasts against the same synthetic binary events.
# Calibration, discrimination and sharpness are different properties.
# %%
from pathlib import Path
import sys
project=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'companion/src').exists())
sys.path.insert(0,str(project/'companion/src'))
from forecasting_companion.common import *
rng=begin(9); p=rng.beta(2,4,6000); outcomes=rng.binomial(1,p)
over=np.clip(.5+1.6*(p-.5),.01,.99); forecasts={'Calibrated':p,'Overconfident':over,'Base rate':np.repeat(1/3,len(p))}
# %%
plt.figure(); plt.plot([0,1],[0,1],'--',color='.5')
for label,pred in list(forecasts.items())[:2]:
    xs=[]; ys=[]
    for lo in np.arange(0,1,.1):
        mask=(pred>=lo)&(pred<lo+.1)
        if mask.sum()>20: xs.append(pred[mask].mean()); ys.append(outcomes[mask].mean())
    plt.plot(xs,ys,'o-',label=label)
plt.xlabel('Mean forecast probability'); plt.ylabel('Observed frequency'); plt.legend(fontsize=7)
save(9,1,'Calibration requires repeated outcomes','Reliability curves from 6,000 synthetic events. Only bins with more than twenty observations are shown.','### Calibration, Accuracy, and Resolution')
# %%
scores={k:brier(v,outcomes) for k,v in forecasts.items()}
plt.figure(); plt.barh(list(scores),list(scores.values())); plt.xlabel('Brier score (lower is better)')
save(9,2,'Keep score on the same questions','Synthetic events scored with mean squared probability error. The constant reference uses the known generating base rate of one third.','### The Brier Score')
# %%
confidence=np.maximum(over,1-over); correct=(over>=.5)==outcomes
xs=[]; ys=[]; counts=[]
for lo in np.arange(.5,1,.1):
    mask=(confidence>=lo)&(confidence<lo+.1)
    xs.append(confidence[mask].mean()); ys.append(correct[mask].mean()); counts.append(mask.sum())
plt.figure(); plt.plot([.5,1],[.5,1],'--',color='.5',label='Perfect calibration'); plt.plot(xs,ys,'o-',label='Forecasts')
for x,y,n in zip(xs,ys,counts): plt.annotate(f'n={n}',(x,y),xytext=(6,-10),textcoords='offset points',fontsize=6,ha='left',va='top',bbox=dict(boxstyle='round,pad=0.15',fc='white',ec='none',alpha=.85))
plt.legend(loc='upper left',frameon=False)
plt.xlabel('Stated confidence in favored outcome'); plt.ylabel('Fraction correct')
save(9,3,'Confidence is a testable claim','Synthetic overconfident forecasts grouped by confidence, with event counts. A single confident success proves little.','### Overconfidence Revisited')
print(scores)
# %% [markdown]
# ## Limits and exercise
# A constant 50% forecast is calibrated only in a population with 50% event frequency.
# Resolution measures differences in conditional event rates, not extremeness alone.
# Change the generating base rate and observe what happens to constant forecasts.
# %% [markdown]
# <!-- APPLIED-WORKSHOP-START -->
# ## Guided application workshop
# The sections below connect the controlled figures to a complete applied input/output workflow.
# %% [markdown]
# # Chapter 9 workshop: from lesson to decision
#
# ## Explain the mechanism
#
# Proper scores reward honest probabilities over repeated events. Calibration asks whether events given similar probabilities occur at corresponding frequencies. A forecaster can be calibrated yet offer little differentiation among events.
#
# ## Work through the arithmetic
#
# For p=[.7,.2] and outcomes [1,0], Brier contributions are .09 and .04, averaging .065. A .5 baseline scores .25 on both. On these two events the difference is -.185, but two events cannot certify skill or calibration.
#
# Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.
#
# ## Adapt the lesson to reader data
#
# Replace generated p/outcomes with recorded eligible forecasts and resolved outcomes. Retain the fixed event set across comparisons. Do not use the observed full-sample event rate as though it were known when historical baseline forecasts were issued.
#
# Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.
#
# For this chapter, settle these questions before fitting: Which events and forecast lead time are shared? Were forecasts recorded before resolution? What baseline was predeclared? Are outcomes missing or selectively reported?
#
# ## Interpret the actual lesson outputs
#
# The lesson’s 6,000 events are synthetic and its one-third baseline is known from the generator. The confidence plot annotates counts. A visually diagonal curve does not establish causality, and confidence in the favored outcome differs from probability of the same named event.
#
# The current applied adapter adds a separately inspectable numerical result:
#
# - `results.csv`: `bin_lower,count,mean_probability,frequency,frequency_lower,frequency_upper`.
# - `summary.json`: inspect `brier,baseline_brier`.
#
# The scoring adapter requires one resolved outcome per event and uses fixed probability bins. Wilson frequency bounds assume independent events. Preserve unresolved/late forecasts outside this scoring input and report their exclusions in the accompanying analysis.
#
# The [fixture](../data/examples/ch09.csv) and [config](../configs/ch09.json) match the current interface. Run the `apply` command in the [skill entrypoint](../../forecasting-skills/forecasting-ch09-expert-scoring/SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.
#
# ## Decide what the evidence supports
#
# Lower Brier is better on the same event set. Extreme probabilities are not automatically good resolution. A constant forecast is calibrated only relative to its population event rate. Small or dependent event samples cannot support confident expert rankings.
#
# Without timestamps, report score eligibility as unverified. Without baseline records, use a transparently labeled retrospective comparator, not a claimed predeclared baseline. Missing outcomes stay excluded; investigate whether missingness favors successful predictions.
#
# The applied deliverable must make these items inspectable: Return per-event and mean Brier, baseline difference, eligibility/exclusion counts, bin means and counts, and limitations of expert comparison.
#
# ## Three exercises with worked solutions
#
# ### Exercise 1
#
# Forecast .9, outcome 0: Brier?
#
# **Worked solution.** .81, a large penalty for confident error.
#
# ### Exercise 2
#
# Every event has true rate .2. Is a constant .5 forecast calibrated?
#
# **Worked solution.** No. In its single forecast bin, observed frequency would approach .2 rather than .5.
#
# ### Exercise 3
#
# Expert A scored easy events, B scored difficult ones. Can mean Brier rank skill fairly?
#
# **Worked solution.** Not without adjusting the comparison design; use common events and lead times or explicitly defend a different comparison.
#
# ## Business-reader application
#
# Use this request with the skill:
#
# > Use chapter 9 to score probabilities.csv on eligible resolved events, compare the recorded baseline and explain calibration with bin counts rather than unsupported rankings.
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
INPUT_PATH = project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists()) / 'companion/data/examples/ch09.csv'
CONFIG_PATH = project_path.parents[2] / 'configs/ch09.json'
# Input paths are explicit and may be replaced with reader-supplied files.
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = pd.read_csv(INPUT_PATH)
workshop_table, workshop_summary = analyze_chapter(9, workshop_input, workshop_config)
print(json.dumps(clean_json(workshop_summary), indent=2))
print(workshop_table.head(12).to_string(index=False))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', CONFIG_PATH.parents[1])) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch09-workshop-results.csv', index=False)
(workshop_output/'ch09-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\n')
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
