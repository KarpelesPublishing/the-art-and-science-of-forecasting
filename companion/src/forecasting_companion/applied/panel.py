"""Panel applications with explicit feature availability and held-out entities."""
import numpy as np
import pandas as pd
from .core import require,numeric,time_frame,integer,result


def panel_analysis(chapter,d,c):
    require(d,['series_id','timestamp','target']);numeric(d,['target'])
    if chapter==13:
        return retail_ml(d,c)
    groups=[]
    for name,g in d.groupby('series_id'):
        f,_=time_frame(g,c,minimum=50);f['series_id']=str(name);groups.append(f)
    if len(groups)<4:raise ValueError('At least four related series are required for a panel lesson')
    reference=groups[0].timestamp.reset_index(drop=True)
    if any(not g.timestamp.reset_index(drop=True).equals(reference) for g in groups[1:]):raise ValueError('Neural panel requires aligned calendar timestamps across entities')
    return neural(groups,c)


def retail_ml(d,c):
    """Chapter 13: gradient boosting on a panel with declared covariates.

    Leakage-safe grouped lags and rolling means, calendar and entity features, covariates
    declared in config (only those known in advance may enter at their own timestamp; the
    rest are lagged one period), rolling-origin evaluation against seasonal naive, direct
    multi-step (one booster per step) or recursive strategy, a feature-group ablation, and
    additive contributions for a sample of rows.
    """
    import lightgbm as lgb
    from .core import expanding_origins, finish
    season=integer(c,'season',7);h=integer(c,'horizon',7);seed=integer(c,'seed',13,0)
    groups=[]
    for name,g in d.groupby('series_id'):
        f,freq=time_frame(g,c,minimum=35);f['series_id']=str(name);groups.append(f)
    if len(groups)<4:raise ValueError('At least four related series are required for a panel lesson')
    f=pd.concat(groups).sort_values(['series_id','timestamp']).reset_index(drop=True)
    available=[col for col in f.columns if col not in ('series_id','timestamp','target')]
    covariates=c.get('covariates',[col for col in ('promo','price') if col in available])
    if not isinstance(covariates,list) or any(col not in available for col in covariates):raise ValueError(f'covariates must name numeric columns present in the data; available: {available}')
    if covariates:numeric(f,covariates)
    known=c.get('known_in_advance',list(covariates))
    if not isinstance(known,list) or not set(known)<=set(covariates):raise ValueError('known_in_advance must be a subset of covariates')
    strategy=c.get('strategy','direct')
    if strategy not in ('direct','recursive'):raise ValueError("strategy must be 'direct' or 'recursive'")
    lags=c.get('lags',[1,season]);rolling=c.get('rolling',[season])
    if not all(isinstance(v,int) and v>=1 for v in lags+rolling):raise ValueError('lags and rolling must be positive integers')
    n_origins=integer(c,'origins',3,2);do_ablation=bool(c.get('ablation',True));shap_rows=integer(c,'shap_rows',1,0)
    daily=pd.tseries.frequencies.to_offset(freq).name.upper() in ('D','B')
    f['entity']=pd.Categorical(f.series_id).codes
    f['calendar']=f.timestamp.dt.dayofweek if daily else f.timestamp.dt.month
    for lag in lags:f[f'lag{lag}']=f.groupby('series_id').target.shift(lag)
    for w in rolling:f[f'roll{w}']=f.groupby('series_id').target.transform(lambda x:x.shift(1).rolling(w).mean())
    for col in covariates:
        if col not in known:f[col]=f.groupby('series_id')[col].shift(1)
    f['seasonal_naive']=f.groupby('series_id').target.shift(season)
    feature_groups={'calendar':['entity','calendar'],'lags':[f'lag{l}' for l in lags],'rolling':[f'roll{w}' for w in rolling],'covariates':list(covariates)}
    features=[col for group in feature_groups.values() for col in group]
    f=f.dropna(subset=features+['seasonal_naive']).reset_index(drop=True)
    dates=sorted(f.timestamp.unique())
    origins=expanding_origins(len(dates),h,max(2*season,20),n_origins)   # positions in the date index
    params={'objective':'regression','verbosity':-1,'num_threads':1,'seed':seed,'num_leaves':15,'learning_rate':.07}
    origin_cols=[col for col in feature_groups['lags']+feature_groups['rolling']]+[col for col in covariates if col not in known]   # information at the origin
    date_cols=['entity','calendar']+[col for col in covariates if col in known]                                                      # information at the target date
    def step_frame(frame,step):
        """Rows whose origin features come from row t and whose date features and target come from row t+step-1, within each series."""
        g=frame.groupby('series_id')
        out=frame[['series_id','timestamp']+origin_cols].copy()
        for col in date_cols+['target','seasonal_naive']:
            out[col]=g[col].shift(-(step-1))
        out['target_timestamp']=g['timestamp'].shift(-(step-1))
        return out.dropna(subset=['target'])
    def fit(train,cols,step):
        tf=step_frame(train,step) if strategy=='direct' else step_frame(train,1)
        return lgb.train(params,lgb.Dataset(tf[cols],label=tf.target),num_boost_round=100)
    def block(origin_pos,cols):
        cutoff=dates[origin_pos];end=dates[min(origin_pos+h,len(dates))-1]
        train=f[f.timestamp<cutoff];test=f[(f.timestamp>=cutoff)&(f.timestamp<=end)].copy()
        test['step']=test.groupby('series_id').cumcount()+1
        origin_rows=test[test.step==1].set_index('series_id')      # lags here use only pre-cutoff actuals
        rows=[]
        if strategy=='direct':
            models={step:fit(train,cols,step) for step in range(1,h+1)}
            for idx,row in test.iterrows():
                x={col:origin_rows.loc[row.series_id,col] for col in origin_cols if col in cols}
                x.update({col:row[col] for col in date_cols if col in cols})
                rows.append((idx,float(models[row.step].predict(pd.DataFrame([x],columns=cols).astype(float))[0])))
        else:
            model=fit(train,cols,1)
            for name,g in test.groupby('series_id'):
                hist=list(train[train.series_id==name].target.to_numpy())
                for idx,row in g.sort_values('timestamp').iterrows():
                    x={col:origin_rows.loc[name,col] for col in origin_cols if col in cols}
                    x.update({col:row[col] for col in date_cols if col in cols})
                    for lag in lags:
                        if f'lag{lag}' in cols:x[f'lag{lag}']=hist[-lag]
                    for w in rolling:
                        if f'roll{w}' in cols:x[f'roll{w}']=float(np.mean(hist[-w:]))
                    pred=float(model.predict(pd.DataFrame([x],columns=cols).astype(float))[0]);rows.append((idx,pred));hist.append(pred)
        test['prediction']=pd.Series(dict(rows))
        return test
    validation=[];ablation={}
    for pos in origins:
        t=block(pos,features)
        validation.append(dict(origin=str(dates[pos]),model_mae=float(abs(t.target-t.prediction).mean()),seasonal_naive_mae=float(abs(t.target-t.seasonal_naive).mean())))
        if do_ablation:
            for group,cols in feature_groups.items():
                if not cols:continue
                keep=[col for col in features if col not in cols]
                if not keep:continue
                tt=block(pos,keep)
                ablation.setdefault(group,[]).append(float(abs(tt.target-tt.prediction).mean()))
    ablation={k:dict(mean_mae=float(np.mean(v)),delta_vs_full=float(np.mean(v)-np.mean([r['model_mae'] for r in validation]))) for k,v in ablation.items()}
    final=block(len(dates)-h,features)
    test_mae=float(abs(final.target-final.prediction).mean());baseline_mae=float(abs(final.target-final.seasonal_naive).mean())
    explanation=None
    if shap_rows:
        model=fit(f[f.timestamp<dates[len(dates)-h]],features,1)
        sample=final.head(shap_rows)
        contrib=model.predict(sample[features],pred_contrib=True)
        pred=model.predict(sample[features])
        if not np.allclose(contrib.sum(axis=1),pred):raise AssertionError('SHAP additivity failed')
        explanation=[dict(zip(features+['base'],map(float,row))) for row in contrib]
    table=final[['series_id','timestamp','step','target','seasonal_naive','prediction']].rename(columns={'step':'horizon','target':'actual'})
    not_done=['Covariates not listed in known_in_advance were lagged one period; future values of known covariates must be supplied by the reader for a live forecast','No hyperparameter search: fixed LightGBM settings','Quantile or count objectives not fitted; use chapter 17 for intervals']
    if not do_ablation:not_done.append('Ablation skipped by config')
    interpretation=(f'{strategy} LightGBM: final-holdout MAE {test_mae:.4g} vs seasonal naive {baseline_mae:.4g}; validation origins {len(origins)}. '
                    +(('Ablation: dropping '+', '.join(f"{k} changes MAE by {v['delta_vs_full']:+.3g}" for k,v in ablation.items())+'. ') if ablation else '')
                    +'Contributions explain the model, not intervention effects.')
    return finish(table,method=f'LightGBM panel model ({strategy} multi-step) with declared covariates',interpretation=interpretation,
                  assumptions=['Feature timing preserved: every feature is available at the forecast origin','Known-in-advance covariates are exactly known for the horizon',f'Seasonal period {season}'],
                  not_done=not_done,status='passed',strategy=strategy,features=features,feature_groups=feature_groups,covariates=covariates,known_in_advance=known,
                  validation=validation,ablation=ablation,test_mae=test_mae,baseline_mae=baseline_mae,first_explanation=explanation,origins=[str(dates[p]) for p in origins])


