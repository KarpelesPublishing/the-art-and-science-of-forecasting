"""Chapter adapters: `analyze(chapter, data, config)` validates the config and dispatches to the chapter tool.

Chapters 4, 6, 12 and 27 use the forecasting engine; most other chapters have a tool module
(`tools_*.py`); the small calculators below serve the remaining chapters. Every path returns
through `core.finish`, so every summary carries method, interpretation, assumptions, not_done
and status."""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import least_squares
from .core import require,numeric,probability,integer,time_frame,finish
from .series import compare,decomposition


def analyze(chapter,d,c):
    common={'source','units','as_of','horizon','season','seed','outcome_due','frequency'}
    engine_keys={'pool','transform','origins','criterion','periods','regressors','future_regressors','country','conformal'}
    options={1:{'rules','k','train_fraction','benford_column'},15:{'checkpoint','quantiles','origins','samples'},4:engine_keys,6:engine_keys,12:engine_keys,5:{'Q','R','model','seasonal','cycle','stochastic_cycle','origins'},2:{'prior_alpha','prior_beta'},7:{'samples','correlation'},10:set(),11:{'extremize_a'},13:{'covariates','known_in_advance','strategy','lags','rolling','origins','ablation','shap_rows'},14:{'context','epochs'},16:{'weekly','yearly','events','regressors','mode','priors','origins'},17:{'alpha','gamma','pool','transform','origins','calibration_size','test_size'},18:{'nodes','S','past_errors','edges','pool','transform','origins','shrinkage','coherent_quantiles','history_tolerance'},19:{'ceilings','future_times','units_at_trial','repeat_kernel','peak','sales_horizon','time_unit','fix_q','parfitt_collins'},20:{'decay_a','decay_b','half_a','half_b','initial_a','initial_b','channels','controls','decay_grid','saturation','alpha','origins','windows','prior_mean','prior_sd','noise_sd','reallocation_total'},21:{'underage_cost','overage_cost','lead_time','review_period','service_level','bootstrap_window','samples','echelons','holding_cost','backorder_cost'},22:{'intervention','identification','controls','placebos','event_window'},23:{'delay_prob','mature_age','max_delay','origins','population','recovery_rate','sigma'},24:{'calibration_size','min_segment','max_breaks','rolling_window','drift_window'},26:{'false_alarm_cost','miss_cost'},27:{'mode','new_product','repeat_rate','repeat_kernel','declared_trial_total','trial_conversion_assumption','pool','transform','origins'}}
    unknown=set(c)-common-options.get(chapter,set())
    if unknown:raise ValueError('Unsupported config keys for this adapter: '+', '.join(sorted(unknown)))
    if chapter in (4,6,12):
        if 'series_id' in d and d.series_id.nunique()>1:
            tables=[]; summaries={}
            for name,g in d.groupby('series_id'):
                t,s=compare(g,c,chapter);t['series_id']=name;tables.append(t);summaries[str(name)]=s
            readiness='needs_evidence' if any(s.get('status')=='needs_evidence' for s in summaries.values()) else ('provisional' if any(s.get('status')=='provisional' for s in summaries.values()) else 'passed')
            chosen={k:v.get('selected') for k,v in summaries.items()}
            return finish(pd.concat(tables,ignore_index=True),method='Per-series rolling-origin comparison (no pooling)',
                          interpretation=f'Each of the {len(summaries)} series has its own chronological comparison; no pooled ranking is imposed. Selected: {chosen}. Overall readiness reflects the least-supported series.',
                          assumptions=['Series are forecast independently; no shared structure is used'],
                          not_done=['No global or hierarchical model across series (chapters 13, 14, 18)'],status=readiness,series=summaries)
        return compare(d,c,chapter)
    if chapter==3:return decomposition(d,c)
    if chapter==1:
        from .tools_markets import rule_backtest
        return rule_backtest(d,c)
    if chapter==5:
        from .tools_statespace import unobserved_components
        return unobserved_components(d,c)
    if chapter==15:
        from .tools_foundation import foundation_forecast
        return foundation_forecast(d,c)
    if chapter==19:
        from .tools_diffusion import diffusion_sales
        return diffusion_sales(d,c)
    if chapter==23:
        from .tools_epidemics import nowcast_and_seir
        return nowcast_and_seir(d,c)
    if chapter==24:
        from .tools_breaks import break_analysis
        return break_analysis(d,c)
    if chapter==16:
        from .tools_prophet import prophet_calendar
        return prophet_calendar(d,c)
    if chapter in (13,14):
        from .panel import panel_analysis
        return panel_analysis(chapter,d,c)
    if chapter==17:
        from .tools_probabilistic import conformal_intervals
        return conformal_intervals(d,c)
    if chapter==20:
        from .tools_mmm import mmm
        return mmm(d,c)
    if chapter==21:
        from .tools_supply import inventory_policy
        return inventory_policy(d,c)
    if chapter==22:
        from .tools_causal import causal_effects
        return causal_effects(d,c)
    if chapter==18 and ('edges' in c or 'timestamp' in d):
        from .tools_hierarchy import reconcile_hierarchy
        return reconcile_hierarchy(d,c)
    dispatch={2:belief,7:simulation,8:delphi,9:scoring,10:journal,11:crowds,17:intervals,18:hierarchy,19:diffusion,25:reference,26:decision,27:directed}
    if chapter not in dispatch:raise ValueError('Unsupported chapter')
    return dispatch[chapter](d,c)



