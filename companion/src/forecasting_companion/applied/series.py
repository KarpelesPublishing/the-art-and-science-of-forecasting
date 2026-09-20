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
    h=integer(c,'horizon',12);season=integer(c,'season',12)
    pool=c.get('pool',CHAPTER_POOL.get(chapter,'full'))
    if pool not in POOLS:raise ValueError(f'pool must be one of {sorted(POOLS)}')
    transform=c.get('transform','auto');origins=integer(c,'origins',5,2)
    f,freq=time_frame(frame,c,minimum=2)
    y=f.target.to_numpy(float)
    minimum=minimum_history(h,season)
    if len(y)<minimum:
        dates=pd.date_range(f.timestamp.iloc[-1],periods=h+1,freq=freq)[1:]
        table=pd.DataFrame({'timestamp':dates,'forecast':np.repeat(y[-1],h),'model':'Provisional naive'})
        if season>1 and len(y)>=season:table['seasonal_naive_scenario']=np.resize(y[-season:],h)
        return finish(table,method='Provisional persistence baseline (history too short for the rolling comparison)',status='provisional',
                      interpretation=f'Only {len(y)} observations; the rolling comparison needs {minimum} (a training slice of 2 seasons + 1 horizon, then 3 more horizons for two selection origins and a holdout). The forecast repeats the last value ({y[-1]:.4g})'+(' with a seasonal-naive scenario column' if 'seasonal_naive_scenario' in table else '')+'. Nothing was validated: no calibrated interval or fitted seasonal parameters are asserted. Shorten the horizon, supply more history, or treat this as a placeholder.',
                      assumptions=['The last observation is the best available guess for the next periods'],
                      not_done=[f'No model comparison: {minimum-len(y)} more observations are needed at horizon {h} and season {season}','No intervals','No seasonal model'],
                      selected='Naive',validation=[],minimum_required=minimum,observations=int(len(y)))
    table,summary=forecast_series(y,f.timestamp,h,season,pool=pool,freq=freq,transform=transform,max_origins=origins)
    skipped=summary.get('skipped') or {}
    not_done=['No regressors, promotions or calendar effects (chapter 13 or 16 add them)','No hierarchy or coherence constraints (chapter 18)','Intervals are the selected model\'s own plus empirical residual quantiles; no distribution-free guarantee (chapter 17)']
    if skipped:not_done.append('Skipped candidates: '+'; '.join(f'{k} ({v})' for k,v in skipped.items()))
    method=summary.pop('method','Rolling-origin model comparison with final holdout');interpretation=summary.pop('interpretation')
    summary.pop('status',None)
    return finish(table,method=method,interpretation=interpretation,status='passed',
                  assumptions=['Regular series with the declared season and no missing periods','The training history\'s pattern continues over the horizon (no regime change)','Specifications are frozen on the first training slice, so later actuals cannot steer selection'],
                  not_done=not_done,**summary)


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


