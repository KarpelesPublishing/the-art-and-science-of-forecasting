"""Bundle declared public-domain observations and visibly synthetic input examples."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from forecasting_companion.applied import SCHEMAS

def main():
    real=ROOT/'data/observed';real.mkdir(exist_ok=True,parents=True);examples=ROOT/'data/examples';examples.mkdir(exist_ok=True,parents=True);configs=ROOT/'configs';configs.mkdir(exist_ok=True)
    registry=[]
    for name in ['elnino','nile','macrodata','strikes','grunfeld']:
        ds=getattr(sm.datasets,name);frame=ds.load_pandas().data.copy()
        path=real/f'{name}.csv';frame.to_csv(path,index=False)
        registry.append(dict(id=name,path=str(path.relative_to(ROOT)),source=ds.SOURCE,notes=ds.NOTE,license=ds.COPYRIGHT,package='statsmodels',version=sm.__version__,retrieved='2026-09-18',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),url=f'https://www.statsmodels.org/stable/datasets/generated/{name}.html',kind='observed historical snapshot',availability='Revised historical observations, not a real-time data vintage'))
    el=sm.datasets.elnino.load_pandas().data;temps=el.iloc[:,1:].to_numpy().ravel();monthly=pd.DataFrame({'timestamp':pd.date_range('1950-01-01',periods=len(temps),freq='MS'),'target':temps})
    monthly.to_csv(real/'monthly-temperature.csv',index=False)
    nile=sm.datasets.nile.load_pandas().data;nileframe=pd.DataFrame({'timestamp':pd.to_datetime(nile.year.astype(int).astype(str)+'-01-01'),'target':nile.volume})
    nileframe.to_csv(real/'annual-nile.csv',index=False)
    registry.extend([dict(id='monthly-temperature',path='data/observed/monthly-temperature.csv',kind='observed derived',source_id='elnino',transformation='Flatten JAN–DEC columns in year order; month-start timestamps',units='degrees Celsius, Niño 1+2 sea-surface temperature',license='Public Domain',sha256=hashlib.sha256((real/'monthly-temperature.csv').read_bytes()).hexdigest()),dict(id='annual-nile',path='data/observed/annual-nile.csv',kind='observed derived',source_id='nile',transformation='Map year to January 1; preserve annual volume',units='10^8 cubic metres',license='Public Domain',sha256=hashlib.sha256((real/'annual-nile.csv').read_bytes()).hexdigest())])
    rng=np.random.default_rng(417);n=144;t=np.arange(n);dates=pd.date_range('2010-01-01',periods=n,freq='MS');y=40+.1*t+8*np.sin(2*np.pi*t/12)+rng.normal(0,2,n);series=pd.DataFrame({'timestamp':dates,'target':y});fixtures={i:series.copy() for i in [3,4,5,6,12,15,16,21,24]}
    missing=series.copy();missing.loc[[20,21,57,90,120],'target']=np.nan;fixtures[5]=missing
    event_idx=list(range(8,n-12,9));event_dates=[dates[i] for i in event_idx];ev=series.copy();ev.loc[event_idx,'target']+=15;fixtures[16]=ev
    close=100+np.cumsum(rng.normal(size=n));op=np.r_[100,close[:-1]];fixtures[1]=pd.DataFrame({'timestamp':dates,'open':op,'close':close,'high':np.maximum(op,close)+1,'low':np.minimum(op,close)-1})
    fixtures[2]=pd.DataFrame({'successes':[7,6,8],'trials':[10,10,12]});fixtures[7]=pd.DataFrame({'component':['labor','materials','shipping'],'mean':[100,60,20],'sd':[25,15,8]})
    rows=[]
    for q in range(8):
        actual=100+q*10
        for expert in range(12):
            estimate=actual+10+rng.normal(0,20)
            for r in [1,2,3]:rows.append(dict(question=q,expert=expert,round=r,estimate=.7**(r-1)*(estimate-actual)+actual,actual=actual))
    fixtures[8]=pd.DataFrame(rows);fixtures[11]=fixtures[8].query('round == 1').drop(columns='round')
    p=rng.uniform(.1,.9,200);outcomes=rng.binomial(1,p);events=pd.DataFrame({'event_id':[f'e{i}' for i in range(200)],'probability':p,'outcome':outcomes,'baseline':.5});fixtures[9]=events;fixtures[26]=events.drop(columns='baseline')
    journal=json.loads((ROOT/'results/ch10-event-journal.json').read_text());(examples/'ch10.json').write_text(json.dumps({'events':journal['events'],'revisions':journal['revisions']},indent=2)+'\n')
    panels=[]
    for entity in range(8):
        promo=rng.binomial(1,.2,n);panels.append(pd.DataFrame({'series_id':f'item-{entity}','timestamp':dates,'target':y+entity*3+10*promo+rng.normal(0,1,n),'promo':promo,'price':10-2*promo}))
    fixtures[13]=pd.concat(panels,ignore_index=True);fixtures[14]=fixtures[13][['series_id','timestamp','target']]
    fixtures[17]=series.copy()   # plain series: the chapter tool builds and checks its own intervals
    leaf_a=60+.06*t+5*np.sin(2*np.pi*t/12)+rng.normal(0,1.5,n);leaf_b=40+.04*t+3*np.cos(2*np.pi*t/12)+rng.normal(0,1,n)
    fixtures[18]=pd.concat([pd.DataFrame({'node':k,'timestamp':dates,'target':v}) for k,v in (('Total',leaf_a+leaf_b),('A',leaf_a),('B',leaf_b))],ignore_index=True)
    time=np.arange(1,13);e=np.exp(-(.025+.35)*time);adopt=100000*(1-e)/(1+.35/.025*e);fixtures[19]=pd.DataFrame({'time':time,'adopters':adopt})
    spend_a=rng.uniform(0,100,n);spend_b=rng.uniform(0,80,n)
    from forecasting_companion.practitioner import adstock
    sa=adstock(spend_a,.5);sb=adstock(spend_b,.5);sales=100+.1*t+8*np.sin(2*np.pi*t/12)+35*sa/(80+sa)+20*sb/(80+sb)+rng.normal(0,2,n)
    fixtures[20]=pd.DataFrame({'timestamp':dates,'sales':sales,'spend_a':spend_a,'spend_b':spend_b})
    control=100+.1*t+rng.normal(size=n);control_2=80+.05*t+rng.normal(size=n);control_3=50+rng.normal(0,3,n);fixtures[22]=pd.DataFrame({'timestamp':dates,'control':control,'control_2':control_2,'control_3':control_3,'treated':12+.6*control+.4*control_2+8*(t>=100)+rng.normal(size=n)})
    rows=[];start=pd.Timestamp('2020-01-01');delay=np.array([.2,.3,.25,.15,.1])
    for i in range(50):
        counts=rng.multinomial(rng.poisson(100),delay)
        for lag,count in enumerate(counts):rows.append(dict(event_date=start+pd.Timedelta(days=i),report_date=start+pd.Timedelta(days=i+lag),count=count))
    fixtures[23]=pd.DataFrame(rows);ratio=rng.lognormal(.3,.5,60);complete=ratio<2;fixtures[25]=pd.DataFrame({'case_id':range(60),'planned':12,'actual':12*np.minimum(ratio,2),'completed':complete})
    fixtures[27]=pd.read_csv(ROOT/'results/ch27-reference-products.csv')
    for chapter,frame in fixtures.items():frame.to_csv(examples/f'ch{chapter:02d}.csv',index=False)
    for chapter in range(1,28):
        cfg={'source':'Seeded synthetic educational input; not business observations','units':'illustrative units','horizon':12,'season':12,'seed':417,'outcome_due':'Declare before issuing a real forecast'}
        if chapter==10:cfg.update(as_of='2026-09-18T00:00:00+00:00',units='binary event probabilities')
        if chapter==16:cfg.update(events=[{'name':'launch','date':str(d.date()),'lower_window':0,'upper_window':1} for d in event_dates],priors=[.001,.05,.5],origins=2)
        if chapter==17:cfg.update(alpha=.2,pool='smoothing',calibration_size=36,test_size=24,origins=3)
        if chapter==18:cfg.update(edges=[['A','Total'],['B','Total']],pool='smoothing',shrinkage=.2,origins=3)
        if chapter==19:cfg.update(ceilings=[110000,150000,200000],units='cumulative unique adopters')
        if chapter==22:cfg.update(intervention=str(dates[100].date()),identification='Synthetic controlled generator; treated-only shock absent by construction',controls=['control','control_2','control_3'],placebos=100)
        if chapter==21:cfg.update(lead_time=2,review_period=1,service_level=.95,echelons=3)
        if chapter==20:cfg.update(channels=['spend_a','spend_b'],saturation='auto',origins=3,windows=3)
        if chapter==23:cfg.update(as_of='2020-02-15',mature_age=5,population=1000000,units='cases')
        if chapter==5:cfg.update(model='local level',seasonal=True,origins=3)
        if chapter==27:cfg.update(mode='launch',horizon=24,trial_conversion_assumption='Synthetic teaching assumption: mature-sales scale transfers to trial; not identified by mature-sales fit',new_product={'eligible_buyers':120000,'awareness':.65,'availability_given_awareness':.7,'interest':.28},repeat_rate=.15,units='triers and purchase units, separately')
        if chapter in [13,14]:cfg['horizon']=7
        (configs/f'ch{chapter:02d}.json').write_text(json.dumps(cfg,indent=2)+'\n')
    for chapter in [3,4,6,12,15,16]:
        cfg=json.loads((configs/f'ch{chapter:02d}.json').read_text());cfg.update(source='Public-domain statsmodels El Niño observations, 1950–2010; historical revised snapshot',units='degrees Celsius');(configs/f'ch{chapter:02d}-observed.json').write_text(json.dumps(cfg,indent=2)+'\n')
    for chapter in [5,24]:
        cfg=json.loads((configs/f'ch{chapter:02d}.json').read_text());cfg.update(source='Public-domain statsmodels Nile annual flow, 1871–1970',units='10^8 cubic metres',season=1,horizon=10)
        if chapter==5:cfg.update(seasonal=False)
        if chapter==24:cfg.update(calibration_size=20)
        (configs/f'ch{chapter:02d}-observed.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (ROOT/'data/registry.json').write_text(json.dumps(registry,indent=2)+'\n')
    print('Bundled five public-domain datasets, two derived time series, 27 input examples and configurations.')
if __name__=='__main__':main()