def belief(d,c):
    a=numeric(d,['successes','trials'],True)
    if np.any(a!=np.floor(a)) or np.any(a[:,0]>a[:,1]) or np.any(a[:,1]<=0):raise ValueError('Integer successes must not exceed trials')
    pa=float(c.get('prior_alpha',2));pb=float(c.get('prior_beta',2))
    if min(pa,pb)<=0 or not np.isfinite([pa,pb]).all():raise ValueError('Positive finite prior parameters required')
    successes=a[:,0].sum();failures=(a[:,1]-a[:,0]).sum();rows=[]
    for strength in [.25,1,4]:
        alpha=pa*strength+successes;beta=pb*strength+failures
        rows.append(dict(prior_strength=strength,posterior_mean=alpha/(alpha+beta),lower=stats.beta.ppf(.025,alpha,beta),upper=stats.beta.ppf(.975,alpha,beta)))
    mid=rows[1]
    return finish(rows,method='Beta-binomial posterior with prior-strength sensitivity',
                  interpretation=f'With {int(successes)} successes in {int(successes+failures)} trials and a Beta({pa:g},{pb:g}) prior, the posterior mean is {mid["posterior_mean"]:.3f} (95% credible {mid["lower"]:.3f} to {mid["upper"]:.3f}). The other rows vary the prior strength while keeping its mean; if they disagree materially, the data are not yet decisive.',
                  assumptions=['Trials are exchangeable Bernoulli draws with one common success probability','The recorded trials are all the trials (no selection of favourable results)','The prior expresses belief before these trials'],
                  not_done=['No pooling across groups or time (a hierarchical model)','Prior parameters were supplied, not elicited or checked against outside evidence'],
                  successes=float(successes),failures=float(failures),posterior_alpha=pa+successes,posterior_beta=pb+failures)


