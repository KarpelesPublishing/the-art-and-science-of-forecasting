# %% [markdown]
# # Chapter 26: How to Be Ready Without Being Certain
# Turn probabilities into actions with explicit costs, evaluate combinations, and
# retain a forecast journal. Synthetic outcomes make the scoring loop inspectable.
# %%
from pathlib import Path
import sys
project=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'companion/src').exists())
sys.path.insert(0,str(project/'companion/src'))
from forecasting_companion.common import *
from scipy.special import expit,logit
rng=begin(26); p=rng.uniform(.05,.95,3000); outcomes=rng.binomial(1,p)
false_alarm,miss=2.,8.; threshold=false_alarm/(false_alarm+miss)
# %%
thresholds=np.linspace(0,1,101); losses=[]
for cut in thresholds:
    action=p>=cut; losses.append(np.mean(false_alarm*(action & (outcomes==0))+miss*((~action)&(outcomes==1))))
plt.figure(); plt.plot(thresholds,losses); plt.axvline(threshold,ls='--',label='Cost-derived threshold'); plt.xlabel('Action threshold'); plt.ylabel('Average realized cost'); plt.legend(fontsize=7)
save(26,1,'A probability becomes a decision through costs','Synthetic events with false-alarm cost two and miss cost eight. The Bayes threshold is 0.2 when probabilities are calibrated and costs fixed.','## Section Three: The Practice')
# %%
a=expit(logit(p)+rng.normal(0,.8,len(p))); b=expit(logit(p)+rng.normal(0,.8,len(p))); combined=(a+b)/2
plt.figure()
for name,pred in [('Model A',a),('Model B',b),('Equal ensemble',combined)]:
    block=[brier(pred[i:i+200],outcomes[i:i+200]) for i in range(0,len(p),200)]; plt.plot(np.arange(1,len(block)+1),block,label=name)
plt.xlabel('Successive 200-event batch'); plt.ylabel('Brier score'); plt.legend(fontsize=7)
save(26,2,'A journal makes the comparison repeatable','Synthetic forecasts constructed from latent event propensities and independent noise, then scored against generated outcomes in successive batches. The ensemble uses fixed equal weights; this is not a historical timestamped journal.','## Section Four: The Full Methodology')
# %%
plt.figure()
for cut in [.2,.5,.8]:
    action=combined>=cut; loss=false_alarm*(action & (outcomes==0))+miss*((~action)&(outcomes==1)); plt.plot(np.cumsum(loss),label=f'Threshold {cut}')
