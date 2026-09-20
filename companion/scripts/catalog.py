"""Assemble the companion catalog and chapter skill documents from reviewed lessons."""
from pathlib import Path
import ast
import hashlib
import json
import re
import nbformat
from provenance import inputs,digest

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent

ANCHORS={
4:{1:'**Simple Exponential Smoothing (SES)**',2:'**Damped Trend Method**',3:'**Holt-Winters Additive and Multiplicative**'},
6:{2:'**ACF and PACF**'},
10:{1:'**Bayesian updating in practice.**',2:'**Extremizing aggregated forecasts.**',3:'**Fermi decomposition.**'},
11:{3:'**How wisdom of crowds works, and when.**'},
12:{3:'**Forecast Combination**'},
15:{2:'**DLinear: A Cautionary Note**'},
17:{1:'**Fan charts**',3:'**Winkler interval score**'},
19:{1:'**The Bass diffusion model.**',3:'**Parameter estimation: practical considerations.**'},
20:{1:'**Adstock.**',2:'**Saturation curves.**',6:'What A/B testing cannot reach'},  # 6 numbers after the desk-model figures
21:{3:'**Inventory optimization fundamentals**',4:'**Intermittent demand methods**'},
22:{1:'**Difference-in-differences**',2:'**CausalImpact**',3:'**Synthetic control**'},
23:{1:'**The SIR model and its parameters**',3:'**Nowcasting: the reporting delay triangle**',4:'**FluSight: the scoring framework**'},
24:{2:'**Concept drift and structural breaks.**',3:'**Champion-challenger framework.**'},
26:{1:'**Forecast and decision.**',2:'**Keeping score.**',3:'**The human-machine relationship.**'},
}

