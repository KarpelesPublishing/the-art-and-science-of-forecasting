# %% [markdown]
# # Chapter 19: Frank Bass and the Television
# Compute Bass adoption and incidence, fit sparse data, and show why early curves
# cannot identify a market ceiling confidently. All observations are synthetic.
# %%
from pathlib import Path
import sys
project=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'companion/src').exists())
sys.path.insert(0,str(project/'companion/src'))
from forecasting_companion.common import *
from scipy.optimize import least_squares
rng=begin(19)
def bass(t,p,q,m):
    e=np.exp(-(p+q)*np.asarray(t)); return m*(1-e)/(1+q/p*e)
t=np.linspace(0,30,301); p,q,m=.025,.35,100000
adopt=bass(t,p,q,m); assert np.all(np.diff(adopt)>=0) and adopt.max()<=m
# %%
plt.figure(); plt.plot(t,adopt); plt.axhline(m,ls='--',color='.5',label='Market ceiling'); plt.xlabel('Years'); plt.ylabel('Cumulative adopters'); plt.legend()
save(19,1,'Adoption accumulates toward a ceiling','Synthetic Bass curve with p=0.025/year, q=0.35/year and a 100,000-adopter ceiling. Parameters are rates, not population fractions.','## Section Two: The Pre-Launch Problem')
# %%
incidence=(p+q*adopt/m)*(m-adopt); peak=np.log(q/p)/(p+q)
plt.figure(); plt.plot(t,incidence); plt.axvline(peak,ls='--',label=f'Peak {peak:.1f} years'); plt.xlabel('Years'); plt.ylabel('New adopters per year'); plt.legend()
save(19,2,'The adoption rate peaks before saturation','Derivative of the synthetic cumulative curve. The interior peak formula applies when q is greater than p; the ceiling scales volume, not peak timing.','## Section Three: From Television to TikTok')
# %% [markdown]
# ## A sparse early history allows very different futures
# Fix alternative ceilings and fit p,q on only the first five years. Similar
# early fits are not evidence that their extrapolations are equally credible.
# %%
early=np.arange(1,6); observed=bass(early,p,q,m)+rng.normal(0,200,5)
plt.figure(); plt.scatter(early,observed,color='black',s=15,label='Early observations')
for ceiling in [60000,100000,180000]:
    fit=least_squares(lambda pars:(bass(early,*pars,ceiling)-observed)/1000,[.03,.3],bounds=([.001,.001],[.2,1.]))
    plt.plot(t,bass(t,*fit.x,ceiling),label=f'Ceiling {ceiling/1000:.0f}k')