def simulation(d,c):
    a=numeric(d,['mean','sd'],True)
    if np.any(a[:,0]<=0):raise ValueError('Lognormal means must be positive')
    n=integer(c,'samples',10000,100);rho=float(c.get('correlation',0))
    k=len(a)
    if not 0<=rho<1:raise ValueError('Shared-normal correlation must be in [0,1)')
    sigma=np.sqrt(np.log1p((a[:,1]/a[:,0])**2));mu=np.log(a[:,0])-.5*sigma**2
    rng=np.random.default_rng(integer(c,'seed',7,0));z=np.sqrt(rho)*rng.normal(size=(n,1))+np.sqrt(1-rho)*rng.normal(size=(n,k));totals=np.exp(mu+sigma*z).sum(axis=1)
    q=np.quantile(totals,[.1,.5,.8,.9,.95])
    return finish({'quantile':[.1,.5,.8,.9,.95],'total':q},method='Monte Carlo sum of lognormal components with a shared latent factor',
                  interpretation=f'{n} draws over {k} components: median total {q[1]:.4g}, 90th percentile {q[3]:.4g}, mean {totals.mean():.4g} against an analytic mean of {a[:,0].sum():.4g} (Monte Carlo error {totals.std(ddof=1)/np.sqrt(n):.3g}). Dependence rho={rho:g} is imposed on latent normal draws, not as the Pearson correlation of the components. The quantiles describe the supplied assumptions, not measured real-world risk.',
                  assumptions=['Each component is lognormal with the stated mean and standard deviation','Dependence is one shared normal factor with the same weight for every component','Components add; there are no other interactions'],
                  not_done=['No model uncertainty layer: the distribution shapes are taken as given','No calibration against realized totals'],
                  mean=float(totals.mean()),mean_mcse=float(totals.std(ddof=1)/np.sqrt(n)),analytic_mean=float(a[:,0].sum()),samples=n,correlation=rho)


def delphi(d,c):
    numeric(d,['round','estimate','actual']);require(d,['question','expert'])
    if d.duplicated(['question','expert','round']).any():raise ValueError('Duplicate expert/question/round')
    if (d.groupby('question').actual.nunique()>1).any():raise ValueError('A question must have one resolution')
    rows=[]
    for (q,r),g in d.groupby(['question','round']):
        rows.append(dict(question=q,round=r,n=len(g),median=g.estimate.median(),iqr=g.estimate.quantile(.75)-g.estimate.quantile(.25),absolute_error=abs(g.estimate.median()-g.actual.iloc[0])))
    t=pd.DataFrame(rows);fva={str(q):float(g.sort_values('round').absolute_error.iloc[0]-g.sort_values('round').absolute_error.iloc[-1]) for q,g in t.groupby('question')}
    improved=sum(v>0 for v in fva.values())
    return finish(t,method='Delphi round comparison: median, spread and forecast value added',
                  interpretation=f'Across {len(fva)} questions the final-round median beat the first-round median on {improved}. Positive forecast value added means the panel moved toward the outcome; convergence alone is not accuracy. Check whether panel membership changed between rounds.',
                  assumptions=['Each question has one resolved outcome','Round numbers are comparable across questions','Estimates in a round were made before that round\'s feedback'],
                  not_done=['No test of whether shared information drove the convergence','No weighting of experts by past accuracy'],
                  forecast_value_added=fva,questions=len(fva),rounds=int(d['round'].nunique()))


def scoring(d,c):
    numeric(d,['probability','outcome','baseline']);require(d,['event_id']);p=probability(d.probability);b=probability(d.baseline)
    if d.event_id.duplicated().any() or not d.outcome.isin([0,1]).all():raise ValueError('One resolved binary outcome per event is required')
    y=d.outcome.to_numpy();rows=[]
    for lo in np.arange(0,1,.2):
        mask=(p>=lo)&(p<lo+.2 if lo<.8 else p<=1)
        if mask.any():
            n=mask.sum();rate=y[mask].mean();z=1.96;den=1+z*z/n;center=(rate+z*z/(2*n))/den;half=z*np.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/den
            rows.append(dict(bin_lower=lo,count=n,mean_probability=p[mask].mean(),frequency=rate,frequency_lower=center-half,frequency_upper=center+half))
    brier=float(np.mean((p-y)**2));base=float(np.mean((b-y)**2))
    return finish(rows,method='Brier score with reliability bins against a predeclared baseline',
                  interpretation=f'Brier {brier:.4f} against baseline {base:.4f} over {len(y)} events ({"better" if brier<base else "not better"} than the baseline). Reliability bins show the outcome frequency per probability band with Wilson intervals; those intervals assume independent events and express finite-sample uncertainty, not a guarantee of calibration.',
                  assumptions=['Forecasts were issued before the outcomes were known','Events are independent enough for binomial bin intervals','The baseline was declared before scoring'],
                  not_done=['No decomposition into reliability, resolution and uncertainty','No comparison across forecasters or event types'],
                  brier=brier,baseline_brier=base,events=int(len(y)))


