from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from forecasting_companion.applied.core import run,time_frame,STANDARD_STATUS
from forecasting_companion.applied.methods import analyze
FAST=[n for n in range(1,28) if n not in [13,14,15,16]]   # 13 to 16 load LightGBM, torch, Chronos and Prophet; sync_contracts.py --check covers them

@pytest.mark.parametrize('chapter',FAST)
def test_chapter_adapter_fixture(chapter):
    path=ROOT/'data/examples'/f'ch{chapter:02d}.{ "json" if chapter==10 else "csv"}'
    data=json.loads(path.read_text()) if chapter==10 else pd.read_csv(path)
    config=json.loads((ROOT/'configs'/f'ch{chapter:02d}.json').read_text())
    table,summary=analyze(chapter,data,config)
    assert len(table)>0 and summary.get('interpretation')
    assert np.isfinite(table.select_dtypes(include='number').to_numpy()).all()
    # every tool returns through core.finish: the five standard keys, a valid status, lists for the two lists
    assert {'method','interpretation','assumptions','not_done','status'}<=set(summary)
    assert summary['status'] in STANDARD_STATUS and summary['method']
    assert isinstance(summary['assumptions'],list) and isinstance(summary['not_done'],list)

def test_skill_contracts_match_live_tools():
    sys.path.insert(0,str(ROOT/'scripts'))
    import sync_contracts
    assert sync_contracts.sync(FAST,check=True)==[], 'run scripts/sync_contracts.py to refresh the skills'

def test_provisional_and_needs_evidence_paths_keep_the_contract():
    short=pd.read_csv(ROOT/'data/examples/ch04.csv').iloc[:40]
    _,s=analyze(4,short,{'horizon':12,'season':12})
    assert s['status']=='provisional' and s['not_done'] and s['method'] and s['assumptions']
    _,s=analyze(27,short,{'mode':'estimate','horizon':12})
    assert s['status']=='needs_evidence' and s['not_done'] and s['required_evidence']

def test_applied_output_isolated_and_hashes_change(tmp_path):
    inp=tmp_path/'input.csv';cfg=tmp_path/'config.json'
    pd.DataFrame({'successes':[7],'trials':[10]}).to_csv(inp,index=False)
    cfg.write_text(json.dumps({'source':'synthetic test','units':'probability'}))
    run(2,inp,cfg,tmp_path/'one');r1=json.loads((tmp_path/'one/run.json').read_text())
    pd.DataFrame({'successes':[9],'trials':[10]}).to_csv(inp,index=False)
    run(2,inp,cfg,tmp_path/'two');r2=json.loads((tmp_path/'two/run.json').read_text())
    assert r1['input_sha256']!=r2['input_sha256']
    assert pd.read_csv(tmp_path/'one/results.csv').posterior_mean.iloc[1]<pd.read_csv(tmp_path/'two/results.csv').posterior_mean.iloc[1]
    with pytest.raises(ValueError,match='separate'):run(2,inp,cfg,ROOT/'figures'/'new')
    with pytest.raises(ValueError,match='empty'):run(2,inp,cfg,tmp_path/'one')

def test_future_values_cannot_change_validation_selection():
    data=pd.read_csv(ROOT/'data/examples/ch04.csv');config={'horizon':12,'season':12}
    _,before=analyze(4,data,config);data.loc[len(data)-12:,'target']+=10000
    _,after=analyze(4,data,config)
    assert before['selected']==after['selected']
    assert before['validation']==after['validation']

def test_missing_periods_rejected():
    f=pd.read_csv(ROOT/'data/examples/ch04.csv').drop(index=30)
    with pytest.raises(ValueError,match='Irregular|Missing'):time_frame(f,{})

def test_incomplete_hierarchy_is_not_zero_filled():
    f=pd.DataFrame({'node':['Total','A'],'forecast':[10,5]})
    with pytest.raises(ValueError,match='Complete'):analyze(18,f,{'nodes':['Total','A','B'],'S':[[1,1],[1,0],[0,1]]})

def test_unidentified_survival_quantile_stays_missing():
    f=pd.DataFrame({'case_id':[1,2,3],'planned':[1,1,1],'actual':[1,2,3],'completed':[0,0,0]})
    _,s=analyze(25,f,{})
    assert s['quantiles']['0.9'] is None

def test_sparse_history_refuses_to_manufacture_forecast():
    f=pd.DataFrame({'timestamp':pd.date_range('2020-01-01',periods=4,freq='MS'),'target':[1,2,3,4]})
    table,s=analyze(27,f,{'mode':'history','horizon':12})
    assert s['status']=='needs_evidence' and 'forecast' not in table

