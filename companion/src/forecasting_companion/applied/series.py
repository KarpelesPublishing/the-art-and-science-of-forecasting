"""Past-only evaluation shared by chapter workshops and applied entry points."""
import numpy as np
import pandas as pd
from .core import time_frame,integer,finish


CHAPTER_POOL={4:'smoothing',6:'arima',12:'full',27:'full'}


def compare(frame,c,chapter):
    """Chapters 4, 6, 12 and 27: the real engine, with the chapter's method pool by default.

    Config keys: horizon, season, frequency, as_of, pool (smoothing|arima|full|baseline),
    transform (auto|none|log), origins (max selection origins, default 5).
    Short valid histories return status=provisional with a persistence baseline and,
    when a full cycle exists, a seasonal-naive scenario, and no validation claims.
    """
    from ..engine import forecast_series,POOLS
    h=integer(c,'horizon',12)
    from ..profile import profile_series
    auto=c.get('season')=='auto' or 'season' not in c
    profile=profile_series(frame,{k:v for k,v in c.items() if k!='season' or not auto})   # always look first; warnings survive into the summary
    season=int(profile['season']) if auto else integer(c,'season',12)
    regressor_columns=list(c.get('regressors') or [])
    route_pool={'intermittent':'intermittent','multiseasonal':'multiseasonal','regressors':'regressors'}.get(profile['route'])
    if regressor_columns:route_pool='regressors'
    pool=c.get('pool') or (route_pool if chapter==12 and route_pool else CHAPTER_POOL.get(chapter,'full'))
    if pool not in POOLS:raise ValueError(f'pool must be one of {sorted(POOLS)}')
    transform=c.get('transform','auto');origins=integer(c,'origins',5,2)
    criterion=c.get('criterion');conformal=bool(c.get('conformal',True))
    frame,observed=fill_gaps(frame,profile,c)
    f,freq=time_frame(frame,c,minimum=2)
    y=f.target.to_numpy(float)
    regressors=None
    if pool=='regressors':
        from ..engine_regressors import validate_regressors
        if not regressor_columns:regressor_columns=[col for col in profile.get('extra_columns',[]) if col in frame.columns]
        if not regressor_columns:raise ValueError('the regressors pool needs `regressors`: the driver columns present in the history and in future_regressors')
        future=c.get('future_regressors')
        if isinstance(future,str):future=pd.read_csv(future)
        elif isinstance(future,list):future=pd.DataFrame(future)
        Xh,Xf=validate_regressors(f,future,regressor_columns,h)
        regressors={'X':Xh,'future':Xf,'columns':regressor_columns}
    periods=c.get('periods') or (profile['seasonality']['periods'] if pool=='multiseasonal' else None)
    minimum=minimum_history(h,season)
    if len(y)<minimum:
        return provisional(y,f,h,season,freq,minimum,profile)
    table,summary=forecast_series(y,f.timestamp,h,season,pool=pool,freq=freq,transform=transform,max_origins=origins,criterion=criterion,periods=periods,regressors=regressors,country=c.get('country'),observed=observed,conformal=conformal,per_horizon_buckets=bool(c.get('per_horizon_buckets',False)))
    skipped=summary.get('skipped') or {}
    not_done=([] if pool=='regressors' else ['No regressors, promotions or calendar effects (pool regressors, chapter 13 or 16 add them)'])+['No hierarchy or coherence constraints (chapter 18)',('Conformal bands pool the origin and holdout residuals of the selected model; chapter 17 calibrates on a longer window' if conformal else 'No conformal bands (set conformal: true)')]
    if skipped:not_done.append('Skipped candidates: '+'; '.join(f'{k} ({v})' for k,v in skipped.items()))
    method=summary.pop('method','Rolling-origin model comparison with final holdout');interpretation=summary.pop('interpretation')
    summary.pop('status',None)
    scenario=break_scenario(y,f,h,season,freq,profile)
    if scenario:
        table['break_scenario']=scenario['forecast'];summary['break_scenario']=scenario
        if 'conformal_lower' in table:
            radius=((table['conformal_upper']-table['conformal_lower'])/2).to_numpy()
            z=1.2816;k_post=scenario['band']['k']
            s_post=scenario['s_post'] if scenario['s_post'] is not None else float(radius[0])/z
            widen=np.array([np.sqrt(radius[j]**2+z**2*s_post**2*(1+(1/k_post if scenario['shifted_steps'][j] else 0))) for j in range(len(radius))])
            table['break_scenario_low']=table['break_scenario']-widen;table['break_scenario_high']=table['break_scenario']+widen
            scenario['band_note']=(f'break_scenario_low/high: a scenario band, not a measured interval. The pre-shift conformal radius is combined in quadrature with the post-shift noise (s_post {s_post:.4g} from {k_post} points) and, on re-levelled steps, the shift estimate\'s standard error; no coverage guarantee.')
            scenario['band'].update(s_post=s_post,mean_radius=float(widen.mean()))
        interpretation+=' Profile warning: '+scenario['note']
        not_done.append('The validated selection does not act on the recent level shift; break_scenario is a judgment re-levelling, not a validated forecast')
    return finish(table,method=method,interpretation=interpretation,status='passed',
                  assumptions=['Regular series with the declared season and no missing periods','The training history\'s pattern continues over the horizon (no regime change)','Specifications are frozen on the first training slice, so later actuals cannot steer selection'],
                  not_done=not_done,profile=profile,gaps_filled=int((~observed).sum()) if observed is not None else 0,**summary)