# Chapter-specific input discipline and operational method sequence.
RULES={
1:('OHLC prices with consistent sessions and corporate-action treatment; a stated target and trading friction assumptions.', 'Preserve open/high/low/close, establish persistence, define a pattern before testing, compare on unseen periods. Treat a market price as a signal with risk and carry components.', 'Do not infer predictive power from a visually convincing candle pattern or fit on the evaluation period.'),
2:('Explicit prior, likelihood, sampling/selection mechanism, observations and decision loss.', 'Normalize the posterior, separate persistent signal from measurement noise, identify missing observations and compute a proper score across comparable events.', 'Update odds with likelihood ratios; check selection bias before treating survivors as a representative sample.'),
3:('Time-indexed measurements, sampling frequency, initial state uncertainty, seasonal periods and horizon.', 'Inspect time structure, fit decomposition within each origin, perturb initial conditions, integrate dynamics and measure lead-time error against a common reference.', 'A toy Lorenz trajectory is not a weather forecast; full-series decomposition leaks future information into a backtest.'),
4:('Regular time series, horizon, seasonal period, units and enough training cycles to estimate seasonality.', 'Compare naive and seasonal-naive with SES, Holt, damped Holt and Holt-Winters; evaluate rolling origins and choose complexity only on training/validation observations.', 'Multiplicative components require positive values; do not choose smoothing parameters on the final holdout.'),
5:('Observation sequence, transition/measurement equations, Q/R noise assumptions and initial covariance.', 'Predict state/covariance, update with each observation, log innovations, evaluate coverage; apply smoothing only for retrospective inference.', 'Smoothing uses future measurements; fixed-noise Kalman gain does not automatically adapt to large residual shocks.'),
6:('Regular series, seasonal period, horizon, and origin-known exogenous variables if used.', 'Assess stationarity and differences, inspect training ACF/PACF, fit parsimonious candidate orders, evaluate rolling forecasts and residual diagnostics.', 'White-noise residuals are not proof of complete predictability extraction; future regressors need known values or scenarios.'),
7:('Joint input distributions, dependence assumptions, quantity of interest, simulation budget and random seed.', 'Simulate the actual quantity, estimate Monte Carlo error separately from model uncertainty, inspect chain mixing and effective sample size when using MCMC.', 'Asymmetric proposals require the Hastings proposal ratio; more draws cannot correct a misspecified model.'),
8:('Expert estimates recorded before feedback, elicitation question, reference date and eventual outcomes.', 'Preserve initial estimates, anonymize feedback, compare median and dispersion by round, record new evidence and compute forecast value added when outcomes resolve.', 'Convergence is not accuracy; shared information and bias invalidate claims of independent triangulation.'),
9:('Forecast probabilities, resolution criteria, forecast timestamps and resolved binary outcomes.', 'Align forecasts and outcomes, compute Brier scores and base-rate reference, inspect reliability bins with counts and distinguish discrimination from sharpness.', 'Constant50% is calibrated only for a50% event population; a single correct forecast does not certify calibration.'),
10:('Base rate, likelihood-ratio evidence and dependence, component assumptions, independently recorded forecasts.', 'Update odds, decompose into defensible factors, propagate dependencies, select aggregation/extremization on prior resolved events and score new events.', 'Do not multiply prior probability by a likelihood ratio directly or extremize merely to sound confident.'),
11:('Individual estimates, collection protocol, reference truth where available and shared-information structure.', 'Compare mean, median and trimmed mean; evaluate crowd size and error dependence; train any weights on separate resolved questions.', 'A larger crowd does not remove shared bias and weighted combination is not guaranteed to beat the best member.'),
12:('Panel series, frequency, evaluation origins, horizons, scoring rule and baseline definitions.', 'Freeze origins, fit every candidate with the same available information, compute comparable horizon scores, then evaluate fixed or validation-trained combinations.', 'MASE=1 refers to the training naive scale, not necessarily the held-out naive error; handle zero scale explicitly.'),
13:('Series IDs, timestamps, target, calendar and covariates with availability times; entity grouping.', 'Create lagged/shifted features within series, split chronologically, fit global LightGBM, compare seasonal-naive and ablations; evaluate explanations on held-out rows.', 'SHAP values describe the fitted model, not causal effects; unknown future promotions cannot be used as observed features.'),
14:('Related panel series, entity IDs, forecast origins, distributional target and training budget.', 'Separate held-out entities for cold start, scale using training history, train a global autoregressive probabilistic model, recursively sample paths and score against local baselines.', 'Report the actual architecture: the bundled small MLP is not DeepAR; do not let held-out entities enter training.'),
15:('Series history, horizon, exact pretrained checkpoint/revision, training-data provenance and device limits.', 'Load the pinned checkpoint, run real inference, benchmark against naive/seasonal-naive, record downloads/runtime, investigate contamination and distribution shift.', 'Do not substitute a statistical model for a missing foundation model or certify training exclusion from a dataset publication date alone.'),
16:('Dated target, seasonal periods, future-known holidays/regressors, cutoff and holdout horizons.', 'Fit Prophet components, select changepoint flexibility with temporal validation, compare event/no-event fits on final holdout, measure interval coverage.', 'Default MAP fitting is not full posterior inference; Prophet intervals must be evaluated rather than described as automatically calibrated.'),
17:('Forecast samples or quantiles, nominal levels, held-out observations and serial-dependence assumptions.', 'Check quantile order, evaluate coverage/width and proper scores, inspect PIT, calibrate only using past residuals and label scenario bands separately.', 'Two-model disagreement is not a95% interval. Ordinary split conformal needs exchangeability; with fewer than19 calibration residuals a finite95% bound cannot carry the usual guarantee.'),
18:('Complete hierarchy/aggregation matrix, all node IDs and units, base forecasts aligned by origin/horizon, rolling base-model errors if MinT is requested.', 'Verify completeness and aggregation identities; compare bottom-up and OLS; estimate MinT covariance from prior base-forecast errors with shrinkage; check coherence and out-of-sample error.', 'Never fill a missing node with zero silently or use covariance of differenced actuals as forecast-error covariance. With four observations prefer simple qualified methods; do not invent calibrated intervals.'),
19:('Adoption counts/cumulative totals, time units, durable/repeat-purchase distinction, market-ceiling evidence.', 'Fit bounded Bass parameters, compare assumed ceilings with early-data sensitivity, compute incidence versus cumulative adoption, and add a repeat cohort model for recurring purchases.', 'Bass hazard is a rate; interior peak formula needs q>p. Market size scales volume but does not change peak time for fixed p,q.'),
20:('Sales, spend, exposure timing, price/seasonality/confounders and randomized-lift information where available.', 'Define carryover and saturation, fit with temporal validation, examine confounding, calibrate incremental response against experiments, propagate uncertainty before allocation.', 'Observational attribution and SHAP credit are not causal lift; avoid claiming all Hill curves are concave.'),
21:('Demand, lead/review times, on-hand, pipeline, backlog, service costs and intermittent-demand history.', 'Track inventory position and flow conservation, compare information sharing and ordering policies, calculate critical-fractile inventory and Croston/SBA/TSB alternatives.', 'Use P(D<=Q)=cu/(cu+co); distinguish intermittent/lumpy/erratic quadrants; order-up-to covers lead plus review period.'),
22:('Treatment timing, affected units, candidate controls, pre-period outcomes, spillover and identification assumptions.', 'State the causal estimand, fit using pre-treatment data, compute DiD/counterfactual effect, inspect pretrends and placebo behavior and challenge control validity.', 'Pretrend nonsignificance does not prove identification; plain OLS is not BSTS/CausalImpact and predictive fit is not causal validity.'),
23:('Event/report dates, reporting vintages, population, transmission/removal assumptions and forecast horizon.', 'Separate nowcast from future forecast, conserve SIR population, vary transmission scenarios, estimate reporting-delay completion using available vintages and score prospectively.', 'Synthetic epidemic scenarios are educational; latent period and symptom incubation differ; revised future counts must not leak into as-of nowcasts.'),
24:('Timestamped observations, forecasts logged before outcomes, stable calibration window, alert costs and retraining policy.', 'Monitor standardized errors, calibrate false alarms on prior stable data, record detection delay, compare frozen/rolling/adaptive policies and score overrides.', 'An alarm is evidence to investigate, not a known cause; use observations only once available and evaluate false alarms as well as detections.'),
25:('Reference-class inclusion rules, original plans, actual/censored outcomes and decision costs.', 'Select comparables before choosing the desired result, estimate empirical outcome distribution, evaluate selection sensitivity, select a percentile consistent with decision loss.', 'Do not drop unfinished/abandoned projects silently; a median is optimal under absolute loss, not all decisions.'),
26:('Forecast journal, resolved outcomes, possible actions, asymmetric costs and review cadence.', 'Translate probabilities into cost-sensitive decisions, compare forecast scores and realized costs, retain a baseline and test adjustments on later outcomes.', 'A higher stated confidence level is not inherently a better forecast; evaluate usefulness and calibration together.'),
27:('Target, units, horizon, as-of cutoff, available history/analogues, defended proxy inputs and scoring date.', 'Complete intake, model supported relationships, estimate unsupported launch parameters explicitly, compute two routes, stop on unexplained disagreement, phase annual volume and log assumptions.', 'Agreement is not calibration. Preserve annual totals; reconstructed gamma phasing is not the original Dynamics model or Bass incidence. Scale/calibration constants are case-specific.')}