plt.xlabel('Resolved event'); plt.ylabel('Cumulative realized cost'); plt.legend(fontsize=7)
save(26,3,'Evaluate the decisions as well as the forecasts','The same synthetic ensemble and outcomes under different action thresholds. Costs accumulate even when forecast accuracy appears acceptable.','## Section Five: The Return')
import pandas as pd
journal=pd.DataFrame({'event':np.arange(len(p)),'probability':combined,'outcome':outcomes,'threshold':threshold})
import os
journal.to_csv(Path(os.environ.get('FORECAST_OUTPUT',project/'companion'))/'results/ch26-forecast-journal.csv',index=False)
# %% [markdown]
# ## Limits and exercise
# Reverse the costs and rerun. A 90% interval is not inherently better than a 60%
# interval; evaluate calibration, sharpness and usefulness for the actual decision.
# A single outcome contributes to a proper score even though it cannot establish
# calibration by itself.
# %% [markdown]
# <!-- APPLIED-WORKSHOP-START -->
# ## Guided application workshop
# The sections below connect the controlled figures to a complete applied input/output workflow.
# %% [markdown]
# # Chapter 26 workshop: from lesson to decision
#
# ## Explain the mechanism
#
# Readiness converts uncertain beliefs into contingent actions. A threshold expresses relative consequences, not how confident one should feel. A forecast and the policy using it need separate evaluation because either can fail.
#
# ## Work through the arithmetic
#
# With false-alarm cost 2 and miss cost 8, act when p>=2/(2+8)=.2 under the adapter’s tie rule. At p=.3, acting costs 2×.7=1.4 in expectation; not acting costs 8×.3=2.4. A rare event can therefore justify action well below a .5 threshold.
#
# Treat this hand calculation as a mechanism check. Compare its units and assumptions with the business target before using the executable adapter below.
#
# ## Adapt the lesson to reader data
#
# Replace the synthetic journal with timestamped event probabilities and outcomes; retain baseline predictions made on the same events. Change costs before recomputing policy decisions. If historical decisions were different, do not represent newly optimized retrospective decisions as actions actually taken.
#
# Keep the controlled example as a reproducible teaching case. Work in a copy when replacing its data; retain raw input, a cleaned table and an explanation of exclusions. Real data need a named source, extraction date, usable-as-of date and units. If an actual is revised later, preserve the vintage available when the forecast would have been issued. Never silently label synthetic generator output as an external dataset.
#
# For this chapter, settle these questions before fitting: What actions are available? What is the cost of a false alarm and a miss? Are costs constant and probabilities relevant/calibrated? What capacity or feasibility constraints apply?
#
# ## Interpret the actual lesson outputs
#
# The lesson’s events and journal are synthetic, with fixed equal ensemble weights. The cost curve applies alternate thresholds to the same outcomes; choosing its minimum and reporting that same minimum as future performance would overfit policy selection.
#
# The current applied adapter adds a separately inspectable numerical result:
#
# - `results.csv`: `event_id,probability,outcome,action,loss,cumulative_loss`.
# - `summary.json`: inspect `threshold,brier,mean_loss,best_constant_policy_hindsight_cost`.
#
# The adapter requires resolved events and strictly positive finite costs. It acts at p>=threshold. The reported best constant policy is a hindsight diagnostic, not a pre-recorded baseline. It reports Brier alongside decision loss; chapter 9 adds a fuller calibration diagnosis.
#
# The [fixture](../data/examples/ch26.csv) and [config](../configs/ch26.json) match the current interface. Run the `apply` command in the [skill entrypoint](../../forecasting-skills/forecasting-ch26-decision-readiness/SKILL.md), using a new empty output folder. Any broader methodology in this workshop requires separately recorded evidence or an explicit extension; successful command execution does not imply those steps happened.
#
# ## Decide what the evidence supports
#
# The threshold formula assumes zero cost for correct actions and fixed misclassification costs. Capacity limits, intervention effectiveness and heterogeneous costs can require a different optimization. A good score does not automatically imply useful decisions, and one outcome cannot establish calibration.
#
# Without credible costs, present the threshold/cost tradeoff and ask for the material missing preference rather than declare an optimal action. With unresolved outcomes, log expected decisions but do not compute realized loss. Uncertain probabilities warrant sensitivity around the decision boundary.
#
# The applied deliverable must make these items inspectable: Return loss table, threshold and assumptions, event-level probabilities/actions, realized costs and proper scores where resolved, benchmark policies, unresolved counts and revision plan.
#
# ## Three exercises with worked solutions
#
# ### Exercise 1
#
# False alarm 9, miss 1: optimal simple threshold?
#
# **Worked solution.** 9/(9+1)=.9.
#
# ### Exercise 2
#
# p=.4, false alarm 2, miss 8: expected costs?
#
# **Worked solution.** Act: 2×.6=1.2; do not act: 8×.4=3.2. Act under the simple loss table.
#
# ### Exercise 3
#
# A threshold tuned to all outcomes has lower realized cost. Is deployment improvement established?
#
# **Worked solution.** No. Freeze it and evaluate later events; retrospective optimization is not untouched policy evidence.
#
# ## Business-reader application
#
# Use this request with the skill:
#
# > Use chapter 26 to translate probabilities.csv into an explicit action policy under our costs, preserve unresolved cases and evaluate both probability quality and realized decision loss.
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
INPUT_PATH = project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists()) / 'companion/data/examples/ch26.csv'
CONFIG_PATH = project_path.parents[2] / 'configs/ch26.json'
# Input paths are explicit and may be replaced with reader-supplied files.
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = pd.read_csv(INPUT_PATH)
workshop_table, workshop_summary = analyze_chapter(26, workshop_input, workshop_config)
print(json.dumps(clean_json(workshop_summary), indent=2))
print(workshop_table.head(12).to_string(index=False))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', CONFIG_PATH.parents[1])) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch26-workshop-results.csv', index=False)
(workshop_output/'ch26-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\n')
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