def journal(d,c):
    from ..practitioner import score_journal
    if not isinstance(d,dict) or not {'events','revisions'}<=set(d):raise ValueError('JSON requires events and revisions arrays')
    if not c.get('as_of'):raise ValueError('Timezone-aware as_of is required for scoring')
    as_of=str(c['as_of'])
    if len(as_of)==10:as_of+='T00:00:00+00:00'          # a brief's date-only cutoff is read as UTC midnight
    rows=score_journal(d['events'],d['revisions'],as_of=as_of)
    eligible_ids={r['event_id'] for r in rows}
    excluded=[e['event_id'] for e in d['events'] if e['event_id'] not in eligible_ids]
    if not rows:
        return finish({'event_id':excluded,'scoring_status':['unresolved or no eligible forecast']*len(excluded)},method='Forecast journal scoring',status='needs_evidence',
                      interpretation='No eligible resolved forecasts to score yet. Preserve the journal and revisit at the declared resolution date; missing outcomes are not failures.',
                      assumptions=['Revisions carry honest timestamps'],not_done=['Nothing scored: no event has resolved with an eligible pre-resolution forecast'],excluded_event_ids=excluded)
    brier=float(np.mean([r['brier'] for r in rows]));base=float(np.mean([r['baseline_brier'] for r in rows]))
    return finish(rows,method='Forecast journal scoring: latest eligible revision per resolved event',
                  interpretation=f'{len(rows)} resolved events scored, Brier {brier:.4f} against baseline {base:.4f}; {len(excluded)} events excluded as unresolved or without an eligible forecast. Unselected revisions include superseded or ineligible entries, not necessarily errors. Editable timestamps are not authenticated; retain an external append-only history.',
                  assumptions=['Revisions were recorded at the timestamps they carry','One forecast per event counts: the latest revision before the cutoff'],
                  not_done=['No reliability bins (use chapter 9 on the scored rows)','No authentication of the journal timestamps'],
                  brier=brier,baseline_brier=base,excluded_event_ids=excluded,unselected_revision_count=len(d['revisions'])-len(rows))


def crowds(d,c):
    from scipy.stats import trim_mean
    numeric(d,['estimate','actual']);require(d,['question','expert'])
    if d.duplicated(['question','expert']).any() or (d.groupby('question').actual.nunique()>1).any():raise ValueError('Require unique expert/question and one outcome per question')
    rows=[]
    for q,g in d.groupby('question'):
        rows.append(dict(question=q,actual=g.actual.iloc[0],mean=g.estimate.mean(),median=g.estimate.median(),trimmed=trim_mean(g.estimate,.2)))
    table=pd.DataFrame(rows);names=['mean','median','trimmed'];note=''
    a=c.get('extremize_a')
    if a is not None:
        a=float(a)
        if not np.isfinite(a) or a<=0:raise ValueError('extremize_a must be a positive number')
        if ((d.estimate<0)|(d.estimate>1)|(~d.actual.isin([0,1]))).any():raise ValueError('extremize_a applies to probability estimates in [0,1] with binary actuals')
        pooled=table['mean'].clip(1e-6,1-1e-6);logit=np.log(pooled/(1-pooled));table['extremized']=1/(1+np.exp(-a*logit));names.append('extremized')
        note=f' Logit extremization with a={a:g} pushes the pooled probability toward 0 or 1 on the assumption that experts share information; it is scored here by Brier alongside the plain mean and helps only when the pool was too timid.'
    scores={name:float(abs(table[name]-table.actual).mean()) for name in names}
    best=min(scores,key=scores.get)
    return finish(table,method='Crowd aggregation rules (mean, median, trimmed mean'+(', logit extremization' if a is not None else '')+') scored on identical questions',
                  interpretation=f'Over {len(table)} questions the lowest MAE came from the {best} ({scores[best]:.4g}); all rules: '+', '.join(f'{k} {v:.4g}' for k,v in scores.items())+'. Unweighted rules are evaluated on identical questions. Precision weights require earlier resolved questions, and shared bias can defeat every aggregation rule.'+note,
                  assumptions=['Each expert answered every question independently of the others','One resolved outcome per question'],
                  not_done=['No accuracy-weighted combination (needs earlier resolved questions)','No test for shared information among experts'],
                  mae=scores,brier={name:float(((table[name]-table.actual)**2).mean()) for name in names} if a is not None else None,extremize_a=a)