def initialize_skill(path, content):
    """Scaffold missing skills only; reviewed instructions are maintained artifacts."""
    if not path.exists():
        path.write_text(content)


def main():
    manifest={'title':'The Art and Science of Forecasting','chapters':[]}
    links=[]; inventory=['# Figure inventory','', '| Figure | Chapter | Title | Insertion section |','|---|---|---|---|']
    coverage=['# Executed method coverage','', 'This generated map ties notebook sections to executed code cells. The full-manuscript [method audit](method-audit.md) separately identifies advanced extensions; those are not counted as implemented merely because the book mentions them.','']
    for lesson in sorted((ROOT/'lessons').glob('*.py')):
        number=int(lesson.name[:2]); chapter=next((PROJECT/'manuscript').glob(f'{number:02d}-*.md'))
        title=chapter.read_text().splitlines()[0].removeprefix('# ')
        nbpath=ROOT/'notebooks'/f'{lesson.stem}.ipynb'
        execution=json.loads((ROOT/'results'/f'ch{number:02d}-execution.json').read_text())
        if execution['status']!='passed' or execution.get('inputs')!=inputs(lesson):
            raise ValueError(f'Chapter {number} needs a current successful execution')
        if execution.get('notebook_sha256')!=digest(nbpath): raise ValueError(f'Notebook changed since execution: {nbpath}')
        for asset,sha in execution.get('artifacts',{}).items():
            if digest(ROOT/asset)!=sha: raise ValueError(f'Artifact changed since execution: {asset}')
        nb=nbformat.read(nbpath,as_version=4)
        coverage.extend([f'## {title}','',f'Notebook: [{lesson.stem}](../notebooks/{lesson.stem}.ipynb). Execution: passed.',''])
        for cell in nb.cells:
            if cell.cell_type=='markdown':
                headings=re.findall(r'^## (.+)',cell.source,flags=re.M)
                for heading in headings: coverage.append(f'- {heading}')
            else: coverage.append(f'  - Executed cell `{cell.id}` (execution {cell.execution_count}).')
        coverage.append('')
        journal=ROOT/'results'/f'ch{number:02d}-figures.json'
        figures=json.loads(journal.read_text())
        for f in figures:
            f['anchor']=ANCHORS.get(number,{}).get(int(f['id'][-2:]),f['anchor'])
            assert f['anchor'] in chapter.read_text(),(number,f['anchor'])
            f['notebook']=f'notebooks/{lesson.stem}.ipynb'
            f['cell_id']=next(c['id'] for c in nb.cells if c.cell_type=='code' and re.search(rf'save\(\s*{number}\s*,\s*{int(f["id"][-2:])}\s*,',c.source))
            f['status']='executed-exported'
            inventory.append(f'| {f["id"]} | {number} | {f["title"]} | {f["anchor"].lstrip("# ")} |')
        figures.sort(key=lambda f:(chapter.read_text().index(f['anchor']),f['id']))
        for book_number,f in enumerate(figures,1): f['book_number']=book_number
        input_requirements,workflow,pitfall=RULES[number]
        skill_name=f'forecasting-ch{lesson.stem}'
        skill=PROJECT/'forecasting-skills'/skill_name/'SKILL.md'
        skill.parent.mkdir(exist_ok=True)
        relative=f'../../companion/notebooks/{lesson.stem}.ipynb'
        content=f'''---
name: {skill_name}
description: "Use when applying {title.replace('Chapter '+str(number)+': ','')} methods or working through forecasting book chapter {number}."
---

# {title}

## Inputs

{input_requirements}

## Apply the method

{workflow}

Read the [executable notebook]({relative}) before adapting its calculations. The
example data are synthetic unless explicitly attributed. Replace assumptions with
documented user inputs; retain the same origin-based separation when applicable.
Use the appropriate existing method skills only after checking their assumptions
against the safeguards below. A deadline does not remove these checks.

## Run the worked example

From the book project root, after following `companion/README.md`:

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter {number}
```

The notebook contains the calculation steps, assertions, exported charts, and
an exercise. Its editable source is `companion/lessons/{lesson.name}`.

## Failure checks

{pitfall}

If inputs are insufficient, identify the missing information and produce only the
supported estimate or scenario. Never fabricate data, backtest performance, source
provenance, or interval coverage. Separate a scenario range from a calibrated
prediction interval, and state skipped methods explicitly.

## Required output

Return target/units/horizon, input provenance and cutoff, the computed result,
benchmark or cross-check, assumptions, limitations, and the generated figure paths.
For a new applied forecast also save the forecast date and outcome/scoring date.
Use the [Complete Forecasting Skill](../all-chapters-forecasting/SKILL.md) to coordinate methods
across chapters; it does not require every model for every problem.
'''
        initialize_skill(skill,content)
        manifest['chapters'].append(dict(number=number,title=title,source=str(chapter.relative_to(PROJECT)),
            source_sha256=hashlib.sha256(chapter.read_bytes()).hexdigest(),notebook=str(nbpath.relative_to(ROOT)),
            lesson=str(lesson.relative_to(ROOT)),skill=str(skill.relative_to(PROJECT)),figures=figures,execution=execution,
            coverage='Executable core; named advanced extensions are explicitly scoped in lesson and method-audit report'))
        links.append(f'| {number:02d} | [{title}](../../{skill_name}/SKILL.md) | [{lesson.stem}](../../../companion/notebooks/{lesson.stem}.ipynb) |')
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'reports/figure-inventory.md').write_text('\n'.join(inventory)+'\n')
    (ROOT/'reports/method-coverage.md').write_text('\n'.join(coverage)+'\n')
    ref=PROJECT/'forecasting-skills/all-chapters-forecasting/references/chapter-map.md'; ref.parent.mkdir(parents=True,exist_ok=True)
    ref.write_text('# Chapter skill map\n\n| Chapter | Skill | Notebook |\n|---|---|---|\n'+'\n'.join(links)+'\n')
    print(f'Catalog: {len(links)} chapters, {sum(len(c["figures"]) for c in manifest["chapters"])} figures')

if __name__=='__main__': main()
