"""Input contracts and reproducible, isolated applied runs."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

SCHEMAS = {
1:'timestamp,open,high,low,close',2:'successes,trials',3:'timestamp,target',4:'timestamp,target',
5:'timestamp,target (empty target allowed)',6:'timestamp,target',7:'component,mean,sd',8:'question,expert,round,estimate,actual',
9:'event_id,probability,outcome,baseline',10:'events,revisions (JSON)',11:'question,expert,estimate,actual',
12:'timestamp,target',13:'series_id,timestamp,target[,covariates...]',14:'series_id,timestamp,target',
15:'timestamp,target',16:'timestamp,target[,regressors...]',17:'timestamp,target | timestamp,actual,lower,median,upper',18:'node,timestamp,target | node,forecast',
19:'time,adopters',20:'timestamp,sales,<channels...>[,controls...]',21:'timestamp,target',22:'timestamp,control,treated[,controls...]',
23:'event_date,report_date,count',24:'timestamp,target',25:'case_id,planned,actual,completed',
26:'event_id,probability,outcome',27:'eligible_buyers,awareness,availability_given_awareness,interest,units_per_buyer_24m,observed_units_24m,split'}

def require(frame, columns):
    missing=set(columns)-set(frame.columns)
    if missing: raise ValueError('Missing columns: '+', '.join(sorted(missing)))
    if frame.empty: raise ValueError('Input has no rows')

def numeric(frame, columns, nonnegative=False):
    require(frame, columns)
    values=frame[columns].apply(pd.to_numeric,errors='raise').to_numpy(float)
    if not np.isfinite(values).all(): raise ValueError('Numeric inputs must be finite and complete')
    if nonnegative and np.any(values<0): raise ValueError('Negative values are not valid for '+', '.join(columns))
    return values

def probability(values):
    a=np.asarray(values,float)
    if not np.isfinite(a).all() or np.any((a<0)|(a>1)): raise ValueError('Probabilities must lie in [0,1]')
    return a

def integer(config,key,default,minimum=1):
    v=config.get(key,default)
    if isinstance(v,bool) or not isinstance(v,int) or v<minimum: raise ValueError(f'{key} must be an integer >= {minimum}')
    return v

def time_frame(frame,config,columns=('target',),minimum=24,allow_missing=False):
    """Validate a regular series. allow_missing=True permits empty target cells (chapter 5 only);
    timestamps must still be complete and the non-missing count must reach the minimum."""
    require(frame,['timestamp',*columns]); f=frame.copy()
    f['timestamp']=pd.to_datetime(f.timestamp,errors='raise',utc=True)
    if f.timestamp.isna().any() or f.timestamp.duplicated().any(): raise ValueError('Timestamps must be present and unique per series')
    f=f.sort_values('timestamp')
    if config.get('as_of'): f=f[f.timestamp<=pd.to_datetime(config['as_of'],utc=True)]
    if allow_missing:
        f['target']=pd.to_numeric(f['target'],errors='raise')
        if f['target'].notna().sum()<minimum: raise ValueError(f'At least {minimum} observed values are required')
        others=[c for c in columns if c!='target']
        if others: numeric(f,others)
    else:
        if len(f)<minimum: raise ValueError(f'At least {minimum} observations are required; do not infer seasonality from sparse history')
        numeric(f,list(columns))
    freq=config.get('frequency') or (pd.infer_freq(f.timestamp) if len(f)>=3 else None)
    if freq is None: raise ValueError('Irregular timestamps: supply a justified regular frequency and resolve missing periods explicitly')
    if not pd.DatetimeIndex(f.timestamp).equals(pd.date_range(f.timestamp.iloc[0],periods=len(f),freq=freq)):
        raise ValueError('Missing periods or timestamps inconsistent with frequency')
    return f,freq

def result(table,**summary):
    return pd.DataFrame(table),summary

def expanding_origins(n,h,min_train,max_origins=5):
    """Origins spaced h apart before an untouched final holdout of h; the engine's rule."""
    final_start=n-h; room=final_start-min_train
    k=int(min(max_origins,room//h)) if room>=0 else 0   # earliest origin keeps min_train observations in the first slice
    if k<2: raise ValueError(f'at least {min_train+3*h} observations are needed for two selection origins plus a final holdout')
    return [final_start-j*h for j in range(k,0,-1)]

STANDARD_STATUS={'passed','provisional','needs_evidence'}

def finish(table,*,method,interpretation,assumptions,not_done=(),status='passed',**extra):
    """Every applied tool ends here so the five standard summary keys are always present."""
    if status not in STANDARD_STATUS: raise ValueError(f'status must be one of {sorted(STANDARD_STATUS)}')
    if not interpretation: raise ValueError('interpretation is required')
    summary=dict(method=method,interpretation=interpretation,assumptions=list(assumptions),not_done=list(not_done),status=status)
    summary.update(extra)
    return pd.DataFrame(table),summary

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def diagnostic_chart(table,summary,config,chapter,path):
    """One honest picture of the returned table: the forecast (with its band and any actuals) when the
    table has one, otherwise the last numeric columns. Nothing is drawn that the table does not contain."""
    from ..common import plt
    fig,ax=plt.subplots(figsize=(7,4))
    cols=set(table.columns);nums=table.select_dtypes(include='number')
    x=pd.to_datetime(table['timestamp'],errors='coerce',utc=True) if 'timestamp' in cols else None
    if x is None or x.isna().any():x=np.arange(len(table));xlabel='Result row (see results.csv)'
    else:xlabel='Date'
    point=next((c for c in ('forecast','prediction','median','nowcast','filtered_state','estimate') if c in cols),None)
    if point is not None and 'series_id' not in cols and 'node' not in cols and 'ceiling' not in cols:
        if 'actual' in cols:ax.plot(x,table['actual'],color='.35',lw=1,label='actual')
        if 'observed' in cols:ax.plot(x,table['observed'],color='.35',lw=1,label='observed')
        ax.plot(x,table[point],color='#163d59',lw=1.6,label=point)
        lo,hi=next(((a,b) for a,b in (('lower','upper'),('split_lower','split_upper'),('empirical_q10','empirical_q90'),('q10','q90')) if a in cols and b in cols),(None,None))
        if lo:ax.fill_between(x,table[lo],table[hi],color='#163d59',alpha=.15,label=f'{lo} to {hi}')
        ax.legend(fontsize=8,frameon=False)
    elif len(nums.columns):
        chosen=[c for c in nums.columns if c not in ('interval_level','alpha_t','horizon','post','relative_period')][-3:] or list(nums.columns[-3:])
        for c in chosen:ax.plot(x,table[c],lw=1.2,label=c)
        ax.legend(fontsize=8,frameon=False)
    else:ax.text(.05,.5,summary.get('interpretation','See summary.json'),wrap=True);ax.set_axis_off()
    ax.set(xlabel=xlabel,ylabel=config.get('units',''),title=f'Chapter {chapter}: {summary.get("method","applied result")}'[:90])
    fig.autofmt_xdate() if xlabel=='Date' else None
    fig.tight_layout();fig.savefig(path,dpi=150);plt.close(fig)

def preview(table,rows=12,digits=3):
    """The first rows of a result table with numbers rounded and timestamps shown as dates, for printing."""
    t=table.head(rows).copy()
    for c in t.columns:
        if pd.api.types.is_numeric_dtype(t[c]) and not pd.api.types.is_bool_dtype(t[c]):t[c]=t[c].round(digits)
        elif pd.api.types.is_datetime64_any_dtype(t[c]):t[c]=pd.to_datetime(t[c]).dt.strftime('%Y-%m-%d')
    return t.to_string(index=False)

def summarize(summary,table=None,max_list=6):
    """A short reading of a tool summary for notebooks and the CLI: the five standard keys, then the
    scalar evidence. Long nested structures (per-origin tables, predictions) are counted, not printed."""
    def fmt(v):
        if isinstance(v,(float,np.floating)):return f'{v:.4g}'
        if isinstance(v,(int,np.integer,str,bool)) or v is None:return str(v)
        if isinstance(v,dict):
            if len(v)<=max_list and all(not isinstance(x,(dict,list)) for x in v.values()):return ', '.join(f'{k}={fmt(x)}' for k,x in v.items())
            return f'<{len(v)} entries>'
        if isinstance(v,(list,tuple,np.ndarray)):
            v=list(v)
            if len(v)<=max_list and all(not isinstance(x,(dict,list)) for x in v):return '['+', '.join(fmt(x) for x in v)+']'
            return f'<{len(v)} rows>'
        return str(v)
    lines=[f'Method: {summary.get("method")}',f'Status: {summary.get("status")}','',f'Interpretation: {summary.get("interpretation")}','']
    if summary.get('assumptions'):lines+=['Assumptions:']+[f'  - {a}' for a in summary['assumptions']]
    if summary.get('not_done'):lines+=['Not done:']+[f'  - {a}' for a in summary['not_done']]
    rest={k:v for k,v in summary.items() if k not in ('method','status','interpretation','assumptions','not_done','chapter','source','units')}
    if rest:lines+=['','Evidence:']+[f'  {k}: {fmt(v)}' for k,v in rest.items()]
    if table is not None:lines+=['',f'Table: {len(table)} rows, columns {list(table.columns)}']
    return '\n'.join(lines)

def clean_json(value):
    if isinstance(value,dict): return {str(k):clean_json(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,np.ndarray)): return [clean_json(v) for v in value]
    if isinstance(value,(np.bool_,)):return bool(value)
    if isinstance(value,(np.integer,)):return int(value)
    if isinstance(value,(float,np.floating)):return float(value) if np.isfinite(value) else None
    if isinstance(value,(pd.Timestamp,Path)):return str(value)
    return value

def run(chapter,input_path,config_path,output):
    from .methods import analyze
    from datetime import datetime,timezone
    from importlib.metadata import version,PackageNotFoundError
    from ..common import plt
    root=Path(__file__).resolve().parents[3]
    output=Path(output).resolve(); source=Path(input_path).resolve(); cfgpath=Path(config_path).resolve()
    # Protect publication and implementation trees, including symlink aliases.
    protected=[root/'figures',root/'results',root/'notebooks',root/'lessons',root/'src',root/'scripts',root/'data',root/'revision',root/'reports',root/'configs',root/'tests',root.parent/'forecasting-skills',root.parent/'manuscript',root.parent/'build',root.parent/'front-matter']
    if output==root or output==root.parent or any(output==p.resolve() or p.resolve() in output.parents for p in protected):
        raise ValueError('Use a separate applied-runs directory, outside publication/source/data folders')
    if root in output.parents and not (root/'applied-runs'==output or root/'applied-runs' in output.parents):
        raise ValueError('Inside companion, applied outputs must be under applied-runs so private results are excluded from bundles')
    if output.exists() and any(output.iterdir()):raise ValueError('Output directory must be empty; choose a new run name')
    config=json.loads(cfgpath.read_text())
    if not config.get('source') or not config.get('units'):raise ValueError('Config must declare source and units')
    if not isinstance(chapter,int) or chapter not in SCHEMAS:raise ValueError('Chapter must be 1–27')
    data=json.loads(source.read_text()) if chapter==10 else pd.read_csv(source)
    table,summary=analyze(chapter,data,config)
    if not np.isfinite(table.select_dtypes(include='number').to_numpy()).all():raise ValueError('Nonfinite result values; inspect model and inputs')
    output.mkdir(parents=True,exist_ok=True)
    table.to_csv(output/'results.csv',index=False)
    summary={'chapter':chapter,'source':config['source'],'units':config['units'],**summary}
    (output/'summary.json').write_text(json.dumps(clean_json(summary),indent=2,allow_nan=False)+'\n')
    diagnostic_chart(table,summary,config,chapter,output/'diagnostic.png')
    versions={}
    for name in ['numpy','pandas','scipy','statsmodels','lightgbm','torch','prophet','chronos-forecasting']:
        try:versions[name]=version(name)
        except PackageNotFoundError:versions[name]=None
    files={str(p.relative_to(root)):sha(p) for p in sorted((root/'src').rglob('*.py'))}
    if summary.get('status') not in STANDARD_STATUS:raise AssertionError('Every tool must return status through core.finish')
    record={'created_at':datetime.now(timezone.utc).isoformat(),'chapter':chapter,'config':config,'input_path':str(source),'input_sha256':sha(source),'config_sha256':sha(cfgpath),'code':files,'versions':versions,'outputs':{p.name:sha(p) for p in output.iterdir() if p.is_file()},'status':summary['status'],'execution_status':'passed','outcome_due':config.get('outcome_due'),'actual_outcome':None}
    (output/'run.json').write_text(json.dumps(clean_json(record),indent=2,allow_nan=False)+'\n')
    return summary