def intervals(d,c):
    a=numeric(d,['actual','lower','median','upper']);alpha=float(c.get('alpha',.2))
    if not 0<alpha<1 or np.any(a[:,1]>a[:,2]) or np.any(a[:,2]>a[:,3]):raise ValueError('Ordered lower <= median <= upper and alpha in (0,1) required')
    y,lo,med,hi=a.T;width=hi-lo;score=width+2/alpha*np.maximum(lo-y,0)+2/alpha*np.maximum(y-hi,0)
    from .core import finish
    coverage=float(np.mean((y>=lo)&(y<=hi)))
    return finish({'timestamp':d['timestamp'] if 'timestamp' in d else np.arange(len(d)),'actual':y,'lower':lo,'median':med,'upper':hi,'covered':(y>=lo)&(y<=hi),'interval_score':score},
                  method='Scoring of supplied prediction intervals',interpretation=f'Supplied intervals covered {coverage:.0%} against a nominal {1-alpha:.0%}; mean width {float(width.mean()):.4g}, mean interval score {float(score.mean()):.4g}. Assess coverage and width jointly. These forecasts must have been issued before outcomes; this file alone cannot authenticate that ordering.',
                  assumptions=['Intervals were issued before the outcomes','Nominal level equals 1 - alpha'],not_done=['No intervals were constructed here; supply a plain timestamp,target series to build conformal intervals'],
                  coverage=coverage,nominal=1-alpha,mean_width=float(width.mean()),mean_interval_score=float(score.mean()),median_mae=float(abs(y-med).mean()))


def hierarchy(d,c):
    numeric(d,['forecast']);require(d,['node']);nodes=c.get('nodes');S=np.asarray(c.get('S'),float)
    if not nodes or d.node.duplicated().any() or set(nodes)!=set(d.node) or len(nodes)!=len(set(nodes)):raise ValueError('Complete unique nodes must match config nodes exactly')
    if S.ndim!=2 or S.shape[0]!=len(nodes) or not np.isfinite(S).all() or np.linalg.matrix_rank(S)!=S.shape[1]:raise ValueError('Finite full-column-rank aggregation matrix required')
    n,m=S.shape
    if not np.allclose(S[-m:],np.eye(m)):raise ValueError('Bottom m rows must be the identity, in declared node order')
    y=d.set_index('node').loc[nodes,'forecast'].to_numpy();ols=S@np.linalg.lstsq(S,y,rcond=None)[0];bottom=S@y[-m:]
    table=pd.DataFrame({'node':nodes,'base':y,'bottom_up':bottom,'OLS':ols});note='MinT omitted: no earlier forecast errors supplied.'
    if 'past_errors' in c:
        e=np.asarray(c['past_errors'],float)
        if e.ndim!=2 or e.shape[1]!=n or len(e)<n+2 or not np.isfinite(e).all():raise ValueError('Past errors need finite rows and one column per node; at least n+2 rows')
        W=np.cov(e,rowvar=False);W=.8*W+.2*np.diag(np.diag(W))
        if np.linalg.eigvalsh(W).min()<=0:raise ValueError('Error covariance is singular; use OLS or acquire more errors')
        inv=np.linalg.inv(W);G=np.linalg.solve(S.T@inv@S,S.T@inv);table['MinT']=S@G@y;note='MinT uses supplied earlier base-forecast errors with fixed 20% diagonal shrinkage.'
    for name in table.columns[2:]:
        if not np.allclose(table[name],S@table[name].to_numpy()[-m:]):raise AssertionError('Reconciliation lost coherence')
    return finish(table,method='Reconciliation of supplied base forecasts (bottom-up, OLS'+(', MinT' if 'MinT' in table else '')+')',
                  interpretation=note+' Coherence does not guarantee improved accuracy or nonnegative forecasts.',
                  assumptions=['The summing matrix S describes the hierarchy completely','Base forecasts are for the same period and units'],
                  not_done=['No base forecasts were fitted here: supply node histories in long form with edges for the full tool','No holdout comparison of the reconciliation methods'],status='provisional',nodes=nodes)