plt.xlabel('Years'); plt.ylabel('Cumulative adopters'); plt.legend(fontsize=7)
save(19,3,'Early fits can hide ceiling uncertainty','Synthetic five-point calibration with three assumed market ceilings. These are sensitivity scenarios, not a calibrated prediction band.','## Section Four: The Full Methodology')
# %%
trial_households=100000*.5*.2
trial_volume=trial_households*1.2; repeat_volume=trial_households*.3*4*1.4
print('Illustrative trial and repeat units:',trial_volume,repeat_volume)
# %% [markdown]
# ## Limits and exercise
# Add mature observations and refit. Durable first adoption differs from recurring
# purchases: incidence alone is not total recurring sales. A repeat-purchase model
# needs cohort retention/cadence. Generalized Bass, conjoint and agent networks are
# extensions with additional data/identification requirements.
# %% [markdown]
# <!-- APPLIED-WORKSHOP-START -->
# ## Guided application workshop
# The sections below connect the controlled figures to a complete applied input/output workflow.
# %% [markdown]
# # Chapter 19 workshop: from lesson to decision
#
# ## Explain the mechanism
#
# Bass separates external adoption pressure p from imitation pressure q times existing penetration. Remaining nonadopters limit growth. Its familiar S-shape is a model of first adoption, not a universal sales law.
#
# ## Work through the arithmetic
#
# With m=10,000, existing adopters N=2,000, p=.02/year and q=.3/year, instantaneous adoption rate is (.02+.3×.2)×8,000=640 adopters/year. If q>p, peak time is log(q/p)/(p+q); here log(15)/.32≈8.463 years under a launch at zero adoption.
#
# Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.
#
# ## Adapt the lesson to reader data
#
# Replace early/observed in the sparse-fit block with elapsed time and cumulative unique adopters. Select ceiling scenarios from external market definitions, not simply from whichever fit pleases the sponsor. Keep repeat-volume arithmetic separate.
#
# Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.
#
# For this chapter, settle these questions before fitting: Does the series count cumulative unique adopters? What is the market ceiling’s evidence? Are time units consistent? Has the inflection or peak been observed? What repeat behavior lies outside adoption?
#
# ## Interpret the actual lesson outputs
#
# The lesson contrasts cumulative adoption with its derivative and fits the first five synthetic years under different ceilings. Similar early fits expose weak identification; they do not assign probabilities to ceilings. Trial/repeat figures use separately assumed purchase factors.
#
# The current applied adapter adds a separately inspectable numerical result:
#
# - `results.csv`: `time,ceiling,bass_trials,gamma_trials,bass_units,gamma_units`.
# - `summary.json`: `fits,ceilings,sales_horizon,peak,kernel,timing_comparison,parfitt_collins,bass_table_rows` plus method, interpretation, assumptions, not_done and status.
#
# The tool fits the Bass model for each declared ceiling (with early-fit holdout, Jacobian condition and peak time), optionally refits with `fix_q` held, then converts adoption into sales over `sales_horizon` periods (24 or more) under two timing curves that share the same trial total: Bass incidence and the author's gamma-shaped launch curve with its `peak` month. Each timing is spread with the repeat kernel into unit sales, and the tool compares peak period, twelve-period units and total units between them. With `parfitt_collins` inputs it reports the steady-state share and a plus or minus 20 percent band on repeat. Price, distribution and advertising are not in the curve; the kernel is assumed, not estimated. The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.
#
# The [fixture](../data/examples/ch19.csv) and [config](../configs/ch19.json) match the current interface. Run the `apply` command in the [skill entrypoint](../../forecasting-skills/forecasting-ch19-diffusion/SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.
#
# ## Decide what the evidence supports
#
# Early adoption often weakly identifies m and can trade off with p,q. An interior incidence peak formula requires q>p. Saturation is a structural assumption, not proof that the market cannot expand. Scenario curves are not a calibrated interval.
#
# With no adoption history use defended analogue parameters and explicit scenarios. With only sales units, obtain unique-adopter/cohort information or change the target; do not treat cumulative repeat sales as cumulative adoption.
#
# The applied deliverable must make these items inspectable: `results.csv` columns: `time,ceiling,bass_trials,gamma_trials,bass_units,gamma_units`; `summary.json` keys: `fits,ceilings,sales_horizon,peak,kernel,timing_comparison,parfitt_collins,bass_table_rows` plus method, interpretation, assumptions, not_done and status. Show both timing curves; the same eventual total can put half the first year in a different quarter.
#
# ## Three exercises with worked solutions
#
# ### Exercise 1
#
# p=.01,q=.2,m=1000,N=100: incidence?
#
# **Worked solution.** (.01+.2×.1)×900=27 adopters per time unit.
#
# ### Exercise 2
#
# If q<=p, should a negative interior peak time be forecast?
#
# **Worked solution.** No. The interior formula does not describe a future peak; incidence is highest at or near launch under the basic model.
#
# ### Exercise 3
#
# Cumulative sales are 10,000 but include three purchases per buyer. Are there 10,000 adopters?
#
# **Worked solution.** No. Unique adopter counts require separate evidence; repeat units cannot be silently equated with adoption.
#
# ## Business-reader application
#
# Use this request with the skill:
#
# > Apply chapter 19 to adoption.csv, defend several market ceilings and show which long-run differences are unsupported by the early history.
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
INPUT_PATH = project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists()) / 'companion/data/examples/ch19.csv'
CONFIG_PATH = project_path.parents[2] / 'configs/ch19.json'
# Input paths are explicit and may be replaced with reader-supplied files.
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = pd.read_csv(INPUT_PATH)
workshop_table, workshop_summary = analyze_chapter(19, workshop_input, workshop_config)
print(json.dumps(clean_json(workshop_summary), indent=2))
print(workshop_table.head(12).to_string(index=False))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', CONFIG_PATH.parents[1])) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch19-workshop-results.csv', index=False)
(workshop_output/'ch19-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\n')
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