def provisional(y,f,h,season,freq,minimum,profile):
    """History too short for the rolling comparison: the best placeholder a careful forecaster would write
    down, labelled as such. With at least one full season: last season's pattern re-levelled by the recent
    growth (the last quarter-season against the same periods a year earlier), with a scenario range from
    the in-sample errors of that rule. Without a season: the last value with a range from the observed
    period-to-period changes. Nothing is validated and the status says so."""
    dates=pd.date_range(f.timestamp.iloc[-1],periods=h+1,freq=freq)[1:]
    n=len(y)
    if season>1 and n>=season+1:
        k=max(1,min(3,season//4))
        recent=y[-k:].mean();same=y[-season-k:-season].mean() if n>=season+k else y[:k].mean()
        growth=float(recent/same) if same>0 and recent>0 else 1.0
        growth=float(np.clip(growth,0.5,2.0))
        base=np.resize(y[-season:],h)
        forecast=base*growth
        insample=[]
        for t in range(season,n):
            g=(y[max(season,t-k):t].mean()/y[max(0,t-season-k):t-season].mean()) if t-season-k>=0 and y[t-season-k:t-season].mean()>0 else 1.0
            insample.append(y[t]-y[t-season]*float(np.clip(g,0.5,2.0)))
        spread=float(np.quantile(np.abs(insample),0.8)) if insample else float(np.std(np.diff(y)))
        method='Provisional placeholder: last season re-levelled by recent growth (not validated)';model='Provisional seasonal naive with growth'
        note=f'the last full season repeated and re-levelled by the recent growth of {growth:.3f} (last {k} periods against the same periods a season earlier); the range is the 80th percentile of that rule\'s in-sample errors ({len(insample)} points), a scenario band, not a measured interval'
        assumptions=[f'The seasonal pattern of the last {season} periods repeats',f'The recent growth ratio {growth:.3f} persists over the horizon']
    else:
        forecast=np.repeat(y[-1],h);diffs=np.diff(y) if n>1 else np.array([0.0])
        spread=float(np.quantile(np.abs(diffs),0.8))*np.sqrt(np.arange(1,h+1)) if len(diffs) else np.zeros(h)
        method='Provisional persistence placeholder (not validated)';model='Provisional naive'
        note=f'the last value ({y[-1]:.4g}) repeated; the range grows with the square root of the horizon from the observed period-to-period changes, a scenario band, not a measured interval'
        assumptions=['The last observation is the best available guess for the next periods']
    table=pd.DataFrame({'timestamp':dates,'forecast':forecast,'model':model,'scenario_low':forecast-spread,'scenario_high':forecast+spread})
    if season>1 and n>=season:table['seasonal_naive_scenario']=np.resize(y[-season:],h)
    return finish(table,method=method,status='provisional',profile=profile,
                  interpretation=f'Only {n} observations; the rolling comparison needs {minimum} (a training slice of 2 seasons + 1 horizon, then 3 more horizons for two selection origins and a holdout). The placeholder is {note}. Nothing was validated against held-out data. Shorten the horizon, supply more history, or carry this as a labelled scenario and score it when the actuals arrive.',
                  assumptions=assumptions,
                  not_done=[f'No model comparison: {minimum-n} more observations are needed at horizon {h} and season {season}','No measured interval coverage: scenario_low/high are in-sample scenario bounds','No fitted seasonal or trend model'],
                  selected=model,validation=[],minimum_required=minimum,observations=int(n),scenario_spread=float(np.mean(spread)) if np.ndim(spread) else float(spread))


def break_scenario(y,f,h,season,freq,profile):
    """When the profile finds a recent level shift, the validated selection was trained mostly before it and its
    holdout straddles it; a re-levelled scenario (last season's shape at the post-break level) is the number a
    careful forecaster puts beside the model's, and chapter 24's policies decide between them."""
    b=profile.get('break') or {}
    if not b.get('found') or b.get('periods_since',10**9)>2*max(season,1) or len(y)<2*season+b['periods_since']:return None
    k=int(b['periods_since']);pos=len(y)-k
    if season>1:
        post=y[pos:];same=y[pos-season:pos-season+k] if pos-season>=0 else None
        d=(post-same) if same is not None and len(same)==len(post) else None
        shift=float(d.mean()) if d is not None else float(b['level_after']-b['level_before'])
        base=np.resize(y[-season:],h)
        shifted=[(len(y)-season+j)<pos for j in range(h)]
        forecast=np.array([base[j]+shift if shifted[j] else base[j] for j in range(h)])
    else:
        post=y[pos:];d=post-post.mean();shift=float(b['level_after']-b['level_before'])
        forecast=np.repeat(float(post.mean()),h);shifted=[True]*h
    s_post=float(np.std(d,ddof=1)) if d is not None and len(d)>=3 else None
    return dict(position=int(pos),periods_since=k,shift=shift,forecast=[float(v) for v in forecast],shifted_steps=shifted,
                s_post=s_post,se_shift=(s_post/np.sqrt(k) if s_post is not None else None),band=dict(level=0.8,guaranteed=False,k=k),
                note=f'a level shift {k} periods before the end ({shift:+.4g}); the validated selection was chosen at origins that mostly predate it. The break_scenario column re-levels last season\'s pattern by the shift; use it, or chapter 24\'s adaptive policy, when the shift is believed to persist.')


def fill_gaps(frame,profile,c):
    """Apply the profile's gap rule: missing periods and empty targets are filled (interpolated, or zero for
    intermittent demand) so the engine sees a regular series, and an `observed` mask marks the fills so they
    are used for fitting but never scored. Refused gaps raise with the profile's reason."""
    action=profile['gaps']['action']
    if action=='none':return frame,None
    if action=='refuse':raise ValueError('gaps: '+profile['gaps']['reason'])
    f=frame.copy();f['timestamp']=pd.to_datetime(f['timestamp'],utc=True,errors='raise');f=f.sort_values('timestamp')
    if c.get('as_of'):f=f[f.timestamp<=pd.to_datetime(c['as_of'],utc=True)]
    freq=c.get('frequency') or profile['frequency']['frequency']
    grid=pd.date_range(f.timestamp.iloc[0],f.timestamp.iloc[-1],freq=freq)
    f=f.set_index('timestamp').reindex(grid);f.index.name='timestamp'
    observed=f['target'].notna().to_numpy()
    f['target']=pd.to_numeric(f['target'],errors='coerce')
    f['target']=f['target'].fillna(0.0) if action=='zero' else f['target'].interpolate(limit_direction='both')
    for col in f.columns:
        if col!='target':f[col]=f[col].interpolate(limit_direction='both') if pd.api.types.is_numeric_dtype(f[col]) else f[col].ffill().bfill()
    return f.reset_index(),observed


def minimum_history(h,season):
    """Observations the engine needs: a first training slice of 2 seasons + 1 horizon (at least 24),
    then two selection origins and an untouched final holdout, each one horizon long. Monthly data with
    a 12-month horizon needs 72 points; a 6-month horizon needs 48; a 3-month horizon needs 36."""
    return max(2*season+h if season>1 else h+8,24)+3*h


def kalman(frame,c):
    f,_=time_frame(frame,c,minimum=30);y=f.target.to_numpy(float);cut=max(10,len(y)//2)
    def filt(obs,Q,R):
        m=float(obs[0]);P=R;means=[];vars=[];res=[];ll=0.
        for z in obs:
            pp=P+Q;v=z-m;F=pp+R;ll+=np.log(F)+v*v/F
            m+=pp/F*v;P=pp*R/F;means.append(m);vars.append(P);res.append(v/np.sqrt(F))
        return np.array(means),np.array(vars),np.array(res),ll
    scale=max(float(np.var(np.diff(y[:cut]))),1e-6)
    grid=[(scale*q,scale*r) for q in [.01,.1,.5] for r in [.1,.5,1.]]
    if ('Q' in c)!=('R' in c):raise ValueError('Supply both Q and R or neither')
    Q,R=(float(c['Q']),float(c['R'])) if 'Q' in c else min(grid,key=lambda qr:filt(y[:cut],*qr)[3])
    if min(Q,R)<=0 or not np.isfinite([Q,R]).all():raise ValueError('Q and R must be finite and positive')
    m,P,z,_=filt(y,Q,R)
    from statsmodels.stats.diagnostic import acorr_ljungbox
    diagnostic=acorr_ljungbox(z[cut:],lags=[min(5,len(z[cut:])//4)],return_df=True)
    return finish({'timestamp':f.timestamp,'observed':y,'filtered_state':m,'lower':m-1.96*np.sqrt(P),'upper':m+1.96*np.sqrt(P)},method='Local-level Kalman filter with manual or first-half-selected noise variances',
                  interpretation=f'Q={Q:.4g}, R={R:.4g} '+('supplied explicitly. ' if 'Q' in c else 'chosen on the first half only. ')+f'Second-half innovation mean {float(z[cut:].mean()):.3g}, Ljung-Box p={float(diagnostic.lb_pvalue.iloc[0]):.3f}. Bands describe a latent state conditional on a local-level Gaussian model, not future observations or verified truth.',
                  assumptions=['Local level: the level follows a random walk with Gaussian noise','Observation noise is Gaussian with constant variance'],
                  not_done=['No trend, seasonal or cycle component (set model to local linear trend or seasonal for the full tool)','No forecast beyond the filtered state'],
                  Q=Q,R=R,selection_end=str(f.timestamp.iloc[cut-1]),test_innovation_mean=float(z[cut:].mean()),ljung_box_p=float(diagnostic.lb_pvalue.iloc[0]))


def decomposition(frame,c):
    from statsmodels.tsa.seasonal import STL
    s=integer(c,'season',12);f,_=time_frame(frame,c,minimum=3*s);y=f.target.to_numpy(float)
    fitted=STL(y,period=s,robust=True).fit();cut=len(y)-s;past=STL(y[:cut],period=s,robust=True).fit()
    revision=np.abs(fitted.trend[:cut]-past.trend)
    return finish({'timestamp':f.timestamp,'observed':y,'trend':fitted.trend,'seasonal':fitted.seasonal,'remainder':fitted.resid},method='Descriptive STL decomposition with a vintage comparison',
                  interpretation=f'STL with period {s} on {len(y)} observations. Refitting without the last {s} points moved the trend by up to {float(revision.max()):.4g}: full-series components describe the past, and their revision after adding observations shows why they cannot be used as origin-known backtest features.',
                  assumptions=['The seasonal period is the declared season','Robust STL weights limit the influence of outliers'],
                  not_done=['No forecast: decomposition is descriptive (chapter 4 or 12 forecast the series)','No test of chaotic sensitivity beyond the vintage comparison'],
                  max_trend_revision=float(revision.max()))