def diffusion(d,c):
    a=numeric(d,['time','adopters'],True);a=a[np.argsort(a[:,0])]
    if len(a)<6 or np.any(np.diff(a[:,0])<=0) or np.any(np.diff(a[:,1])<0):raise ValueError('Six distinct increasing times and nondecreasing cumulative adopters required')
    ceilings=c.get('ceilings')
    if not ceilings or any(not np.isfinite(m) or m<=a[:,1].max() for m in ceilings):raise ValueError('Supply defended ceilings above observed cumulative adoption')
    def bass(t,p,q,m):
        e=np.exp(-(p+q)*t);return m*(1-e)/(1+q/p*e)
    rows=[];fits=[];future=np.asarray(c.get('future_times',np.linspace(a[-1,0],a[-1,0]*2,12)),float)
    if future.ndim!=1 or not len(future) or not np.isfinite(future).all() or np.any(future<a[-1,0]) or np.any(np.diff(future)<=0):raise ValueError('future_times must be finite, increasing and at or after the last observation')
    for m in ceilings:
        fit=least_squares(lambda pars:(bass(a[:,0],*pars,m)-a[:,1])/m,[.03,.3],bounds=([.00001,.00001],[2,3]))
        if not fit.success:raise ValueError('Bass optimizer failed')
        early=least_squares(lambda pars:(bass(a[:-2,0],*pars,m)-a[:-2,1])/m,[.03,.3],bounds=([.00001,.00001],[2,3]))
        if not early.success:raise ValueError('Early Bass optimizer failed')
        holdout_rmse=float(np.sqrt(np.mean((bass(a[-2:,0],*early.x,m)-a[-2:,1])**2)))
        p,q=fit.x;fits.append(dict(ceiling=m,p=p,q=q,early_fit_holdout_rmse=holdout_rmse,fit_rmse=float(np.sqrt(np.mean((bass(a[:,0],p,q,m)-a[:,1])**2))),jacobian_condition=float(np.linalg.cond(fit.jac)),peak_time=float(np.log(q/p)/(p+q)) if q>p else 0.))
        for t,v in zip(future,bass(future,p,q,m)):rows.append(dict(time=t,ceiling=m,cumulative_adopters=v,incidence=(p+q*v/m)*(m-v)))
    return finish(rows,method='Bass diffusion fits under declared market ceilings',fits=fits,ceilings=list(ceilings),
                  interpretation='Alternative ceilings are sensitivity scenarios, not probability bounds. Large Jacobian condition numbers warn of weak local identification. First adoption is not recurring sales.',
                  assumptions=['Cumulative adopters follow a Bass curve under each declared ceiling','The ceiling is a judgment input, not estimated from these data'],
                  not_done=['No sales conversion, repeat purchasing or timing comparison (the chapter 19 tool adds them)'])