def neural(groups,c):
    import torch
    from torch import nn
    seed=integer(c,'seed',14,0);torch.manual_seed(seed);torch.set_num_threads(1);rng=np.random.default_rng(seed)
    context=integer(c,'context',14);h=integer(c,'horizon',7);season=integer(c,'season',7);held=max(1,len(groups)//4);training=groups[:-held];test=groups[-held:]
    cutoff=min(len(g) for g in groups)-h
    if cutoff<max(context+10,season):raise ValueError('Insufficient pre-holdout context')
    def features(hist,t):
        scale=max(float(np.mean(abs(hist))),1e-3);return np.r_[hist/scale-1,np.sin(2*np.pi*t/season),np.cos(2*np.pi*t/season)],scale
    X=[];Y=[]
    for g in training:
        y=g.target.to_numpy()
        for t in range(context,cutoff):
            x,s=features(y[t-context:t],t);X.append(x);Y.append(y[t]/s-1)
    X=torch.tensor(np.array(X),dtype=torch.float32);Y=torch.tensor(Y,dtype=torch.float32);net=nn.Sequential(nn.Linear(context+2,24),nn.Tanh(),nn.Linear(24,2));opt=torch.optim.Adam(net.parameters(),lr=.006)
    for _ in range(integer(c,'epochs',80)):
        mu,raw=net(X).unbind(-1);sd=torch.nn.functional.softplus(raw)+.01;loss=(sd.log()+.5*((Y-mu)/sd)**2).mean();opt.zero_grad();loss.backward();opt.step()
    rows=[]
    with torch.inference_mode():
        for g in test:
            y=g.target.to_numpy();history=y[cutoff-context:cutoff];paths=[]
            for sample in range(100):
                past=list(history);future=[]
                for t in range(cutoff,cutoff+h):
                    x,s=features(np.asarray(past[-context:]),t);mu,raw=net(torch.tensor(x,dtype=torch.float32)).numpy();sd=float(torch.nn.functional.softplus(torch.tensor(raw)))+.01;value=s*(1+mu+sd*rng.normal());past.append(value);future.append(value)
                paths.append(future)
            lo,med,hi=np.quantile(paths,[.1,.5,.9],axis=0);base=np.resize(y[:cutoff][-season:],h)
            for j in range(h):rows.append(dict(series_id=g.series_id.iloc[0],timestamp=g.timestamp.iloc[cutoff+j],actual=y[cutoff+j],baseline=base[j],lower=lo[j],median=med[j],upper=hi[j]))
    table=pd.DataFrame(rows);alpha=.2;score=table.upper-table.lower+2/alpha*np.maximum(table.lower-table.actual,0)+2/alpha*np.maximum(table.actual-table.upper,0)
    return table,dict(method='Gaussian autoregressive MLP (not DeepAR)',training_entities=len(training),held_out_entities=held,coverage=float(((table.actual>=table.lower)&(table.actual<=table.upper)).mean()),interval_score=float(score.mean()),mae=float(abs(table.actual-table['median']).mean()),baseline_mae=float(abs(table.actual-table.baseline).mean()),interpretation='Entity holdout tests transfer of related patterns. 100 recursive paths provide marginal 80% bands. This small Gaussian model is not a count model; hyperparameters are predeclared, not tuned on held-out entities.')
