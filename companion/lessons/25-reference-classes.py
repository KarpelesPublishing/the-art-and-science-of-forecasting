# %% [markdown]
# # Chapter 25: Forecasting Your Own Life
# Estimate duration from comparable completed projects, then examine selection and
# decision risk. Synthetic data deliberately expose overrun tails; they are not
# Flyvbjerg's project database or personal advice.
# %%
from pathlib import Path
import sys
project=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'companion/src').exists())
sys.path.insert(0,str(project/'companion/src'))
from forecasting_companion.common import *
rng=begin(25); ratios=rng.lognormal(.25,.45,1000); planned=12.; durations=planned*ratios
# %%
plt.figure(); plt.hist(durations,bins=45,density=True); plt.axvline(planned,ls='--',color='#b5541c',lw=1.6,zorder=3,label='Inside-view plan'); plt.xlabel('Completion time (months)'); plt.ylabel('Density'); plt.legend()
save(25,1,'Start with outcomes of comparable projects','Synthetic durations for projects initially planned at twelve months. The distribution is right-skewed by construction.','## Section Four: Reference Class Forecasting')
# %%
estimates=[planned,np.median(durations),np.quantile(durations,.8),np.median(durations[durations<24])]
plt.figure(); plt.barh(['Inside view','Full-class median','Full-class P80','Exclude long projects'],estimates); plt.xlabel('Estimated duration (months)')
save(25,2,'The class you select changes the forecast','Synthetic reference-class estimates. Excluding long projects makes the forecast optimistic; dropping abandoned or unfinished projects can introduce related bias.','## Section Five: The Hardest Reference Class')
# %%
prob=np.linspace(.5,.95,30); uplift=(np.quantile(durations,prob)/planned-1)*100
plt.figure(); plt.plot(prob*100,uplift); plt.xlabel('Desired completion probability (%)'); plt.ylabel('Uplift above plan (%)')
save(25,3,'A commitment needs a risk level','Empirical quantiles of the synthetic duration class. Higher completion probabilities require larger contingency; the appropriate percentile depends on costs.','## Section Seven: The Full Methodology')
assert np.all(np.diff(uplift)>=0)
# %% [markdown]
# ## Limits and exercise
# Change the reference class by size, technology or execution environment before
# looking at the preferred answer. The median minimizes absolute error, not every
# decision loss. Unfinished projects require censoring/failure treatment rather than
# simply removing them from the class.
# %% [markdown]
# <!-- APPLIED-WORKSHOP-START -->
# ## Guided application workshop
# The sections below come from the chapter skill: the mechanism, the arithmetic, how to adapt the lesson to your data, exercises with worked solutions, and the exact contract of the applied tool.
# %% [markdown]
# ## Input contract and format example
# CSV case_id,planned,actual,completed; planned > 0, actual >= 0, completed true/false. For incomplete projects actual is elapsed follow-up at extraction, not a completed duration. Record extraction date, class-selection criteria and abandonment status separately when relevant.
#
# Minimal **format illustration**, not sufficient training data:
#
# ```csv
# case_id,planned,actual,completed
# A,12,15,true
# B,12,18,false
# ```
#
# ## Explain the mechanism
#
# The outside view asks what actually happened to comparable efforts before accepting the internal plan. A forecast percentile is a decision choice: median accuracy and a high-confidence commitment are different objectives.
#
# ## Work through the arithmetic
#
# Completed duration ratios [1,1.25,1.5,2] have median 1.375 under midpoint interpolation. A twelve-month plan multiplied by 1.375 gives 16.5 months. Quantile interpolation conventions matter in small samples and should be stated. An ongoing case at eighteen months is known only to exceed eighteen, not to finish then.
#
# ## Adapt the lesson to reader data
#
# Replace generated durations with a documented class and preserve incomplete rows. The original lesson discusses censoring but does not model it; if using the applied Kaplan–Meier route, report its independent-censoring assumption and do not equate that extension with the original empirical-only chart.
#
# For this chapter, settle these questions before fitting: What outcome and decision percentile matter? Which projects were comparable before their outcomes were known? Are unfinished cases censored or failed? Do plans and actuals share units?
#
# ## Interpret the actual lesson outputs
#
# The synthetic distribution deliberately contains overruns. The optimistic selected class drops long projects, illustrating outcome-conditioned selection. The percentile curve is empirical, not an estimate from Flyvbjerg’s proprietary database or personal-life advice.
#
# The current applied adapter adds a separately inspectable numerical result:
#
# - `results.csv`: `duration_ratio,at_risk,completed,survival`.
# - `summary.json`: `quantiles,cases,completed` plus method, interpretation, assumptions, not_done and status.
#
# Kaplan–Meier estimates the ratio survival curve under independent right-censoring. P50/P80/P90 are the first steps crossing their cumulative probabilities, not interpolated empirical quantiles. Unsupported upper quantiles remain null. Abandonment needs a separate outcome interpretation.
#
# ## Decide what the evidence supports
#
# Completion-only data can underestimate durations. Independent censoring is an assumption, not guaranteed by a completed flag. Abandoned projects are not simply completed at their stop date. Small classes and changing execution conditions make high quantiles unstable.
#
# If no comparable class exists, broaden it transparently and show sensitivity rather than asserting precision. If a survival curve never reaches the requested quantile, report that quantile not estimable. Without censoring metadata, show limitations of completed-case estimates.
#
# The applied deliverable must make these items inspectable: `results.csv` columns: `duration_ratio,at_risk,completed,survival`; `summary.json` keys: `quantiles,cases,completed` plus method, interpretation, assumptions, not_done and status. Return class definition/inclusions, completion and censoring counts, empirical or survival quantiles, uplift factors, chosen commitment and its decision rationale, plus unidentifiable tail risks.
#
# ## Three exercises with worked solutions
#
# ### Exercise 1
#
# Median overrun ratio 1.4, new plan 10 months: outside-view median?
#
# **Worked solution.** 14 months, conditional on class comparability.
#
# ### Exercise 2
#
# An unfinished project has elapsed 20 months. Should actual=20 be treated as a completed duration?
#
# **Worked solution.** No. It is right-censored at 20 if the observation mechanism supports that interpretation.
#
# ### Exercise 3
#
# Estimated completion probability reaches only .7 by last follow-up. Can P90 be reported numerically?
#
# **Worked solution.** Not from that observed survival curve without additional tail assumptions; mark it unestimable.
#
# ## Business-reader application
#
# Use this request with the skill:
#
# > Apply chapter 25 to projects.csv, retain censored cases, defend the reference class and translate supported quantiles into a commitment aligned with delay costs.
#
# ## Real-data boundary
#
# The [data registry](../data/registry.json) and [data notes](../data/README.md) distinguish bundled observations from controlled fixtures. No matching observed-data application is claimed for this chapter. Supply the chapter-specific records and their provenance before treating the exercise as business evidence; an observed outcome table is not automatically a historical forecast journal or identified experiment.
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
INPUT_PATH = project_path / 'companion/data/examples/ch25.csv'      # replace with your file
CONFIG_PATH = project_path / 'companion/configs/ch25.json'            # replace with your configuration
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = pd.read_csv(INPUT_PATH)
workshop_table, workshop_summary = analyze_chapter(25, workshop_input, workshop_config)
print(summarize(workshop_summary, workshop_table))
print()
print(preview(workshop_table))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', project_path / 'companion')) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch25-workshop-results.csv', index=False)
_ = (workshop_output/'ch25-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\n')