def reference(d,c):
    numeric(d,['planned','actual'],True);require(d,['case_id','completed'])
    if d.case_id.duplicated().any() or not d.completed.isin([True,False,0,1]).all() or np.any(d.planned<=0):raise ValueError('Unique cases, binary completion and positive plans required')
    ratio=(d.actual/d.planned).to_numpy();event=d.completed.astype(bool).to_numpy();surv=1.;rows=[]
    for t in sorted(set(ratio)):
        risk=np.sum(ratio>=t);deaths=np.sum((ratio==t)&event);surv*=1-deaths/risk;rows.append(dict(duration_ratio=t,at_risk=risk,completed=deaths,survival=surv))
    table=pd.DataFrame(rows);quantiles={}
    for p in [.5,.8,.9]:
        hits=table[table.survival<=1-p];quantiles[str(p)]=float(hits.duration_ratio.iloc[0]) if len(hits) else None
    known={k:v for k,v in quantiles.items() if v is not None}
    return finish(table,method='Kaplan-Meier distribution of actual/planned ratios in the reference class',
                  interpretation=f'{len(d)} reference cases, {int(event.sum())} completed. '+(' '.join(f'{float(k):.0%} of cases finished within {v:.2f}x plan;' for k,v in known.items()) if known else 'No quantile is identified yet;')+' unidentified upper quantiles stay null rather than being invented. Kaplan-Meier treats incomplete actual durations as right-censored elapsed time, which requires noninformative censoring; abandonment as failure may violate it.',
                  assumptions=['The reference class was chosen before looking at the outcome','Censoring is noninformative: unfinished cases are not systematically the worst'],
                  not_done=['No adjustment for differences between the new case and the class (a regression on case features)','No decision-loss percentile was chosen; the reader picks it'],
                  quantiles=quantiles,cases=int(len(d)),completed=int(event.sum()))


def decision(d,c):
    numeric(d,['probability','outcome']);require(d,['event_id']);p=probability(d.probability);y=d.outcome.to_numpy()
    if d.event_id.duplicated().any() or not np.isin(y,[0,1]).all():raise ValueError('Unique resolved binary events required')
    fp=float(c.get('false_alarm_cost',2));fn=float(c.get('miss_cost',8))
    if min(fp,fn)<=0 or not np.isfinite([fp,fn]).all():raise ValueError('Positive finite costs required')
    threshold=fp/(fp+fn);action=p>=threshold;loss=fp*(action&(y==0))+fn*(~action&(y==1));baseline=np.minimum(fp*np.sum(y==0),fn*np.sum(y==1))/len(y)
    return finish({'event_id':d.event_id,'probability':p,'outcome':y,'action':action,'loss':loss,'cumulative_loss':np.cumsum(loss)},method='Cost-weighted decision threshold applied to probability forecasts',
                  interpretation=f'Acting when probability >= {threshold:.3f} (false alarm {fp:g}, miss {fn:g}) gave mean loss {loss.mean():.4g} per event over {len(y)} events; the best constant policy in hindsight costs {baseline:.4g}. The threshold is Bayes-optimal only for calibrated probabilities and the stated loss structure; the hindsight cost is a diagnostic, not a preselected baseline.',
                  assumptions=['Probabilities are calibrated','Costs are fixed per event and known in advance'],
                  not_done=['No recalibration of the probabilities before thresholding','No value-of-information analysis for waiting'],
                  threshold=threshold,brier=float(np.mean((p-y)**2)),mean_loss=float(loss.mean()),best_constant_policy_hindsight_cost=float(baseline))


