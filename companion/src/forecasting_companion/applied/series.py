"""Past-only evaluation shared by chapter workshops and applied entry points."""
import numpy as np
import pandas as pd
from .core import time_frame,integer,result


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
    minimum=max(2*season+h if season>1 else h+8,24)+2*h   # two selection origins plus the final holdout
    if len(y)<minimum:
        dates=pd.date_range(f.timestamp.iloc[-1],periods=h+1,freq=freq)[1:]
        table=pd.DataFrame({'timestamp':dates,'forecast':np.repeat(y[-1],h),'model':'Provisional naive'})
        if season>1 and len(y)>=season:table['seasonal_naive_scenario']=np.resize(y[-season:],h)
        return table,dict(status='provisional',selected='Naive',validation=[],interpretation=f'Only {len(y)} observations; the rolling comparison requires {minimum}. Persistence is a provisional baseline, not a validated seasonal model. No calibrated interval or fitted seasonal parameters are asserted.')
    table,summary=forecast_series(y,f.timestamp,h,season,pool=pool,freq=freq,transform=transform,max_origins=origins)
    summary['status']='passed'
    return table,summary


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
    return result({'timestamp':f.timestamp,'observed':y,'filtered_state':m,'lower':m-1.96*np.sqrt(P),'upper':m+1.96*np.sqrt(P)},method='Local-level Kalman filter',Q=Q,R=R,selection_end=str(f.timestamp.iloc[cut-1]),test_innovation_mean=float(z[cut:].mean()),ljung_box_p=float(diagnostic.lb_pvalue.iloc[0]),interpretation='Bands describe a latent state conditional on a local-level Gaussian model, not future observations or verified truth. '+('Q/R supplied explicitly.' if 'Q' in c else 'Q/R chosen on the first half only.'))


def decomposition(frame,c):
    from statsmodels.tsa.seasonal import STL
    s=integer(c,'season',12);f,_=time_frame(frame,c,minimum=3*s);y=f.target.to_numpy(float)
    fitted=STL(y,period=s,robust=True).fit();cut=len(y)-s;past=STL(y[:cut],period=s,robust=True).fit()
    revision=np.abs(fitted.trend[:cut]-past.trend)
    return result({'timestamp':f.timestamp,'observed':y,'trend':fitted.trend,'seasonal':fitted.seasonal,'remainder':fitted.resid},method='Descriptive STL with vintage comparison',max_trend_revision=float(revision.max()),interpretation='Full-series components describe the past. Their revision after adding observations demonstrates why they cannot be used as origin-known backtest features.')


def monitoring(frame,c):
    f,_=time_frame(frame,c,minimum=80);y=f.target.to_numpy(float);warm=integer(c,'calibration_size',30,10)
    if warm>=len(y)//2:raise ValueError('Reserve at least half the series for monitoring')
    mu=y[:warm].mean();sd=y[:warm].std(ddof=1)
    if sd<=0:raise ValueError('Stable calibration window needs positive variability')
    # Calibrate a finite-horizon max statistic under an explicitly assumed iid normal null.
    rng=np.random.default_rng(integer(c,'seed',24,0)); z=rng.normal(size=(2000,len(y)-warm));s=np.zeros(2000);mx=s.copy()
    for j in range(z.shape[1]):s=np.maximum(0,s+z[:,j]-.5);mx=np.maximum(mx,s)
    threshold=float(np.quantile(mx,.95));s=0.;last=warm;rows=[]
    for t in range(warm,len(y)):
        frozen=mu;rolling=y[max(0,t-20):t].mean();adaptive=y[last:t].mean() if t>last else y[t-1]
        s=max(0,s+(y[t]-mu)/sd-.5);alarm=s>threshold
        rows.append(dict(timestamp=f.timestamp.iloc[t],actual=y[t],frozen=frozen,rolling=rolling,adaptive=adaptive,cusum_before_reset=s,alarm=alarm))
        if alarm:s=0.;last=t
    table=pd.DataFrame(rows)
    return table,dict(method='One-sided CUSUM and alarm-triggered refitting',threshold=threshold,alarm_count=int(table.alarm.sum()),mae={k:float(abs(table.actual-table[k]).mean()) for k in ['frozen','rolling','adaptive']},interpretation='Threshold targets a 5% chance of any alarm over this horizon under an iid normal null with plug-in mean/SD; dependence or parameter uncertainty changes that rate. Alarms are known only after the observation. Adaptive forecasts restart estimation after an alarm; fixed monitoring reference may cause repeated alarms.')