def test_diffusion_invalid_future_rejected():
    f=pd.read_csv(ROOT/'data/examples/ch19.csv')
    with pytest.raises(ValueError):analyze(19,f,{'ceilings':[200000],'future_times':[-5,0,float('nan')]})

def test_neural_calendar_leakage_rejected():
    frames=[]
    for i in range(4):
        dates=pd.date_range('2020-01-01' if i==3 else '2025-01-01',periods=60,freq='D')
        frames.append(pd.DataFrame({'series_id':str(i),'timestamp':dates,'target':np.arange(60)+10}))
    with pytest.raises(ValueError,match='aligned calendar'):analyze(14,pd.concat(frames),{'horizon':7,'season':7,'epochs':1})

def test_pending_forecast_is_not_marked_ready(tmp_path):
    inp=tmp_path/'small.csv';cfg=tmp_path/'config.json'
    pd.DataFrame({'timestamp':pd.date_range('2020-01-01',periods=4,freq='MS'),'target':[1,2,3,4]}).to_csv(inp,index=False)
    cfg.write_text(json.dumps({'source':'synthetic','units':'units','mode':'history','horizon':12}))
    run(27,inp,cfg,tmp_path/'run')
    record=json.loads((tmp_path/'run/run.json').read_text())
    assert record['status']=='needs_evidence' and record['execution_status']=='passed'

@pytest.mark.parametrize('chapter',range(1,28))
def test_unknown_configuration_is_never_silently_ignored(chapter):
    with pytest.raises(ValueError,match='Unsupported config'):
        analyze(chapter,pd.DataFrame(),{'made_up_option':True})

def test_launch_requires_conversion_and_preserves_explicit_kernel():
    data=pd.read_csv(ROOT/'data/examples/ch27.csv');config=json.loads((ROOT/'configs/ch27.json').read_text())
    del config['trial_conversion_assumption']
    with pytest.raises(ValueError,match='trial_conversion_assumption'):analyze(27,data,config)
    config['declared_trial_total']=1000;config['repeat_kernel']=[1.]+[0.]*23
    table,summary=analyze(27,data,config)
    assert summary['trial_total']==1000
    assert np.allclose(table.units,table.trials)
    assert np.allclose(table.groupby('peak').trials.sum(),1000)
    config['declared_trial_total']=1e9
    with pytest.raises(ValueError,match='jointly reached'):analyze(27,data,config)

def test_pending_journal_is_a_valid_unscored_result():
    d={'events':[{'event_id':'pending','cutoff':'2026-01-01T00:00:00+00:00','resolved_at':None,'outcome':None,'baseline':.5}], 'revisions':[]}
    table,summary=analyze(10,d,{'as_of':'2026-09-18T00:00:00+00:00'})
    assert summary['status']=='needs_evidence' and summary['excluded_event_ids']==['pending']

def test_short_history_yields_honest_provisional_baseline():
    frame=pd.read_csv(ROOT/'data/examples/ch04.csv').iloc[:18]
    table,summary=analyze(4,frame,{'horizon':6,'season':12})
    assert len(table)==6 and summary['status']=='provisional'
    assert np.allclose(table.forecast,frame.target.iloc[-1])
    assert not summary['validation']

def test_panel_provisional_readiness_is_preserved():
    a=pd.read_csv(ROOT/'data/examples/ch04.csv').iloc[:18].copy();a['series_id']='a'
    b=a.copy();b['series_id']='b'
    _,summary=analyze(12,pd.concat([a,b]),{'horizon':6,'season':12})
    assert summary['status']=='provisional'

def test_unexcluded_companion_output_path_is_rejected(tmp_path):
    inp=ROOT/'data/examples/ch02.csv';cfg=ROOT/'configs/ch02.json'
    with pytest.raises(ValueError,match='applied-runs'):run(2,inp,cfg,ROOT/'private-client-example')

def test_inventory_infinite_cost_is_rejected():
    frame=pd.read_csv(ROOT/'data/examples/ch21.csv')
    with pytest.raises(ValueError,match='finite'):analyze(21,frame,{'overage_cost':float('inf')})

@pytest.mark.parametrize('folder',['build','front-matter'])
def test_other_packaged_publication_roots_are_protected(folder):
    with pytest.raises(ValueError,match='separate'):
        run(2,ROOT/'data/examples/ch02.csv',ROOT/'configs/ch02.json',ROOT.parent/folder/'private-client')