def directed(d,c):
    from ..practitioner import calibrate_scale,launch_trials,cohort_units
    mode=c.get('mode','launch')
    if mode in ('history','estimate'):
        require(d,['timestamp','target'])
        if mode=='estimate' or len(d)<max(36,4*integer(c,'horizon',12)):
            return finish({'available_observations':[len(d)]},method='Chapter 27 routing check',status='needs_evidence',
                          interpretation=f'{len(d)} observations do not establish seasonal structure (the rolling comparison needs at least {max(36,4*integer(c,"horizon",12))}). Supply defensible reference products, population/reach/trial assumptions and a distinct cross-check; no numeric forecast is manufactured.',
                          assumptions=[],not_done=['No forecast: history too short or mode=estimate; use launch mode with calibration products or the reconcile-tdbu desk model'],
                          required_evidence=['Target and decision','Comparable outcomes','Defended proxy inputs','Uncertainty and scoring plan'])
        return compare(d,c,27)
    if mode!='launch':raise ValueError('mode must be launch, history or estimate')
    columns=['eligible_buyers','awareness','availability_given_awareness','interest','units_per_buyer_24m','observed_units_24m'];a=numeric(d,columns,True);require(d,['split'])
    probability(a[:,1:4]);train=d.split=='calibration';test=d.split=='validation'
    if train.sum()<3 or test.sum()<2 or not (train|test).all():raise ValueError('Need at least 3 calibration and 2 validation products with explicit split')
    exposure=np.prod(a[:,:5],axis=1);scale=calibrate_scale(exposure[train],a[train,5]);new=c.get('new_product',{})
    keys=columns[:4]
    if any(k not in new for k in keys):raise ValueError('new_product requires eligible_buyers, awareness, availability_given_awareness, interest')
    vals=np.asarray([new[k] for k in keys],float);probability(vals[1:])
    if not np.isfinite(vals[0]) or vals[0]<0:raise ValueError('Eligible buyers must be finite and nonnegative')
    if 'declared_trial_total' in c:
        total=float(c['declared_trial_total'])
    else:
        if not c.get('trial_conversion_assumption'):raise ValueError('State trial_conversion_assumption explicitly or supply a defended declared_trial_total; mature sales do not identify unique trials')
        total=float(vals.prod()*scale)
    if not np.isfinite(total) or total<0 or total>vals[:3].prod():raise ValueError('Trial total must be finite, nonnegative and no larger than jointly reached eligible buyers')
    h=integer(c,'horizon',24,24)
    if 'repeat_kernel' in c:
        kernel=np.asarray(c['repeat_kernel'],float)
        if kernel.ndim!=1 or len(kernel)!=h or not np.isfinite(kernel).all() or np.any(kernel<0):raise ValueError('repeat_kernel needs one finite nonnegative units-per-trier value per horizon month')
    else:
        if 'repeat_rate' not in c:raise ValueError('Supply repeat_rate or repeat_kernel explicitly')
        repeat=float(c['repeat_rate'])
        if repeat<0 or not np.isfinite(repeat):raise ValueError('Repeat rate must be nonnegative and finite')
        kernel=np.r_[1.,np.full(h-1,repeat)]
    rows=[]
    for peak in [3,4,5]:
        trial=launch_trials(total,peak=peak,horizon=h,denominator='horizon');units=cohort_units(trial,kernel)
        for month in range(h):rows.append(dict(month=month+1,peak=peak,trials=trial[month],units=units[month]))
    table=pd.DataFrame(rows);year1={int(p):float(g.units[:12].sum()) for p,g in table.groupby('peak')}
    return finish(table,method='Exposure model calibrated on reference products, trial timing curves (peak month 3, 4, 5) and repeat cohorts',
                  interpretation=f'Shared scale {scale:.3f} from {int(train.sum())} calibration products (held-out MAE {float(abs(exposure[test]*scale-a[test,5]).mean()):.4g} on {int(test.sum())}); trial total {total:,.0f}. Year-one units: '+', '.join(f'peak {p}: {v:,.0f}' for p,v in year1.items())+'. Mature-sales calibration does not identify trial conversion separately from repeat; transferring the scale is an additional assumption. Peaks 3/4/5 are scenarios, not probabilities; the standard allocates 80% of the declared trial total to year one.',
                  assumptions=['The exposure-to-units relationship of the reference products transfers to the new product','Trial timing follows the gamma launch curve with the stated peak month','Repeat purchasing follows the supplied kernel (units per original trier per month)'],
                  not_done=['No independent cross-check from a different mechanism (channel capacity, market share)','No uncertainty band: the three peaks are timing scenarios, not a distribution','Media, distribution and awareness build are inputs here, not modelled (see reconcile-tdbu)'],
                  scale=scale,trial_total=total,held_out_mae=float(abs(exposure[test]*scale-a[test,5]).mean()),year_one_units=year1)