def pretrained(frame,c):
    import torch
    from chronos import ChronosPipeline
    h=integer(c,'horizon',12);s=integer(c,'season',12);f,freq=time_frame(frame,c,minimum=max(3*s,h+30))
    y=f.target.to_numpy(float);torch.manual_seed(integer(c,'seed',15,0));torch.set_num_threads(1)
    model='amazon/chronos-t5-tiny';revision='29d808298f1a62493e7b9a5e08529d0d930fa189'
    pipeline=ChronosPipeline.from_pretrained(model,revision=revision,device_map='cpu',torch_dtype=torch.float32)
    with torch.inference_mode():draws=pipeline.predict([torch.tensor(y[:-h],dtype=torch.float32),torch.tensor(y,dtype=torch.float32)],prediction_length=h,num_samples=64).numpy()
    lo,med,hi=np.quantile(draws,[.1,.5,.9],axis=1);actual=y[-h:]
    dates=pd.date_range(f.timestamp.iloc[-1],periods=h+1,freq=freq)[1:]
    return result({'timestamp':dates,'lower':lo[1],'forecast':med[1],'upper':hi[1]},method=model,revision=revision,test_mae=float(abs(actual-med[0]).mean()),baseline_mae=float(abs(actual-np.resize(y[:-h][-s:],h)).mean()),test_coverage=float(np.mean((actual>=lo[0])&(actual<=hi[0]))),interpretation='64 sampled paths yield marginal 80% bands. One holdout cannot establish calibration; pretrained corpus exclusion is not certified.')


def prophet_fit(frame,c):
    from prophet import Prophet
    seed=integer(c,'seed',16,0);np.random.seed(seed)
    h=integer(c,'horizon',12);f,freq=time_frame(frame,c,minimum=max(4*h,60));y=f.target.to_numpy(float)
    d=pd.DataFrame({'ds':f.timestamp.dt.tz_localize(None),'y':y});end=len(d)-h
    def fit(stop,prior):
        m=Prophet(changepoint_prior_scale=prior,weekly_seasonality=c.get('weekly',False),yearly_seasonality=c.get('yearly',True),daily_seasonality=False,uncertainty_samples=200)
        m.fit(d.iloc[:stop],seed=seed);return m
    scores=[]
    for p in [.001,.05,.5]:
        m=fit(end-h,p);pred=m.predict(d[['ds']].iloc[end-h:end]);scores.append(float(abs(pred.yhat.to_numpy()-y[end-h:end]).mean()))
    chosen=[.001,.05,.5][int(np.argmin(scores))];m=fit(end,chosen);test=m.predict(d[['ds']].iloc[end:]);final=fit(len(d),chosen)
    dates=pd.date_range(d.ds.iloc[-1],periods=h+1,freq=freq)[1:];future=final.predict(pd.DataFrame({'ds':dates}))
    return result({'timestamp':dates,'lower':future.yhat_lower,'forecast':future.yhat,'upper':future.yhat_upper},method='Prophet',prior=chosen,validation_mae=scores,test_mae=float(abs(test.yhat.to_numpy()-y[end:]).mean()),interpretation='Calendar regressors are not supplied in this generic application. The chapter demonstration separately tests event calendars. Bands are nominal model-based 80% intervals, not certified coverage.')
